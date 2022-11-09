# GPSeq-Pipeline

## Overview

There are multiple ways to run the GPSeq pipeline. Specifically, you can either use a docker container (which contains all the necessary packages), or run the commands manually (which requires installation of all the correct packages. 

[Docker instructions](./docker/)

[Manual instructions](./manual) 

Tutorial modified from https://github.com/GG-space/gpseq-preprocessing-tutorial


Used this to install docker: https://docs.docker.com/engine/install/ubuntu/

To add user to docker group: sudo usermod -aG docker $USER

if this doesn't work right away, try logging out and logging back in

To see users in docker group: grep /etc/group -e "docker"

To list docker images: docker image ls

Building the docker image (docker build -t $image -f ./Dockerfile .) took roughly 15 minutes. 

If build fails with error "Connection reset by peer" or "error: retrieving gpg key timed out," it could be that your machine is running too many processes at once. Try running it again after some time. 
- can also try running each command in thee build.sh file individually to see which command is causing issues. 

If buiild was sucessfull, docker image ls should show three new entries: 

REPOSITORY       TAG       IMAGE ID       CREATED         SIZE
bicrolab/gpseq   1.0       537f5c282500   3 minutes ago   2.97GB
bicrolab/gpseq   latest    537f5c282500   3 minutes ago   2.97GB
gpseq            latest    537f5c282500   3 minutes ago   2.97GB

Make reference folder: 
cd $HOME/GPSeq_processing
mkdir -p reference
cd reference
wget https://hgdownload.cse.ucsc.edu/goldenpath/hg19/bigZips/hg19.chrom.sizes
cp /media/bs2-pro/GG-BACKUP/projects/gpseq-human-neuronal-differentiation/data/centrality-radical/2018-07-09.GG.manual_mask.centro_telo.for_centrality_tracks.tsv .
-> maybe just have these included in the repository 
-> one for hg19 and one for mm10
-> also include masks

cd ..
nano BICRO323.config 
For each line have sampleID (libraryID) tab barcode

when changing run file and setting path to input: in the local input, need fastq folder with all fastq files

change enzyme
