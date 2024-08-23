from PyQt6 import QtWidgets,QtCore,QtGui
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6 import QtCore, QtGui, QtWidgets
import util
import time
import file
import logging
import text
import enumtypes
import copy
logger=logging.getLogger(__name__)

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
        self.fileoriginalcontent=""
        self.fileoriginalfullpath=None
        self.setAcceptDrops(True)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.lineNumberArea = LineNumberArea(self)

        self.textChanged.connect(self.updateLineNumberAreaWidth)
        self.verticalScrollBar().valueChanged.connect(self.updateLineNumberArea)
        #self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.highlight_modified_lines)
        self.updateLineNumberAreaWidth()
        #self.highlightCurrentLine()
        self.modified_lines = set()
        self.editbyuser=True
        self.textmode=enumtypes.TextMode.FROMUSER
        self._translate = QtCore.QCoreApplication.translate
        self.demandedOriginalDict={}
        self.diff_dict={}
        
        
    def bindsavebutton(self,button:QtWidgets.QPushButton):
        self.savebutton=button
        
    def bindlabel(self,label:QtWidgets.QLabel):
        self.label=label
        self.label.setText(self._translate("MainWindow", "手动编辑模式"))

    def highlight_modified_lines(self):
        if self.editbyuser==False:
            return 
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        line_number = cursor.blockNumber()
        logger.debug(f"text changed:{cursor.block().text()}")
        if line_number not in self.modified_lines:
            self.modified_lines.add(line_number)
            self.highlight_line(cursor)
            logger.debug(f"highligh a modified line: {cursor.blockNumber()}, line column is: {cursor.columnNumber()}, line content is:{cursor.block().text()}")

    def highlight_line(self, cursor:QtGui.QTextCursor):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(QtCore.Qt.GlobalColor.cyan))  
        cursor.setCharFormat(fmt)
        
    def dropEvent(self,  e: QtGui.QDropEvent):
        logger.debug("drop event")
        for url in e.mimeData().urls(): 
            logger.debug(f"received file: {url}")
            logger.debug(f"received file: {url.toLocalFile()}")
            if url.isLocalFile():
                path=url.toLocalFile()
                self.openfilepath(path)
                
    def uploadfile(self):
        logger.debug(f"test read file")
        self.modified_lines = set()
        file_name,file2=QtWidgets.QFileDialog.getOpenFileName(self, "Open tgz and text file", "", "All Files (*)")
        if file_name=="":
            return
        logger.debug(f"file name {file_name}")
        logger.debug(f"file name {file2}")
        self.openfilepath(file_name)
    
    def openfilepath(self,fullpath:str):
        self.editbyuser=False
        root,ext=util.split_filename(fullpath)
        self.fileoriginalfullpath=fullpath
        if ext.endswith("gz"):
            self.textfilenameingz,self.fileoriginalcontent=file.load_tgz_to_string(fullpath)
            self.setCurrentCharFormat(QTextCharFormat())
            self.setPlainText(self.fileoriginalcontent)
        else:
            self.fileoriginalcontent=file.load_textfile_to_string(fullpath)
            self.setCurrentCharFormat(QTextCharFormat())
            self.setPlainText(self.fileoriginalcontent)
            
        self.savebutton.setEnabled(True)
        self.savebutton.setText(self._translate("MainWindow", f"保存到文件(功能未完成)"))
        self.textmode=enumtypes.TextMode.FROMFILE
        self.label.setText(self._translate("MainWindow", f"文件编辑模式: {self.fileoriginalfullpath}"))
        self.editbyuser=True
                    
    def savecurrenttextintofile(self):
        if self.fileoriginalfullpath is None:
            logger.critical(f"undefined save action")
            return
        content = self.toPlainText()
        if self.textmode==enumtypes.TextMode.FROMFILE: 
            #直接保存，不会有任何解析
            if self.fileoriginalfullpath.endswith("gz"):
                file.save_string_to_tgz(content,self.fileoriginalfullpath)
            else:
                file.save_string_to_textfile(content,self.fileoriginalfullpath)
            self.fileoriginalcontent=content
            self.setCurrentCharFormat(QTextCharFormat())
            self.setPlainText(self.fileoriginalcontent)
        elif self.textmode==enumtypes.TextMode.DIFF:
            try:
                self.parsedifftomodifycontent()
                if self.fileoriginalfullpath.endswith("gz"):
                    file.save_string_to_tgz(self.fileoriginalcontent,self.fileoriginalfullpath,self.textfilenameingz)
                else:
                    file.save_string_to_textfile(self.fileoriginalcontent,self.fileoriginalfullpath)
            except file.InvaildInputError as e:
                warning_box=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning,"warning",f"invalid input at line {e}")
                warning_box.exec()
        else:
            logger.critical(f"unknown textmode:{self.textmode.name}") 
            
    def parsedifftomodifycontent(self):#直接修改fileoriginalcontent
        newdiffdict=file.parse_diff_string(self.toPlainText())

        self.fileoriginalcontent=file.modify_string_by_diff(self.fileoriginalcontent,file.diff_diff_dict(copy.deepcopy(self.diff_dict), newdiffdict))
        
        
    
    def lineNumberAreaWidth(self):
        digits = len(str(self.document().blockCount())) + 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    def updateLineNumberArea(self, dy):
        self.lineNumberArea.scroll(0, dy)
        logger.debug(f"scroll value {dy}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtCore.Qt.GlobalColor.lightGray)
        # 获取首个可见文本块
        first_visible_block_number = self.cursorForPosition(QtCore.QPoint(0, 1)).blockNumber()
        # 从首个文本块开始处理
        blockNumber = first_visible_block_number
        
        block = self.document().findBlockByNumber(blockNumber)
        top = self.viewport().geometry().top()
        if blockNumber == 0:
            additional_margin = int(self.document().documentMargin() - 1 - self.verticalScrollBar().sliderPosition())
        else:
            prev_block = self.document().findBlockByNumber(blockNumber - 1)
            additional_margin = int(self.document().documentLayout().blockBoundingRect(
                prev_block).bottom()) - self.verticalScrollBar().sliderPosition()
        top += additional_margin
        bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
        last_block_number = self.cursorForPosition(QtCore.QPoint(0, self.height() - 1)).blockNumber()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()) and blockNumber <= last_block_number:
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.GlobalColor.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, QtCore.Qt.AlignmentFlag.AlignCenter, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.document().documentLayout().blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QtWidgets.QPlainTextEdit.ExtraSelection()
            lineColor =QtGui.QColor(QtCore.Qt.GlobalColor.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.TextUnderlineStyle, QtWidgets.QTextFormat.UnderlineStyle.NoUnderline)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)
        
        
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
        
        
        
    def demandingDict(self):
        if self.textmode==enumtypes.TextMode.FROMFILE or self.textmode==enumtypes.TextMode.DIFF:
            logger.debug(f"using the saved content to compute dict")
            self.demandedOriginalDict = file.parse_string(self.fileoriginalcontent)
        elif self.textmode==enumtypes.TextMode.FROMUSER:
            logger.debug(f"using the content in window to compute dict")
            self.demandedOriginalDict = file.parse_string(self.toPlainText())


class Ui_MainWindow_2(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1124, 901)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 2, 2, 1, 1)
        self.textEdit = DrapDropTextEdit(parent=self.centralwidget)
        self.textEdit.setMinimumSize(QtCore.QSize(550, 763))
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 2)
        self.textEdit_2 = DrapDropTextEdit(parent=self.centralwidget)
        self.textEdit_2.setMinimumSize(QtCore.QSize(550, 763))
        self.textEdit_2.setObjectName("textEdit_2")
        self.gridLayout.addWidget(self.textEdit_2, 1, 2, 1, 2)
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 3, 0, 1, 4)
        self.pushButton_5 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 2, 3, 1, 1)
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1124, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        
        
        self.pushButton_3.clicked.connect(self.refresh_diff)
        self.pushButton.clicked.connect(self.textEdit.uploadfile)
        self.textEdit_2.bindsavebutton(self.pushButton_5)
        self.textEdit.bindsavebutton(self.pushButton_4)
        self.textEdit.bindlabel(self.label)
        self.textEdit_2.bindlabel(self.label_2)
        self.pushButton_2.clicked.connect(self.textEdit_2.uploadfile)
        self.pushButton_4.clicked.connect(self.textEdit.savecurrenttextintofile)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.clicked.connect(self.textEdit_2.savecurrenttextintofile)  
        self.pushButton_5.setEnabled(False)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_3.setText(_translate("MainWindow", "刷新差异"))
        self.pushButton_5.setText(_translate("MainWindow", "保存"))
        self.pushButton_2.setText(_translate("MainWindow", "导入"))
        self.pushButton.setText(_translate("MainWindow", "导入"))
        self.pushButton_4.setText(_translate("MainWindow", "保存"))
        self.label_2.setText(_translate("MainWindow", "编辑模式"))
        self.label.setText(_translate("MainWindow", "编辑模式"))
        
    def refresh_diff(self):
        try:
            self.textEdit.demandingDict()
            self.textEdit_2.demandingDict()
            self.textEdit_2.output_diff_by_stringindict(copy.deepcopy(self.textEdit.demandedOriginalDict))
            self.textEdit.output_diff_by_stringindict(copy.deepcopy(self.textEdit_2.demandedOriginalDict))
            logging.debug(f"debug demandingdict{self.textEdit.demandedOriginalDict}")
        except file.InvaildInputError as e:
            warning_box=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning,"warning",f"invalid input at line {e}")
            warning_box.exec()
