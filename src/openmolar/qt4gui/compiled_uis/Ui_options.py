# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'options.ui'
#
# Created: Sun Oct  4 20:51:34 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(26, 10, 191, 20))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 40, 161, 19))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(30, 70, 161, 19))
        self.label_3.setObjectName("label_3")
        self.leftMargin_spinBox = QtGui.QSpinBox(Dialog)
        self.leftMargin_spinBox.setGeometry(QtCore.QRect(220, 40, 50, 25))
        self.leftMargin_spinBox.setMinimum(-99)
        self.leftMargin_spinBox.setObjectName("leftMargin_spinBox")
        self.topMargin_spinBox = QtGui.QSpinBox(Dialog)
        self.topMargin_spinBox.setGeometry(QtCore.QRect(220, 70, 50, 25))
        self.topMargin_spinBox.setMinimum(-99)
        self.topMargin_spinBox.setObjectName("topMargin_spinBox")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_( u"Dialog"))
        self.label.setText(_( u"NHS Form Printer Settings"))
        self.label_2.setText(_( u"Left Margin Width"))
        self.label_3.setText(_( u"Top Margin Width"))
