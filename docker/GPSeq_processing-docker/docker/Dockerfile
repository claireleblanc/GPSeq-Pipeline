# import ubuntu 20 image
FROM ubuntu:20.04
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
ENV PATH "$PATH:/app/bin"
ENV ZIP=bowtie2-2.4.1-linux-x86_64.zip
ENV URL=https://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.4.1
ENV FOLDER=bowtie2-2.4.1-linux-x86_64
ENV DST=/app/bin
ENV ULOCAL=/usr/local/bin

RUN mkdir -p /app
RUN mkdir -p $DST
WORKDIR /app
COPY requirements.txt .

RUN apt update \
    && apt install -y wget unzip

RUN wget $URL/$ZIP/download -O $DST/$ZIP && \
    unzip $DST/$ZIP -d $DST && \
    rm $DST/$ZIP && \
    mv $DST/$FOLDER/* $DST && \
    rmdir $DST/$FOLDER

RUN apt install -y python3.8 python3-pip curl \
    && pip3 install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 

RUN conda config --add channels defaults \
    && conda config --add channels bioconda \
    && conda config --add channels conda-forge \
    && conda install -c bioconda sambamba

RUN pip3 install -r requirements.txt

RUN apt update \
    && apt install -y --no-install-recommends fastqc \
    && rm -rf /var/lib/apt/lists/*

## following are for installing R and packages
## This was not needed before but we need it now
ENV DEBIAN_FRONTEND noninteractive

RUN apt update \
	&& apt install -y --no-install-recommends software-properties-common dirmngr ed less \
    locales vim-tiny ca-certificates \
    && add-apt-repository --enable-source --yes "ppa:marutter/rrutter4.0" \
    && add-apt-repository --enable-source --yes "ppa:c2d4u.team/c2d4u4.0+"

## Configure default locale, see https://github.com/rocker-org/rocker/issues/19
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
	&& locale-gen en_US.utf8 \
	&& /usr/sbin/update-locale LANG=en_US.UTF-8

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8


## Otherwise timedatectl will get called which leads to 'no systemd' inside Docker
ENV TZ UTC

# Now install R and littler, and create a link for littler in /usr/local/bin
# Default CRAN repo is now set by R itself, and littler knows about it too
# r-cran-docopt is not currently in c2d4u so we install from source
RUN apt update \
    && apt install -y --no-install-recommends littler r-base r-base-dev r-recommended \
  	&& ln -s /usr/lib/R/site-library/littler/examples/install.r /usr/local/bin/install.r \
 	&& ln -s /usr/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
 	&& ln -s /usr/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
 	&& ln -s /usr/lib/R/site-library/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r \
 	&& install.r docopt \
 	&& rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
 	&& rm -rf /var/lib/apt/lists/*

RUN R -e "install.packages(c('argparser', 'cowplot', 'data.table', 'ggplot2', 'pbapply','R.utils'))"
RUN R -e "install.packages(c('logging', 'BiocManager', 'outliers'))"

RUN apt update \
    && apt install -y libcurl4-openssl-dev libxml2-dev\
    && rm -rf /var/lib/apt/lists/*

RUN R -e "install.packages(c('RCurl'))"
RUN R -e "BiocManager::install('rtracklayer')"
WORKDIR /app
RUN wget https://github.com/ggirelli/GPSeq-RadiCal/archive/refs/tags/v0.0.9.zip \
    && unzip v0.0.9.zip \
    && rm v0.0.9.zip \
    && cd GPSeq-RadiCal-0.0.9

RUN wget https://github.com/bedops/bedops/releases/download/v2.4.40/bedops_linux_x86_64-v2.4.40.tar.bz2 \
    && tar jxvf bedops_linux_x86_64-v2.4.40.tar.bz2

RUN apt-get update -y \
    && apt-get install -y samtools

CMD [ "/bin/bash" ]
