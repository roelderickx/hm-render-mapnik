# Render paper maps from Openstreetmap data using mapnik.

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
| `-f, --format` | Output format. Consult the mapnik documentation for possible values, default png
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

## Prerequisites

To run this script you should have a working installation of [python 3](https://www.python.org/) and [mapnik](http://mapnik.org/). Make sure you also have [python-mapnik](https://github.com/mapnik/python-mapnik/) installed.

## Configuration of the mapnik stylesheet

The mapnik stylesheet should be configured before use and you need to set up a datasource as well. Consult the HTML documentation in this repository for a detailed explanation on how to achieve this.

## TODO

Since most of the time the same configuration and tile source will be used, the program should be able to read these parameters from a config file.

