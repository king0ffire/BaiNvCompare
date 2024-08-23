class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1124, 901)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        
        self.textEdit = DrapDropTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(0, 0, 511, 821))
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = DrapDropTextEdit(parent=self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(610, 0, 511, 821))
        self.textEdit_2.setObjectName("textEdit_2")
        
        
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(220, 830, 75, 23))
        self.pushButton.setObjectName("pushButton")        
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(840, 830, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(520, 360, 75, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.refresh_diff)
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1124, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "保存"))
        self.pushButton_2.setText(_translate("MainWindow", "保存"))
        self.pushButton_3.setText(_translate("MainWindow", "刷新差异"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
    '''  
    def refresh_diff(self):
        self.textEdit.setPlainText(self.textEdit.fileoriginalcontent)
        self.textEdit_2.setPlainText(self.textEdit_2.fileoriginalcontent)   
        filedict1=file.parse_string(self.textEdit.toPlainText())
        filedict2=file.parse_string(self.textEdit_2.toPlainText())
        result=file.compare_diff_dict_2comparedto1(filedict1,filedict2)
        text.highlight_text(self.textEdit_2,result.copy())
        text.highlight_text_opposite(self.textEdit,result.copy())
        self.textEdit_2.viewport().update()
        self.textEdit_2.repaint()
    '''  
    def refresh_diff(self):
        filedict1=file.parse_string(self.textEdit.fileoriginalcontent)
        filedict2=file.parse_string(self.textEdit_2.fileoriginalcontent)
        self.textEdit_2.output_diff_by_stringindict(filedict1)
        self.textEdit.output_diff_by_stringindict(filedict2)
