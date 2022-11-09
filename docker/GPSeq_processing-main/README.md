## To build the docker container, go into docker folder and run
bash build.sh

## Run the built image. Simple version
1. set localdir for volume mount in run.sh. the default mounting location is /app/
2. run.sh# GPSeq_processing

## prepare the projXXX folder
1. search the fastq files in /media/bs2-seq/BICROXXX/fastq
2. copy the fastq files to the input folder: cp /media/bs2-seq/BICROXXX/fastq/filename.fastq /home/username/projXXX/fastq

## prepare the reference folder
1. download the size of chromosomes of hg19 by "wget https://hgdownload.cse.ucsc.edu/goldenpath/hg19/bigZips/hg19.chrom.sizes"
2. reform the file to bed: cat hg19.chrom.sizes | grep -v "_" | grep -v "chrM" | awk -F"\t" '{print$1"\t""0""\t"$2}' > hg19_chrom_size.bed
3. Copy a mask file from GG for the GPSeq score calculation. Currently we use "2018-07-09.GG.manual_mask.centro_telo.for_centrality_tracks.tsv" for human and "mm10_low_mappability.UMAP_S50.bins_1e+06_1e+05.tsv" for mouse. 

## prepare the config files
1. we need a config file (projXXX.config) for GPSeq preprocessing.
Example with tab delimited: column 1 sample ID, column 2 barcode.  
SW1	CATCACGC
SW6	GTCGTATC

2. another config file (projXXX_centrality_GPSeq_meta.tsv) for GPSeq score calcuation.
Example with tab delimited:
exid	cond	libid	fpath
projXXX	5s	SW1	/home/projXXX/bed/SW1.bed.gz
projXXX	5min	SW6	/home/projXXX/bed/SW6.bed.gz


## prepare the run script (run_projXXX.sh)
1. copy a tempalte run_projXXX.sh
2. change the proj ID.
3. provide the correct path to the projXXX folder.
4. procide the correct path to the reference folder.
5. make sure the names of config files are in correct format. 


## run the script of gpseq processing
bash run_projXXX.sh
