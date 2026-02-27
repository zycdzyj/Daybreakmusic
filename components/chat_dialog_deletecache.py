# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'chat_dialog_deletecache.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QTabWidget, QTextEdit, QWidget)

class Ui_Dialog_deletecache(object):
    def setupUi(self, Dialog_deletecache):
        if not Dialog_deletecache.objectName():
            Dialog_deletecache.setObjectName(u"Dialog_deletecache")
        Dialog_deletecache.resize(601, 324)
        Dialog_deletecache.setStyleSheet(u"")
        self.tabWidget = QTabWidget(Dialog_deletecache)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(20, 20, 561, 281))
        self.tabWidget.setStyleSheet(u"*{\n"
"	color:black;\n"
"}")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.pushButton_2 = QPushButton(self.tab)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(430, 210, 104, 42))
        self.pushButton_2.setStyleSheet(u"")
        self.pushButton = QPushButton(self.tab)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(430, 130, 104, 42))
        self.pushButton.setStyleSheet(u"")
        self.textEdit = QTextEdit(self.tab)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 20, 521, 51))
        self.textEdit.setStyleSheet(u"QTextEdit {\n"
"    background-color: transparent;\n"
"    border: 0px;\n"
"    border-radius: 0px;\n"
"    padding: 8px;\n"
"    color: white;\n"
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
"    height: 0px;\n"
"    background: transparent;\n"
"}\n"
"")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(Dialog_deletecache)

        QMetaObject.connectSlotsByName(Dialog_deletecache)
    # setupUi

    def retranslateUi(self, Dialog_deletecache):
        Dialog_deletecache.setWindowTitle(QCoreApplication.translate("Dialog_deletecache", u"Dialog", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog_deletecache", u"\u53d6\u6d88", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog_deletecache", u"\u786e\u5b9a", None))
        self.textEdit.setHtml(QCoreApplication.translate("Dialog_deletecache", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog_deletecache", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog_deletecache", u"Tab 2", None))
    # retranslateUi

