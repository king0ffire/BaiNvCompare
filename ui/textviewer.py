from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QTextCharFormat
from core import diffengine, modifyengine, highlightengine
import util.helper as helper
import util.filemanger as filemanger
import logging
import util.enumtypes as enumtypes

logger = logging.getLogger(__name__)


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QtCore.QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class DrapDropTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(DrapDropTextEdit, self).__init__(parent)
        self.originalcontent = ""
        self.fileoriginalfullpath = None
        self.setAcceptDrops(True)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.lineNumberArea = LineNumberArea(self)

        self.textChanged.connect(self.updateLineNumberAreaWidth)
        self.verticalScrollBar().valueChanged.connect(self.updateLineNumberArea)
        # self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.highlight_modified_lines)
        self.updateLineNumberAreaWidth()
        # self.highlightCurrentLine()
        self.modified_lines = set()
        self.editbyuser = True
        self.textmode = enumtypes.TextMode.FROMUSER
        self._translate = QtCore.QCoreApplication.translate
        self._original_dict = {}
        self._diff_dict = {}

        self._diff_engine = diffengine.DiffEngine()
        self._highlight_engine = highlightengine.HighLightEngine()
        self._modify_engine = modifyengine.ModifyEngine()

    def bindsavebutton(self, button: QtWidgets.QPushButton):
        self.savebutton = button

    def bindlabel(self, label: QtWidgets.QLabel):
        self.label = label
        self.label.setText(self._translate("MainWindow", "手动编辑模式"))

    def highlight_modified_lines(self):
        if self.editbyuser == False:
            return
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        line_number = cursor.blockNumber()
        logger.debug(f"text changed:{cursor.block().text()}")
        if line_number not in self.modified_lines:
            self.modified_lines.add(line_number)
            self._highlight_engine.highlight_user_modified_line(cursor)
            logger.debug(
                f"highligh a modified line: {cursor.blockNumber()}, line column is: {cursor.columnNumber()}, line content is:{cursor.block().text()}"
            )

    def dropEvent(self, e: QtGui.QDropEvent):
        logger.debug("drop event")
        for url in e.mimeData().urls():
            logger.debug(f"received file: {url}")
            logger.debug(f"received file: {url.toLocalFile()}")
            if url.isLocalFile():
                path = url.toLocalFile()
                self.openfilepath(path)

    def uploadfile(self):
        logger.debug(f"test read file")
        self.modified_lines = set()
        file_name, file2 = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open tgz and text file", "", "All Files (*)"
        )
        if file_name == "":
            return
        logger.debug(f"file name {file_name}")
        logger.debug(f"file name {file2}")
        self.openfilepath(file_name)

    def openfilepath(self, fullpath: str):
        self.editbyuser = False
        root, ext = helper.split_filename(fullpath)
        self.fileoriginalfullpath = fullpath
        if ext.endswith("gz"):
            self.textfilenameingz, self.originalcontent = filemanger.load_tgz_to_string(
                fullpath
            )
            self.setCurrentCharFormat(QTextCharFormat())
            self.setPlainText(self.originalcontent)
        else:
            self.originalcontent = filemanger.load_textfile_to_string(fullpath)
            self.setCurrentCharFormat(QTextCharFormat())
            self.setPlainText(self.originalcontent)

        self.savebutton.setEnabled(True)
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
            logger.critical(f"undefined save action")
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
            if self.fileoriginalfullpath.endswith("gz"):
                filemanger.save_string_to_tgz(content, self.fileoriginalfullpath)
            else:
                filemanger.save_string_to_textfile(content, self.fileoriginalfullpath)
            self.originalcontent = content
            self.setCurrentCharFormat(QTextCharFormat())
            self.setPlainText(self.originalcontent)
        elif self.textmode == enumtypes.TextMode.DIFF:
            try:
                self.originalcontent = self._modify_engine.process_diff_modification(
                    self.originalcontent, self.toPlainText(), self._diff_dict
                )
            except helper.InvaildInputError as e:
                warning_box = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Icon.Warning,
                    "warning",
                    f"invalid input at line {e}",
                )
                warning_box.exec()
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
        else:
            logger.critical(f"unknown textmode:{self.textmode.name}")

    def construct_diff_dict(self, opponent_dict: dict[str, dict[str, str]]):
        self._diff_dict = helper.diff_dict_by_dict(self.originalcontent, opponent_dict)

    def output_diff_dict(self):
        self.editbyuser = False
        self.clear()
        cursor = self.textCursor()

        self._diff_engine.output_diff_dict(self._diff_dict, cursor.insertText)

        logger.debug("switch to DIFF MODE")
        self.textmode = enumtypes.TextMode.DIFF
        self.savebutton.setText(
            self._translate("MainWindow", f"同步差异到文件")
        )
        self.label.setText(
            self._translate("MainWindow", f"差异编辑模式: {self.fileoriginalfullpath}")
        )
        self.editbyuser = True

    def lineNumberAreaWidth(self):
        digits = len(str(self.document().blockCount())) + 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, dy):
        self.lineNumberArea.scroll(0, dy)
        logger.debug(f"scroll value {dy}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtCore.Qt.GlobalColor.lightGray)
        # 获取首个可见文本块
        first_visible_block_number = self.cursorForPosition(
            QtCore.QPoint(0, 1)
        ).blockNumber()
        # 从首个文本块开始处理
        blockNumber = first_visible_block_number

        block = self.document().findBlockByNumber(blockNumber)
        top = self.viewport().geometry().top()
        if blockNumber == 0:
            additional_margin = int(
                self.document().documentMargin()
                - 1
                - self.verticalScrollBar().sliderPosition()
            )
        else:
            prev_block = self.document().findBlockByNumber(blockNumber - 1)
            additional_margin = (
                int(
                    self.document()
                    .documentLayout()
                    .blockBoundingRect(prev_block)
                    .bottom()
                )
                - self.verticalScrollBar().sliderPosition()
            )
        top += additional_margin
        bottom = top + int(
            self.document().documentLayout().blockBoundingRect(block).height()
        )
        last_block_number = self.cursorForPosition(
            QtCore.QPoint(0, self.height() - 1)
        ).blockNumber()
        height = self.fontMetrics().height()
        while (
            block.isValid()
            and (top <= event.rect().bottom())
            and blockNumber <= last_block_number
        ):
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.GlobalColor.black)
                painter.drawText(
                    0,
                    top,
                    self.lineNumberArea.width(),
                    height,
                    QtCore.Qt.AlignmentFlag.AlignCenter,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + int(
                self.document().documentLayout().blockBoundingRect(block).height()
            )
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QtWidgets.QPlainTextEdit.ExtraSelection()
            lineColor = QtGui.QColor(QtCore.Qt.GlobalColor.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(
                QtGui.QTextFormat.TextUnderlineStyle,
                QtWidgets.QTextFormat.UnderlineStyle.NoUnderline,
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def prepareoriginaldict(self):
        if (
            self.textmode == enumtypes.TextMode.FROMFILE
            or self.textmode == enumtypes.TextMode.DIFF
        ):
            logger.debug(f"using the saved content to compute dict")
            self._original_dict = helper.parse_string(self.originalcontent)
        elif self.textmode == enumtypes.TextMode.FROMUSER:
            logger.debug(f"using the content in window to compute dict")
            self.originalcontent = self.toPlainText()
            self._original_dict = helper.parse_string(self.originalcontent)

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
