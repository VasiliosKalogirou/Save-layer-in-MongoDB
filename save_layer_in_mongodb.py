# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveLayerInMongoDB
                                 A QGIS plugin
 This plugin saves data from a layer into a MongoDB database.
                              -------------------
        begin                : 2016-07-26
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Vasilios Kalogirou
        email                : kalogirou.vasilis@gmail.com
 ***************************************************************************/

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
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from save_layer_in_mongodb_dialog import SaveLayerInMongoDBDialog
import os.path

try:
    from pymongo import MongoClient, GEO2D
except ImportError as e:
    QMessageBox.critical(iface.mainWindow(),
                         "Missing module",
                         "Pymongo module is required",
                         QMessageBox.Ok)


class SaveLayerInMongoDB:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SaveLayerInMongoDB_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SaveLayerInMongoDBDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Save Layer in MongoDB')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SaveLayerInMongoDB')
        self.toolbar.setObjectName(u'SaveLayerInMongoDB')

        # Populate the comboBox_layers QComboBox with the layers on screen
        self.populate_layerbox()

        # Call the connect_to_mongo function when the user clicks on the pushButton_save QPushButton
        self.dlg.pushButton_save.clicked.connect(self.connect_to_mongo)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SaveLayerInMongoDB', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SaveLayerInMongoDB/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Save data in MongoDB'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Save Layer in MongoDB'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        self.populate_layerbox()
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result: # if the OK button is clicked
            # Call the connect_to_mongo function to connect to MongoDB
            pass

    def populate_layerbox(self):
        self.dlg.comboBox_layers.clear() # Clear the comboBox_layers QComboBox
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())

        self.dlg.comboBox_layers.addItems(list(set(layer_list)))
        del layers, layer_list

    def connect_to_mongo(self):
        # try to get the server name
        server = str(self.dlg.lineEdit_server.text())
        if server == "":
            msgBox = QMessageBox()
            msgBox.setText("Please enter a valid server name!")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
            return

        # try to get the port number
        try:
            port = int(self.dlg.lineEdit_port.text())
        except:
            msgBox = QMessageBox()
            msgBox.setText("Please enter a valid port number!")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
            return

        #try to get the database name
        db_name = str(self.dlg.lineEdit_database.text())
        if db_name == "":
            msgBox = QMessageBox()
            msgBox.setText(
                "Please enter a valid database name!" + '\n' + "Please note that if the database does not exist,"
                                                               "it will be created automatically by MongoDB.")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
            return

        #try to get the collection name
        collection_name = str(self.dlg.lineEdit_collection.text())
        if collection_name == "":
            msgBox = QMessageBox()
            msgBox.setText("Please enter a valid connection name!" + '\n' +
                           "Please note that if the collection does not exist,"
                            "it will be created automatically by MongoDB.")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
            return

        #try to get the geometry field name
        geometry_field = str(self.dlg.lineEdit_geometry.text())
        if geometry_field == "":
            msgBox = QMessageBox()
            msgBox.setText(
                "Please enter a valid geometry field name!")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
            return

        try: #try to connect to the server
            self.client = MongoClient(str(server), port, serverSelectionTimeoutMS=500) # establish connection to the mongoDB server
            sFeaturesCount = self.save_data(self.client, db_name, collection_name, geometry_field) # Call the save_data function to save the data in MongoDB
            msgBox = QMessageBox()
            msgBox.setText("Connection successful!\n" +
                           str(sFeaturesCount) + " features saved in the " + '"' + collection_name + '"' + " collection within the " +
                           '"' + db_name + '"' + " database!")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
        except: # if connection unsuccessful then show a message box to the user that something is wrong
            msgBox = QMessageBox()
            msgBox.setText("Connection unsuccessful! Check server name or check if server is offline!")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.exec_()
            return

    def save_data(self, mclient, db_name, collection_name, geom_field):
        db = mclient[db_name] # this is the database name

        # Find which layer the user has selected using the "comboBox_layers" QComboBox
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dlg.comboBox_layers.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        fields = selectedLayer.pendingFields() # Get the fields from the selected layer

        # If the user clicks on the checkBox_features QCheckBox then  save only the layer's selected features
        if self.dlg.checkBox_features.isChecked():
            sFeatures = selectedLayer.selectedFeatures()
        else:
            sFeatures = selectedLayer.getFeatures()

        sFeaturesCount = 0  # Create a variable to count the number of features that will be saved in the collection
        for f in sFeatures: # Iterate through the features
            # Call the return_geometry function to get the type of the geometry and the coordinates of each feature
            feature_type, coords = self.return_geometry(f.geometry())

            # Construct an empty dictionary for every feature
            fdict = dict()

            # Iterate through all the fields of the layer and construct a dictionary of the fields for each feature
            for field in fields:
                # if str(field.typeName()) == 'String':
                if str(type(f[field.name()])) == "<class 'PyQt4.QtCore.QPyNullVariant'>":
                    fdict[str(field.name())] = "null"
                elif str(type(f[field.name()])) == "<type 'unicode'>":
                    fdict[str(field.name())] = f[field.name()].encode("utf-8")
                else:
                    fdict[str(field.name())] = f[field.name()]

            # Save each feature as a single document in MongoDB
            db[collection_name].insert_one({geom_field: {"type": feature_type, "coordinates": coords},
                                            "properties": fdict})
            sFeaturesCount = sFeaturesCount + 1

        return sFeaturesCount
        del layers, selectedLayerIndex, fields, sFeatures


    def return_geometry(self, feature_geom):
        coordinates = [] # Construct an empty array to store the coordinates of each feature in it
        if feature_geom.type() == 0:
            type = 'Point'
            coordinates = [feature_geom.asPoint().x(), feature_geom.asPoint().y()]
        elif feature_geom.type() == 1:
            type = 'LineString'
            for p in range(len(feature_geom.asPolyline())): # Iterate through all the points of the line
                point = [feature_geom.asPolyline()[p].x(), feature_geom.asPolyline()[p].y()]
                coordinates.append(point)
        elif feature_geom.type() == 2:
            type = 'Polygon'
            coordinates = []
            for l in range(len(feature_geom.asPolygon())): # Iterate through all the parts of the polygon
                line =[]
                for p in range(len(feature_geom.asPolygon()[l])): # Iterate through all the points of each part
                    point = [feature_geom.asPolygon()[l][p].x(), feature_geom.asPolygon()[l][p].y()]
                    line.append(point)
                coordinates.append(line)
        else:
            type = 'multi-geometry'
        return type, coordinates
