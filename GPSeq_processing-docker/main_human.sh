#!/bin/bash

run_id=$1
libid=$2
input="/home/${run_id}/fastq/${libid}.fastq.gz"
cut_enzyme="MboI"
cut_seq="GATC"

ref_genome="Homo_sapiens.GRCh37"
version="75"
ref_dir="/home/ref"
bowtie2_ref="${ref_dir}/${ref_genome}.${version}.dna.primary_assembly"
cutsite_path="${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.${cut_enzyme}_sites.bed.gz"

output="/home/${run_id}"

threads=$3
barcode=$4

# Set up references
mkdir -p ${ref_dir}

if [[ ! -s "${bowtie2_ref}.rev.2.bt2" ]]
then
    wget -O ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.noChr.fa.gz http://ftp.ensembl.org/pub/release-${version}/fasta/homo_sapiens/dna/${ref_genome}.${version}.dna.primary_assembly.fa.gz
    zcat ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.noChr.fa.gz | sed 's/>/>chr/' | cut -d" " -f 1 | gzip > ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.fa.gz
    rm ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.noChr.fa.gz
    /app/bin/bowtie2-build ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.fa.gz ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly --threads 4 --verbose
fi

if [[ ! -s "${cutsite_path}" ]]
then
    fbarber find_seq ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.fa.gz ${cut_seq} --case-insensitive --global-name --output ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.${cut_enzyme}_sites.bed.gz --log-file ${ref_dir}/${ref_genome}.${version}.dna.primary_assembly.${cut_enzyme}_sites.log
fi

cd $output

# FASTQ quality control
mkdir -p fastqc
fastqc $input -o fastqc --nogroup

# Extract flags and filter by UMI quality
mkdir -p fastq_hq
fbarber flag extract \
   "$input" fastq_hq/$libid.hq.fastq.gz \
   --filter-qual-output fastq_hq/$libid.lq.fastq.gz \
   --unmatched-output fastq_hq/$libid.unmatched.fastq.gz \
   --log-file fastq_hq/$libid.log \
   --pattern 'umi8bc8cs4' --simple-pattern \
   --flagstats bc cs --filter-qual-flags umi,30,.2 \
   --threads $threads --chunk-size 200000

# Filter by prefix
mkdir -p fastq_prefix
fbarber flag regex \
    fastq_hq/$libid.hq.fastq.gz fastq_prefix/$libid.fastq.gz \
    --unmatched-output fastq_prefix/$libid.unmatched.fastq.gz \
    --log-file fastq_prefix/$libid.log \
    --pattern "bc,^(?<bc>"${barcode}"){s<2}$" "cs,^(?<cs>GATC){s<2}$" \
    --threads $threads --chunk-size 200000

# Align
mkdir -p mapping
bowtie2 \
    -x "$bowtie2_ref" fastq_prefix/$libid.fastq.gz \
    --very-sensitive -L 20 --score-min L,-0.6,-0.2 --end-to-end --reorder -p $threads \
    -S mapping/$libid.sam &> mapping/$libid.mapping.log

# Filter alignment
sambamba view -q -S mapping/$libid.sam -f bam -t $threads > mapping/$libid.bam
rm -i mapping/$libid.sam

sambamba view -q mapping/$libid.bam -f bam \
    -F "mapping_quality<30" -c -t $threads \
    > mapping/$libid.lq_count.txt
sambamba view -q mapping/$libid.bam -f bam \
    -F "ref_name=='chrM'" -c -t $threads \
    > mapping/$libid.chrM.txt
sambamba view -q mapping/$libid.bam -f bam -t $threads \
    -F "mapping_quality>=30 and not secondary_alignment and not unmapped and not chimeric and ref_name!='chrM'" \
    > mapping/$libid.clean.bam
sambamba view -q mapping/$libid.clean.bam -f bam -c -t $threads > mapping/$libid.clean_count.txt


# Correct aligned position
mkdir -p atcs
sambamba view -q -t $threads -h -f bam -F "reverse_strand" \
    mapping/$libid.clean.bam -o atcs/$libid.clean.revs.bam
sambamba view -q -t $threads atcs/$libid.clean.revs.bam | \
    convert2bed --input=sam --keep-header - > atcs/$libid.clean.revs.bed
cut -f 1-4 atcs/$libid.clean.revs.bed | tr "~" $'\t' | cut -f 1,3,7,16 | gzip \
    > atcs/$libid.clean.revs.umi.txt.gz
rm atcs/$libid.clean.revs.bam atcs/$libid.clean.revs.bed

sambamba view -q -t $threads -h -f bam -F "not reverse_strand" \
    mapping/$libid.clean.bam -o atcs/$libid.clean.plus.bam
sambamba view -q -t $threads atcs/$libid.clean.plus.bam | \
    convert2bed --input=sam --keep-header - > atcs/$libid.clean.plus.bed
cut -f 1-4 atcs/$libid.clean.plus.bed | tr "~" $'\t' | cut -f 1,2,7,16 | gzip \
    > atcs/$libid.clean.plus.umi.txt.gz
rm atcs/$libid.clean.plus.bam atcs/$libid.clean.plus.bed

# Group UMIs
/home/scripts/group_umis.py \
    atcs/$libid.clean.plus.umi.txt.gz \
    atcs/$libid.clean.revs.umi.txt.gz \
    atcs/$libid.clean.umis.txt.gz \
    --compress-level 6 --len 4
rm atcs/$libid.clean.plus.umi.txt.gz atcs/$libid.clean.revs.umi.txt.gz

# Assign UMIs to cutsites
/home/scripts/umis2cutsite.py \
    atcs/$libid.clean.umis.txt.gz $cutsite_path \
    atcs/$libid.clean.umis_at_cs.txt.gz --compress --threads $threads
rm atcs/$libid.clean.umis.txt.gz

# Deduplicate
mkdir -p dedup
Rscript /home/scripts/umi_dedupl.R \
    atcs/$libid.clean.umis_at_cs.txt.gz \
    dedup/$libid.clean.umis_dedupd.txt.gz \
    -c $threads -r 10000

# Generate final bed
mkdir -p bed
zcat dedup/$libid.clean.umis_dedupd.txt.gz | \
    awk 'BEGIN{FS=OFS="\t"}{print $1 FS $2 FS $2 FS "pos_"NR FS $4}' | \
    gzip > bed/$libid.bed.gz


