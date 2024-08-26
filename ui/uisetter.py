from PyQt6 import QtWidgets, QtCore
from ui.textviewer import DrapDropTextEdit
import logging
from util import helper

logger = logging.getLogger(__name__)


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

        self.pushButton_3.clicked.connect(self.diffandrefresh)
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
        MainWindow.setWindowTitle(_translate("MainWindow", "Config Merge"))
        self.pushButton_3.setText(_translate("MainWindow", "刷新差异"))
        self.pushButton_5.setText(_translate("MainWindow", "保存"))
        self.pushButton_2.setText(_translate("MainWindow", "导入"))
        self.pushButton.setText(_translate("MainWindow", "导入"))
        self.pushButton_4.setText(_translate("MainWindow", "保存"))
        self.label_2.setText(_translate("MainWindow", "编辑模式"))
        self.label.setText(_translate("MainWindow", "编辑模式"))

    def diffandrefresh(self):
        warning_box = None
        try:
            self.textEdit.prepareoriginaldict()
            logging.debug(f"debug original dict{self.textEdit._original_dict}")
        except helper.InvaildInputError as e:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"invalid input in left window at line {int(e.args[0])+1}",
            )
            warning_box.exec()
        try:
            self.textEdit_2.prepareoriginaldict()
        except helper.InvaildInputError as e:
            warning_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"invalid input in right window at line {int(e.args[0])+1}",
            )
            warning_box.exec()
        if warning_box is None:
            self.textEdit_2.construct_diff_dict(self.textEdit._original_dict)
            self.textEdit_2.output_diff_dict()
            self.textEdit.construct_diff_dict(self.textEdit_2._original_dict)
            self.textEdit.output_diff_dict()
