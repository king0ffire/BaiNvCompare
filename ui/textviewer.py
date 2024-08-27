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

    def resizeEvent(self, event):
        super().resizeEvent(event)

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

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class DrapDropTextEdit(LineNumberEditor):
    def __init__(self, parent=None, alias=None):
        super(DrapDropTextEdit, self).__init__(parent)
        self.alias = alias
        self.originalcontent = ""
        self.fileoriginalfullpath = None
        self.numberofmodification = 0
        self.setAcceptDrops(True)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)

        self.cursorPositionChanged.connect(
            self.highlight_cursor
        )  # 保证新插入的东西能正常被标记（粘贴和插入）
        self.textChanged.connect(self.highlight_modified_lines)
        # self.modified_lines = set()
        self._lastmodified_line = None
        self.editbyuser = True
        self.textmode = enumtypes.TextMode.FROMUSER
        self._translate = QtCore.QCoreApplication.translate
        self._original_dict = {}
        self._diff_dict = {}
        self.cursorhighlighted = False

        self._diff_engine = diffengine.DiffEngine()
        # self._highlight_engine = highlightengine.HighLightEngine()
        self._modify_engine = modifyengine.ModifyEngine()

    def bindsavebutton(self, button: QtWidgets.QPushButton):
        self.savebutton = button

    def bindlabel(self, label: QtWidgets.QLabel):
        self.label = label
        self.label.setText(self._translate("MainWindow", "手动编辑模式"))

    def highlight_cursor(self):
        if self.editbyuser == False:
            return
        self.editbyuser = False
        cursor = self.textCursor()
        if not cursor.hasSelection():
            self._highlight_engine.highlight_cursor(self, "cyan")
        logger.debug(
            f"user changed cursor position, the cursor is changed color. line: {cursor.blockNumber()}, line column is: {cursor.columnNumber()}, line content is:{cursor.block().text()}"
        )
        self.editbyuser = True

    def highlight_modified_lines(self):
        if self.editbyuser == False:
            return
        cursor = self.textCursor()
        linenumber = cursor.blockNumber()
        if self._lastmodified_line == linenumber:
            return
        self._lastmodified_line = linenumber
        cursor.select(cursor.SelectionType.LineUnderCursor)
        logger.debug(f"{self.alias}: text changed:{cursor.block().text()}")
        self._highlight_engine.highlight_cursor_with_selection(cursor)
        logger.info(
            f"{self.alias}: highligh a modified line: {cursor.blockNumber()}, line column is: {cursor.columnNumber()}, line content is:{cursor.block().text()}"
        )

    def dropEvent(self, e: QtGui.QDropEvent):
        for url in e.mimeData().urls():
            logger.debug(f"{self.alias}: received file: {url}")
            logger.debug(f"{self.alias}: received file: {url.toLocalFile()}")
            if url.isLocalFile():
                path = url.toLocalFile()
                logger.info(f"{self.alias}: file full path is {path}")
                self.openfilepath(path)

    def uploadfile(self):
        logger.debug(f"{self.alias}: test read file")
        self.modified_lines = set()
        file_name, file2 = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open tgz and text file", "", "All Files (*)"
        )
        if file_name == "":
            return
        logger.info(f"{self.alias}: file full path is  {file_name}")
        self.openfilepath(file_name)

    def openfilepath(self, fullpath: str):
        self.editbyuser = False
        root, ext = helper.split_filename(fullpath)
        self.fileoriginalfullpath = fullpath
        if ext.endswith("gz"):
            self.textfilenameingz, self.originalcontent = filemanger.load_tgz_to_string(
                fullpath
            )
            self._highlight_engine.highlight_cursor(self, "normal")
            self.setPlainText(self.originalcontent)
        else:
            self.originalcontent = filemanger.load_textfile_to_string(fullpath)
            self._highlight_engine.highlight_cursor(self, "normal")
            self.setPlainText(self.originalcontent)

        self.savebutton.setEnabled(False)
        self.savebutton.setText(
            self._translate("MainWindow", f"保存到文件(功能未完成)")
        )
        self.textmode = enumtypes.TextMode.FROMFILE
        self.label.setText(
            self._translate("MainWindow", f"文件编辑模式: {self.fileoriginalfullpath}")
        )
        self.editbyuser = True

    def savecurrenttextintofile(self):
        if self.fileoriginalfullpath is None:
            logger.critical(f"{self.alias}: undefined save action")
            return
        content = self.toPlainText()
        """
        if self.textmode==enumtypes.TextMode.DIFF:
            try:
                self.originalcontent=self._modify_engine.process_diff_modification(self)
            except helper.InvaildInputError as e:
                warning_box=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning,"warning",f"invalid input at line {e}")
                warning_box.exec()
        if self.fileoriginalfullpath.endswith("gz"):
            filemanger.save_string_to_tgz(content,self.fileoriginalfullpath)
        else:
            filemanger.save_string_to_textfile(content,self.fileoriginalfullpath)
        """

        if self.textmode == enumtypes.TextMode.FROMFILE:
            # 直接保存，不会有任何解析
            try:
                if self.fileoriginalfullpath.endswith("gz"):
                    filemanger.save_string_to_tgz(content, self.fileoriginalfullpath)
                else:
                    filemanger.save_string_to_textfile(
                        content, self.fileoriginalfullpath
                    )
            except Exception as e:
                logger.info(f"{self.alias}: save file error:{e}")
                warning_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Warning,
                    "warning",
                    f"Save file error: Please check if the file path exists and is available for writing.",
                )
                warning_box.exec()
                return
            self.originalcontent = content
            self._highlight_engine.highlight_cursor(self, "normal")
            self.setPlainText(self.originalcontent)
        elif self.textmode == enumtypes.TextMode.DIFF:
            try:
                self.originalcontent, self.numberofmodification = self._modify_engine.process_diff_modification(
                    self.originalcontent, self.toPlainText(), self._diff_dict,self.alias
                )
            except helper.InvaildInputError as e:
                logger.info(f"{self.alias}: invaild input error {e}")
                warning_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Warning,
                    "warning",
                    f"invalid input at line {e}",
                )
                warning_box.exec()
            try:
                if self.fileoriginalfullpath.endswith("gz"):
                    filemanger.save_string_to_tgz(
                        self.originalcontent,
                        self.fileoriginalfullpath,
                        self.textfilenameingz,
                    )
                else:
                    filemanger.save_string_to_textfile(
                        self.originalcontent, self.fileoriginalfullpath
                    )
            except Exception as e:
                logger.info(f"{self.alias}: save file error:{e}")
                warning_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Warning,
                    "warning",
                    f"Save file error: Please check if the file path exists and is available for writing.",
                )
                warning_box.exec()
            information_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Information,
                "Saved Successfully",
                f"There are {self.numberofmodification} key-value lines changed in the file.",
            )
            information_box.exec()
        else:
            logger.critical(f"{self.alias}: unknown textmode:{self.textmode.name}")

    def construct_diff_dict(self, opponent_dict: dict[str, dict[str, str]]):
        self._diff_dict = self._diff_engine.diff_dict_by_dict(
            self.originalcontent, opponent_dict,self.alias
        )

    def output_diff_dict(self):
        self.editbyuser = False
        self.clear()
        cursor = self.textCursor()

        self._diff_engine.output_diff_dict(self._diff_dict, cursor.insertText)

        logger.debug(f"{self.alias}: switch to DIFF MODE")
        self.textmode = enumtypes.TextMode.DIFF
        self.savebutton.setText(self._translate("MainWindow", f"同步差异到文件"))
        self.savebutton.setEnabled(True)
        self.label.setText(
            self._translate("MainWindow", f"差异编辑模式: {self.fileoriginalfullpath}")
        )
        self.editbyuser = True

    def prepareoriginaldict(self):
        if (
            self.textmode == enumtypes.TextMode.FROMFILE
            or self.textmode == enumtypes.TextMode.DIFF
        ):
            logger.debug(f"{self.alias}: using the saved content to compute dict")
            self._original_dict = helper.parse_string(self.originalcontent)
        elif self.textmode == enumtypes.TextMode.FROMUSER:
            logger.debug(f"{self.alias}: using the content in window to compute dict")
            self.originalcontent = self.toPlainText()
            self._original_dict = helper.parse_string(self.originalcontent)

    def search_in_editor(self):
        # 从文本的开头开始查找
        # editor.moveCursor(QtGui.QTextCursor.MoveOperation.Start)  # 将光标移动到文本的起始位置
        # 弹出搜索框
        logger.debug("show search dialog")
        text, ok = QtWidgets.QInputDialog.getText(
            self.parent(), f"Search in {self.alias}", "根据光标位置搜索下一个:"
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
                        f" {self.alias}中没有找到哦",
                    )
                    warning_box.exec()

    """    
    def output_diff_by_stringindict(self,opponent_dict:dict):
        self.editbyuser=False
        self.clear()
        self.diff_dict={}
        green_format = QTextCharFormat()
        green_format.setBackground(QColor("green"))
        yellow_format = QTextCharFormat()
        yellow_format.setBackground(QColor("yellow"))
        red_format = QTextCharFormat()
        red_format.setBackground(QColor("red"))
        normal_format = QTextCharFormat()
        
        logger.info("start compare diff by string")
        if self.fileoriginalfullpath is None:
            content=self.toPlainText()
        else:
            content=self.fileoriginalcontent
        lines=content.split('\n')
        current_section=None
        self.diff_dict[current_section]={}
        sectionhasdifference=False
        cursor=self.textCursor()
        for line in lines:
            line=line.strip()
            logger.debug(f"line has {line}; section has value:{sectionhasdifference}")
            if line.startswith('[') and line.endswith(']'):
                if current_section in opponent_dict:
                    for key,value in opponent_dict[current_section].items():
                        logger.debug(f"missing section:{current_section},key:{key},value:{value}")
                        cursor.insertText(f"missing:{key} = {value}\n",red_format)
                        self.diff_dict[current_section][key]=(value,enumtypes.DiffType.REMOVED)
                    del opponent_dict[current_section]            
                if sectionhasdifference == False:
                    cursor.movePosition(QtGui.QTextCursor.MoveOperation.PreviousBlock,cursor.MoveMode.KeepAnchor)
                    logger.debug(f"clearing {cursor.block().text()}")
                    cursor.removeSelectedText()
                    logger.debug(f"after clearing {cursor.block().text()}")
                current_section=line[1:-1]
                logger.debug(f"current section={current_section}")
                self.diff_dict[current_section]={}
                sectionhasdifference=False
                logger.debug(f"new section:{current_section}")
                cursor.insertText(f"{line}\n",normal_format) 
            elif '=' in line:             
                key,value =line.split('=',1)
                key=key.strip()
                value=value.strip()
                if current_section in opponent_dict and key in opponent_dict[current_section]:
                    if value!=opponent_dict[current_section][key]:
                        logger.debug(f"insert yellow: section:{current_section},key:{key},value:{value}")
                        cursor.insertText(f"{line}\n",yellow_format)
                        self.diff_dict[current_section][key]=(value,enumtypes.DiffType.MODIFIED)
                        sectionhasdifference=True
                    del opponent_dict[current_section][key]
                else:
                    logger.debug(f"insert green: section:{current_section},key:{key},value:{value}")
                    cursor.insertText(f"{line}\n",green_format)
                    self.diff_dict[current_section][key]=(value,enumtypes.DiffType.ADDED)
                    sectionhasdifference=True
        if current_section in opponent_dict:
            for key,value in opponent_dict[current_section].items():
                logger.debug(f"missing section:{current_section},key:{key},value:{value}")
                cursor.insertText(f"missing:{key} = {value}\n",red_format)
                self.diff_dict[current_section][key]=(value,enumtypes.DiffType.REMOVED)
            del opponent_dict[current_section]            
        if sectionhasdifference == False:
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.PreviousBlock,cursor.MoveMode.KeepAnchor)
            logger.debug(f"clearing {cursor.block().text()}")
            cursor.removeSelectedText()
            logger.debug(f"after clearing {cursor.block().text()}")
        current_section = None
        
        
        logger.debug(f"missing sections:{opponent_dict}")
        cursor.movePosition(cursor.MoveOperation.End,cursor.MoveMode.MoveAnchor)
        logger.debug(
            f"cursor line number:{cursor.block().lineCount()},cursor block content:{cursor.block().text()}"
        )
        for missing_section in opponent_dict:
            logger.debug(
                f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
            )
            cursor.insertText(f"missing section:[{missing_section}]\n",red_format)
            current_section=missing_section
            self.diff_dict[missing_section]={}
            logger.debug(f"currrent missing section:[{missing_section}]")
            for key, value in opponent_dict[missing_section].items():
                logger.debug(f"=========missing start=========")
                logger.debug(
                    f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                )
                cursor.insertText(f"missing:{key} = {value}\n",red_format)
                self.diff_dict[current_section][key]=(value,enumtypes.DiffType.REMOVED)
                logger.debug(
                    f"cursor position:{cursor.position()},cursor block content:{cursor.block().text()}"
                )
                logger.debug(f"=========missing stop=========")
                
        logger.debug("switch to DIFF MODE") 
        self.textmode=enumtypes.TextMode.DIFF
        self.savebutton.setText(self._translate("MainWindow", f"同步差异到文件(功能未完成)"))
        self.label.setText(self._translate("MainWindow", f"差异编辑模式: {self.fileoriginalfullpath}"))
        self.editbyuser=True
        
    """
