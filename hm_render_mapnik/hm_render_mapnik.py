#!/usr/bin/env python3

# hm-render-mapnik -- render maps on paper using data from OpenStreetMap
# Copyright (C) 2019  Roel Derickx <roel.derickx AT gmail>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, argparse, math, mapnik
from xml.dom import minidom

# global constants
earthCircumference = 40041.44 # km (average, equatorial 40075.017 km / meridional 40007.86 km)
cmToKmFactor = 100000.0
inch = 2.54 # cm

def search_configfile():
    filename = 'hm-render-mapnik.config.xml'
    if os.path.exists(filename):
        return os.path.abspath(filename)
    elif os.path.exists(os.path.join(os.path.expanduser('~'), '.' + filename)):
        return os.path.join(os.path.expanduser('~'), '.' + filename)
    else:
        return None


def get_xml_subtag_value(xmlnode, sublabelname):
    elements = xmlnode.getElementsByTagName(sublabelname)
    return str(elements[0].firstChild.nodeValue) if elements and elements[0].childNodes else None


def parse_configfile():
    config = {}
    config['mapstyle'] = 'mapnik_style.xml'
    config['hikingmapstyle'] = 'hikingmap_style.xml'
    config['output_format'] = 'png'
    config['dpi'] = 300
    config['scale_factor'] = 1.0

    configfile = search_configfile()
    
    if configfile:
        xmldoc = None
        xmlmapnik = None
        
        try:
            xmldoc = minidom.parse(configfile)
        except:
            pass
        
        if xmldoc:
            xmlmapnik_element = xmldoc.getElementsByTagName('hm-render-mapnik')
            if xmlmapnik_element:
                xmlmapnik = xmlmapnik_element[0]
        
        if xmlmapnik:
            mapstyle = get_xml_subtag_value(xmlmapnik, 'mapstyle')
            if mapstyle:
                config['mapstyle'] = mapstyle
            
            hikingmapstyle = get_xml_subtag_value(xmlmapnik, 'hikingmapstyle')
            if hikingmapstyle:
                config['hikingmapstyle'] = hikingmapstyle
            
            output_format = get_xml_subtag_value(xmlmapnik, 'outputformat')
            if output_format:
                config['output_format'] = output_format
            
            dpi = get_xml_subtag_value(xmlmapnik, 'dpi')
            if dpi:
                config['dpi'] = int(dpi)
            
            scale_factor = get_xml_subtag_value(xmlmapnik, 'scalefactor')
            if scale_factor:
                config['scale_factor'] = float(scale_factor)
            
            xmlfontdirlist = xmlmapnik.getElementsByTagName('fontdirs')
            
            for xmlfontdir in xmlfontdirlist:
                fontdir = get_xml_subtag_value(xmlfontdir, 'fontdir')
                if fontdir:
                    mapnik.FontEngine.register_fonts(fontdir, True)
    
    return config


def parse_commandline():
    config = parse_configfile()

    parser = argparse.ArgumentParser(description = "Render a map on paper using mapnik")
    parser.add_argument('--pagewidth', dest = 'pagewidth', type = float, default = 20.0, \
                        help = "page width in cm")
    parser.add_argument('--pageheight', dest = 'pageheight', type = float, default = 28.7, \
                        help = "page height in cm")
    parser.add_argument('-b', '--basename', dest = 'basefilename', default = "detail", \
                        help = "base filename without extension")
    parser.add_argument('-t', dest = 'temptrackfile', \
                        help = "temp track file to render")
    parser.add_argument('-y', dest = 'tempwaypointfile', \
                        help = "temp waypoints file to render")
    parser.add_argument('-v', dest = 'verbose', action = 'store_true')
    # hm-render-mapnik specific parameters
    parser.add_argument('-d', '--dpi', type=int, default=config['dpi'], \
                        help = "amount of detail to render in dots per inch (default: %(default)s)")
    parser.add_argument('-S', '--scale-factor', type=float, default=config['scale_factor'], \
                        help = "scale factor (default: %(default)s)")
    parser.add_argument('-m', '--mapstyle', default=config['mapstyle'], \
                        help = "mapnik stylesheet file (default: %(default)s)")
    parser.add_argument('--hikingmapstyle', default=config['hikingmapstyle'], \
                        help = "hikingmap stylesheet file, contains the CartoCSS for " + \
                               "the tracks and the waypoints (default: %(default)s)")
    parser.add_argument('-f', '--format', dest='output_format', default=config['output_format'], \
                        help = "output format, consult the mapnik documentation for " + \
                               "possible values (default: %(default)s)")
    # --
    parser.add_argument('gpxfiles', nargs = '*')
    
    subparsers = parser.add_subparsers(dest='mode', required=True, \
                                       help='bounding box or center mode')
    
    # create the parser for the bbox command
    parser_bbox = subparsers.add_parser('bbox', help='define bounding box')
    parser_bbox.add_argument('-o', '--minlon', type=float, required = True, \
                        help = "minimum longitude")
    parser_bbox.add_argument('-O', '--maxlon', type=float, required = True, \
                        help = "maximum longitude")
    parser_bbox.add_argument('-a', '--minlat', type=float, required = True, \
                        help = "minimum latitude")
    parser_bbox.add_argument('-A', '--maxlat', type=float, required = True, \
                        help = "maximum latitude")

    # create the parser for the atlas command
    parser_atlas = subparsers.add_parser('center', help='define center mode')
    parser_atlas.add_argument('--lon', type=float, required=True, \
                              help='longitude of the center of map')
    parser_atlas.add_argument('--lat', type=float, required=True, \
                              help='latitude of the center of map')
    parser_atlas.add_argument('--scale', type=int, default=50000, \
                              help='scale denominator')

    return parser.parse_args()


def convert_cm_to_degrees_lon(lengthcm, scale, latitude):
    lengthkm = lengthcm / cmToKmFactor * scale
    return lengthkm / ((earthCircumference / 360.0) * math.cos(math.radians(latitude)))


def convert_cm_to_degrees_lat(lengthcm, scale):
    lengthkm = lengthcm / cmToKmFactor * scale
    return lengthkm / (earthCircumference / 360.0)


def assure_bbox_mode(parameters):
    if parameters.mode == 'center':
        pagesize_lon = convert_cm_to_degrees_lon(parameters.pagewidth, \
                                                 parameters.scale, parameters.lat)
        pagesize_lat = convert_cm_to_degrees_lat(parameters.pageheight, parameters.scale)
        
        parameters.minlon = parameters.lon - pagesize_lon / 2
        parameters.minlat = parameters.lat - pagesize_lat / 2
        parameters.maxlon = parameters.lon + pagesize_lon / 2
        parameters.maxlat = parameters.lat + pagesize_lat / 2

def render(parameters):
    if not parameters.verbose:
        mapnik.logger.set_severity(getattr(mapnik.severity_type, 'None'))

    merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
    longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

    imgwidth = math.trunc(parameters.pagewidth / inch * parameters.dpi)
    imgheight = math.trunc(parameters.pageheight / inch * parameters.dpi)

    m = mapnik.Map(imgwidth, imgheight)
    mapnik.load_map(m, parameters.mapstyle)
    mapnik.load_map(m, parameters.hikingmapstyle)
    m.srs = merc.params()

    if hasattr(mapnik, 'Box2d'):
        bbox = mapnik.Box2d(parameters.minlon, parameters.minlat, parameters.maxlon, parameters.maxlat)
    else:
        bbox = mapnik.Envelope(parameters.minlon, parameters.minlat, parameters.maxlon, parameters.maxlat)

    transform = mapnik.ProjTransform(longlat, merc)
    merc_bbox = transform.forward(bbox)
    m.zoom_to_box(merc_bbox)

    for gpxfile in parameters.gpxfiles:
        gpxlayer = mapnik.Layer('GPXLayer')
        gpxlayer.datasource = mapnik.Ogr(file = gpxfile, layer = 'tracks')
        gpxlayer.styles.append('GPXStyle')
        m.layers.append(gpxlayer)

    if parameters.temptrackfile:
        overviewlayer = mapnik.Layer('OverviewLayer')
        overviewlayer.datasource = mapnik.Ogr(file = parameters.temptrackfile, layer = 'tracks')
        overviewlayer.styles.append('GPXStyle')
        m.layers.append(overviewlayer)
    
    if parameters.tempwaypointfile:
        waypointlayer = mapnik.Layer('WaypointLayer')
        waypointlayer.datasource = mapnik.Ogr(file = parameters.tempwaypointfile, layer = 'waypoints')
        waypointlayer.styles.append('WaypointStyle')
        m.layers.append(waypointlayer)

    mapnik.render_to_file(m, parameters.basefilename + "." + parameters.output_format,
                          parameters.output_format,
                          parameters.scale_factor)


def main():
    parameters = parse_commandline()
    assure_bbox_mode(parameters)
    
    render(parameters)


if __name__ == '__main__':
    main()

