# Tutorial

Before proceeding, please first consult the requirements page [here](./Requirements.md).

<!-- MarkdownTOC -->

- [0. Create basic folders](#0-create-basic-folders)
- [1. Download input](#1-download-input)
- [2. Prepare metadata table](#2-prepare-metadata-table)
- [3. Run GPSeq-RadiCal](#3-run-gpseq-radical)
- [4. Inspect output](#4-inspect-output)

<!-- /MarkdownTOC -->

## 0. Create basic folders

```bash
cd $HOME/GPSeq-RadiCal-0.0.6
mkdir tutorial
cd tutorial
mkdir input
```

## 1. Download input

These will be the files generated in the pre-processing steps. For the tutorial, you can download the following example pre-processed input files: 
```bash
cd input
curl "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM4037078&format=file&file=GSM4037078%5FExp1%5F10min%2Ebed%2Egz" -o GSM4037078_Exp1_10min.bed.gz
curl "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM4037079&format=file&file=GSM4037079%5FExp1%5F15min%2Ebed%2Egz" -o GSM4037079_Exp1_15min.bed.gz
curl "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM4037080&format=file&file=GSM4037080%5FExp1%5F30min%2Ebed%2Egz" -o GSM4037080_Exp1_30min.bed.gz
curl "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM4037081&format=file&file=GSM4037081%5FExp1%5F1h%2Ebed%2Egz" -o GSM4037081_Exp1_1h.bed.gz
curl "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM4037082&format=file&file=GSM4037082%5FExp1%5F2h%2Ebed%2Egz" -o GSM4037082_Exp1_2h.bed.gz
cd ..
```

## 2. Prepare metadata table

Create the metadata table. It should have a line with the following header (where each entry is separated by a tab), followed by a line for each condition:
| exid  |  cond  |  libid  | fpath |
| ----------- | ----------- | ----------- | ----------- |

An example table has been provided for the example input data here: 

```bash
# Download metadata table
curl "https://raw.githubusercontent.com/GG-space/gpseq-score-calculation-example/main/data/metadata.tsv" -o metadata.tsv

# To visualize table
less metadata.tsv
# Press 'q' to exit
```

## 3. Run GPSeq-RadiCal

```bash
curl "https://raw.githubusercontent.com/GG-space/gpseq-score-calculation-example/main/data/hg19_chrom_size.bed" -o hg19_chrom_size.bed

../gpseq-radical.R metadata.tsv output -c hg19_chrom_size.bed
```

## 4. Inspect output

By default, `GPSeq-RadiCal` will calculate GPSeq score in two resolutions: 1 Mb bins with 100 kb step, and 100 kb bins with 10 kb step.

The output can be inspected with (press `q` to exit):

```
zcat output/TUTORIAL/rescaled.bins_1e+06_1e+05.tsv.gz | less
zcat output/TUTORIAL/rescaled.bins_1e+05_1e+04.tsv.gz | less
```
