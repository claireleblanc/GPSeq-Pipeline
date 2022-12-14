#!/bin/bash

run_id="WK303"

localinput="/mnt/Storage2/${run_id}/"
localref="/home/wenjing/GPSeq_processing/ref/"
config_centraligy="./B303_centrality_GPSeq_meta.tsv"


docker run -it --rm -d --name gpseq_container_${run_id} -v $localinput:/home/${run_id} -v $localref:/home/ref gpseq:latest 

docker cp ./main_mouse.sh gpseq_container_${run_id}:/home
docker cp ./scripts gpseq_container_${run_id}:/home

#find $localinput -name "*.fastq.gz" | awk -F"/" '{print $NF}' | sort | awk -F"." '{print$1}' > ${run_id}.config


input="${run_id}.config"
while IFS= read -r line
do
    sample=$(echo "$line" | cut -f 1)
    barcode=$(echo "$line" | cut -f 2)
    echo ${sample}
    echo ${barcode}
    docker exec gpseq_container_${run_id} bash /home/main_mouse.sh ${run_id} ${sample} 20 ${barcode}
done < "$input"

docker exec gpseq_container_${run_id} /home/scripts/mk_summary_table.py /home/${run_id}


## gpseq score calculation

docker cp ${config_centraligy} gpseq_container_${run_id}:/home

outpath="/home/${run_id}/radical-out-gpseq"
basename_config_centraligy=$(basename $config_centraligy)
metadata="/home/${basename_config_centraligy}"
mask_path="/home/ref/mm10_low_mappability.UMAP_S50.bins_1e+06_1e+05.tsv"

ref_genome="Mus_musculus.GRCm38"
ref_dir="/home/ref"
cut_enzyme="MboI"
cutsite_path="${ref_dir}/${ref_genome}.95.dna.primary_assembly.${cut_enzyme}_sites.bed.gz"

docker exec gpseq_container_${run_id} rm -r ${outpath}
docker exec gpseq_container_${run_id} /app/GPSeq-RadiCal-0.0.9/gpseq-radical.R "$metadata" "$outpath" \
       --chromosome-wide -b 1e6:1e5,5e5:5e4,1e5:1e4,5e4:5e4,25e3:25e3 \
       --normalize-by lib \
       --ref-genome mm10 --chrom-tag 19:X,Y \
       --threads 6 --export-level 1 \
       --site-domain universe --site-bed "$cutsite_path" \
       --mask-bed "$mask_path" \
       -c ${ref_dir}/mm10_chrom_size.bed
