# Render paper maps from Openstreetmap data using mapnik

This program renders an area with given boundaries using data from Openstreetmap. It is designed to work with hikingmap but it can be used standalone as well if desired.

## Installation
Clone this repository and run the following command in the created directory.
```bash
python setup.py install
```

## Usage

`hm-render-mapnik [OPTION]... [gpxfiles]... bbox|center ...`

Options:

| Parameter | Description
| --------- | -----------
| `--pagewidth` | Page width in cm
| `--pageheight` | Page height in cm
| `-b, --basename` | Base filename without extension
| `-t` | Temp track file to render. This is used by hikingmap to draw the page boundaries of the overview map, the tracks will be saved as a temporary GPX file.
| `-y` | Temp waypoints file to render. This is used by hikingmap to render the distance each kilometer or mile, the waypoints will be saved as a temporary GPX file.
| `-v, --verbose` | Display extra information while processing.
| `-h, --help` | Display help
| `-d, --dpi` | Amount of detail to render in dots per inch, default 300
| `-S, --scale-factor` | Scale factor, default 1.0
| `-m, --mapstyle` | Mapnik stylesheet file, default mapnik_style.xml
| `--hikingmapstyle` | Hikingmap stylesheet file, contains the CartoCSS for the tracks and the waypoints. The default is hikingmapstyle.xml, see the repository for an example.
| `-f, --format` | Output format. Consult the [mapnik documentation](http://mapnik.org/docs/v2.2.0/api/python/mapnik._mapnik-module.html#render_to_file) for possible values, default png
| `gpxfiles` | The GPX track(s) to render.

After these parameters you are required to make a choice between bbox and center. In bbox mode the rendered area will be a defined bounding box and in center mode you can specify a center coordinate and a scale.

Options for bbox mode:

| Parameter | Description
| --------- | -----------
| `-o, --minlon` | Minimum longitude of the page
| `-O, --maxlon` | Maximum longitude of the page
| `-a, --minlat` | Minimum latitude of the page
| `-A, --maxlat` | Maximum latitude of the page

Note that mapnik will maintain the aspect ratio, the rendered area may not correspond exactly to the given boundary.

Options for center mode:

| Parameter | Description
| --------- | -----------
| `--lon` | Longitude of the center of the page
| `--lat` | Latitude of the center of the page
| `--scale` | Scale denominator, default 50000

## Configuration file

Because most of the time you will want to use the same parameters, you can optionally override the defaults in a configuration file. hm-render-mapnik will search for a file hm-render-mapnik.config.xml in the current directory, if not found it will resort to ~/.hm-render-mapnik.config.xml

```
<?xml version="1.0" encoding="utf-8"?>
<hm-render-mapnik>
    <mapstyle>mapnik_style.xml</mapstyle>
    <hikingmapstyle>hikingmap_style.xml</hikingmapstyle>
    <outputformat>pdf</outputformat>
    <dpi>300</dpi>
    <scalefactor>1.0</scalefactor>
    <fontdirs>
        <fontdir>/usr/share/fonts/noto</fontdir>
        <fontdir>/usr/share/fonts/noto-cjk</fontdir>
        <fontdir>/usr/share/fonts/TTF</fontdir>
    </fontdirs>
</hm-render-mapnik>
```

Options:

| Tag | Description
| --- | -----------
| mapstyle | Mapnik stylesheet file, contains the style to draw the map.
| hikingmapstyle | Hikingmap stylesheet file, contains the CartoCSS for the tracks and the waypoints, see the repository for an example.
| outputformat | Output format. Consult the [mapnik documentation](http://mapnik.org/docs/v2.2.0/api/python/mapnik._mapnik-module.html#render_to_file) for possible values.
| dpi | Amount of detail to render in dots per inch. This value is unrelated to the setting on your printer, a higher value will simply result in smaller icons, thinner roads and unreadable text.
| scalefactor | The scale factor to compensate for a higher dpi value.
| fontdirs | Optional. Can contain one or more fontdir subtags with additional font directories to be used by mapnik.

## Prerequisites

To run this script you should have a working installation of [python 3](https://www.python.org/) and [mapnik](http://mapnik.org/). Make sure you also have [python-mapnik](https://github.com/mapnik/python-mapnik/) installed.

## Configuration of the mapnik stylesheet

The mapnik stylesheet should be configured before use and you need to set up a datasource as well. Consult CONFIG.md in this repository for a detailed explanation on how to achieve this.

## Roadmap

* Copyright text on the bottom of each page, as requested by [OpenStreetMap](http://www.openstreetmap.org/copyright).
* A new stylesheet allowing the map to be printed in black and white. There is nothing wrong with the OpenStreetMap stylesheet, but when printed the difference between for example water and forest is not clear. Text is not always readable and some information is irrelevant for hiking or cycling.
* Hillshading. There is an experimental script to import elevation data as hillshading in the database but it is probably better to work with a geotiff file. The subject needs more studying first.

