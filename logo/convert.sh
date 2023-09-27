#!/bin/sh

FOLDERS=(english dutch)
for FOLDER in "${FOLDERS[@]}"
do
    mkdir -p $FOLDER/bw
    mkdir -p $FOLDER/rgb
    cd $FOLDER/eps
    for f in *.eps
    do
        filename="${f%.*}"
        
        gs -o ../bw/$filename.pdf -sDEVICE=pdfwrite \
            -c "/setrgbcolor {pop pop pop 0 setgray} bind def" \
            -dEPSCrop -f $filename.eps
        gs -o ../rgb/$filename.pdf -sDEVICE=pdfwrite \
            -dEPSCrop -f $filename.eps
    done
    cd ../..
done