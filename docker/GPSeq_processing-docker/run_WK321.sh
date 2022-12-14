#!/bin/bash

run_id="WK321"

localinput="/mnt/Storage2/${run_id}/"
localref="/home/wenjing/GPSeq_processing/ref/"
config_centraligy="./B321_centrality_GPSeq_meta.tsv"


docker run -it --rm -d --name gpseq_container -v $localinput:/home/${run_id} -v $localref:/home/ref gpseq:latest 

docker cp ./main_human.sh gpseq_container:/home
docker cp ./scripts gpseq_container:/home

input="${run_id}.config"
while IFS= read -r line
do
    sample=$(echo "$line" | cut -f 1)
    barcode=$(echo "$line" | cut -f 2)
    echo ${sample}
    echo ${barcode}
    docker exec gpseq_container bash /home/main_human.sh ${run_id} ${sample} 20 ${barcode}
done < "$input"

docker exec gpseq_container /home/scripts/mk_summary_table.py /home/${run_id}


## gpseq score calculation

docker cp ${config_centraligy} gpseq_container:/home

outpath="/home/${run_id}/radical-out-gpseq"
basename_config_centraligy=$(basename $config_centraligy)
metadata="/home/${basename_config_centraligy}"
mask_path="/home/ref/2018-07-09.GG.manual_mask.centro_telo.for_centrality_tracks.tsv"

ref_genome="Homo_sapiens.GRCh37"
version="75"
ref_dir="/home/ref"
cut_enzyme="MboI"
cutsite_path="${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.${cut_enzyme}_sites.bed.gz"

docker exec gpseq_container rm -r ${outpath}
docker exec gpseq_container /app/GPSeq-RadiCal-0.0.9/gpseq-radical.R "$metadata" "$outpath" \
       --chromosome-wide -b 1e6:1e5,5e5:5e4,1e5:1e4,5e4:5e4,25e3:25e3 \
       --normalize-by lib \
       --ref-genome hg19 --chrom-tag 22:X,Y \
       --threads 6 --export-level 1 \
       --site-domain universe --site-bed "$cutsite_path" \
       --mask-bed "$mask_path" \
       -c ${ref_dir}/hg19_chrom_size.bed
