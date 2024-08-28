from PyQt6 import QtWidgets, QtCore, QtGui
from core import diffengine, modifyengine, highlightengine
import util.helper as helper
import util.filemanger as filemanger
import logging
import util.enumtypes as enumtypes

logger = logging.getLogger(__name__)


class LineNumberEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(LineNumberEditor, self).__init__(parent)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.lineNumberArea = LineNumberArea(self)
        self._highlight_engine = highlightengine.HighLightEngine()

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)
        # self.cursorPositionChanged.connect(self.highlightCurrentLine)

    def lineNumberAreaPaintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor(QtCore.Qt.GlobalColor.lightGray))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        self.cursorRect().y()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).y()
        )
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0,
                    top,
                    self.lineNumberArea.width(),
                    self.fontMetrics().height(),
                    QtCore.Qt.AlignmentFlag.AlignRight,
                    str(blockNumber + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def resizeEvent(self, e):
        super().resizeEvent(e)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QtCore.QRect(
                cr.left(),
                cr.top(),
                self.lineNumberArea.lineNumberAreaWidth(),
                cr.height(),
            )
        )

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberArea.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0, rect.y(), self.lineNumberArea.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def highlightCurrentLine(self):
        cursor = self.textCursor()
        self._highlight_engine.highlightCurrentLine(cursor, self.setExtraSelections)


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor: LineNumberEditor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QtCore.QSize(self.lineNumberAreaWidth(), 0)

    def lineNumberAreaWidth(self):
        digits = len(str(self.codeEditor.blockCount())) + 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def paintEvent(self, a0):
        self.codeEditor.lineNumberAreaPaintEvent(a0)


class DrapDropTextEdit(LineNumberEditor):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        master: "DrapDropTextEdit|None" = None,
        alias: str = "",
    ):
        super(DrapDropTextEdit, self).__init__(parent)
        self._master = master
        self._alias = alias
        self._original_content = ""
        self._file_original_full_path = None
        self._numberofmodification = 0
        self._lastmodified_block_number = None
        self._editbyuser = True
        self._textmode = enumtypes.TextMode.FROMUSER
        self._translate = QtCore.QCoreApplication.translate
        self._original_dict = {}
        self._original_list = []
        self._original_extraselections: list[QtWidgets.QTextEdit.ExtraSelection] = []
        self._new_extraselections = []
        self._diff_dict = {}
        self._cursor_last_block_number = 0
        self._cursor_last_block_length = 0
        self._cursor_last_last_block_number = 0
        self._cursor_last_last_block_length = 0
        self._line_highlighted = True

        self.setAcceptDrops(True)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)

        self.cursorPositionChanged.connect(
            self.update_cursor_status
        )  # 保证新插入的东西能正常被标记（粘贴和插入）
        self.textChanged.connect(self.update_extraselections)

        self._diff_engine = diffengine.DiffEngine()
        self._modify_engine = modifyengine.ModifyEngine()

    def bindsavebutton(self, button: QtWidgets.QPushButton):
        self.savebutton = button

    def bindlabel(self, label: QtWidgets.QLabel):
        self.label = label
        self.label.setText(self._translate("MainWindow", "手动编辑模式"))

    def bindslave(self, textedit: QtWidgets.QPlainTextEdit):
        self._slave = textedit

    def sync_scroll_bar(
        self,
    ):  # 'self' scroll value is influenced by opponent scroll bar
        if self._master is not None:
            self._master.verticalScrollBar().valueChanged.connect(
                lambda: self.verticalScrollBar().setValue(
                    self._master.verticalScrollBar().value()
                )
            )
        else:
            self._slave.verticalScrollBar().valueChanged.connect(
                lambda: self.verticalScrollBar().setValue(
                    self._slave.verticalScrollBar().value()
                )
            )

    def update_cursor_status(self):
        cursor = self.textCursor()
        logger.debug(f"cursor changed to line: {cursor.blockNumber()}")

        new_block_number = cursor.blockNumber()
        new_block_length = cursor.block().length()
        if (
            self._cursor_last_block_number == new_block_number
            and self._cursor_last_last_block_number != new_block_number
        ):
            self._line_highlighted = False
        self._cursor_last_last_block_number = self._cursor_last_block_number
        # self._cursor_last_last_block_length=self.document().findBlockByLineNumber(self._cursor_last_last_block_number).length()
        self._cursor_last_block_number = new_block_number
        # self._cursor_last_last_block_length=new_block_length

    def highlight_cursor(self):
        if self._editbyuser == False:
            return
        self._editbyuser = False
        cursor = self.textCursor()
        if not cursor.hasSelection():
            self._highlight_engine.highlight_cursor(self, "cyan")
        logger.debug(
            f"user changed cursor position, the cursor is changed color. line: {cursor.blockNumber()}, line column is: {cursor.columnNumber()}, line content is:{cursor.block().text()}"
        )
        self._editbyuser = True

    def update_extraselections(self):
        if self._editbyuser == False:
            return
        cursor = self.textCursor()
        block_number = cursor.blockNumber()
        logger.debug(f"text changed, current block number is {block_number}, cursor last block number is {self._cursor_last_block_number}, cursor last last block number is {self._cursor_last_last_block_number}")

        if self._cursor_last_last_block_number < block_number:  # newlines
            # if self._cursor_last_last_block_length!=self.document().findBlockByLineNumber(self._cursor_last_last_block_number).length():
            # self._extraselections.append(self._highlight_engine.extraselectLine(self,self._cursor_last_last_block_number))
            for i in range(self._cursor_last_last_block_number, block_number + 1):
                self._new_extraselections.append(
                    self._highlight_engine.extraselectLine(self, i)
                )
                logger.debug(f"current block number:{i}")
        elif (
            self._cursor_last_last_block_number >= block_number
        ):  # deletions and same line edit
            self._new_extraselections.append(
                self._highlight_engine.extraselectCurrentLine(self)
            )
        self._lastmodified_block_number = block_number
        self.setExtraSelections(
            self._original_extraselections + self._new_extraselections
        )

    def highlight_modified_lines(self):
        if self._editbyuser == False:
            return
        cursor = self.textCursor()
        linenumber = cursor.blockNumber()
        if self._lastmodified_block_number == linenumber:
            return
        self._lastmodified_block_number = linenumber
        cursor.select(cursor.SelectionType.LineUnderCursor)
        logger.debug(f"{self._alias}: text changed:{cursor.block().text()}")
        self._highlight_engine.highlight_cursor_with_selection(cursor)
        logger.info(
            f"{self._alias}: highligh a modified line: {cursor.blockNumber()}, line column is: {cursor.columnNumber()}, line content is:{cursor.block().text()}"
        )

    def dropEvent(self, e: QtGui.QDropEvent):
        super().dropEvent(e)
        for url in e.mimeData().urls():
            logger.debug(f"{self._alias}: received file: {url}")
            logger.debug(f"{self._alias}: received file: {url.toLocalFile()}")
            if url.isLocalFile():
                path = url.toLocalFile()
                logger.info(f"{self._alias}: file full path is {path}")
                self._open_file(path)
        self.setFocus()

    def uploadfile(self):
        logger.debug(f"{self._alias}: test read file")
        file_path, file2 = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open tgz and text file", "", "All Files (*)"
        )
        if file_path == "":
            return
        logger.info(f"{self._alias}: file full path is  {file_path}")
        self._open_file(file_path)

    def _open_file(self, fullpath: str):
        self._editbyuser = False
        root, ext = helper.split_filename(fullpath)
        self._file_original_full_path = fullpath
        if ext.endswith("gz"):
            self.textfilenameingz, self._original_content = (
                filemanger.load_tgz_to_string(fullpath)
            )
            self._highlight_engine.highlight_cursor(self, "normal")
            self.setPlainText(self._original_content)
        else:
            self._original_content = filemanger.load_textfile_to_string(fullpath)
            self._highlight_engine.highlight_cursor(self, "normal")
            self.setPlainText(self._original_content)
        self._original_extraselections = []
        self._new_extraselections = []
        self._highlight_engine.clearExtraselections(self)
        self.savebutton.setText(self._translate("MainWindow", f"保存到文件"))
        self._textmode = enumtypes.TextMode.FROMFILE
        self.label.setText(
            self._translate(
                "MainWindow", f"文件编辑模式: {self._file_original_full_path}"
            )
        )
        self.prepare_original_data()
        self.savebutton.setEnabled(True)
        self.setFocus()
        self._editbyuser = True

    def save_current_text_tofile(self):
        self._editbyuser = False
        if self._file_original_full_path is None:
            logger.critical(f"{self._alias}: undefined save action")
            return
        current_content = self.toPlainText()
        if (
            self._textmode == enumtypes.TextMode.FROMFILE
            or self._textmode == enumtypes.TextMode.DIFF
        ):
            # 查询改动量，保存全文到文件
            try:
                keyvaluecount, sectioncount = self._modify_engine.record_modification(
                    self._original_dict, current_content
                )
            except helper.InvaildInputError as e:
                logger.info(
                    f"{self._alias}: invaild input error at line {int(e.args[0])+1}"
                )
                critical_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Warning,
                    "warning",
                    f"invalid input at line {int(e.args[0])+1}",
                )
                critical_box.exec()
                return
            try:
                if self._file_original_full_path.endswith("gz"):
                    filemanger.save_string_to_tgz(
                        current_content,
                        self._file_original_full_path,
                        self.textfilenameingz,
                    )
                else:
                    filemanger.save_string_to_textfile(
                        current_content, self._file_original_full_path
                    )
            except PermissionError as e:
                logger.info(f"{self._alias}: save file error:{e}")
                critical_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Warning,
                    "warning",
                    f"Save file error: Please check if the file path exists and is available for writing.",
                )
                critical_box.exec()
                return
            except Exception as e:
                logger.error(f"{self._alias}: save file error:{e}")
                critical_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Critical,
                    "critical",
                    f"崩了，只能看看日志发生了什么",
                )
                critical_box.exec()
                return
            self._original_content = current_content
            self.prepare_original_data()
            # self._highlight_engine.highlight_cursor(self, "normal")
            # self.NewPlainText(self._original_content)
            information_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Information,
                "Saved Successfully",
                f"There are {keyvaluecount} key-value lines and {sectioncount} node changed by you.",
            )
            logger.info(
                f"There are {keyvaluecount} key-value lines and {sectioncount} node changed by you."
            )
            information_box.exec()

        else:
            logger.critical(f"{self._alias}: unknown textmode:{self._textmode.name}")
        self._editbyuser = False

    def construct_diff_dict(self, opponent_dict: dict[str, dict[str, str]]):
        self._diff_dict = self._diff_engine.diff_dict_by_dict(
            self._original_content, opponent_dict, self._alias
        )

    def output_diff_dict(self):
        self._editbyuser = False
        self.clear()
        cursor = self.textCursor()

        self._diff_engine.output_diff_dict(self._diff_dict, cursor.insertText)

        logger.debug(f"{self._alias}: switch to DIFF MODE")
        self._textmode = enumtypes.TextMode.DIFF
        self.savebutton.setText(self._translate("MainWindow", f"同步差异到文件"))
        self.savebutton.setEnabled(True)
        self.label.setText(
            self._translate(
                "MainWindow", f"差异编辑模式: {self._file_original_full_path}"
            )
        )
        self._editbyuser = True

    def prepare_original_data(self):
        if (
            self._textmode == enumtypes.TextMode.FROMFILE
            or self._textmode == enumtypes.TextMode.DIFF
        ):
            logger.debug(f"{self._alias}: using the existing content to compute dict")
        elif self._textmode == enumtypes.TextMode.FROMUSER:
            logger.debug(f"{self._alias}: using the content in window to compute dict")
            self._original_content = self.toPlainText()

        if self._master is None:
            self._original_list = helper.parse_string_tolist(self._original_content)
        logger.info(f"{self._alias} has prepared its original list")
        self._original_dict = helper.parse_string_todict(self._original_content)
        logger.info(f"{self._alias} has prepared its original dict")

    def search_in_editor(self):
        # 从文本的开头开始查找
        # editor.moveCursor(QtGui.QTextCursor.MoveOperation.Start)  # 将光标移动到文本的起始位置
        # 弹出搜索框
        logger.debug("show search dialog")
        text, ok = QtWidgets.QInputDialog.getText(
            self.parent(), f"Search in {self._alias}", "根据光标位置搜索下一个:"
        )
        if ok and text:
            # 查找文本
            found = self.find(text)

            if not found:
                self.moveCursor(QtGui.QTextCursor.MoveOperation.Start)
                found = self.find(text)
                if not found:
                    warning_box = QtWidgets.QMessageBox(
                        QtWidgets.QMessageBox.Icon.Warning,
                        "warning",
                        f" {self._alias}中没有找到哦",
                    )
                    warning_box.exec()

    def NewPlainText(self, content: str):
        self._editbyuser = False
        self.clear()
        self.setCurrentCharFormat(QtGui.QTextCharFormat())
        self.setPlainText(content)
        self._original_extraselections = []
        self._editbyuser = True

    def find_next_extraselection(self):
        currentblocknumber = self.textCursor().blockNumber()
        for extraselection in self._original_extraselections:
            extraselectionblock = extraselection.cursor.block()
            if extraselectionblock.isValid():
                extraselectionblocknumber = extraselectionblock.blockNumber()
                logger.debug(f"current block : {currentblocknumber}, extraselection block : {extraselectionblocknumber}")
                if currentblocknumber < extraselectionblocknumber:
                    logger.info(f"found the next diff at block: {extraselectionblocknumber}")
                    self.setTextCursor(extraselection.cursor)
                    self.moveCursor(QtGui.QTextCursor.MoveOperation.EndOfBlock)
                    self.setFocus() 
                    return
        warning_box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Icon.Warning,
            "warning",
            f" {self._alias} 从光标到文件底，没有找到下一个差异",
        )
        warning_box.exec()
