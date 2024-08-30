from PyQt6 import QtWidgets, QtCore,QtGui
from core import diffengine, highlightengine
from ui.textviewer import DrapDropTextEdit
import logging
from util import helper,enumtypes

logger = logging.getLogger(__name__)


class Ui_MainWindow_2(object):
    def setupUi(self, MainWindow:QtWidgets.QMainWindow):
        self._translate = QtCore.QCoreApplication.translate
        self.MainWindow=MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_next_diff = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)    
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_next_diff.sizePolicy().hasHeightForWidth())
        self.pushButton_next_diff.setSizePolicy(sizePolicy)
        self.pushButton_next_diff.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_next_diff.setObjectName("pushButton_next_diff")
        self.gridLayout.addWidget(self.pushButton_next_diff, 4, 3, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_right_mode = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_right_mode.sizePolicy().hasHeightForWidth())
        self.label_right_mode.setSizePolicy(sizePolicy)
        self.label_right_mode.setObjectName("label_right_mode")
        self.horizontalLayout_2.addWidget(self.label_right_mode)
        self.label_right_path = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_right_path.sizePolicy().hasHeightForWidth())
        self.label_right_path.setSizePolicy(sizePolicy)
        self.label_right_path.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_right_path.setObjectName("label_right_path")
        self.horizontalLayout_2.addWidget(self.label_right_path)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 2, 1, 2)
        self.plainTextEdit_master = DrapDropTextEdit(ui=self,parent=self.centralwidget,alias="左窗口")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit_master.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_master.setSizePolicy(sizePolicy)
        self.plainTextEdit_master.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.plainTextEdit_master.setObjectName("plainTextEdit_master")
        self.gridLayout.addWidget(self.plainTextEdit_master, 1, 0, 1, 2)
        self.plainTextEdit_slave = DrapDropTextEdit(ui=self,master=self.plainTextEdit_master,parent=self.centralwidget,alias="右窗口")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit_slave.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_slave.setSizePolicy(sizePolicy)
        self.plainTextEdit_slave.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.plainTextEdit_slave.setObjectName("plainTextEdit_slave")
        self.gridLayout.addWidget(self.plainTextEdit_slave, 1, 2, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_left_mode = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_left_mode.sizePolicy().hasHeightForWidth())
        self.label_left_mode.setSizePolicy(sizePolicy)
        self.label_left_mode.setObjectName("label_left_mode")
        self.horizontalLayout.addWidget(self.label_left_mode)
        self.label_left_path = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_left_path.sizePolicy().hasHeightForWidth())
        self.label_left_path.setSizePolicy(sizePolicy)
        self.label_left_path.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_left_path.setObjectName("label_left_path")
        self.horizontalLayout.addWidget(self.label_left_path)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.pushButton_left_load = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_left_load.sizePolicy().hasHeightForWidth())
        self.pushButton_left_load.setSizePolicy(sizePolicy)
        self.pushButton_left_load.setObjectName("pushButton_left_load")
        self.gridLayout.addWidget(self.pushButton_left_load, 3, 0, 1, 1)
        self.pushButton_refresh_diff = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_refresh_diff.sizePolicy().hasHeightForWidth())
        self.pushButton_refresh_diff.setSizePolicy(sizePolicy)
        self.pushButton_refresh_diff.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_refresh_diff.setObjectName("pushButton_refresh_diff")
        self.gridLayout.addWidget(self.pushButton_refresh_diff, 4, 0, 1, 2)
        self.pushButton_previous_diff = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_previous_diff.sizePolicy().hasHeightForWidth())
        self.pushButton_previous_diff.setSizePolicy(sizePolicy)
        self.pushButton_previous_diff.setMinimumSize(QtCore.QSize(0, 40))
        self.pushButton_previous_diff.setObjectName("pushButton_previous_diff")
        self.gridLayout.addWidget(self.pushButton_previous_diff, 4, 2, 1, 1)

        self.pushButton_left_save = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_left_save.sizePolicy().hasHeightForWidth())
        self.pushButton_left_save.setSizePolicy(sizePolicy)
        self.pushButton_left_save.setObjectName("pushButton_left_save")
        self.gridLayout.addWidget(self.pushButton_left_save, 3, 1, 1, 1)
        self.pushButton_right_save = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_right_save.sizePolicy().hasHeightForWidth())
        self.pushButton_right_save.setSizePolicy(sizePolicy)
        self.pushButton_right_save.setObjectName("pushButton_right_save")
        self.gridLayout.addWidget(self.pushButton_right_save, 3, 3, 1, 1)
        self.pushButton_right_load = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_right_load.sizePolicy().hasHeightForWidth())
        self.pushButton_right_load.setSizePolicy(sizePolicy)
        self.pushButton_right_load.setObjectName("pushButton_right_load")
        self.gridLayout.addWidget(self.pushButton_right_load, 3, 2, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_4.addWidget(self.lineEdit)
        self.pushButton_search_next = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_search_next.setObjectName("pushButton_search_next")
        self.horizontalLayout_4.addWidget(self.pushButton_search_next)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        logger.debug("ui component init")
        
        self.plainTextEdit_master.bindslave(self.plainTextEdit_slave)
        self._diff_engine=diffengine.DiffEngine_sync()
        self._highlight_engine=highlightengine.HighLightEngine()
        self.plainTextEdit_master.sync_scroll_bar()
        self.plainTextEdit_slave.sync_scroll_bar()
        shortcut=QtGui.QShortcut(QtGui.QKeySequence("F5"),MainWindow)
        shortcut.activated.connect(self.diffandrefresh)
        #shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), MainWindow)
        #shortcut.activated.connect(self.handle_search)

        self._last_focus=self.plainTextEdit_master.alias

        self.pushButton_refresh_diff.setShortcut("F5")
        self.pushButton_refresh_diff.clicked.connect(self.diffandrefresh)
        self.pushButton_next_diff.clicked.connect(self.handle_next_diff)
        self.pushButton_previous_diff.clicked.connect(self.handle_previous_diff)
        #self.pushButton_next_diff.setEnabled(False)
        self.pushButton_right_load.clicked.connect(self.plainTextEdit_slave.uploadfile)
        self.plainTextEdit_slave.bindsavebutton(self.pushButton_right_save)
        self.plainTextEdit_master.bindsavebutton(self.pushButton_left_save)
        self.plainTextEdit_master.bindlabel((self.label_left_mode,self.label_left_path))
        self.plainTextEdit_slave.bindlabel((self.label_right_mode,self.label_right_path))
        self.pushButton_left_load.clicked.connect(self.plainTextEdit_master.uploadfile)
        self.pushButton_left_save.clicked.connect(self.plainTextEdit_master.save_current_text_tofile)
        self.pushButton_left_save.setEnabled(False)
        self.pushButton_right_save.clicked.connect(self.plainTextEdit_slave.save_current_text_tofile)
        self.pushButton_right_save.setEnabled(False)
        self.plainTextEdit_master.bind_last_focus(self.set_last_focus)
        self.plainTextEdit_slave.bind_last_focus(self.set_last_focus)
        self.pushButton_search_next.clicked.connect(self.handle_search_with_text)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow:QtWidgets.QMainWindow):
        _translate = self._translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BaiNvComp   V2.1.0"))
        self.pushButton_next_diff.setText(_translate("MainWindow", "下一处原始差异"))
        self.label_right_mode.setText(_translate("MainWindow", "编辑模式:"))
        self.label_left_mode.setText(_translate("MainWindow", "编辑模式:"))
        self.pushButton_left_load.setText(_translate("MainWindow", "导入"))
        self.pushButton_refresh_diff.setText(_translate("MainWindow", "刷新差异 (F5)"))
        self.pushButton_previous_diff.setText(_translate("MainWindow", "上一处原始差异"))
        self.pushButton_left_save.setText(_translate("MainWindow", "保存"))
        self.pushButton_right_save.setText(_translate("MainWindow", "保存"))
        self.pushButton_right_load.setText(_translate("MainWindow", "导入"))
        self.pushButton_search_next.setText(_translate("MainWindow", "查找下一个"))

    def diffandrefresh(self):
        warning_box = None
        try:
            self.plainTextEdit_master.prepare_original_data()
            logging.debug(f"debug {self.plainTextEdit_master.alias}original dict{self.plainTextEdit_master._original_list}")
        except helper.InvaildInputError as e:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"invalid input in left window at line {int(e.args[0])+1}",
            )
            warning_box.exec()
        try:
            self.plainTextEdit_slave.prepare_original_data()
            logging.debug(f"debug {self.plainTextEdit_slave.alias}original dict{self.plainTextEdit_slave._original_dict}")
        except helper.InvaildInputError as e:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"invalid input in right window at line {int(e.args[0])+1}",
            )
            warning_box.exec()
        if warning_box is None:
            master_new_content,slave_new_content,diff_list=self._diff_engine.string_all_and_parsed_diff_2(self.plainTextEdit_master._original_list, self.plainTextEdit_slave._original_dict)
            self.plainTextEdit_master.NewPlainText(master_new_content)
            self.plainTextEdit_slave.NewPlainText(slave_new_content)
            self.plainTextEdit_master._textmode=enumtypes.TextMode.DIFF
            self.label_left_mode.setText(self._translate("MainWindow", "差异比对和编辑:"))
            self.plainTextEdit_slave._textmode=enumtypes.TextMode.DIFF
            self.label_right_mode.setText(self._translate("MainWindow", "差异比对和编辑:"))
            self.plainTextEdit_master._original_extraselections=self._highlight_engine.extraselectLines(diff_list, self.plainTextEdit_master,False, self.plainTextEdit_master.alias)
            self.plainTextEdit_slave._original_extraselections=self._highlight_engine.extraselectLines(diff_list, self.plainTextEdit_slave,True, self.plainTextEdit_slave.alias)
            

    
    def handle_search(self):
        if self._last_focus==self.plainTextEdit_master.alias:
            self.plainTextEdit_master.search_in_editor()
            #self.textEdit_slave.force_sync_self_scroll_bar()
            self.plainTextEdit_master.setFocus()
        elif  self._last_focus==self.plainTextEdit_slave.alias:
            self.plainTextEdit_slave.search_in_editor()
            #self.textEdit_master.force_sync_self_scroll_bar()
            self.plainTextEdit_slave.setFocus()
            
    def handle_search_with_text(self):
        search_text=self.lineEdit.text()
        if search_text.strip()=="":
            logger.info("empty search text")
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"You did not enter search text",
            )
            warning_box.exec()
            return
        if self._last_focus==self.plainTextEdit_master.alias:
            self.plainTextEdit_master.search_text_in_editor(search_text)
        elif  self._last_focus==self.plainTextEdit_slave.alias:
            self.plainTextEdit_slave.search_text_in_editor(search_text)

            
    def handle_next_diff(self):
        if self.plainTextEdit_master._textmode==enumtypes.TextMode.DIFF and self.plainTextEdit_master._textmode==enumtypes.TextMode.DIFF:
            logger.debug(f"self._last_focus:{self._last_focus}, master scroll bar value:{self.plainTextEdit_master.verticalScrollBar().value()}, slave scroll bar value:{self.plainTextEdit_slave.verticalScrollBar().value()}")
            if  self._last_focus==self.plainTextEdit_master.alias:
                self.plainTextEdit_master.find_next_extraselection()
                #self.textEdit_slave.force_sync_self_scroll_bar()
                self.plainTextEdit_master.setFocus()
            elif  self._last_focus==self.plainTextEdit_slave.alias:
                self.plainTextEdit_slave.find_next_extraselection()
                #self.textEdit_master.force_sync_self_scroll_bar()
                self.plainTextEdit_slave.setFocus()

        else:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"Make sure you have refreshed their diff.",
            )
            warning_box.exec()
    
    def handle_previous_diff(self):
        if self.plainTextEdit_master._textmode==enumtypes.TextMode.DIFF and self.plainTextEdit_master._textmode==enumtypes.TextMode.DIFF:
            logger.debug(f"self._last_focus:{self._last_focus}, master scroll bar value:{self.plainTextEdit_master.verticalScrollBar().value()}, slave scroll bar value:{self.plainTextEdit_slave.verticalScrollBar().value()}")
            if  self._last_focus==self.plainTextEdit_master.alias:
                self.plainTextEdit_master.find_previous_extraselection()
                #self.textEdit_slave.force_sync_self_scroll_bar()
                self.plainTextEdit_master.setFocus()
            elif  self._last_focus==self.plainTextEdit_slave.alias:
                self.plainTextEdit_slave.find_previous_extraselection()
                #self.textEdit_master.force_sync_self_scroll_bar()
                self.plainTextEdit_slave.setFocus()

        else:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"Make sure you have refreshed their diff.",
            )
            warning_box.exec()
    def on_focus_out_edit1(self, e:QtGui.QFocusEvent):
        # 如果plain_text_edit1失去焦点，则将焦点设置到plain_text_edit2
        if not self.plainTextEdit_slave.hasFocus():
            self.plainTextEdit_slave.setFocus()
        # 调用原始的 focusOutEvent
        QtWidgets.QPlainTextEdit.focusOutEvent(self.plainTextEdit_master, e)
        
    def on_focus_out_edit2(self, e:QtGui.QFocusEvent):
        # 如果plain_text_edit1失去焦点，则将焦点设置到plain_text_edit2
        if not self.plainTextEdit_master.hasFocus():
            self.plainTextEdit_master.setFocus()
        # 调用原始的 focusOutEvent
        QtWidgets.QPlainTextEdit.focusOutEvent(self.plainTextEdit_slave, e)
        

    def focus_in_edit1(self,e:QtGui.QFocusEvent):
        self._last_focus=0
    def focus_in_edit2(self,e:QtGui.QFocusEvent):
        self._last_focus=1
        
    def set_last_focus(self,focus:str|int):
        self._last_focus=focus
        