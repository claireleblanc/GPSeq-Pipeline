# Setup

Before proceeding, please consult the requirements page [here](../Requirements.md).

<!-- MarkdownTOC -->

- [Input](#input)
- [Reference genome](#reference-genome)
- [Restriction site list](#restriction-site-list)
- [Download other scripts](#download-other-scripts)
- [Parameters](#parameters)
- [Tutorial](#tutorial)

<!-- /MarkdownTOC -->

## Input

Create a folder where to perform the analysis:

```bash
mkdir $HOME/gpseq-tutorial
cd $HOME/gpseq-tutorial
```

Check if `sratools` are available by running:

```bash
fasterq-dump -h
```

If the output is `command not found: fastq-dump`, install them (only for the current tutorial) by running:

```
mkdir -p $HOME/gpseq-tutorial/tools/sra-tools/
cd $HOME/gpseq-tutorial/tools/sra-tools/
curl https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.9.6/sratoolkit.2.9.6-ubuntu64.tar.gz -o sratoolkit.2.9.6-ubuntu64.tar.gz
tar -xvzf sratoolkit.2.9.6-ubuntu64.tar.gz
export PATH=$HOME/gpseq-tutorial/tools/sra-tools/sratoolkit.2.9.6-ubuntu64/bin:$PATH
fasterq-dump -h # check installation
```

Then, download the input data with the following (*NOTE. As the file is ~15 GB it might take a few minutes to complete the download.*):

```bash
cd $HOME/gpseq-tutorial
mkdir fastq
fasterq-dump SRR9974287 -O fastq -p
mv fastq/SRR9974287.fastq fastq/TUTORIAL01_S1_LALL_R1_001.fastq
gzip fastq/TUTORIAL01_S1_LALL_R1_001.fastq
```

While the input file downloads and compresses, we recommend moving on to the next step and prepare the reference.

## Reference genome

Download the `GRCh38.r104` reference genome with the following:

```bash
mkdir reference
curl http://ftp.ensembl.org/pub/release-104/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz --output reference/Homo_sapiens.GRCh38.dna.primary_assembly.noChr.fa.gz
zcat reference/Homo_sapiens.GRCh38.dna.primary_assembly.noChr.fa.gz | sed 's/>/>chr/' | gzip > reference/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
rm reference/Homo_sapiens.GRCh38.dna.primary_assembly.noChr.fa.gz
```

Then, build the bowtie2 index with (*NOTE. The number of threads should be adapted to your machine.*):

```bash
cd $HOME/gpseq-tutorial/reference
bowtie2-build Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz Homo_sapiens.GRCh38.dna.primary_assembly --threads 10 --verbose
cd $HOME/gpseq-tutorial
```

While the aligner index is building, we recommend moving already to the next step and generate the list of restriction sites.

## Restriction site list

Generate a BED file with the location of restriction sites by running the following:

```bash
fbarber find_seq reference/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz AAGCTT --case-insensitive --global-name --output reference/Homo_sapiens.GRCh38.dna.primary_assembly.HindIII_sites.bed.gz --log-file reference/Homo_sapiens.GRCh38.dna.primary_assembly.HindIII_sites.log

# Check the output file
zcat reference/Homo_sapiens.GRCh38.dna.primary_assembly.HindIII_sites.bed.gz | less
```

**NOTE**. If using Python 3.6 or 3.7, version 0.1.3 will be installed instead, which has a known issue with running `fbarber find_seq` with the `--case-insensitive` option. We recommend upgrading to Python3.8+ or skipping the `--case-insensitive` option (in the scope of this tutorial).

## Download other scripts

```bash
git clone https://github.com/GG-space/gpseq-preprocessing-example.git
cp -rv gpseq-preprocessing-example/scripts .
rm -rf gpseq-preprocessing-example
chmod +x scripts/*
```

## Parameters

Execute the following to set the parameter values.

```bash
# Parameters
input="$HOME/gpseq-tutorial/fastq/TUTORIAL01_S1_LALL_R1_001.fastq.gz"
libid="TUTORIAL01"
bowtie2_ref="$HOME/gpseq-tutorial/reference/Homo_sapiens.GRCh38.dna.primary_assembly"
cutsite_path="$HOME/gpseq-tutorial/reference/Homo_sapiens.GRCh38.dna.primary_assembly.HindIII_sites.bed.gz"
threads=10
```

Five parameters are required to run the pipeline:

* `input` is the path to the input fastq file (generally gzipped and merge by all lanes).
* `libid` is the library ID (for Illumina filenames, the first bit of the fastq name).
* `bowtie2_ref` is the path to the bowtie2 index.
* `cutsite_ref` is the path to a (gzipped) BED file with the location of known restriction sites.
* `threads` is the number of threads used for parallelization.

## Tutorial

Now you can proceed with the [tutorial](../PreProcessing.md).
