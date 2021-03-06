#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import logging

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.qt4gui.compiled_uis import Ui_toothprops_full_edit
from openmolar.qt4gui.customwidgets.chartwidget import ToothImage

LOGGER = logging.getLogger("openmolar")


class ToothPropEditor(Ui_toothprops_full_edit.Ui_Dialog, QtWidgets.QDialog):

    def __init__(self, tooth, chart, lineEdit, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.tooth = tooth
        self.chart = chart
        self.setLabel()
        self.lineEdit = lineEdit
        hlayout = QtWidgets.QHBoxLayout(self.frame)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.lineEdit)
        self.setData()
        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 150)
        self.signals()

    def setLabel(self):
        if self.chart == "st":
            type = _("Static")
        elif self.chart == "pl":
            type = _("Planned")
        else:
            type = _("Completed")

        self.tooth_label.setText("%s - %s items" % (self.tooth.upper(), type))

    def setData(self):
        self.initialVal = str(self.lineEdit.text())
        props = self.initialVal.split(" ")
        while "" in props:
            props.remove("")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(len(props))
        self.tableWidget.setHorizontalHeaderLabels(
            ["", _("Item Shortcut"), _("Demote"), _("Erase")])

        for row, prop in enumerate(props):
            self.fillRow(prop, row)

    def fillRow(self, prop, row):
        if prop and prop[0] != "!":
            self.drawProp(prop, row)
        else:
            self.drawComment(prop, row)
        self.addEraseButton(prop, row)
        self.addDownArrow(prop, row)

    def drawComment(self, prop, row):
        '''
        just puts "comment" into column 1 for now... might add an icon?
        '''
        item = QtWidgets.QTableWidgetItem("!")
        self.tableWidget.setItem(row, 0, item)

        item = QtWidgets.QTableWidgetItem(prop)
        self.tableWidget.setItem(row, 1, item)

    def drawProp(self, prop, row):
        '''
        adds a graphical representation of the "property" to the table
        '''
        tooth = ToothImage(self.tooth, [str(prop).lower()])
        icon_tableitem = QtWidgets.QTableWidgetItem()
        image = tooth.image.scaled(40, 40)
        icon_tableitem.setData(QtCore.Qt.DecorationRole, image)
        icon_tableitem.setToolTip(_("click to edit Item - ") + prop)

        self.tableWidget.setItem(row, 0, icon_tableitem)
        prop_tableitem = QtWidgets.QTableWidgetItem(prop)
        self.tableWidget.setItem(row, 1, prop_tableitem)

    def addEraseButton(self, prop, row):
        '''
        adds a pushbutton to the tableWidget
        '''
        p_map = QtGui.QPixmap(":/eraser.png").scaled(24, 24)
        tableItem = QtWidgets.QTableWidgetItem()
        tableItem.setData(QtCore.Qt.DecorationRole, p_map)
        tableItem.setToolTip(_("click to delete item - ") + prop)
        self.tableWidget.setItem(row, 3, tableItem)

    def addDownArrow(self, prop, row):
        p_map = QtGui.QPixmap(QtGui.QPixmap(":/down.png")).scaled(24, 24)
        tableItem = QtWidgets.QTableWidgetItem()
        tableItem.setData(QtCore.Qt.DecorationRole, p_map)
        tableItem.setToolTip(_("click to promote Item - ") + prop)
        self.tableWidget.setItem(row, 2, tableItem)

    def signals(self):
        self.tableWidget.cellPressed.connect(self.tableClicked)

    def tableClicked(self, row, column):
        if column == 3:
            self.deleteRow(row)
        if column == 2:
            self.promoteRow(row)

    def deleteRow(self, row):
        self.tableWidget.removeRow(row)
        self.updateLineEdit()

    def promoteRow(self, row):
        if row + 1 < self.tableWidget.rowCount():
            self.tableWidget.insertRow(row)
            self.fillRow(self.tableWidget.item(row + 2, 1).text(), row)
            self.tableWidget.removeRow(row + 2)
            self.updateLineEdit()

    def updateLineEdit(self):
        s = ""
        for row in range(self.tableWidget.rowCount()):
            s += self.tableWidget.item(row, 1).text() + " "
        self.lineEdit.setText(s)

    def exec_(self):
        if QtWidgets.QDialog.exec_(self):
            self.result = self.lineEdit.text()
            if self.initialVal != self.result:
                self.result = str(self.result)
                return True
        return False
