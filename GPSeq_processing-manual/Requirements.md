# Requirements

The tutorial requires the following software ad packages:

* Python packages
    - `fastx-barber v0.1.5`
        + **NOTE**. If using Python 3.6 or 3.7, version 0.1.3 will be installed instead, which has a known issue with running `fbarber find_seq` with the `--case-insensitive` option. We recommend upgrading to Python3.8+ or skipping the `--case-insensitive` option (in the scope of this tutorial).
    - `joblib`
    - `numpy`
    - `pandas`
    - `rich`
    - `tqdm`
* R packages
    - `argparser`
    - `cowplot`
    - `data.table`
    - `ggplot2`
    - `pbapply`
* Other software
    - `bowtie2 v2.3.5.1`
    - `fastqc v0.11.9`
    - `sambamba v0.7.1`

## Install Python packages

To verify if the packages are already installed, run:

```bash
pip3 list | grep fastx-barber
pip3 list | grep joblib
pip3 list | grep numpy
pip3 list | grep pandas
pip3 list | grep rich
pip3 list | grep tqdm
```

The output should be a list of the packages and their installed versions. if a package is missing from the output of the command above, install it with the command below (*NOTE. Include only packages that are not already installed.*):

```bash
pip3 install fastx-barber joblib numpy pandas rich tqdm
```

## Install R packages

To verify if the packages are already installed, run the following in an R shell:

```R
required_list = c("argparser", "cowplot", "data.table", "ggplot2", "pbapply")
for ( name in required_list ) {
    if ( ! name %in% rownames(installed.packages()) ) {
        cat(sprintf("Package '%s' not found.\n", name))
    }
}
```

Install missing R packages by running the following in an R shell (*NOTE. Include only packages that are not already installed.*):

```R
install.packages(c("argparser", "cowplot", "data.table", "ggplot2", "pbapply"))
```

## Install Other software

### On Ubuntu

To check if the software is already available, run:

```bash
which bowtie2
which sambamba
which fastqc
```

The command will output `softwareName not found` for any missing software. If the software is installed, a path to it will be printed instead. Install any missing programs by running the following (*NOTE. Include only software that are not already installed.*):

```bash
sudo apt update
sudo apt install bowtie2 sambamba fastqc
```
