#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from collections import defaultdict
import gzip
import logging
from rich.logging import RichHandler  # type: ignore
import sys
from tqdm import tqdm  # type: ignore
from typing import DefaultDict, IO, List, Tuple

version = "0.0.2"


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

parser = argparse.ArgumentParser(
    description="""
Group UMIs starting from chrom|pos|seq|qual UMI files, one per strand.
Shifts reads from positive strand based on cutsite length.
Input files are expected to be sorted, this is currently not checked.
""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument("plus", type=str, help="Path to plus strand file.")
parser.add_argument("revs", type=str, help="Path to rev strand file.")
parser.add_argument("output", type=str, help="Path to output file.")

parser.add_argument("--len", type=int, help="Cutsite length. Default: 0", default=0)
parser.add_argument(
    "--sep", type=str, help="Column separator. Default: TAB", default="\t"
)

parser.add_argument(
    "--compress-level",
    type=int,
    default=0,
    help="""GZip compression level. Default: 0 (i.e., no compression).""",
)

parser.add_argument(
    "--version",
    action="version",
    version=f"{sys.argv[0]} v{version}",
)

args = parser.parse_args()


def get_ih(path: str) -> IO:
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    else:
        return open(path, "r")


def get_oh(path: str, compress_level: int = 0) -> IO:
    if 0 == compress_level:
        return open(path, "w+")
    else:
        if not path.endswith(".gz"):
            path += ".gz"
        return gzip.open(path, "wt+", compress_level)


UMIDict = DefaultDict[str, DefaultDict[int, Tuple[List[str], List[str]]]]


def populate_dict(
    umi_dict: UMIDict, path: str, cs_len: int = 0, sep: str = "\t"
) -> UMIDict:
    with get_ih(path) as IH:
        for line in tqdm(IH, "Record"):
            chrom, pos, seq, qual = line.strip().split("\t")
            pos = int(pos) - cs_len
            umi_dict[chrom][pos][0].append(seq)
            umi_dict[chrom][pos][1].append(qual)
    return umi_dict


umi_dict: UMIDict = defaultdict(lambda: defaultdict(lambda: ([], [])))

logging.info(f"Processing plus strand ('{args.plus}'), shifting of {args.len} bases")
umi_dict = populate_dict(umi_dict, args.plus, args.len, sep=args.sep)

logging.info(f"Processing rev strand ('{args.revs}')")
umi_dict = populate_dict(umi_dict, args.revs, sep=args.sep)

with get_oh(args.output, args.compress_level) as OH:
    logging.info(f"Writing output to: {OH.name}")
    if args.compress_level > 0:
        logging.info(f"Compression level: {args.compress_level}")
    for chrom, pos_dict in tqdm(umi_dict.items(), desc="Chromosome"):
        for pos, (seq, qual) in tqdm(pos_dict.items(), desc="Position"):
            OH.write(
                args.sep.join([chrom, str(pos), " ".join(seq), " ".join(qual)]) + "\n"
            )
