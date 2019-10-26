# Mapnik renderer

## Introduction

This document describes how to render maps using mapnik, with the OpenStreetMap data loaded in a PostgreSQL database.

## Disclaimer

The procedure in this document is verified to work in a Linux environment. There is no reason it shouldn't work on Windows, Mac OS or other operating systems, but it might require additional steps or a slightly different approach. If you have any questions or feedback, you are welcome to contact me on roel.derickx --at-- gmail.

## Prerequisites

Rendering maps is a complex task, requiring several software components to work together. Since extensive documentation is available online, this tutorial will not explain how to install and configure these components. The version numbers in the following list are merely indicative, other versions might work as well:

* [PostgreSQL 11.5.4](http://www.postgresql.org/), the database where map data will be stored.
* [Postgis 2.5.3](http://postgis.net/), a plugin for PostgreSQL adding support for geographic objects.
* [osm2pgsql 0.93.0](https://github.com/openstreetmap/osm2pgsql), the tool to import OpenStreetMap data in the local PostgreSQL database.
* [OpenStreetMap CartoCSS](https://github.com/gravitystorm/openstreetmap-carto), the standard OpenStreetMap stylesheet.
* [Lua 5.3.5](http://www.lua.org/), a programming language used by the OpenStreetMap stylesheet to transform tags.
* [Node.js 12.13.0](https://nodejs.org/), a javascript interpreter to run [CartoCSS 1.2.0](https://github.com/mapbox/carto).
* [Mapnik 3.0.22](http://mapnik.org/), the toolkit to actually render the maps. You also need [python-mapnik](https://github.com/mapnik/python-mapnik/), the Python bindings for this library.
* [GDAL 3.0.1](http://www.gdal.org/), or Geospatial Data Abstraction Library.
* Some scripts use the bash shell, which is available on most systems. If you happen to run Windows, it's also recommended to install [cygwin](http://cygwin.com/)
    
## Setting up the database

### Preparing the database

It is highly recommended to create a new database where all map and elevation data will be stored. Open a command-line interface to PostgreSQL using the database administrator account, which is most likely called postgres:
```bash
psql -U postgres
```
First create a user. For the rest of this tutorial it is assumed the user is named gis with password gis, but of course you are free to choose a different username and/or password:
```bash
postgres=# CREATE USER gis PASSWORD 'gis';
CREATE ROLE
```
Continue to create a database:
```bash
postgres=# CREATE DATABASE gis OWNER gis;
CREATE DATABASE
```
Change to the new database and enable both the postgis and the hstore plugin:
```bash
postgres=# \c gis
You are now connected to database "gis" as user "postgres".
gis=# CREATE EXTENSION postgis;
CREATE EXTENSION
gis=# CREATE EXTENSION hstore;
CREATE EXTENSION
```

### Loading data in the database

The next step is importing OpenStreetMap data in the newly created database. The data can be obtained from several sources online, for example from [Geofabrik](http://download.geofabrik.de/). You will have the choice between several file types of which the binary format (*.pbf) is the best choice. It has the smallest file size and is natively supported in osm2pgsql. Once the desired area is downloaded, run the following command to import the data:
```bash
osm2pgsql -d gis -U gis -s data.osm.pbf --style openstreetmap-carto.style --tag-transform-script openstreetmap-carto.lua --hstore-all
```
The files openstreetmap-carto.style and openstreetmap-carto.lua can be found in the OpenStreetMap CartoCSS package. It might be useful to specify the -C parameter to define the amount of cache memory and --number-processes to define the amount of threads used by osm2pgsql.  
Note that it is impossible to import map data which is overlapping with data already in the database. This happens not only when you import the same area twice, but also when areas with common borders are imported. To resolve this problem, drop the planet\_osm\_% tables from your gis database, concatenate all osm files you want to import using a tool called [Osmosis](https://github.com/openstreetmap/osmosis) and re-import the resulting file.
    
## Configuring the stylesheet

The design of the map can be completely configured, allowing control over colors, fonts, icons and linestyles. This is achieved using a language called CartoCSS, somewhat similar in syntax to CSS but designed specifically to define maps. The syntax of this language is far beyond the scope of this document, but an introduction can be found [here](https://github.com/mapbox/carto/blob/master/docs/api/mapnik/3.0.6.rst).  
The easiest way to start is using the freely available OpenStreetMap stylesheet. After unzipping the archive you will find a file called INSTALL.md with detailed information on how to download the extra required shapefiles. You should also make sure all necessary fonts are installed.  
Mapnik requires the stylesheet to be one single XML file. Because lengthy files are rather cumbersome to edit, the stylesheet is developed in several smaller files, assembled together using CartoCSS.  
First of all you should specify how mapnik should connect to the database by specifying the user and password. To do so open the file project.mml and look for the osm2pgsql section, you should edit it to look like this:
```
  osm2pgsql: &osm2pgsql
  type: "postgis"
  dbname: "gis"
  user: "gis"
  password: "gis"
  key_field: ""
  geometry_field: "way"
  extent: "-20037508,-20037508,20037508,20037508"
```
Next you can generate the XML file which you will need to run hm-render-mapnik:
```bash
carto -a "3.0.0" project.mml > mapnik_style.xml
```
Carto is able to generate stylesheets for specific versions of mapnik, it is good practice to pass the exact mapnik version you use to the -a parameter.
    
## Elevation data

When using maps for outdoor purposes like hiking or cycling, elevation lines are a must. However, the OpenStreetMap data does not include elevation data and as such this is also not rendered by default by the OpenStreetMap stylesheet.
    
### Obtaining elevation data

First of all you should download elevation data, often called DEM (digital elevation model) or DTM (digital terrain model). It is important to find a model with an acceptable resolution, generally a precision of 3 arc-seconds is enough, meaning that there is one value for the altitude in each area of 3 arc-seconds squared. This value may not be accurate when it is measured by a satelite, the height of trees, snow or other objects may be measured in stead of the height of the terrain itself.

* NASA's [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/), version 2.1. For land areas between 60 degrees south and 60 degrees north they offer a resolution of [3 arc-seconds](http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/), but for the United States a [1 arc-second version](http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/) is available.
* NASA's Shuttle Radar Topography Mission, version 3. This source covers the same area as version 2.1, but in a 1 arc-second resolution. You need to register first before having access to the [EarthExplorer](https://earthexplorer.usgs.gov/) and it is suggested to use the Bulk Download Application to download vast areas. For more information please consult [the help index](https://lta.cr.usgs.gov/EEHelp/ee_help).
* However, version 3 of NASA's SRTM seems to contain large voids, a [void-filled version](https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/) is around as well. You need to register first and the user account is not the same as for the EarthExplorer.
* [Viewfinder Panoramas](http://www.viewfinderpanoramas.org/dem3.html). This source offers global coverage in a 3-arc second resolution, it is the only option beyond 60 degrees north. There is a limited selection of areas in a 1 arc-second resolution as well.
* Resolution does not always equals accuracy, data may have been interpolated from lower resolutions or inserted from other sources. For a limited selection of European countries there is a 1-arc second resolution available with a [higher accuracy]((https://data.opendataportal.at/dataset/dtm-europe)). The data is obtained using laserscan (LiDAR) in stead of satelites.
* Commercial elevation models, which may offer a higher resolution or more accurate data. Keep in mind that the data may be offered in a different projection, use the GDAL tools to reproject the data. Also note that each country has a different definition of sea level, your altitude lines may shift at the borders when importing several elevation models in the same database.

Make sure you obtain either HGT or GeoTIFF files or to convert them to either format using GDAL.

### Importing elevation data in the database

While it is possible to use the height files [without prior processing](https://wiki.openstreetmap.org/wiki/Contour_relief_maps_using_mapnik), it is highly recommended to import the data in the database. To do so you should copy import\_in\_db.sh to the directory where you saved the elevation files. Open the script and configure the parameters at the start. You can configure the file extension of the files to import, either hgt, tif or zip is valid. The database schema, user, password and table name can als be configured. Note that when modifying the table name you are required to modify the queries in the stylesheet below accordingly.  
Warning: the script will delete certain files to minimize disk space while processing. Keep in mind not to put other valuable files apart from the downloaded files and the import script in the same directory!
    
### Rendering elevation lines

It is of course important to tell mapnik how to render the elevation lines. Open the file project.mml from the OpenStreetMap CartoCSS for editing and add a new database connection, with the same connection parameters as the osm2pgsql connection but with a different geometry field:
```
elevation2pgsql: &elevation2pgsql
  type: "postgis"
  dbname: "gis"
  user: "gis"
  password: "gis"
  key_field: ""
  geometry_field: "geom"
  extent: "-20037508,-20037508,20037508,20037508"
```
Continue to the section Stylesheet, just below the database connections. It should include a link to a new file elevation.mss, which is included in the hikingmap package:
```
Stylesheet:
  - style.mss
  - fonts.mss
  - shapefiles.mss
  - landcover.mss
  - elevation.mss
  - water.mss
  - water-features.mss
  - road-colors-generated.mss
  - roads.mss
  - power.mss
  - placenames.mss
  - buildings.mss
  - stations.mss
  - amenity-points.mss
  - ferry-routes.mss
  - aerialways.mss
  - admin.mss
  - addressing.mss
```
Next look for a section landuse-overlay and add three new sections below:
```
  - id: srtm-10
    name: srtm-10
    class: ""
    geometry: linestring
    extent: "-180,-89.99,180,89.99"
    srs-name: "900913"
    srs: "+proj=latlong +datum=WGS84"
    <<: *extents
    Datasource:
      <<: *elevation2pgsql
      table: |-
        (SELECT geom, height
         FROM elevation
         WHERE height::integer % 10 = 0 AND height::integer % 50 != 0
        ) AS contours10
    properties:
      minzoom: 14
    advanced: {}
  - id: srtm-50
    name: srtm-50
    class: ""
    geometry: linestring
    extent: "-180,-89.99,180,89.99"
    srs-name: "900913"
    srs: "+proj=latlong +datum=WGS84"
    <<: *extents
    Datasource:
      <<: *elevation2pgsql
      table: |-
        (SELECT geom, height
         FROM elevation
         WHERE height::integer % 50 = 0 AND height::integer % 100 != 0
        ) AS contours50
    properties:
      minzoom: 12
    advanced: {}
  - id: srtm-100
    name: srtm-100
    class: ""
    geometry: linestring
    extent: "-180,-89.99,180,89.99"
    srs-name: "900913"
    srs: "+proj=latlong +datum=WGS84"
    <<: *extents
    Datasource:
      <<: *elevation2pgsql
      table: |-
        (SELECT geom, height
         FROM elevation
         WHERE height::integer % 100 = 0
        ) AS contours100
    properties:
      minzoom: 11
    advanced: {}
```
When all is in place you have to regenerate the XML style (see [above](#configuring-the-stylesheet)) before rendering maps with elevation lines.
    
## Roadmap

* Inclusion of copyright text on the bottom of each page, as requested by [OpenStreetMap](http://www.openstreetmap.org/copyright).
* A new stylesheet allowing the map to be printed in black and white. There is nothing wrong with the OpenStreetMap stylesheet, but when printed the difference between for example water and forest is not clear. Text is not always readable and some information is irrelevant for hiking or cycling.
* Hillshading. There is an experimental script to import elevation data as hillshading in the database but the subject needs more studying first.

## License

![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)

This tutorial is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

