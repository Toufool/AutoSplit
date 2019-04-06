# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_aboutVideoAutoSplitterWidget(object):
    def setupUi(self, aboutVideoAutoSplitterWidget):
        aboutVideoAutoSplitterWidget.setObjectName(_fromUtf8("aboutVideoAutoSplitterWidget"))
        aboutVideoAutoSplitterWidget.resize(276, 249)
        aboutVideoAutoSplitterWidget.setMinimumSize(QtCore.QSize(276, 249))
        aboutVideoAutoSplitterWidget.setMaximumSize(QtCore.QSize(276, 249))
        self.okButton = QtGui.QPushButton(aboutVideoAutoSplitterWidget)
        self.okButton.setGeometry(QtCore.QRect(200, 220, 71, 21))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.createdbyLabel = QtGui.QLabel(aboutVideoAutoSplitterWidget)
        self.createdbyLabel.setGeometry(QtCore.QRect(10, 33, 151, 16))
        self.createdbyLabel.setObjectName(_fromUtf8("createdbyLabel"))
        self.versionLabel = QtGui.QLabel(aboutVideoAutoSplitterWidget)
        self.versionLabel.setGeometry(QtCore.QRect(10, 10, 71, 16))
        self.versionLabel.setObjectName(_fromUtf8("versionLabel"))
        self.donatetextLabel = QtGui.QLabel(aboutVideoAutoSplitterWidget)
        self.donatetextLabel.setGeometry(QtCore.QRect(48, 86, 191, 41))
        self.donatetextLabel.setObjectName(_fromUtf8("donatetextLabel"))
        self.donatebuttonLabel = QtGui.QLabel(aboutVideoAutoSplitterWidget)
        self.donatebuttonLabel.setGeometry(QtCore.QRect(52, 127, 171, 91))
        self.donatebuttonLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.donatebuttonLabel.setObjectName(_fromUtf8("donatebuttonLabel"))
        self.githubLabel = QtGui.QLabel(aboutVideoAutoSplitterWidget)
        self.githubLabel.setGeometry(QtCore.QRect(10, 60, 46, 13))
        self.githubLabel.setObjectName(_fromUtf8("githubLabel"))

        self.retranslateUi(aboutVideoAutoSplitterWidget)
        QtCore.QObject.connect(self.okButton, QtCore.SIGNAL(_fromUtf8("clicked()")), aboutVideoAutoSplitterWidget.close)
        QtCore.QMetaObject.connectSlotsByName(aboutVideoAutoSplitterWidget)

    def retranslateUi(self, aboutVideoAutoSplitterWidget):
        aboutVideoAutoSplitterWidget.setWindowTitle(_translate("aboutVideoAutoSplitterWidget", "About Video Auto Splitter", None))
        self.okButton.setText(_translate("aboutVideoAutoSplitterWidget", "OK", None))
        self.createdbyLabel.setText(_translate("aboutVideoAutoSplitterWidget", "<html><head/><body><p>Created by <a href=\"https://twitter.com/toufool\"><span style=\" text-decoration: underline; color:#0000ff;\">Toufool</span></a> and <a href=\"https://twitter.com/faschz\"><span style=\" text-decoration: underline; color:#0000ff;\">Faschz</span></a></p></body></html>", None))
        self.versionLabel.setText(_translate("aboutVideoAutoSplitterWidget", "Version: 1.0.0", None))
        self.donatetextLabel.setText(_translate("aboutVideoAutoSplitterWidget", "If you enjoy using this program, please\n"
"      consider donating. Thank you!", None))
        self.donatebuttonLabel.setText(_translate("aboutVideoAutoSplitterWidget", "<html><head/><body><p><a href=\"https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=BYRHQG69YRHBA&amp;item_name=Video+Auto+Splitter+Development&amp;currency_code=USD&amp;source=url\"><img src=\":/donateButton/PayPal-Donate-Button-PNG-Clipart.png\"/></a></p></body></html>", None))
        self.githubLabel.setText(_translate("aboutVideoAutoSplitterWidget", "<html><head/><body><p><a href=\"https://github.com/austinryan/Video-Auto-Splitter\"><span style=\" text-decoration: underline; color:#0000ff;\">Github</span></a></p></body></html>", None))

import donatebutton_rc
