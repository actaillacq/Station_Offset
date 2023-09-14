# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StationOffset
                                 A QGIS plugin
 This plugin computes the station and offset of points along polylines and exports those values to csv for other applications
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-17
        copyright            : (C) 2023 by Tailwater Limited
        email                : applications@tailwaterlimited.com
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

__author__ = 'Tailwater Limited'
__date__ = '2023-08-04'
__copyright__ = '(C) 2023 by Tailwater Limited'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load StationOffset class from file StationOffset.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .streamTools import StreamToolsPlugin
    return StreamToolsPlugin()
