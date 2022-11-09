#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from joblib import delayed, Parallel  # type: ignore
import logging
import numpy as np  # type: ignore
import os
import pandas as pd  # type: ignore
from rich.console import Console  # type: ignore
from rich.logging import RichHandler  # type: ignore
import sys
from tqdm import tqdm  # type: ignore

version = "0.0.1"


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

parser = argparse.ArgumentParser(
    description="""
Maps UMIs to cutsites and discards those farther than a minimum distance.
UMI file: chrom|pos|seqs|quals; cutsites file in BED3+ format.
Input files are expected to be sorted, this is currently not checked.
""",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument("umis", type=str, help="Path to umis file.")
parser.add_argument("cutsites", type=str, help="Path to cutsites file.")
parser.add_argument("output", type=str, help="Path to output file.")

parser.add_argument(
    "--min-dist",
    type=int,
    help="Minimum distance to closest cutsite. Default: 20",
    default=20,
)
parser.add_argument(
    "--sep", type=str, help="Column separator for UMIs file. Default: TAB", default="\t"
)
parser.add_argument("--threads", type=int, default=1)

parser.add_argument(
    "--compress",
    action="store_const",
    dest="do_compress",
    const=True,
    default=False,
    help="Compress output (gzip).",
)
parser.add_argument(
    "--version",
    action="version",
    version=f"{sys.argv[0]} v{version}",
)

args = parser.parse_args()


def run_single_chrom(chrom_umi, chrom_rss):
    chrom_rss.sort_values("start", inplace=True)
    chrom_umi.sort_values("pos", inplace=True)

    chrom_rss.reset_index(drop=True, inplace=True)
    chrom_umi.reset_index(drop=True, inplace=True)

    chrom_rss["pos"] = chrom_rss["start"]

    d_rss, assigned_rss_pos = getD_for_single_chrom(chrom_umi, chrom_rss)

    chrom_umi["d_rs"] = d_rss
    chrom_umi["rs_pos"] = assigned_rss_pos

    return chrom_umi


def getD_for_single_chrom(chrom_umi, chrom_rss):
    assert 1 <= chrom_rss.shape[0]
    rssid = 1

    rss_pos = chrom_rss["pos"].values
    d_rss = []
    assigned_rss_pos = []

    for umiid in chrom_umi.index:
        umi_mid = chrom_umi.loc[umiid, "pos"]
        while rss_pos[rssid] < umi_mid and rssid < chrom_rss.shape[0] - 1:
            rssid += 1
        prev_pos = rss_pos[rssid - 1]
        curr_pos = rss_pos[rssid]
        d_prev = np.abs(umi_mid - prev_pos)
        d_curr = np.abs(umi_mid - curr_pos)
        if d_prev > d_curr:
            d_rss.append(d_curr)
            assigned_rss_pos.append(curr_pos)
        else:
            d_rss.append(d_prev)
            assigned_rss_pos.append(prev_pos)
    return (d_rss, assigned_rss_pos)


def merge_UMIs_for_single_chrom(umi_clean):
    chrom = umi_clean["chr"].values.tolist()
    pos = umi_clean["pos"].values.tolist()
    seq = umi_clean["seq"].values.tolist()
    qual = umi_clean["qual"].values.tolist()
    n = umi_clean["n"].values.tolist()

    umid = 1
    while umid < len(chrom) - 1:
        if pos[umid] == pos[umid - 1]:
            chrom.pop(umid)
            pos.pop(umid)
            seq[umid - 1] = " ".join([seq[umid - 1], seq[umid]])
            seq.pop(umid)
            qual[umid - 1] = " ".join([qual[umid - 1], qual[umid]])
            qual.pop(umid)
            n[umid - 1] = n[umid] + n[umid - 1]
            n.pop(umid)
        else:
            umid += 1

    return pd.DataFrame.from_dict(dict(chr=chrom, pos=pos, seq=seq, qual=qual, n=n))


if args.output.endswith(".gz"):
    args.do_compress = True
args.orphan = os.path.join(
    os.path.dirname(args.output), f"orphan.{os.path.basename(args.output)}"
)
args.log = os.path.join(
    os.path.dirname(args.output),
    f"{os.path.splitext(os.path.basename(args.output))[0]}.log",
)

assert not os.path.isdir(args.log)
log_dir = os.path.dirname(args.log)
assert os.path.isdir(log_dir) or "" == log_dir
fh = RichHandler(console=Console(file=open(args.log, mode="w+")), markup=True)
fh.setLevel(logging.INFO)
logging.getLogger().addHandler(fh)
logging.info(f"[green]Log to[/]\t\t{args.log}")

logging.info("Reading RSs")
rss = pd.read_csv(args.cutsites, "\t", names=["chrom", "start", "end", "name"])

logging.info("Reading UMIs")
umi = pd.read_csv(
    args.umis,
    sep="\t",
    header=None,
    names=("chrom", "pos", "seq", "qual"),
)

chrom_list = sorted(set(umi["chrom"].values))
rss_chrom_list = sorted(set(rss["chrom"].values))
logging.info(f"Found {len(chrom_list)} chromosomes")

chrom_list_clean = []
for chrom_sel in chrom_list:
    if chrom_sel not in rss_chrom_list:
        logging.info(f"Skipping {chrom_sel} (missing from RSs data)")
        continue
    else:
        chrom_list_clean.append(chrom_sel)

logging.info("Assigning UMIs to RSs")
pd_list = Parallel(n_jobs=args.threads, verbose=11)(
    delayed(run_single_chrom)(
        umi.loc[umi["chrom"] == chrom_sel, :].copy(),
        rss.loc[rss["chrom"] == chrom_sel, :].copy(),
    )
    for chrom_sel in chrom_list_clean
)
umi_final = pd.concat(pd_list)

logging.info("Counting UMIs per RS")
n = []
for seqs in tqdm(umi_final["seq"].values, desc="UMIs"):
    n.append(len(seqs.split(" ")))
umi_final["n"] = n

n_pos = umi_final.shape[0]
n_umis = umi_final["n"].sum()
logging.info(f"Input: {n_umis} UMI sequences over {n_pos} locations")
logging.info(f"Distance from RS, summary")
logging.info(f"     min: {np.min(umi_final['d_rs'])}")
logging.info(f"    mean: {np.mean(umi_final['d_rs'])}")
logging.info(f"     max: {np.max(umi_final['d_rs'])}")

logging.info("Cleaning")
umi_orphan = umi_final.loc[umi_final["d_rs"] > args.min_dist, :].copy()
umi_clean = umi_final.loc[umi_final["d_rs"] <= args.min_dist, :].copy()
n_clean_pos = umi_clean.shape[0]
n_clean_umis = umi_clean["n"].sum()
logging.info(
    (
        f"Intermediate: {n_clean_umis} ({n_clean_umis/n_umis*100:.2f}%) UMI"
        + f" sequences over {n_clean_pos} ({n_clean_pos/n_pos*100:.2f}%) locations"
    )
)

umi_orphan.drop(["pos", "d_rs"], axis=1, inplace=True)
umi_orphan.rename({"rs_pos": "pos", "chrom": "chr"}, axis=1, inplace=True)
umi_orphan = umi_orphan.reindex(["chr", "pos", "seq", "qual", "n"], axis=1)
umi_orphan.sort_values(["chr", "pos"], inplace=True)

umi_clean.drop(["pos", "d_rs"], axis=1, inplace=True)
umi_clean.rename({"rs_pos": "pos", "chrom": "chr"}, axis=1, inplace=True)
umi_clean = umi_clean.reindex(["chr", "pos", "seq", "qual", "n"], axis=1)
umi_clean.sort_values(["chr", "pos"], inplace=True)
logging.info("Merging UMIs assigned to the same RS")
chrom_list = sorted(set(umi_clean["chr"].values))
umi_clean = pd.concat(
    Parallel(n_jobs=args.threads, verbose=11)(
        delayed(merge_UMIs_for_single_chrom)(
            umi_clean.loc[umi_clean["chr"] == chrom_sel, :].copy()
        )
        for chrom_sel in chrom_list
    )
)

n_clean_pos = umi_clean.shape[0]
n_clean_umis = umi_clean["n"].sum()
logging.info(
    (
        f"Output: {n_clean_umis} ({n_clean_umis/n_umis*100:.2f}%) UMI"
        + f" sequences over {n_clean_pos} ({n_clean_pos/n_pos*100:.2f}%) locations"
    )
)

umi_orphan.drop(["n"], axis=1, inplace=True)
umi_clean.drop("n", axis=1, inplace=True)

if args.do_compress and not args.output.endswith(".gz"):
    args.output += ".gz"
    args.orphan += ".gz"
logging.info("Writing output")
umi_orphan.to_csv(args.orphan, sep="\t", index=False, header=False, compression="infer")
umi_clean.to_csv(args.output, sep="\t", index=False, header=False, compression="infer")
