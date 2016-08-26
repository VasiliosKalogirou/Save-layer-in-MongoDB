# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveLayerInMongoDB
                                 A QGIS plugin
 This plugin saves data from a layer in a MongoDB database.
                             -------------------
        begin                : 2016-08-25
        copyright            : (C) 2016 by Vasilios Kalogirou
        email                : kalogirou.vasilis@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SaveLayerInMongoDB class from file SaveLayerInMongoDB.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .save_layer_in_mongodb import SaveLayerInMongoDB
    return SaveLayerInMongoDB(iface)
