from PyQt6 import QtWidgets, QtCore,QtGui
from core import diffengine, highlightengine
from ui.textviewer import DrapDropTextEdit
import logging
from util import helper,enumtypes

logger = logging.getLogger(__name__)


class Ui_MainWindow_2(object):
    def setupUi(self, MainWindow:QtWidgets.QMainWindow):
        self.MainWindow=MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1124, 901)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_left_load = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_left_load.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_left_load, 2, 2, 1, 1)
        self.textEdit_master = DrapDropTextEdit(ui=self, parent=self.centralwidget, alias="左窗口")
        self.textEdit_master.setMinimumSize(QtCore.QSize(550, 763))
        self.textEdit_master.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit_master, 1, 0, 1, 2)
        self.textEdit_slave = DrapDropTextEdit(ui=self,parent=self.centralwidget,master=self.textEdit_master, alias="右窗口")
        self.textEdit_master.bindslave(self.textEdit_slave)
        self.textEdit_slave.setMinimumSize(QtCore.QSize(550, 763))
        self.textEdit_slave.setObjectName("textEdit_2")
        self.gridLayout.addWidget(self.textEdit_slave, 1, 2, 1, 2)
        self.pushButton_refresh_diff = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_refresh_diff.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_refresh_diff.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_refresh_diff, 3, 0, 1, 2)
        self.pushButton_right_save = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_right_save.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_right_save, 2, 3, 1, 1)
        self.pushButton_right_load = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_right_load.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton_right_load, 2, 0, 1, 1)
        self.pushButton_next_diff = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_next_diff.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_next_diff.setObjectName("pushButton_6")
        self.gridLayout.addWidget(self.pushButton_next_diff, 3, 2, 1, 2)
        self.label_right = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_right.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_right, 0, 2, 1, 1)
        self.pushButton_left_save = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_left_save.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_left_save, 2, 1, 1, 1)
        self.label_left = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_left.setObjectName("label")
        self.gridLayout.addWidget(self.label_left, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1124, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self._diff_engine=diffengine.DiffEngine_sync()
        self._highlight_engine=highlightengine.HighLightEngine()
        self.textEdit_master.sync_scroll_bar()
        self.textEdit_slave.sync_scroll_bar()
        shortcut=QtGui.QShortcut(QtGui.QKeySequence("F5"),MainWindow)
        shortcut.activated.connect(self.diffandrefresh)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), MainWindow)
        shortcut.activated.connect(self.handle_search)

        self._last_focus=self.textEdit_master._alias
        
        self.pushButton_refresh_diff.setShortcut("F5")
        self.pushButton_refresh_diff.clicked.connect(self.diffandrefresh)
        self.pushButton_next_diff.clicked.connect(self.handle_next_diff)
        #self.pushButton_next_diff.setEnabled(False)
        self.pushButton_right_load.clicked.connect(self.textEdit_master.uploadfile)
        self.textEdit_slave.bindsavebutton(self.pushButton_right_save)
        self.textEdit_master.bindsavebutton(self.pushButton_left_save)
        self.textEdit_master.bindlabel(self.label_left)
        self.textEdit_slave.bindlabel(self.label_right)
        self.pushButton_left_load.clicked.connect(self.textEdit_slave.uploadfile)
        self.pushButton_left_save.clicked.connect(self.textEdit_master.save_current_text_tofile)
        self.pushButton_left_save.setEnabled(False)
        self.pushButton_right_save.clicked.connect(self.textEdit_slave.save_current_text_tofile)
        self.pushButton_right_save.setEnabled(False)
        self.textEdit_master.bind_last_focus(self.set_last_focus)
        self.textEdit_slave.bind_last_focus(self.set_last_focus)
        


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow:QtWidgets.QMainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BaiNvCompare  V2.0.1"))
        self.pushButton_refresh_diff.setText(_translate("MainWindow", "刷新差异 (F5)"))
        self.pushButton_right_save.setText(_translate("MainWindow", "保存"))
        self.pushButton_left_load.setText(_translate("MainWindow", "导入"))
        self.pushButton_right_load.setText(_translate("MainWindow", "导入"))
        self.pushButton_left_save.setText(_translate("MainWindow", "保存"))
        self.label_right.setText(_translate("MainWindow", "编辑模式"))
        self.label_left.setText(_translate("MainWindow", "编辑模式"))
        self.pushButton_next_diff.setText(_translate("MainWindow", "下一处原始差异"))

    def diffandrefresh(self):
        warning_box = None
        try:
            self.textEdit_master.prepare_original_data()
            logging.debug(f"debug {self.textEdit_master._alias}original dict{self.textEdit_master._original_list}")
        except helper.InvaildInputError as e:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"invalid input in left window at line {int(e.args[0])+1}",
            )
            warning_box.exec()
        try:
            self.textEdit_slave.prepare_original_data()
            logging.debug(f"debug {self.textEdit_slave._alias}original dict{self.textEdit_slave._original_dict}")
        except helper.InvaildInputError as e:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"invalid input in right window at line {int(e.args[0])+1}",
            )
            warning_box.exec()
        if warning_box is None:
            master_new_content,slave_new_content,diff_list=self._diff_engine.string_all_and_parsed_diff_2(self.textEdit_master._original_list, self.textEdit_slave._original_dict)
            self.textEdit_master.NewPlainText(master_new_content)
            self.textEdit_slave.NewPlainText(slave_new_content)
            self.textEdit_master._textmode=enumtypes.TextMode.DIFF
            self.textEdit_slave._textmode=enumtypes.TextMode.DIFF
            self.textEdit_master._original_extraselections=self._highlight_engine.extraselectLines(diff_list, self.textEdit_master,False, self.textEdit_master._alias)
            self.textEdit_slave._original_extraselections=self._highlight_engine.extraselectLines(diff_list, self.textEdit_slave,True, self.textEdit_slave._alias)
            

    
    def handle_search(self):
        if self._last_focus==self.textEdit_master._alias:
            self.textEdit_master.search_in_editor()
            self.textEdit_slave.verticalScrollBar().setValue(self.textEdit_master.verticalScrollBar().value())
            self.textEdit_slave.setFocus()
            self.textEdit_master.setFocus()
        elif  self._last_focus==self.textEdit_slave._alias:
            self.textEdit_slave.search_in_editor()
            self.textEdit_master.verticalScrollBar().setValue(self.textEdit_slave.verticalScrollBar().value())
            self.textEdit_master.setFocus()
            self.textEdit_slave.setFocus()
        
            
    def handle_next_diff(self):
        if self.textEdit_master._textmode==enumtypes.TextMode.DIFF and self.textEdit_master._textmode==enumtypes.TextMode.DIFF:
            logger.debug(f"self._last_focus:{self._last_focus}, master scroll bar value:{self.textEdit_master.verticalScrollBar().value()}, slave scroll bar value:{self.textEdit_slave.verticalScrollBar().value()}")
            if  self._last_focus==self.textEdit_master._alias:
                self.textEdit_master.find_next_extraselection()
                self.textEdit_slave.verticalScrollBar().setValue(self.textEdit_master.verticalScrollBar().value())
                self.textEdit_slave.setFocus()
                self.textEdit_master.setFocus()
            elif  self._last_focus==self.textEdit_slave._alias:
                self.textEdit_slave.find_next_extraselection()
                self.textEdit_master.verticalScrollBar().setValue(self.textEdit_slave.verticalScrollBar().value())
                self.textEdit_master.setFocus()
                self.textEdit_slave.setFocus()

        else:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"Make sure you have refreshed their diff.",
            )
            warning_box.exec()
    
    def on_focus_out_edit1(self, e:QtGui.QFocusEvent):
        # 如果plain_text_edit1失去焦点，则将焦点设置到plain_text_edit2
        if not self.textEdit_slave.hasFocus():
            self.textEdit_slave.setFocus()
        # 调用原始的 focusOutEvent
        QtWidgets.QPlainTextEdit.focusOutEvent(self.textEdit_master, e)
        
    def on_focus_out_edit2(self, e:QtGui.QFocusEvent):
        # 如果plain_text_edit1失去焦点，则将焦点设置到plain_text_edit2
        if not self.textEdit_master.hasFocus():
            self.textEdit_master.setFocus()
        # 调用原始的 focusOutEvent
        QtWidgets.QPlainTextEdit.focusOutEvent(self.textEdit_slave, e)
        

    def focus_in_edit1(self,e:QtGui.QFocusEvent):
        self._last_focus=0
    def focus_in_edit2(self,e:QtGui.QFocusEvent):
        self._last_focus=1
        
    def set_last_focus(self,focus:str|int):
        self._last_focus=focus
        