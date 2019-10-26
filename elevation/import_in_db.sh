#!/bin/bash

FILE_EXT='hgt'
GIS_DB=gis
GIS_USER=gis
TABLE_NAME=elevation
CREATE_TABLE=1 # modify to 0 if your table already exists and you just want to add data

function cleanup_temp_files() {
    compgen -G *.aux.xml > /dev/null && rm *.aux.xml
    compgen -G *.shp > /dev/null && rm *.shp
    compgen -G *.shx > /dev/null && rm *.shx
    compgen -G *.dbf > /dev/null && rm *.dbf
    compgen -G *.index > /dev/null && rm *.index
    compgen -G *.prj > /dev/null && rm *.prj
    compgen -G *.sql > /dev/null && rm *.sql
}

# parameters: file and file_ext
function unpack_if_needed() {
    if [ $2 == "zip" ]; then
        unzip "$1"
        FILE=`zipinfo -1 "$1"`
        BASEFILE=${FILE%%.`echo $FILE | cut -d '.' -f2- -`}
    else
        FILE="$1"
        BASEFILE=${FILE%%.$2}
    fi
}

# parameters file and file_ext
function cleanup_unpacked() {
    if [ $2 == "zip" ]; then
        rm "$1"
    fi
}

# parameters file and basefile
function create_insert_statements() {
    DEM_MIN=$(gdalinfo -stats "$1" | grep 'STATISTICS_MINIMUM' | awk -F '=' '{print $2}')
    DEM_MAX=$(gdalinfo -stats "$1" | grep 'STATISTICS_MAXIMUM' | awk -F '=' '{print $2}')

    # if we have less than 700 meter of altitude difference we can import the file at once
    if [ $(($DEM_MAX-$DEM_MIN)) -le 700 ]; then
        gdal_contour -i 10 -snodata 32767 -a height "$1" "$2"c10.shp
        shapeindex "$2"c10.shp
        
        if [ $CREATE_TABLE -eq 1 ]; then
            shp2pgsql -c -D -s 4326 -i "$2"c10.shp $TABLE_NAME >> elevation.sql
            CREATE_TABLE=2
        else
            shp2pgsql -a -D -s 4326 -i "$2"c10.shp $TABLE_NAME >> elevation.sql
        fi
    # otherwise the intermediate shape file might be larger than 4 GB, gdal_contour doesn't like this
    else
        # for loop with interval is not supported as of OS/X 10.8.2
        # calculate first multiplicity of 10 above $DEM_MIN
        mod=$(($DEM_MIN % 10))
        if [ $mod -le 0 ]; then
	        i=$(($DEM_MIN - $mod))
        else
	        i=$(($DEM_MIN + 10 - $mod))
        fi
        while [ $i -le $DEM_MAX ];
        do
            gdal_contour -fl $i $(($i+10)) $(($i+20)) $(($i+30)) $(($i+40)) $(($i+50)) $(($i+60)) $(($i+70)) $(($i+80)) $(($i+90)) -snodata 32767 -a height "$1" "$2"c$i.shp
            shapeindex "$2"c$i.shp

            if [ $CREATE_TABLE -eq 1 ]; then
                shp2pgsql -c -D -s 4326 -i "$2"c$i.shp $TABLE_NAME >> elevation.sql
                CREATE_TABLE=2
            else
                shp2pgsql -a -D -s 4326 -i "$2"c$i.shp $TABLE_NAME >> elevation.sql
            fi
            
            i=$(($i+100))
        done
    fi
}

function insert_data() {
    # disable analyze after each insert to improve performance
    sed -i -e 's/ANALYZE/--ANALYZE/g' elevation.sql
    # insert data
    psql -d $GIS_DB -U $GIS_USER -f elevation.sql
}

function analyze_create_index() {
    # analyze table
    echo "ANALYZE \"$TABLE_NAME\"" | psql -d $GIS_DB -U $GIS_USER
    # create the index we omitted in the beginning (shp2pgsql -c in stead of shp2pgsql -c -I)
    if [ $CREATE_TABLE -eq 2 ]; then
        echo "CREATE INDEX ON \"$TABLE_NAME\" USING GIST (\"geom\");" | psql -d $GIS_DB -U $GIS_USER
    fi
}

cleanup_temp_files

for X in *.$FILE_EXT
do
    [ -e "$X" ] || continue
    
    unpack_if_needed $X $FILE_EXT
    
    create_insert_statements $FILE $BASEFILE
    
    insert_data
    
    cleanup_unpacked $FILE $FILE_EXT
    cleanup_temp_files
done

analyze_create_index

