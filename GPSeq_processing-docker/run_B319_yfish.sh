#!/bin/bash

run_id="WK319"
outdir="/mnt/Storage2/${run_id}/yfish"


mkdir -p ${outdir}

for id in $(cat B319_yfish_meta.tsv)
do
    cd ${outdir}
    echo ${id}
    #id="iKG187"
    inputdir=$(find /media/bs2-microscopy/Deconwolfed/Katta/ -name "${id}*")
    #inputdir=$(find /media/bs2-microscopy/Deconwolfed/Katta/ -name "${id}*")
    echo ${inputdir}
    dirname=$(basename ${inputdir})
    cp -r ${inputdir} ${outdir}
    cd ${outdir}/${dirname}
    radiant tiff_findoof . --threads 5 --rename --inreg 'dw_dapi.*\.tiff$'
    radiant tiff_segment . --TCZYX --threads 5 --inreg "dw_dapi.*\.tiff$" -y
    radiant measure_objects . dapi --threads 5 -y
    radiant select_nuclei --k-sigma 2 --threads 5 . dapi -y
    rm *mask.tiff
    radiant radial_population --aspect 200 130 130 --mask-suffix mask_selected --threads 5 . dapi -y
done

cd ${outdir}

radiant report .
