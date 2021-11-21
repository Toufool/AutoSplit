# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'update_availablepMCRpm.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os


class Ui_UpdateChecker(object):
    def setupUi(self, UpdateChecker):
        if not UpdateChecker.objectName():
            UpdateChecker.setObjectName(u"UpdateChecker")
        UpdateChecker.setEnabled(True)
        UpdateChecker.resize(313, 133)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(UpdateChecker.sizePolicy().hasHeightForWidth())
        UpdateChecker.setSizePolicy(sizePolicy)
        UpdateChecker.setMinimumSize(QSize(313, 133))
        UpdateChecker.setMaximumSize(QSize(313, 133))
        self.labelUpdateStatus = QLabel(UpdateChecker)
        self.labelUpdateStatus.setObjectName(u"labelUpdateStatus")
        self.labelUpdateStatus.setGeometry(QRect(17, 10, 281, 16))
        self.labelCurrentVersion = QLabel(UpdateChecker)
        self.labelCurrentVersion.setObjectName(u"labelCurrentVersion")
        self.labelCurrentVersion.setGeometry(QRect(17, 30, 91, 16))
        self.labelLatestVersion = QLabel(UpdateChecker)
        self.labelLatestVersion.setObjectName(u"labelLatestVersion")
        self.labelLatestVersion.setGeometry(QRect(17, 50, 81, 16))
        self.labelGoToDownload = QLabel(UpdateChecker)
        self.labelGoToDownload.setObjectName(u"labelGoToDownload")
        self.labelGoToDownload.setGeometry(QRect(17, 103, 241, 16))
        self.pushButtonLeft = QPushButton(UpdateChecker)
        self.pushButtonLeft.setObjectName(u"pushButtonLeft")
        self.pushButtonLeft.setGeometry(QRect(150, 100, 75, 24))
        self.pushButtonRight = QPushButton(UpdateChecker)
        self.pushButtonRight.setObjectName(u"pushButtonRight")
        self.pushButtonRight.setGeometry(QRect(230, 100, 75, 24))
        self.labelCurrentVersionNumber = QLabel(UpdateChecker)
        self.labelCurrentVersionNumber.setObjectName(u"labelCurrentVersionNumber")
        self.labelCurrentVersionNumber.setGeometry(QRect(120, 32, 181, 16))
        self.labelLatestVersionNumber = QLabel(UpdateChecker)
        self.labelLatestVersionNumber.setObjectName(u"labelLatestVersionNumber")
        self.labelLatestVersionNumber.setGeometry(QRect(120, 50, 181, 16))
        self.pushButtonRight.clicked.connect(UpdateChecker.close)
        self.pushButtonLeft.clicked.connect(UpdateChecker.openUpdate)
        self.retranslateUi(UpdateChecker)

        QMetaObject.connectSlotsByName(UpdateChecker)
    # setupUi

    def retranslateUi(self, UpdateChecker):
        UpdateChecker.setWindowTitle(QCoreApplication.translate("UpdateChecker", u"Update Checker", None))
        self.labelUpdateStatus.setText("")
        self.labelCurrentVersion.setText(QCoreApplication.translate("UpdateChecker", u"Current Version:", None))
        self.labelLatestVersion.setText(QCoreApplication.translate("UpdateChecker", u"Latest Version:", None))
        self.labelGoToDownload.setText("")
        self.pushButtonLeft.setText("")
        self.pushButtonRight.setText("")
        self.labelCurrentVersionNumber.setText("")
        self.labelLatestVersionNumber.setText("")
    # retranslateUi

    def openUpdate(self):
        os.system("start \"\" https://github.com/Toufool/Auto-Split/releases/latest")
        self.close()


