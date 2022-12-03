# Docker

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

Create the config file in `~/GPSeq-Pipeline/docker/GPSeq_processing-main`

It should be named `RunID.config` (replacing RunID with a unique identifier for this experiment. The file should contain two tab-separated columns, the first for the sequencing libraryID and the next for the barcode corresponding to that ID. There should be a row for each condition (timepoint): 
|  |  |
| ----------- | ----------- |
| cond1 library id | barcode |
| cond2 library id | barcode |
| cond3 library id | barcode |

The example file **example.config** can be used as a template to create this file. 

Create the config_centrality tsv file. It should have a line with the following header (where each entry is separated by a tab), followed by a line for each condition:

| exid  |  cond  |  libid  | fpath |
| ----------- | ----------- | ----------- | ----------- |

The example file **example.tsv** can be used as a template to create this file.

## Update the run file

Create a copy of the **run_example_human.sh** file with `cp run_example_human.sh run_RunID.sh` where runID is the unique identifier for this experiment. 

Open this new file in a text editor (such as nano) and update the lines with comments. Specifically, update:
- The run_id, which should match the run id used when naming the config file
- The path to the input fastq files. The path provided should be the path to a folder containing a `fastq` folder which contains the files of interest. Inside this `fastq` folder, the fastq files must be named as `libraryID.fastq`
- The name of the config_centrality file
- The name of the restriction enzyme used in the GPSeq experiment
- Optional: The parameters of the GPSeq score calculation script. 

## Run the pipeline

Depending on the input size, this could take days to run. We recommmend running in the background (we recommend tmux)

Go into the correct folder:
`cd /home/GPSeq-Pipeline/docker/GPSeq_processing-main/`

Run the script: `bash run_RunID.sh` wherer runID is the unique identifier for this experiment.

## If container finished with error:

run `docker ps` to see id of container you created

You will see something like: 
| CONTAINER ID |  IMAGE    |      COMMAND   |    CREATED   |   STATUS  |    PORTS  |   NAMES |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| 2e1601de5977  | gpseq:latest |  "/bin/bash" |   5 days ago  | Up 5 days   |   |       gpseq_container |

stop the conntainer with `docker stop containerID` ex. `docker stop 2e1601de5977`
