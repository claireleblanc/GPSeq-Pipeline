#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from glob import glob
import logging
import os
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import regex as re  # type: ignore
from rich.logging import RichHandler  # type: ignore
import sys

version = "0.0.1"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

parser = argparse.ArgumentParser(
    description="Assemble summary table after running rereprpr.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument("root", type=str, help="Path to root folder.")

parser.add_argument(
    "--version",
    action="version",
    version=f"{sys.argv[0]} v{version}",
)

args = parser.parse_args()

logging.info(f"Looking into '{args.root}'...")

patterns = {}
patterns[
    "quality_filters"
] = ".* ([0-9]+)/([0-9]+) \(([0-9\.%]+)\).*flag_extract\.py:246"
patterns[
    "prefix"
] = ".* ([0-9]+)/([0-9]+) \(([0-9\.%]+)\).*flag_regex\.py:156"
patterns["mapping_unmapped"] = ".* ([0-9]+) \([0-9\.]+%\) aligned 0 times"
patterns["mapping_2nd_aln"] = ".* ([0-9]+) \([0-9\.]+%\) aligned >1 times"
patterns["fromCS"] = ".* Output: ([0-9]+) \(([0-9\.]+%)\) UMI"
patterns["dedup"] = "([0-9]+) UMIs left after deduplication."

dataframe = pd.DataFrame()

fastq_dir_path = os.path.join(args.root, "fastq")
assert os.path.isdir(fastq_dir_path)

fastq_list = glob(os.path.join(fastq_dir_path, "*"))
library_id_list = [os.path.basename(x).split(".")[0] for x in fastq_list]
dataframe["prep_run"] = np.repeat(os.path.basename(args.root), len(library_id_list))

logging.info(f"Found {len(library_id_list)} library IDs: {library_id_list}")
dataframe["library_id"] = library_id_list

logging.info("Reading quality filter results...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "fastq_hq", f"{library_id}.log")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        matched = False
        for line in LH:
            match = re.match(patterns["quality_filters"], line)
            if match is None:
                continue
            matched = True
            dataframe.loc[library_iid, "input"] = int(match.groups()[1])
            dataframe.loc[library_iid, "umi_hq"] = int(match.groups()[0])
            dataframe.loc[library_iid, "umi_hq%"] = match.groups()[2]
        assert matched, f"missing quality filters output line [{library_id}]"

logging.info("Reading prefix results...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "fastq_prefix", f"{library_id}.log")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        matched = False
        for line in LH:
            match = re.match(patterns["prefix"], line)
            if match is None:
                continue
            matched = True
            dataframe.loc[library_iid, "prefix"] = int(match.groups()[0])
            dataframe.loc[library_iid, "prefix%"] = match.groups()[2]
        assert matched, f"missing prefix output line [{library_id}]"

logging.info("Reading unmapped counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "mapping", f"{library_id}.mapping.log")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        matched = False
        for line in LH:
            match = re.match(patterns["mapping_unmapped"], line)
            if match is None:
                continue
            matched = True
            dataframe.loc[library_iid, "unmapped"] = int(match.groups()[0])
        assert matched, f"missing unmapped count line [{library_id}]"

logging.info("Reading 2nd alignment counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "mapping", f"{library_id}.mapping.log")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        matched = False
        for line in LH:
            match = re.match(patterns["mapping_2nd_aln"], line)
            if match is None:
                continue
            matched = True
            dataframe.loc[library_iid, "2nd_aln"] = int(match.groups()[0])
        assert matched, f"missing 2nd alignment count line [{library_id}]"

logging.info("Reading chrM alignment counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "mapping", f"{library_id}.chrM.txt")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        dataframe.loc[library_iid, "chrM"] = int(LH.readlines()[0].strip())

logging.info("Reading low quality alignment counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "mapping", f"{library_id}.lq_count.txt")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        dataframe.loc[library_iid, "low_mapq"] = int(LH.readlines()[0].strip())

logging.info("Reading filtered alignment counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "mapping", f"{library_id}.clean_count.txt")
    assert os.path.isfile(log_path)
    with open(log_path) as LH:
        dataframe.loc[library_iid, "mapped"] = int(LH.readlines()[0].strip())
        mapped_perc = (
            dataframe.loc[library_iid, "mapped"]
            / dataframe.loc[library_iid, "prefix"]
            * 100
        )
        dataframe.loc[library_iid, "mapped%"] = f"{mapped_perc:.2f}%"

logging.info("Reading non orphan counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(args.root, "atcs", f"{library_id}.clean.umis_at_cs.txt.log")
    assert os.path.isfile(log_path), f"file not found: '{log_path}'"
    with open(log_path) as LH:
        matched = False
        for line in LH:
            match = re.match(patterns["fromCS"], line)
            if match is None:
                continue
            matched = True
            dataframe.loc[library_iid, "fromCS"] = int(match.groups()[0])
            dataframe.loc[library_iid, "fromCS%"] = match.groups()[1]
        assert matched, f"missing non orphan count line [{library_id}]"

logging.info("Reading deduplicated counts...")
for library_iid in range(len(library_id_list)):
    library_id = library_id_list[library_iid]
    log_path = os.path.join(
        args.root, "dedup", f"{library_id}.clean.umis_at_cs.txt.gz.umi_prep_notes.txt"
    )
    assert os.path.isfile(log_path), f"file not found: '{log_path}'"
    with open(log_path) as LH:
        matched = False
        for line in LH:
            match = re.match(patterns["dedup"], line)
            if match is None:
                continue
            matched = True
            dataframe.loc[library_iid, "uniq"] = int(match.groups()[0])
        assert matched, f"missing deduplication count line [{library_id}]"
        deduped_perc = (
            dataframe.loc[library_iid, "uniq"]
            / dataframe.loc[library_iid, "fromCS"]
            * 100
        )
        dataframe.loc[library_iid, "uniq%"] = f"{deduped_perc:.2f}%"
        output_perc = (
            dataframe.loc[library_iid, "uniq"]
            / dataframe.loc[library_iid, "input"]
            * 100
        )
        dataframe.loc[library_iid, "out%"] = f"{output_perc:.2f}%"


dataframe.sort_values("library_id").to_csv(
    os.path.join(args.root, "summary_table.tsv"), sep="\t", index=False
)
