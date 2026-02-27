# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'chat_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLineEdit, QPushButton,
    QSizePolicy, QTabWidget, QTextEdit, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(537, 311)
        Dialog.setStyleSheet(u"")
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 0, 531, 301))
        self.tabWidget.setStyleSheet(u"*{\n"
"	color:black\n"
"}")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.textEdit = QTextEdit(self.tab)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(0, 0, 521, 81))
        self.textEdit.setStyleSheet(u"QLineEdit:hover {\n"
"    border: 1px solid #a0a0a0;\n"
"    background-color: #fafafa;\n"
"}\n"
"QTextEdit {\n"
"    background-color: transparent;\n"
"    border: 0px;\n"
"    border-radius: 0px;\n"
"    padding: 8px;\n"
"    color: black;\n"
"    selection-background-color: #0078d7;\n"
"    selection-color: #ffffff;\n"
"}\n"
"\n"
"/* \u83b7\u53d6\u7126\u70b9\u65f6\u7684\u6837\u5f0f */\n"
"QTextEdit:focus {\n"
"    border: 0px;\n"
"    outline: none;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"/* \u7981\u7528\u72b6\u6001 */\n"
"QTextEdit:disabled {\n"
"    background-color: transparent;\n"
"    color: #999999;\n"
"}\n"
"\n"
"/* \u53ea\u8bfb\u72b6\u6001 */\n"
"QTextEdit:read-only {\n"
"    background-color: transparent;\n"
"    color: #666666;\n"
"}\n"
"\n"
"/* \u9690\u85cf\u5782\u76f4\u6eda\u52a8\u6761 */\n"
"QTextEdit QScrollBar:vertical {\n"
"    width: 0px;\n"
"    background: transparent;\n"
"}\n"
"\n"
"/* \u9690\u85cf\u6c34\u5e73\u6eda\u52a8\u6761 */\n"
"QTextEdit QScrollBar:horizontal {\n"
" "
                        "   height: 0px;\n"
"    background: transparent;\n"
"}")
        self.lineEdit = QLineEdit(self.tab)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(0, 90, 511, 31))
        self.lineEdit.setStyleSheet(u"")
        self.pushButton = QPushButton(self.tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(410, 140, 104, 42))
        self.pushButton.setStyleSheet(u"")
        self.pushButton_2 = QPushButton(self.tab)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(410, 200, 104, 42))
        self.pushButton_2.setStyleSheet(u"")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u4fee\u6539cookie", None))
        self.textEdit.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u901a\u8fc7cookie\u7684\u8bbe\u7f6e\u53ef\u4ee5\u8ba9\u4f60\u4f7f\u7528\u7f51\u6613\u4e91\u97f3\u4e50vip\u8d26\u53f7\u6765\u5728\u8fd9\u4e2a\u5ba2\u6237\u7aef\u4e0a\u542c\u97f3\u4e50,\u5982\u679c\u4f60\u8981\u83b7\u53d6cookie\u4f60\u53ef\u4ee5\u5728\u6d4f\u89c8\u5668\u7684\u5f00\u53d1\u8005\u6a21\u5f0f\u4e2d\u7684music_u\u627e\u5230\u5b83</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0"
                        "px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u8f93\u5165music_u\u4ee5\u6fc0\u6d3b:</p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"\u786e\u5b9a", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"\u53d6\u6d88", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog", u"Tab 2", None))
    # retranslateUi

