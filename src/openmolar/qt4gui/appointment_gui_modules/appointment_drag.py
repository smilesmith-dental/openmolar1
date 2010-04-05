import datetime
import cPickle
import pickle
import sys

from PyQt4 import QtGui, QtCore

class simple_model(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(simple_model, self).__init__(parent)
        self.list = []
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def clear(self):
        self.list = []
        self.reset()

    def addAppointment(self, app):
        '''
        add an appointment to this list - arg is of type dragAppointment
        '''
        self.list.append(app)
        self.reset()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.list)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole: #show just the name
            app = self.list[index.row()]
            info = "%s mins %s with %s"% (
                    app.length, app.trt1, app.dent_inits)
            return QtCore.QVariant(info)
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            app = self.list[index.row()]
            return app
        return QtCore.QVariant()

    def removeRow(self, position):
        self.list = self.list[:position] + self.list[position+1:]
        self.reset()


class draggableList(QtGui.QListView):
    '''
    a listView whose items can be moved
    '''
    def __init__(self, parent=None):
        super(draggableList, self).__init__(parent)
        self.setDragEnabled(True)
        self.dropwidth = self.width()
        self.pixels_per_min = 2
        
    def setScaling(self, width, height_per_minute):
        '''
        make the list aware of the scaling of the widget available for drops
        this will differ depending on whether a day or week view is visible
        a 20 minutes slot will be x pixels high...
        '''
        self.dropwidth = width
        self.pixels_per_min = height_per_minute
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-appointment"):
            event.setDropAction(QtCore.Qt.QMoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        ## selected is the relevant person object
        selected = self.model().data(index,QtCore.Qt.UserRole)

        ## convert to  a bytestream
        bstream = cPickle.dumps(selected)
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-appointment", bstream)
        drag = QtGui.QDrag(self)    
        
        drag.setMimeData(mimeData)
        drag.setDragCursor(QtGui.QPixmap(), QtCore.Qt.MoveAction)
        pixmap = QtGui.QPixmap(self.dropwidth, 
            selected.length * self.pixels_per_min)
        pixmap.fill(QtGui.QColor("orange"))
        
        drag.setPixmap(pixmap)

        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)
        result = drag.start(QtCore.Qt.MoveAction)
        if result: # == QtCore.Qt.MoveAction:
            self.model().removeRow(index.row())

    def mouseMoveEvent(self, event):
        self.startDrag(event)


if __name__ == "__main__":
    '''
    the try catch here is to ensure that the app exits cleanly no matter what
    makes life better for SPE
    '''
    from openmolar.qt4gui.customwidgets import appointmentwidget
    from openmolar.qt4gui.customwidgets import appointment_overviewwidget
    
    from openmolar.dbtools import appointments
    from openmolar.settings import localsettings
    localsettings.initiate()
    
    class testDialog(QtGui.QDialog):
        def __init__(self, parent=None):
            super(testDialog, self).__init__(parent)
            self.setWindowTitle("Drag Drop Test")
            layout = QtGui.QHBoxLayout(self)

            label = QtGui.QLabel("Drag Name From This List")

            self.model = simple_model()
            appts = appointments.get_pts_appts(1)
            for appt in appts:
                if appt.unscheduled:
                    self.model.addAppointment(appt)

            self.listView = draggableList()
            self.listView.setModel(self.model)
            
            self.book = appointmentwidget.appointmentWidget(self, "1000", 
            "1200")
            self.book.setDentist(1)
            self.book.setStartTime(1015)
            self.book.setEndTime(1145)
            for appoint in (
            (1, 1030, 1045, 'MCDONALD I', 6155L, 'EXAM', '', '', '', 1, 73, 0, 0)
            ,(1, 1115, 1130, 'EMERGENCY', 0L, '', '', '', '', -128, 0, 0, 0)):
                self.book.setAppointment(appoint)
    
            self.OVbook = appointment_overviewwidget.bookWidget(1, 
            "1000", "1200", 15, 2, self)
            d1 = appointments.dentistDay(1)

            d1.start=1015
            d1.end=1145
            d1.memo="hello"
            
            frame = QtGui.QFrame()
            layout2 = QtGui.QVBoxLayout(frame)
            label = QtGui.QLabel("")
            label.setMinimumHeight(80)
            
            self.OVbook.dents=[d1,]
            self.OVbook.clear()
            self.OVbook.init_dicts()
            
            self.OVbook.setStartTime(d1)
            self.OVbook.setEndTime(d1)
            self.OVbook.setMemo(d1)
            self.OVbook.setFlags(d1)
        
            self.OVbook.freeslots[1] = ((1045, 30), )
            self.OVbook.appts[1] = ((1030,15),)
            self.OVbook.eTimes[1] = ((1115, 15),)
            self.OVbook.setMinimumWidth(200)
            
            layout2.addWidget(label)
            layout2.addWidget(self.OVbook)
            
            layout.addWidget(self.listView)
            layout.addWidget(self.book)
            layout.addWidget(frame)
            
    try:
        app = QtGui.QApplication([])
        dl = testDialog()
        dl.exec_()
    except Exception as e:
        print e
    sys.exit(app.closeAllWindows())
