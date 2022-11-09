# Docker

## Overview

## Installation

Instructions on how install docker [here](https://docs.docker.com/engine/install/ubuntu/)

## Setting up docker group

Once docker is installed, users who want to use docker must be added to the docker group. Do that with: 

- `sudo usermod -aG docker $USER`

After updating the groups, the specified user may have to re-log in to see the changes. 

You can check that a user has been added by running 

- `grep /etc/group -e "docker"`

## Building the docker image

The next step is to build the docker image. First, pull the repository: `git clone https://github.com/claireleblanc/GPSeq-Pipeline.git`

Go into the correct folder: `cd GPSeq-Pipeline/docker/GPSeq_processing-main/docker`

Build the docker image: `docker build -t $image -f ./Dockerfile .` This is expected to take around 15 minutes, but may varry depending on your machine. 

To check whether build was sucessful, run: `docker image ls`

If buiild was sucessfull, this should show three new entries: 

| REPOSITORY | TAG | IMAGE ID | CREATED | SIZE |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| bicrolab/gpseq | 1.0 | 537f5c282500 | 3 minutes ago | 2.97GB |
| bicrolab/gpseq | latest | 537f5c282500 | 3 minutes ago | 2.97GB |
| gpseq | latest | 537f5c28250 | 3 minutes ago | 2.97GB |

If build fails with the error `Connection reset by peer` or `error: retrieving gpg key timed out,` it could be that your machine is running too many processes at once. Try running it again later, when less things are running the machine. You can also try running each command in thee build.sh file individually to see which command is causing issues. 


## Preparing the files to run the pipeline

Reference files and mask files for hg19 and mm10 genomes are provided. Custom files can also be used and should be similarly uploaded to the reference folder. 

Create the config file. It should have two tab-separated columns, the first for the sequencing libraryID and the next for the barcode corresponding to that ID. There should be a row for each condition (timepoint): 
|  |  |
| ----------- | ----------- |
| cond1 | barcode |
| cond2 | barcode |
| cond3 | barcode |

The example file **example.config** can be used as a template to create this file. 

Create the tsv file. It should have 
| experiment ID | condition (time point) | libraryID | file path | 
| ----------- | ----------- | ----------- | ----------- |


when changing run file and setting path to input: in the local input, need fastq folder with all fastq files

change enzyme
