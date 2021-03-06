# -*- coding: utf8 -*-
"""
Author: Robert Moerman
Contact: robert@afrispatial.co.za
Company: AfriSpatial

This is a collection of custom QDialogs.

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
from qgisToolbox import featureSelector
from PyQt4Widgets import XQPushButton, XQDialogButtonBox
from database import *

def _fromUtf8(s):
    return s

# All dialogs using selector tool have a captured function
# All dialogs have a getReturn function

class dlg_DatabaseConnection(QDialog):
    """ This dialog enables the user to choose a database connection
    defined through DB Manager
    """
    
    def __init__(self):
        # initialize QDialog class
        super(dlg_DatabaseConnection, self).__init__(None, Qt.WindowStaysOnTopHint)
        # initialize ui
        self.conn = None
        self.setupUi()
        self.populateDatabaseChoices()

    def getDatabaseConnection(self):
        return self.conn

    def populateDatabaseChoices(self):
        """ Populate database connection choices
        """
        settings = QSettings()
        settings.beginGroup('PostgreSQL/connections')
        self.cmbbx_conn.addItem(_fromUtf8(""))
        self.cmbbx_conn.setItemText(0, QApplication.translate(
            "dlg_DatabaseConnection", 
            "", 
            None
        ))
        for i,db in enumerate(settings.childGroups()):
            self.cmbbx_conn.addItem(_fromUtf8(""))
            self.cmbbx_conn.setItemText(i + 1, QApplication.translate(
                "dlg_DatabaseConnection", 
                db, 
                None
            ))

    def testDatabaseConnection(self):
        """ Test database connection has necessary tables
        """
        conn = str(self.cmbbx_conn.currentText())
        if not bool(conn.replace(" ", "")):
            QMessageBox.information(self, "Database Connection", "Please select a database connection")
        else:
            self.conn = conn
            self.accept()

    def setupUi(self):
        """ Initialize ui
        """
        # define ui widgets
        self.setObjectName(_fromUtf8("dlg_DatabaseConnection"))
        self.resize(370, 200)
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setModal(True)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lbl_instr = QLabel(self)
        self.lbl_instr.setWordWrap(True)
        self.lbl_instr.setObjectName(_fromUtf8("lbl_instr"))
        self.verticalLayout.addWidget(self.lbl_instr)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lbl_conn = QLabel(self)
        self.lbl_conn.setObjectName(_fromUtf8("lbl_conn"))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.lbl_conn)
        self.cmbbx_conn = QComboBox(self)
        self.cmbbx_conn.setObjectName(_fromUtf8("cmbbx_conn"))
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.cmbbx_conn)
        self.verticalLayout.addLayout(self.formLayout)
        self.lbl_aside = QLabel(self)
        self.lbl_aside.setWordWrap(True)
        self.lbl_aside.setObjectName(_fromUtf8("lbl_aside"))
        self.verticalLayout.addWidget(self.lbl_aside)
        self.btnbx_options = XQDialogButtonBox(self)
        self.btnbx_options.setOrientation(Qt.Horizontal)
        self.btnbx_options.setStandardButtons(XQDialogButtonBox.Cancel|XQDialogButtonBox.Ok)
        self.btnbx_options.setObjectName(_fromUtf8("btnbx_options"))
        self.verticalLayout.addWidget(self.btnbx_options)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate(
            "dlg_DatabaseConnection",
            "Database Connection", 
            None, 
            QApplication.UnicodeUTF8
        ))
        self.lbl_conn.setText(QApplication.translate(
            "dlg_DatabaseConnection", 
            "Connection: ", 
            None
        ))
        self.lbl_aside.setText(QApplication.translate(
            "dlg_DatabaseConnection", 
            "*If your database connection cannot be found above then please define it through the PostGIS Connection Manager.", 
            None
        ))
        self.lbl_instr.setText(QApplication.translate(
            "dlg_DatabaseConnection", 
            "A database connection has not yet been selected or is no longer valid. Please select a database connection.", 
            None
        ))
        # connect ui widgets
        self.btnbx_options.accepted.connect(self.testDatabaseConnection)
        self.btnbx_options.rejected.connect(self.reject)
        QMetaObject.connectSlotsByName(self)


class dlg_Selector(QDialog):
    """ This dialog enables the selection of single features on a 
    vector layer by means of the feature selector tool defined in 
    qgisToolbox
    """

    def __init__(self, db, iface, requiredLayer, mode, query, preserve = False, parent = None):
        # initialize QDialog class
        super(dlg_Selector, self).__init__(parent, Qt.WindowStaysOnTopHint)
        # initialize ui
        self.setupUi(requiredLayer, mode)
        self.db = db
        self.iface = iface
        self.layer = requiredLayer
        self.mode = mode
        self.query = query
        self.preserve = preserve
        self.confirmed = False
        self.featID = None
        # initialize selector tool
        self.selector = featureSelector(iface, requiredLayer.layer, True, self)
        # save qgis tool
        self.tool = self.selector.parentTool
    
    def getFeatureId(self):
        return self.featID

    def executeOption(self, button):
        """ Perform validation and close the dialog
        """
        if self.btnbx_options.standardButton(button) == QDialogButtonBox.Ok:
            # check that a feature has been selected
            if self.featID is None: 
                QMessageBox.information(
                    self, 
                    "No %s Selected" %(self.layer.name.title(),), 
                    "Please select a %s." %(self.layer.name.lower(),)
                )
                return
            # check confirmation
            if not self.confirmed: 
                QMessageBox.information(
                    self, 
                    "No Confirmation", 
                    "Please tick the confimation check box."
                )
                return
            # reset qgis tool
            self.iface.mapCanvas().setMapTool(self.tool)
            # remove selection if needed 
            if not self.preserve: self.layer.layer.removeSelection()
            # accept dialog
            self.accept()
        else: 
            # reset qgis tool
            self.iface.mapCanvas().setMapTool(self.tool)
            # remove selection
            self.layer.layer.removeSelection()
            # reject dialog
            self.reject()
    
    def captured(self, selected):
        """ Notify the dialog of a feature selection and disable selecting
        """
        # disable selector tool
        self.selector.disableCapturing()
        # update dialog
        self.featID = selected[0]
        self.lnedt_featID.setText(str(self.db.query(self.query, (self.featID,))[0][0]))
        self.pshbtn_re.setEnabled(True)
        self.chkbx_confirm.setEnabled(True)
        
    def reselect(self):
        """ Blat original selection and re-enable selecting
        """
        # update dialog
        self.pshbtn_re.setEnabled(False)
        self.chkbx_confirm.setEnabled(False)
        self.lnedt_featID.setText("")
        self.featID = None
        # clear selector tool selection
        self.selector.clearSelection()
        # enable selector tool 
        self.selector.enableCapturing()

    def confirm(self, state):
        """ Confirm that the selected feature is correct
        """
        self.pshbtn_re.setEnabled(not bool(state))
        self.confirmed = bool(state)

    def setupUi(self, layer, mode):
        """ Initialize ui
        """
        # define ui widgets
        self.setObjectName(_fromUtf8("dlg_Selector"))
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lbl_featID = QLabel(self.widget)
        self.lbl_featID.setObjectName(_fromUtf8("lbl_featID"))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.lbl_featID)
        self.lnedt_featID = QLineEdit(self.widget)
        self.lnedt_featID.setEnabled(False)
        self.lnedt_featID.setObjectName(_fromUtf8("lnedt_featID"))
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lnedt_featID)
        self.pshbtn_re = QPushButton(self.splitter)
        self.pshbtn_re.setEnabled(False)
        self.pshbtn_re.setObjectName(_fromUtf8("pshbtn_re"))
        self.pshbtn_re.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout.addWidget(self.splitter)
        self.chkbx_confirm = QCheckBox(self)
        self.chkbx_confirm.setEnabled(False)
        self.chkbx_confirm.setObjectName(_fromUtf8("chkbx_confirm"))
        self.chkbx_confirm.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout.addWidget(self.chkbx_confirm)
        self.btnbx_options = QDialogButtonBox(self)
        self.btnbx_options.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.btnbx_options.setObjectName(_fromUtf8("btnbx_options"))
        self.btnbx_options.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout.addWidget(self.btnbx_options)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate("dlg_Selector", 
            "%s %s" %(layer.name.title(), mode.actor.title()), 
            None, 
            QApplication.UnicodeUTF8))
        self.lbl_featID.setText(QApplication.translate("dlg_Selector", 
            "%s ID" %(layer.name.title(),), 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_re.setText(QApplication.translate("dlg_Selector", 
            "Re-select", 
            None, 
            QApplication.UnicodeUTF8))
        self.chkbx_confirm.setText(QApplication.translate("dlg_Selector", 
            "I am sure I want to %s this %s" %(mode.action.lower(), layer.name.lower()), 
            None, 
            QApplication.UnicodeUTF8))
        # connect ui widgets
        self.pshbtn_re.clicked.connect(self.reselect)
        self.chkbx_confirm.stateChanged.connect(self.confirm)
        self.btnbx_options.clicked.connect(self.executeOption)
        QMetaObject.connectSlotsByName(self)


class dlg_Manager(QDialog):
    """ This dialog enables the user to select an option with regards to managing a vector layer
    """

    def __init__(self, requiredLayer, parent=None):
        super(dlg_Manager, self).__init__(parent, Qt.WindowStaysOnTopHint)
        self.setupUi(requiredLayer)
        self.layer = requiredLayer
        self.option = None

    def getOption(self):
        return self.option

    def executeOption(self, button):
        """ Perform validation and close the dialog
        """
        if self.btnbx_options.standardButton(button) == QDialogButtonBox.Ok:
            # get selected option
            for i, rdbtn in enumerate(self.findChildren(QRadioButton)): 
                if rdbtn.isChecked(): 
                    self.option = i
                    break
            # check that an option was selected
            if self.option is not None: 
                # accept dialog
                self.accept()
            else: QMessageBox.information(self, "Invalid Selection", "Please select an option before clicking OK")
        else:
            # reject dialog
            self.reject()
    
    def setupUi(self, layer):
        """ Initialize ui
        """
        # define ui widgets
        self.setObjectName(_fromUtf8("dlg_Manager"))
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setModal(True)
        self.mainlyt = QGridLayout(self)
        self.mainlyt.setSizeConstraint(QLayout.SetFixedSize)
        self.mainlyt.setObjectName(_fromUtf8("mainlyt"))
        self.vrtlyt = QVBoxLayout()
        self.vrtlyt.setObjectName(_fromUtf8("vrtlyt"))
        self.grdlyt = QGridLayout()
        self.grdlyt.setObjectName(_fromUtf8("grdlyt"))
        self.rdbtn_add = QRadioButton(self)
        self.rdbtn_add.setObjectName(_fromUtf8("rdbtn_add"))
        self.rdbtn_add.setCursor(QCursor(Qt.PointingHandCursor))
        self.grdlyt.addWidget(self.rdbtn_add, 0, 0, 1, 1)
        self.rdbtn_edit = QRadioButton(self)
        self.rdbtn_edit.setObjectName(_fromUtf8("rdbtn_edit"))
        self.rdbtn_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.grdlyt.addWidget(self.rdbtn_edit, 1, 0, 1, 1)
        self.rdbtn_del = QRadioButton(self)
        self.rdbtn_del.setObjectName(_fromUtf8("rdbtn_del"))
        self.rdbtn_del.setCursor(QCursor(Qt.PointingHandCursor))
        self.grdlyt.addWidget(self.rdbtn_del, 2, 0, 1, 1)
        self.vrtlyt.addLayout(self.grdlyt)
        self.btnbx_options = QDialogButtonBox(self)
        self.btnbx_options.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.btnbx_options.setCenterButtons(False)
        self.btnbx_options.setObjectName(_fromUtf8("btnbx_options"))
        self.btnbx_options.setCursor(QCursor(Qt.PointingHandCursor))
        self.vrtlyt.addWidget(self.btnbx_options)
        self.mainlyt.addLayout(self.vrtlyt, 0, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate(
            "dlg_Manager", 
            "%s Manager" %(layer.name.title(),), 
            None, 
            QApplication.UnicodeUTF8
        ))
        self.rdbtn_add.setText(QApplication.translate(
            "dlg_Manager",
            "Create New %s" %(layer.name.title(),), 
            None, 
            QApplication.UnicodeUTF8
        ))
        self.rdbtn_edit.setText(QApplication.translate(
            "dlg_Manager",
            "Edit Existing %s" %(layer.name.title(),), 
            None, 
            QApplication.UnicodeUTF8
        ))
        self.rdbtn_del.setText(QApplication.translate(
            "dlg_Manager",
            "Delete Existing %s" %(layer.name.title(),), 
            None, 
            QApplication.UnicodeUTF8
        ))
        # connect ui widgets
        self.btnbx_options.clicked.connect(self.executeOption)
        QMetaObject.connectSlotsByName(self)


class dlg_FormBeacon(QDialog):
    """ This dialog enables a user to define and modify a beacon
    """

    def __init__(self, db, query, fields, values=[], parent = None):
        # initialize QDialog class
        super(dlg_FormBeacon, self).__init__(parent, Qt.WindowStaysOnTopHint)
        # initialize ui
        self.setupUi(fields)
        # initialize instance variables
        self.db = db
        self.query = query
        self.fields = fields
        self.values_old = {}
        self.values_new = {}
        self.colours = {
            "REQUIRED":"background-color: rgba(255, 107, 107, 150);",
            "TYPE":"background-color: rgba(107, 107, 255, 150);",
            "UNIQUE":"background-color: rgba(107, 255, 107, 150);"
        }
        # populate form if values are given
        if bool(values): 
            self.populateForm(values)
    
    def getValues(self):
        """ Return intended variable(s) after the dialog has been accepted
        """
        return (self.values_old, self.values_new)

    def populateForm(self, values):
        """ Populate form with given values
        """
        for index,v in enumerate(values):
            if v is not None: self.lnedts[index].setText(str(v))
            self.values_old[self.fields[index].name] = v

    def executeOption(self, button):
        """ Perform validation and close the dialog
        """
        if self.btnbx_options.standardButton(button) == QDialogButtonBox.Save:
            values_new = {}
            # check required fields        
            valid = True
            for lnedt in self.lnedts:
                if bool(lnedt.property("REQUIRED")):
                    if str(lnedt.text()).strip() is "":
                        lnedt.setStyleSheet(self.colours["REQUIRED"])
                        valid = False
                    else: lnedt.setStyleSheet("")
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Empty Required Fields", 
                    "Please ensure that all required fields are completed."
                )
                return
            # check correct field types
            valid = True
            for index,lnedt in enumerate(self.lnedts):
                try:
                    if str(lnedt.text()).strip() is not "":
                        cast = self.fields[index].type
                        tmp = cast(str(lnedt.text()).strip())
                        values_new[self.fields[index].name] = tmp
                        lnedt.setStyleSheet("")
                    else:
                        values_new[self.fields[index].name] = None
                except Exception as e:
                    lnedt.setStyleSheet(self.colours["TYPE"])
                    valid = False
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Invalid Field Types", 
                    "Please ensure that fields are completed with valid types."
                )
                return
            # check unique fields
            valid = True
            for index,lnedt in enumerate(self.lnedts):
                if str(lnedt.text()).strip() is "": continue
                if bool(lnedt.property("UNIQUE")):
                    if self.fields[index].name in self.values_old.keys() and values_new[self.fields[index].name] == self.values_old[self.fields[index].name]:
                        lnedt.setStyleSheet("")
                    elif bool(int(self.db.query(self.query %(self.fields[index].name, "%s"), (values_new[self.fields[index].name],))[0][0])): 
                        lnedt.setStyleSheet(self.colours["UNIQUE"])
                        valid = False
                    else: lnedt.setStyleSheet("")
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Fields Not Unique", 
                    "Please ensure that fields are given unique values."
                )
                return
            # save values
            self.values_new = values_new
            # accept dialog
            self.accept()
        else:
            # reject dialog
            self.reject()

    def setupUi(self, fields):
        """ Initialize ui
        """
        # define ui widgets
        self.setObjectName(_fromUtf8("dlg_FormBeacon"))
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setModal(True)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))        
        self.lbls = []
        self.lnedts = []
        # define form fields dynamically from the database schema
        for index, f in enumerate(fields):
            lbl = QLabel(self)
            lbl.setObjectName(_fromUtf8("lbl_%s" %(f.name,)))
            self.formLayout.setWidget(index, QFormLayout.LabelRole, lbl)
            self.lbls.append(lbl)
            lnedt = QLineEdit(self)
            lnedt.setProperty("REQUIRED", f.required)
            lnedt.setProperty("UNIQUE", f.unique)
            lnedt.setObjectName(_fromUtf8("lnedt_%s" %(f.name,)))
            self.formLayout.setWidget(index, QFormLayout.FieldRole, lnedt)
            self.lnedts.append(lnedt)
            lbl.setText(QApplication.translate("dlg_FormBeacon", 
                ("*" if bool(self.lnedts[index].property("REQUIRED")) else "") + f.name.title(), 
                None, 
                QApplication.UnicodeUTF8))
            lnedt.setProperty("TYPE", QApplication.translate("dlg_FormBeacon", str(f.type), None, QApplication.UnicodeUTF8))
        self.verticalLayout.addLayout(self.formLayout)
        self.line_1 = QFrame(self)
        self.line_1.setFrameShape(QFrame.HLine)
        self.line_1.setFrameShadow(QFrame.Sunken)
        self.line_1.setObjectName(_fromUtf8("line_1"))
        self.verticalLayout.addWidget(self.line_1)
        self.label = QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.line_2 = QFrame(self)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout.addWidget(self.line_2)
        self.btnbx_options = QDialogButtonBox(self)
        self.btnbx_options.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.btnbx_options.setObjectName(_fromUtf8("btnbx_options"))
        self.btnbx_options.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout.addWidget(self.btnbx_options)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate("dlg_FormBeacon", "Beacon Form", None, QApplication.UnicodeUTF8))        
        self.label.setText(QApplication.translate("dlg_FormBeacon", "<html><head/><body><p><span style=\" color:#ff0000;\">*Required Field</span></p></body></html>", None, QApplication.UnicodeUTF8))
        # connect ui widgets
        self.btnbx_options.clicked.connect(self.executeOption)
        QMetaObject.connectSlotsByName(self)


class dlg_FormParcel(QDialog):
    """ This dialog enables a user to define and modify a parcel
    """
    
    def __init__(self, db, iface, requiredLayers, SQL_BEACONS, SQL_PARCELS, autocomplete=[], data={}, parent=None):
        # initialize QDialog class
        super(dlg_FormParcel, self).__init__(parent, Qt.WindowStaysOnTopHint)
        # initialize ui
        self.setupUi(autocomplete)
        self.db = db
        self.iface = iface
        self.layers = requiredLayers
        self.SQL_BEACONS = SQL_BEACONS
        self.SQL_PARCELS = SQL_PARCELS
        self.autocomplete = autocomplete
        self.values_old = {}
        self.values_new = {}
        self.sequence = []
        self.new_accepted = False
        # initialize selector tool
        self.selector = featureSelector(iface, requiredLayers[0].layer, False, self)
        # save qgis tool
        self.tool = self.selector.parentTool
        # populate form if values are given
        if bool(data): 
            self.populateForm(data)
            self.pshbtn_reset.setEnabled(True)

    def getValues(self):
        return (self.values_old, self.values_new)
    
    def populateForm(self, data):
        """ Populte form with values given
        """
        # get values
        checker = lambda d, k: d[k] if k in d.keys() else None
        feat_id = checker(data, "parcel_id")
        feat_sequence = checker(data, "sequence")
        # use values
        if bool(feat_id): 
            # populate parcel_id
            self.values_old["parcel_id"] = self.db.query(
                self.SQL_PARCELS["SELECT"], (feat_id,)
            )[0][0]
            self.lnedt_parcelID.setText(str(self.values_old["parcel_id"]))
            self.highlightFeature(self.layers[1].layer, feat_id)
        if bool(feat_sequence):
            # populate sequence
            self.sequence = []
            self.values_old["sequence"] = []
            for id in feat_sequence:
                beacon_id = str(self.db.query(self.SQL_BEACONS["SELECT"], (id,))[0][0])
                self.sequence.append(beacon_id)
                self.values_old["sequence"].append(beacon_id)
                self.lstwdg_sequence.addItem(beacon_id.replace("\n",""))
            self.highlightFeatures(self.layers[0].layer, feat_sequence)
            self.selector.selected = feat_sequence
            # update selector selection
            self.selector.selected = feat_sequence

    def highlightFeature(self, layer, feature):
        """ Highlight a single feature on a vector layer
        """
        self.highlightFeatures(layer, [feature,])

    def highlightFeatures(self, layer, features):
        """ Highlight multiple features on a vector layer
        """
        layer.setSelectedFeatures(features)

    def captured(self, selected):
        """ Notify the dialog of a feature selection and disable selecting
        """
        pass 
                    
    def executeOption(self, button):
        """ Perform validation and close the dialog
        """
        if self.btnbx_options.standardButton(button) == QDialogButtonBox.Save:
            parcel_id = str(self.lnedt_parcelID.text()).strip()
            # check that parcel id exists
            if parcel_id == "": 
                QMessageBox.information(
                    self, 
                    "Invalid Parcel ID", 
                    "Please enter a parcel ID."
                )
                return
            # check that parcel id is an int
            try:
                int(parcel_id)
            except ValueError:
                QMessageBox.information(
                    self, 
                    "Invalid Parcel ID", 
                    "Please enter a number for the parcel ID."
                )
                return
            # check that parcel id is valid (i.e. current, unique, available)
            if "parcel_id" in self.values_old.keys() and str(self.values_old["parcel_id"]) == parcel_id:
                pass
            elif not bool(self.db.query(
                self.SQL_PARCELS["UNIQUE"], (int(parcel_id),)
            )[0][0]):
                if not self.new_accepted and QMessageBox.question(
                    self, 
                    'Confirm New Parcel ID', 
                    "Are you sure you want to create a new parcel ID?", 
                    QMessageBox.Yes, 
                    QMessageBox.No
                ) == QMessageBox.No: 
                    return
                self.new_accepted = True
            else:
                if not bool(self.db.query(
                    self.SQL_PARCELS["AVAILABLE"], 
                    (parcel_id,)
                )[0][0]):
                    QMessageBox.information(
                        self, 
                        "Duplicated Parcel ID", 
                        "Please enter a unique or available parcel ID."
                    )
                    return
            # check that at least 3 beacons exist within the sequence
            if len(self.selector.selected) < 3: 
                QMessageBox.information(
                    self, 
                    "Too Few Beacons", 
                    "Please ensure that there are at least 3 beacons listed in the sequence."
                )
                return
            # save parcel id
            self.values_new["parcel_id"] = parcel_id
            # save sequence
            self.values_new["sequence"] = self.sequence
            # reset qgis tool
            self.iface.mapCanvas().setMapTool(self.tool)
            # remove selection
            for l in self.layers: l.layer.removeSelection()
            # accept dialog
            self.accept()
        else:
            # reset qgis tool
            self.iface.mapCanvas().setMapTool(self.tool)
            # remove selection
            for l in self.layers: l.layer.removeSelection()
            # accept dialog
            self.reject()

    def newBeacon(self):
        """ Define a new beacon on the fly to be added to the parcel sequence
        """
        # disable self
        self.setEnabled(False)
        # get fields
        fields = self.db.getSchema(
            self.layers[0].table, [
            self.layers[0].geometry_column, 
            self.layers[0].primary_key
        ])
        # display form
        frm = dlg_FormBeacon(
            self.db, 
            self.SQL_BEACONS["UNIQUE"],
            fields
        )
        frm.show()
        frm_ret = frm.exec_()
        if bool(frm_ret):
            # add beacon to database
            values_old, values_new = frm.getValues() 
            id = self.db.query(
                self.SQL_BEACONS["INSERT"].format(fields = ", ".join(sorted(values_new.keys())), values = ", ".join(["%s" for k in values_new.keys()])), [values_new[k] for k in sorted(values_new.keys())])[0][0]
            self.iface.mapCanvas().refresh()
            self.highlightFeature(self.layers[0].layer, id)
            self.selector.appendSelection(id)
        # enable self
        self.setEnabled(True)

    def startSeq(self):
        """ Start sequence capturing
        """
        # enable capturing
        self.selector.enableCapturing()
        # perform button stuffs
        self.pshbtn_start.setEnabled(False)
        self.pshbtn_reset.setEnabled(False)
        self.pshbtn_stop.setEnabled(True)
        self.pshbtn_new.setEnabled(True)
    
    def stopSeq(self):
        """ Stop sequence capturing
        """
        # disable capturing
        self.selector.disableCapturing()
        # perform button stuffs
        self.pshbtn_stop.setEnabled(False)
        self.pshbtn_new.setEnabled(False)
        self.lstwdg_sequence.clear()
        self.sequence = []
        for i in self.selector.selected:
            beacon_id = str(self.db.query(self.SQL_BEACONS["SELECT"], (i,))[0][0])
            self.sequence.append(beacon_id)
            self.lstwdg_sequence.addItem(beacon_id.replace("\n",""))
        self.pshbtn_start.setEnabled(True)
        self.pshbtn_reset.setEnabled(True)
    
    def resetSeq(self):
        """ Reset captured sequence
        """
        # clear selection
        self.selector.clearSelection()
        self.sequence = []
        # clear sequence
        self.lstwdg_sequence.clear()
        # perform button stuffs
        self.pshbtn_reset.setEnabled(False)
        self.pshbtn_start.setEnabled(True)

    def setupUi(self, autocomplete):
        """ Initialize ui
        """
        # define ui widgets
        self.setObjectName(_fromUtf8("dlg_FormParcel"))
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lbl_parcelID = QLabel(self)
        self.lbl_parcelID.setObjectName(_fromUtf8("lbl_parcelID"))
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.lbl_parcelID)
        self.lnedt_parcelID = QLineEdit(self)
        self.lnedt_parcelID.setObjectName(_fromUtf8("lnedt_parcelID"))
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lnedt_parcelID)
        model = QStringListModel()
        model.setStringList(autocomplete)
        completer = QCompleter()        
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(model)
        self.lnedt_parcelID.setCompleter(completer)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lbl_sequence = QLabel(self)
        self.lbl_sequence.setObjectName(_fromUtf8("lbl_sequence"))
        self.horizontalLayout_2.addWidget(self.lbl_sequence)
        spacerItem_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem_1)
        self.pshbtn_new = QPushButton(self)
        self.pshbtn_new.setEnabled(False)
        self.pshbtn_new.setObjectName(_fromUtf8("pshbtn_new"))
        self.pshbtn_new.setCursor(QCursor(Qt.PointingHandCursor))
        self.horizontalLayout_2.addWidget(self.pshbtn_new)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_1 = QHBoxLayout()
        self.horizontalLayout_1.setObjectName(_fromUtf8("horizontalLayout_1"))
        self.verticalLayout_1 = QVBoxLayout()
        self.verticalLayout_1.setObjectName(_fromUtf8("verticalLayout_1"))
        self.pshbtn_start = QPushButton(self)
        self.pshbtn_start.setEnabled(True)
        self.pshbtn_start.setObjectName(_fromUtf8("pshbtn_start"))
        self.pshbtn_start.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout_1.addWidget(self.pshbtn_start)
        self.pshbtn_stop = QPushButton(self)
        self.pshbtn_stop.setEnabled(False)
        self.pshbtn_stop.setObjectName(_fromUtf8("pshbtn_stop"))
        self.pshbtn_stop.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout_1.addWidget(self.pshbtn_stop)
        self.pshbtn_reset = QPushButton(self)
        self.pshbtn_reset.setEnabled(False)
        self.pshbtn_reset.setObjectName(_fromUtf8("pshbtn_reset"))
        self.pshbtn_reset.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout_1.addWidget(self.pshbtn_reset)
        spacerItem_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_1.addItem(spacerItem_2)
        self.horizontalLayout_1.addLayout(self.verticalLayout_1)
        self.lstwdg_sequence = QListWidget(self)
        self.lstwdg_sequence.setEnabled(False)
        self.lstwdg_sequence.setObjectName(_fromUtf8("lstwdg_sequence"))
        self.horizontalLayout_1.addWidget(self.lstwdg_sequence)
        self.verticalLayout_2.addLayout(self.horizontalLayout_1)
        self.btnbx_options = QDialogButtonBox(self)
        self.btnbx_options.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.btnbx_options.setObjectName(_fromUtf8("btnbx_options"))
        self.btnbx_options.setCursor(QCursor(Qt.PointingHandCursor))
        self.verticalLayout_2.addWidget(self.btnbx_options)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate("dlg_FormParcel", 
            "Parcel Form", None, QApplication.UnicodeUTF8))
        self.lbl_parcelID.setText(QApplication.translate("dlg_FormParcel", 
            "Parcel ID", None, QApplication.UnicodeUTF8))
        self.lbl_sequence.setText(QApplication.translate("dlg_FormParcel", 
            "Beacon Sequence", None, QApplication.UnicodeUTF8))
        self.pshbtn_new.setText(QApplication.translate("dlg_FormParcel", 
            "New Beacon", None, QApplication.UnicodeUTF8))
        self.pshbtn_start.setText(QApplication.translate("dlg_FormParcel", 
            "Start", None, QApplication.UnicodeUTF8))
        self.pshbtn_stop.setText(QApplication.translate("dlg_FormParcel", 
            "Stop", None, QApplication.UnicodeUTF8))
        self.pshbtn_reset.setText(QApplication.translate("dlg_FormParcel", 
            "Reset", None, QApplication.UnicodeUTF8))
        # connect ui widgets
        self.pshbtn_new.clicked.connect(self.newBeacon)
        self.pshbtn_start.clicked.connect(self.startSeq)
        self.pshbtn_stop.clicked.connect(self.stopSeq)
        self.pshbtn_reset.clicked.connect(self.resetSeq)
        self.btnbx_options.clicked.connect(self.executeOption)
        QMetaObject.connectSlotsByName(self)


class dlg_FormBearDist(QDialog):
    """ This dialog enables the user to define bearings and distances
    """

    def __init__(self, db, SQL_BEARDIST, SQL_BEACONS, requiredLayers, parent = None):
        # initialize QDialog class
        super(dlg_FormBearDist, self).__init__(parent, Qt.WindowStaysOnTopHint)
        # initialize ui
        self.setupUi()
        self.db = db
        self.SQL_BEARDIST = SQL_BEARDIST
        self.SQL_BEACONS = SQL_BEACONS
        self.layers = requiredLayers
        self.auto = {
            "SURVEYPLAN":self.db.query(
                SQL_BEARDIST["AUTO_SURVEYPLAN"]
                )[0][0],
            "REFERENCEBEACON":self.db.query(
                SQL_BEARDIST["AUTO_REFERENCEBEACON"]
                )[0][0],
            "FROMBEACON":[]
        }
        self.surveyPlan = None
        self.referenceBeacon = None
        self.beardistChain = []
        self.beardistStr = "%s" + u"\u00B0" + " and %sm from %s to %s"
        # initialize initial step
        self.initItemSurveyPlan()
        
    def getReturn(self):
        """ Return intended variable(s) after the dialog has been accepted
        @returns (<survey plan number>, <reference beacon>, <beardist chain>) (tuple)
        """
        return (self.surveyPlan, self.referenceBeacon, self.beardistChain)

    def setCurrentItem(self, index, clear=False, enabled=False):
        """ Set the current toolbox item and disable all other toolbox items
        """
        # clear editable fields if needed
        if clear:
            for widget in self.tlbx.widget(index).findChildren(QWidget):
                if type(widget) in [QLineEdit]:
                    widget.setText("")
        # enable editable fields if needed
        if enabled:
            for widget in self.tlbx.widget(index).findChildren(QWidget):
                if type(widget) in [QLineEdit]:
                    widget.setEnabled(True)
        # disable all items
        for i in range(self.count): 
            self.tlbx.setItemEnabled(i, False)
        # enable and display desired item
        self.tlbx.setCurrentIndex(index)
        self.tlbx.setItemEnabled(index, True)

    def initItemSurveyPlan(self, forward=True):
        """ Initialize form elements for the survey plan item
        """
        if not forward:
            if not self.confirmBack():
                return
        # update autocompletion
        model = QStringListModel()
        model.setStringList(self.auto["SURVEYPLAN"])
        completer = QCompleter()        
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(model)
        self.lnedt_plan.setCompleter(completer)
        # reset variables associated with item
        self.surveyPlan = None
        # display survey plan item
        self.setCurrentItem(0)
        
    def checkItemSurveyPlan(self, forward):
        """ Validate form elements before proceding from the survey plan item
        """
        # check direction
        if forward: 
            # check that a server plan number was specified
            surveyPlan = str(self.lnedt_plan.text()).strip() 
            if surveyPlan is "":
                QMessageBox.information(
                    self, 
                    "Empty Survey Plan Number", 
                    "Please enter a surver plan number."
                )
                return
            # set survey plan number
            self.surveyPlan = surveyPlan
            # display next toolbox item
            self.initItemReferenceBeacon()
        else: pass

    def initItemReferenceBeacon(self, forward=True):
        """ Initialize form elements for the reference beacon item
        """
        if not forward:
            if not self.confirmBack():
                return
        # update autocompletion
        model = QStringListModel()
        model.setStringList(self.auto["REFERENCEBEACON"])
        completer = QCompleter()        
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModel(model)
        self.lnedt_ref.setCompleter(completer)
        # reset variables associated with items
        self.referenceBeacon = None
        # check direction whence it came
        if forward:
            # check if survey plan number has a pre-defined reference beacon
            if self.surveyPlan in self.auto["SURVEYPLAN"]:
                # update item contents
                self.lnedt_ref.setEnabled(False)
                self.lnedt_ref.setText(str(self.db.query(
                    self.SQL_BEARDIST["EXIST_REFERENCEBEACON"], 
                    (self.surveyPlan,)
                )[0][0]))
            else:
                # update item contents
                self.lnedt_ref.setEnabled(True)
                self.lnedt_ref.setText("")
        # display reference beacon item
        self.setCurrentItem(1)
        
    def checkItemReferenceBeacon(self, forward):
        """ Validate form elements before proceding from the reference beacon item
        """
        # check direction
        if forward: 
            # check that a reference beacon was specified
            referenceBeacon = str(self.lnedt_ref.text()).strip()
            if referenceBeacon is "":
                QMessageBox.information(
                    self, 
                    "Empty Reference Beacon", 
                    "Please enter a reference beacon."
                )
                return
            # check if reference beacon exists
            if referenceBeacon in self.auto["REFERENCEBEACON"]:
                # set reference beacon
                self.referenceBeacon = referenceBeacon
                # display next toolbox item
                self.initItemBearDistChain()
            else:
                # disable self
                self.setEnabled(False)
                # present beacon form
                column_index = self.db.query(
                    self.SQL_BEARDIST["INDEX_REFERENCEBEACON"]
                )[0][0]
                # get fields
                fields = self.db.getSchema(
                    self.layers[0].table, [
                    self.layers[0].geometry_column, 
                    self.layers[0].primary_key
                ])
                # display form
                frm = dlg_FormBeacon(
                    self.db, 
                    self.SQL_BEACONS["UNIQUE"],
                    fields,
                    parent = self
                )
                frm.lnedts[column_index].setText(referenceBeacon)
                frm.lnedts[column_index].setEnabled(False)
                frm.show()
                frm_ret = frm.exec_()
                if bool(frm_ret):
                    # add beacon to database
                    values_old, values_new = frm.getValues() 
                    self.db.query(
                        self.SQL_BEACONS["INSERT"].format(fields = ", ".join(sorted(values_new.keys())), values = ", ".join(["%s" for k in values_new.keys()])), [values_new[k] for k in sorted(values_new.keys())])
                    # set reference beacon
                    self.referenceBeacon = referenceBeacon
                    self.auto["REFERENCEBEACON"].append(referenceBeacon)
                    # enable self
                    self.setEnabled(True)
                    # display next toolbox item
                    self.initItemBearDistChain()
                else:
                    # enable self
                    self.setEnabled(True)
        else:
            self.initItemSurveyPlan(False)

    def initItemBearDistChain(self, forward=True):
        """ Initialize form elements for the beardist chain item
        """
        # reset variables associated with items
        self.beardistChain = []
        self.auto["FROMBEACON"] = []
        self.lst_chain.clear()
        self.auto["FROMBEACON"].append(self.referenceBeacon)
        # perform button stuffs
        self.pshbtn_chain_edt.setEnabled(False)
        self.pshbtn_chain_del.setEnabled(False)
        self.pshbtn_chain_finish.setEnabled(False)
        # check if reference beacon is predefined
        if self.referenceBeacon in self.auto["REFERENCEBEACON"]:
            # check if survey plan number is predefined
            if self.surveyPlan in self.auto["SURVEYPLAN"]:
                # get defined bearings and distances
                records = self.db.query(
                    self.SQL_BEARDIST["EXIST_BEARDISTCHAINS"], 
                    (self.surveyPlan,)
                )
                if records not in [None, []]:
                    for oid,link in enumerate(records):
                        self.beardistChain.append([list(link), "NULL", oid])
                    self.updateBearDistChainDependants()
                    self.pshbtn_chain_finish.setEnabled(True)
                    self.pshbtn_chain_edt.setEnabled(True)
                    self.pshbtn_chain_del.setEnabled(True)  
        # display beardist chain item
        self.setCurrentItem(2)

    def checkItemBearDistChain(self, forward):
        """ Validate form elements before proceding from the beardist chain item
        """
        # check direction
        if forward:
            if not bool(self.surveyPlan):
                QMessageBox.information(
                    self, 
                    "No Survey Plan", 
                    "Please specify a survey plan number"
                )
                return
            if not bool(self.referenceBeacon):
                QMessageBox.information(
                    self, 
                    "No Reference Beacon", 
                    "Please specify a reference beacon"
                )
                return
            if not bool(self.beardistChain):
                QMessageBox.information(
                    self, 
                    "No Bearing and Distance Chain", 
                    "Please capture bearings and distances"
                )
                return
            self.accept()
        else:
            self.initItemReferenceBeacon(False)

    def canFindReferenceBeacon(self, beacon_name):
        while True:
            beacon_to = None
            for link in self.beardistChain:
                if beacon_name == link[0][3]:
                    beacon_to = link[0][2]
                    break
            if beacon_to is None: return False
            if beacon_to == beacon_name: return False
            if beacon_to == self.referenceBeacon: return True
    
    def isEndLink(self, index):
        """ Test whether or not the link is safe to edit or delete
        """
        beacon_to = self.beardistChain[index][0][3]
        for link in self.beardistChain:
            beacon_from = link[0][2]
            if beacon_to == beacon_from:
                return False
        return True
    
    def isLastAnchorLink(self, index):
        """ Test whether or not the link is the only one using the reference beacon
        """
        beacon_ref = self.beardistChain[index][0][2]
        # check if reference beacon is used
        if beacon_ref != self.referenceBeacon: return False
        # count number of reference beacon occurrences
        count = 0
        for link in self.beardistChain:
            beacon_from = link[0][2]
            if beacon_from == beacon_ref: count += 1
        # check count
        return True if count == 1 else False

    def getSelectedIndex(self, action):
        """ Captures selected link from the chain list
        """
        # get list of selected items
        items = self.lst_chain.selectedItems()
        # check list is non-empty
        if len(items) == 0:
            QMessageBox.information(
                self, 
                "No Link Selected", 
                "Please select a link to edit"
            )
            return None
        # check list does not contain more than one item
        if len(items) > 1: 
            QMessageBox.information(
                self, 
                "Too Many Links Selected", 
                "Please select only one link to edit"
            )
            return None
        # get item index
        index = self.lst_chain.row(items[0])
        # check that index is of an end link
        if not bool(self.isEndLink(index)):
            if QMessageBox.question(
                self, 
                "Non End Link Selected", 
                "The link you selected is not at the end of a chain. If you {action} this link it will {action} all links that depend on this one. Are you sure you want to {action} this link?".format(action=action.lower()), 
                QMessageBox.Yes, QMessageBox.No) == QMessageBox.No: 
                return None
        # return index
        return index

    def updateBearDistChainDependants(self):
        """ Reinitialize all variables defined from the beardist chain
        """
        # clear dependants
        self.lst_chain.clear()
        self.auto["FROMBEACON"] = [self.referenceBeacon]
        # populate dependants
        for link in self.beardistChain:
            #QMessageBox.information(self,QString(','.join(link[0][:4])))
            self.lst_chain.addItem(self.beardistStr %tuple(link[0][:4]))
            self.auto["FROMBEACON"].append(link[0][3])
        self.auto["FROMBEACON"].sort()            

    def addLink(self):
        """ Add a link to the beardist chain
        """
        while True:
            dlg = dlg_FormBearDistLink(
                self.db,
                self.auto["FROMBEACON"], 
                self.SQL_BEACONS["UNIQUE"], 
                parent = self
            )
            dlg.show()
            dlg_ret = dlg.exec_()
            if bool(dlg_ret):
                values = dlg.getValues()
                self.beardistChain.append([values, "INSERT", None])
                self.updateBearDistChainDependants()
            else: break
        if len(self.beardistChain) >= 1: 
            self.pshbtn_chain_finish.setEnabled(True)
            self.pshbtn_chain_edt.setEnabled(True)
            self.pshbtn_chain_del.setEnabled(True)

    def editLink(self):
        """ Edit a link from the beardist chain
        """
        # get selected index
        index = self.getSelectedIndex("edit")
        # check selection
        if index is not None:
            # display dialog
            dlg = dlg_FormBearDistLink(
                self.db,
                self.auto["FROMBEACON"],
                self.SQL_BEACONS["UNIQUE"],
                values = self.beardistChain[index][0], 
                parent = self)
            if self.isLastAnchorLink(index): dlg.lnedts[2].setEnabled(False)
            dlg.show()
            dlg_ret = dlg.exec_()
            if bool(dlg_ret):
                values = dlg.getValues()
                # check if anything was changed
                if values == self.beardistChain[index][0]: return
                # check if reference beacon can be found
                if not self.canFindReferenceBeacon(self.beardistChain[index][0][3]):
                    QMessageBox.information(None, "", "oops")
                # recursively update beacon names if changed
                if self.beardistChain[index][0][3] != values[3]:
                    tmp = []
                    for link in self.beardistChain:
                        if link[0][2] == self.beardistChain[index][0][3]:
                            link[0][2] = values[3]
                        tmp.append(link)
                    self.beardistChain = tmp
                # update beardist chain entry
                if self.beardistChain[index][1] in ["NULL","UPDATE"]:
                    self.beardistChain[index] = [values, "UPDATE", self.beardistChain[index][-1]]
                elif self.beardistChain[index][1] == "INSERT": 
                    self.beardistChain[index] = [values, "INSERT", None]
                self.updateBearDistChainDependants()

    def deleteLink(self):
        """ Delete a link from the beardist chain
        """
        # get selected index
        index = self.getSelectedIndex("delete")
        # check selection
        if index is not None:
            # prevent last link to use reference beacon from being deleted
            if self.isLastAnchorLink(index):
                QMessageBox.warning(
                    self, 
                    "Last Link To Reference Beacon", 
                    "Cannot remove last link to reference beacon"
                )
                return
            # recursively delete dependant links
            self.deleteLinkDependants(self.beardistChain[index][0][3])
            # delete link
            del self.beardistChain[index]   
            self.updateBearDistChainDependants()
            if len(self.beardistChain) == 0: 
                self.pshbtn_chain_finish.setEnabled(False)
                self.pshbtn_chain_edt.setEnabled(False)
                self.pshbtn_chain_del.setEnabled(False)

    def deleteLinkDependants(self, beacon_to):
        """ Recursively delete dependant links
        """
        gone = False
        while not gone:
            gone = True
            index = -1
            for i, link in enumerate(self.beardistChain):
                if link[0][2] == beacon_to:
                    if not self.isLastAnchorLink(i):
                        index = i
                        gone = False
                        break
            if index != -1:
                if not self.isEndLink(index):
                    self.deleteLinkDependants(self.beardistChain[index][0][3])
                del self.beardistChain[index]

    def setupUi(self):
        """ Initialize ui
        """
        # define dialog
        self.setObjectName(_fromUtf8("dlg_FormBearDist"))
        self.resize(450, 540)
        self.setModal(True)
        # define dialog layout manager 
        self.grdlyt_dlg = QGridLayout(self)
        self.grdlyt_dlg.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.grdlyt_dlg.setObjectName(_fromUtf8("grdlyt_dlg"))
        # define toolbox
        self.tlbx = QToolBox(self)
        self.tlbx.setFrameShape(QFrame.StyledPanel)
        self.tlbx.setObjectName(_fromUtf8("tlbx"))
        self.count = 3
        # define first item: survey plan
        self.itm_plan = QWidget()
        self.itm_plan.setObjectName(_fromUtf8("itm_plan"))
        self.grdlyt_plan = QGridLayout(self.itm_plan)
        self.grdlyt_plan.setObjectName(_fromUtf8("grdlyt_chain"))
        self.vrtlyt_plan = QVBoxLayout()
        self.vrtlyt_plan.setObjectName(_fromUtf8("vrtlyt_plan"))
        self.frmlyt_plan = QFormLayout()
        self.frmlyt_plan.setObjectName(_fromUtf8("frmlyt_plan"))
        self.lbl_plan = QLabel(self.itm_plan)
        self.lbl_plan.setObjectName(_fromUtf8("lbl_plan"))
        self.frmlyt_plan.setWidget(0, QFormLayout.LabelRole, self.lbl_plan)
        self.lnedt_plan = QLineEdit(self.itm_plan)
        self.lnedt_plan.setObjectName(_fromUtf8("lnedt_plan"))
        self.frmlyt_plan.setWidget(0, QFormLayout.FieldRole, self.lnedt_plan)
        self.vrtlyt_plan.addLayout(self.frmlyt_plan)
        self.vrtspc_plan = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vrtlyt_plan.addItem(self.vrtspc_plan)
        self.hrzlyt_plan = QHBoxLayout()
        self.hrzlyt_plan.setObjectName(_fromUtf8("hrzlyt_plan"))
        self.hrzspc_plan = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hrzlyt_plan.addItem(self.hrzspc_plan)
        self.pshbtn_plan_next = XQPushButton(self.itm_plan)
        self.pshbtn_plan_next.setObjectName(_fromUtf8("pshbtn_plan_next"))
        self.hrzlyt_plan.addWidget(self.pshbtn_plan_next)
        self.vrtlyt_plan.addLayout(self.hrzlyt_plan)
        self.grdlyt_plan.addLayout(self.vrtlyt_plan, 0, 0, 1, 1)
        self.tlbx.addItem(self.itm_plan, _fromUtf8(""))
        # define second item: reference beacon
        self.itm_ref = QWidget()
        self.itm_ref.setObjectName(_fromUtf8("itm_ref"))
        self.grdlyt_ref = QGridLayout(self.itm_ref)
        self.grdlyt_ref.setObjectName(_fromUtf8("grdlyt_ref"))
        self.vrtlyt_ref = QVBoxLayout()
        self.vrtlyt_ref.setObjectName(_fromUtf8("vrtlyt_ref"))
        self.frmlyt_ref = QFormLayout()
        self.frmlyt_ref.setObjectName(_fromUtf8("frmlyt_ref"))
        self.lbl_ref = QLabel(self.itm_ref)
        self.lbl_ref.setObjectName(_fromUtf8("lbl_ref"))
        self.frmlyt_ref.setWidget(0, QFormLayout.LabelRole, self.lbl_ref)
        self.lnedt_ref = QLineEdit(self.itm_ref)
        self.lnedt_ref.setObjectName(_fromUtf8("lnedt_ref"))
        self.frmlyt_ref.setWidget(0, QFormLayout.FieldRole, self.lnedt_ref)
        self.vrtlyt_ref.addLayout(self.frmlyt_ref)
        self.vrtspc_ref = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vrtlyt_ref.addItem(self.vrtspc_ref)
        self.hrzlyt_ref = QHBoxLayout()
        self.hrzlyt_ref.setObjectName(_fromUtf8("hrzlyt_ref"))
        self.pshbtn_ref_back = XQPushButton(self.itm_ref)
        self.pshbtn_ref_back.setObjectName(_fromUtf8("pshbtn_ref_back"))
        self.hrzlyt_ref.addWidget(self.pshbtn_ref_back)
        self.hrzspc_ref = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hrzlyt_ref.addItem(self.hrzspc_ref)
        self.pshbtn_ref_next = XQPushButton(self.itm_ref)
        self.pshbtn_ref_next.setObjectName(_fromUtf8("pshbtn_ref_next"))
        self.hrzlyt_ref.addWidget(self.pshbtn_ref_next)
        self.vrtlyt_ref.addLayout(self.hrzlyt_ref)
        self.grdlyt_ref.addLayout(self.vrtlyt_ref, 0, 0, 1, 1)
        self.tlbx.addItem(self.itm_ref, _fromUtf8(""))
        # define third item: beardist chain
        self.itm_chain = QWidget()
        self.itm_chain.setObjectName(_fromUtf8("itm_chain"))
        self.grdlyt_chain = QGridLayout(self.itm_chain)
        self.grdlyt_chain.setObjectName(_fromUtf8("grdlyt_chain"))
        self.vrtlyt_chain = QVBoxLayout()
        self.vrtlyt_chain.setObjectName(_fromUtf8("vrtlyt_chain"))
        self.lst_chain = QListWidget(self.itm_chain)
        self.lst_chain.setObjectName(_fromUtf8("lst_chain"))
        self.vrtlyt_chain.addWidget(self.lst_chain)
        self.hrzlyt_chain_link = QHBoxLayout()
        self.hrzlyt_chain_link.setObjectName(_fromUtf8("hrzlyt_chain_link"))
        self.vrtlyt_chain_link = QVBoxLayout()
        self.vrtlyt_chain_link.setObjectName(_fromUtf8("vrtlyt_chain_link"))
        self.pshbtn_chain_add = XQPushButton(self.itm_chain)
        self.pshbtn_chain_add.setObjectName(_fromUtf8("pshbtn_chain_add"))
        self.vrtlyt_chain_link.addWidget(self.pshbtn_chain_add)
        self.pshbtn_chain_edt = XQPushButton(self.itm_chain)
        self.pshbtn_chain_edt.setObjectName(_fromUtf8("pshbtn_chain_edt"))
        self.vrtlyt_chain_link.addWidget(self.pshbtn_chain_edt)
        self.pshbtn_chain_del = XQPushButton(self.itm_chain)
        self.pshbtn_chain_del.setObjectName(_fromUtf8("pshbtn_chain_del"))
        self.vrtlyt_chain_link.addWidget(self.pshbtn_chain_del)
        self.hrzlyt_chain_link.addLayout(self.vrtlyt_chain_link)
        self.hrzspc_chain_link = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hrzlyt_chain_link.addItem(self.hrzspc_chain_link)
        self.vrtlyt_chain.addLayout(self.hrzlyt_chain_link)
        self.vrtspc_chain = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vrtlyt_chain.addItem(self.vrtspc_chain)
        self.hrzlyt_chain_step = QHBoxLayout()
        self.hrzlyt_chain_step.setObjectName(_fromUtf8("hrzlyt_chain_step"))
        self.pshbtn_chain_back = XQPushButton(self.itm_chain)
        self.pshbtn_chain_back.setObjectName(_fromUtf8("pshbtn_chain_back"))
        self.hrzlyt_chain_step.addWidget(self.pshbtn_chain_back)
        self.hrzspc_chain_step = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hrzlyt_chain_step.addItem(self.hrzspc_chain_step)
        self.pshbtn_chain_finish = XQPushButton(self.itm_chain)
        self.pshbtn_chain_finish.setObjectName(_fromUtf8("pshbtn_chain_finish"))
        self.hrzlyt_chain_step.addWidget(self.pshbtn_chain_finish)
        self.vrtlyt_chain.addLayout(self.hrzlyt_chain_step)
        self.grdlyt_chain.addLayout(self.vrtlyt_chain, 0, 0, 1, 1)
        self.tlbx.addItem(self.itm_chain, _fromUtf8(""))
        # finish dialog definition
        self.grdlyt_dlg.addWidget(self.tlbx, 0, 0, 1, 1)
        self.btnbx_options = XQDialogButtonBox(self)
        self.btnbx_options.setOrientation(Qt.Horizontal)
        self.btnbx_options.setStandardButtons(XQDialogButtonBox.Cancel)
        self.btnbx_options.setObjectName(_fromUtf8("btnbx_options"))
        self.grdlyt_dlg.addWidget(self.btnbx_options, 1, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate(
            "dlg_FormBearDist", 
            "Bearings and Distances Form", 
            None, 
            QApplication.UnicodeUTF8))
        self.lbl_plan.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Survey Plan", 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_plan_next.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Next", 
            None, 
            QApplication.UnicodeUTF8))
        self.tlbx.setItemText(self.tlbx.indexOf(self.itm_plan), 
            QApplication.translate(
                "dlg_FormBearDist", 
                "Step 1: Define Survey Plan", 
                None, 
                QApplication.UnicodeUTF8))
        self.lbl_ref.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Reference Beacon", 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_ref_back.setText(QApplication.translate(
            "dlg_FormBearDist",
            "Back", 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_ref_next.setText(QApplication.translate(
            "dlg_FormBearDist",
            "Next", 
            None, 
            QApplication.UnicodeUTF8))
        self.tlbx.setItemText(self.tlbx.indexOf(self.itm_ref), 
            QApplication.translate(
                "dlg_FormBearDist", 
                "Step 2: Define Reference Beacon", 
                None, 
                QApplication.UnicodeUTF8))
        self.pshbtn_chain_add.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Add Link", 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_chain_edt.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Edit Link", 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_chain_del.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Delete Link", 
            None, 
            QApplication.UnicodeUTF8))
        self.pshbtn_chain_back.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Back",
            None,
            QApplication.UnicodeUTF8))
        self.pshbtn_chain_finish.setText(QApplication.translate(
            "dlg_FormBearDist", 
            "Finish", 
            None, 
            QApplication.UnicodeUTF8))
        self.tlbx.setItemText(self.tlbx.indexOf(self.itm_chain), 
                QApplication.translate(
                    "dlg_FormBearDist", 
                    "Step 3: Define Bearings and Distances Chain", 
                    None, 
                    QApplication.UnicodeUTF8))
        # connect ui widgets
        self.btnbx_options.accepted.connect(self.accept)
        self.btnbx_options.rejected.connect(self.reject)
        self.pshbtn_chain_finish.clicked.connect(lambda: self.checkItemBearDistChain(True))
        self.pshbtn_chain_back.clicked.connect(lambda: self.checkItemBearDistChain(False))
        self.pshbtn_ref_next.clicked.connect(lambda: self.checkItemReferenceBeacon(True))
        self.pshbtn_ref_back.clicked.connect(lambda: self.checkItemReferenceBeacon(False))
        self.pshbtn_plan_next.clicked.connect(lambda : self.checkItemSurveyPlan(True))
        self.pshbtn_chain_add.clicked.connect(self.addLink)
        self.pshbtn_chain_edt.clicked.connect(self.editLink)
        self.pshbtn_chain_del.clicked.connect(self.deleteLink)
        QMetaObject.connectSlotsByName(self)

    def confirmBack(self):
        return QMessageBox.question(
            self, 
            "Going Back", 
            "Any changes made will be lost. Are your sure that you want to go back?", 
            QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes 


class dlg_FormBearDistLink(QDialog):
    """ This dialog enables the user to add a bearing and distance link
    """

    def __init__(self, db, fromBeacons, query, values=[], parent = None):
        # initialize QDialog class
        super(dlg_FormBearDistLink, self).__init__(parent, Qt.WindowStaysOnTopHint)
        # initialize ui
        self.setupUi(fromBeacons)
        # initialize instance variables
        self.values_old = values
        self.values_new = []
        self.db = db
        self.query = query
        self.fromBeacons = fromBeacons
        self.colours = {
            "EMPTY":"background-color: rgba(255, 107, 107, 150);",
            "TYPE":"background-color: rgba(107, 107, 255, 150);",
            "BEACON":"background-color: rgba(107, 255, 107, 150);",
            "UNIQUE":"background-color: rgba(107, 255, 107, 150);"
        }
        # populate form if values are given
        if bool(values): 
            self.populateForm(values)

    def populateForm(self, values):
        """ Populte form with values given
        """
        for index, lnedt in enumerate(self.lnedts): 
            if values[index] is not None: 
                lnedt.setText(str(values[index]))

    def getValues(self):
        return self.values_new

    def executeOption(self, button):
        """ Perform validation and close the dialog
        """
        if self.btnbx_options.standardButton(button) == QDialogButtonBox.Save:
            values_new = []
            # check required fields        
            valid = True
            for index,lnedt in enumerate(self.lnedts):
                if self.fields[index].required:
                    if str(lnedt.text()).strip() is "":
                        lnedt.setStyleSheet(self.colours["EMPTY"])
                        valid = False
                    else: lnedt.setStyleSheet("")
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Empty Required Fields", 
                    "Please ensure that all required fields are completed."
                )
                return
            # check correct field types
            valid = True
            for index,lnedt in enumerate(self.lnedts):
                try:
                    cast = self.fields[index].type
                    txt = str(lnedt.text()).strip()
                    if txt is "": tmp = None
                    else: tmp = cast(txt)
                    values_new.append(tmp)
                    lnedt.setStyleSheet("")
                except Exception as e:
                    lnedt.setStyleSheet(self.colours["TYPE"])
                    valid = False
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Invalid Field Types", 
                    "Please ensure that fields are completed with valid types."
                )
                return
            # check valid from beacon field
            valid = True
            for index,lnedt in enumerate(self.lnedts):
                if self.fields[index].name.lower() == "from":
                    if str(lnedt.text()) not in self.fromBeacons:
                        lnedt.setStyleSheet(self.colours["BEACON"])
                        valid = False
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Invalid Reference", 
                    "Please ensure that specified beacons are valid."
                )
                return
            # check valid to beacon field
            valid = True
            for index,lnedt in enumerate(self.lnedts):
                if self.fields[index].name.lower() == "to": 
                    if bool(self.values_old):
                        if str(lnedt.text()) not in self.values_old:
                            if str(lnedt.text()) in self.fromBeacons:
                                lnedt.setStyleSheet(self.colours["UNIQUE"])
                                valid = False
                                break
                    elif not bool(self.values_old):
                        if str(lnedt.text()) in self.fromBeacons:
                            lnedt.setStyleSheet(self.colours["UNIQUE"])
                            valid = False
                            break
                    if bool(int(self.db.query(self.query %('beacon', "%s"), (str(lnedt.text()),))[0][0])):
                        lnedt.setStyleSheet(self.colours["UNIQUE"])
                        valid = False
                        break
            if not valid: 
                QMessageBox.information(
                    self, 
                    "Invalid Reference", 
                    "Please ensure that the new beacon is unique."
                )
                return
            # save values
            self.values_new = values_new
            # accept dialog
            self.accept()
        else:
            # reject dialog
            self.reject()

    def setupUi(self, fromBeacons):
        """ Initialize ui
        """
        # define dialog
        self.gridLayout = QGridLayout(self)
        self.setModal(True)
        self.gridLayout.setSizeConstraint(QLayout.SetFixedSize)        
        self.formLayout = QFormLayout()
        self.lbls = []
        self.lnedts = []
        self.fields = [
            Field("Bearing", float, True, False),
            Field("Distance", float, True, False),
            Field("From", str, True, False),
            Field("To", str, True, False),
            Field("Location", str, False, False),
            Field("Surveyor", str, False, False)
        ]
        for index, f in enumerate(self.fields):
            lbl = QLabel(self)
            self.formLayout.setWidget(index, QFormLayout.LabelRole, lbl)
            lbl.setText(QApplication.translate(
                "dlg_FormBearDistEntry", 
                ("*" if f.required else "") + f.name.title(), 
                None, 
                QApplication.UnicodeUTF8
            ))
            self.lbls.append(lbl)
            lnedt = QLineEdit(self)
            self.formLayout.setWidget(index, QFormLayout.FieldRole, lnedt)
            self.lnedts.append(lnedt)
            if f.name.lower() == "from":
                model = QStringListModel()
                model.setStringList(fromBeacons)
                completer = QCompleter()        
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setModel(model)
                lnedt.setCompleter(completer)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.btnbx_options = QDialogButtonBox(self)
        self.btnbx_options.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnbx_options.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.gridLayout.addWidget(self.btnbx_options, 1, 0, 1, 1)
        # translate ui widgets' text
        self.setWindowTitle(QApplication.translate(
            "dlg_FormBearDistEntry", 
            "Link Form", 
            None, 
            QApplication.UnicodeUTF8
        ))
        # connect ui widgets
        self.btnbx_options.clicked.connect(self.executeOption)
        QMetaObject.connectSlotsByName(self)

