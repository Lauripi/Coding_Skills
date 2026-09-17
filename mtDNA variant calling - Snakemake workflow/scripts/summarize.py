#!/usr/bin/env python
"""Summary step of the mtDNA variant-calling workflow (rule `summary` in the Snakefile).

Gathers what the assignment asks for from the reports of the tools that were used in
the Galaxy analysis - MultiQC (FastQC raw vs trimmed), Qualimap (mapping) and
FreeBayes/IGV (variants) - into one folder, 08_summary/:

  Q2  q2_trimming_qc.csv       FastQC module status raw -> trimmed, read counts, read
                               length - taken from MultiQC's table (multiqc_fastqc.txt)
  Q4  q4_mapping_quality.csv   mapped reads, coverage, mapping quality, error rate -
                               taken from Qualimap's genome_results.txt
  Q5  q5_snp_counts.csv        SNPs per sample, heterozygous vs homozygous - counted
                               from the FreeBayes VCF (same rule as the course's awk)
      figures/                 copies of the tool-made plots: MultiQC's per-base quality
                               plot (raw vs trimmed) and Qualimap's coverage and
                               mapping-quality plots
      summary.md               the three tables, the figures and a link to the IGV report

Nothing is plotted here: every figure is made by MultiQC (--export), Qualimap or
igv-reports, i.e. the same tools as in the Galaxy / IGV analysis.

Snakemake runs this file through the `script:` directive. It can also be run by hand
on any finished run:

    python scripts/summarize.py \
        --multiqc-table 06_multiqc/multiqc_data/multiqc_fastqc.txt \
        --multiqc-plot  06_multiqc/multiqc_plots/png/fastqc_per_base_sequence_quality_plot.png \
        --qualimap      05_qualimap/*/genome_results.txt \
        --vcf           07_vcf/all_samples.vcf \
        --igv-report    09_igv/igv_report.html \
        --outdir        08_summary

Only the standard library and pandas are needed.
"""
# NB: no `from __future__ import annotations` here - Snakemake prepends code to the
# script when it runs it through `script:`, so it would no longer be the first statement.

import argparse
import glob
import math
import re
import shutil
import sys
from pathlib import Path

if "snakemake" in globals() and snakemake.log:  # noqa: F821  (Snakemake mode)
    # redirect everything (incl. import errors below) to the rule's log file
    sys.stdout = sys.stderr = open(snakemake.log[0], "w")  # noqa: F821

import pandas as pd  # noqa: E402

# FastQC modules as named in the FastQC report / MultiQC column name in multiqc_fastqc.txt
FASTQC_MODULES = {
    "Per base sequence quality": "per_base_sequence_quality",
    "Per tile sequence quality": "per_tile_sequence_quality",
    "Per sequence quality scores": "per_sequence_quality_scores",
    "Per base sequence content": "per_base_sequence_content",
    "Per sequence GC content": "per_sequence_gc_content",
    "Per base N content": "per_base_n_content",
    "Sequence Length Distribution": "sequence_length_distribution",
    "Sequence Duplication Levels": "sequence_duplication_levels",
    "Overrepresented sequences": "overrepresented_sequences",
    "Adapter Content": "adapter_content",
}

# Qualimap figures (images_qualimapReport/<name>.png) collected into 08_summary/figures/
QUALIMAP_PLOTS = [
    "genome_coverage_across_reference",
    "genome_mapping_quality_across_reference",
    "genome_mapping_quality_histogram",
]

OUTPUT_FILES = {
    "trimming": "q2_trimming_qc.csv",
    "mapping": "q4_mapping_quality.csv",
    "snps": "q5_snp_counts.csv",
    "report": "summary.md",
}
FIGURE_DIR = "figures"
MULTIQC_FIGURE = "multiqc_fastqc_per_base_sequence_quality.png"


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def norm_sample(name: str) -> str:
    """Galaxy/FreeBayes use 'Blood-PCR1', the files use 'Blood_PCR1' -> one spelling."""
    return name.replace("-", "_")


def df_to_markdown(df: pd.DataFrame, floatfmt: str = "{:,.2f}") -> str:
    """Small markdown-table writer (avoids the `tabulate` dependency of df.to_markdown)."""

    def fmt(v):
        if isinstance(v, float):
            return "" if math.isnan(v) else floatfmt.format(v)
        if isinstance(v, int) and not isinstance(v, bool):
            return f"{v:,}"
        return str(v)

    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(v) for v in row.tolist()) + " |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Q2 - MultiQC table of the FastQC results (raw and trimmed reads)
# ----------------------------------------------------------------------------
def read_multiqc_fastqc(path: str) -> pd.DataFrame:
    """multiqc_data/multiqc_fastqc.txt: one row per FastQC report, indexed by sample."""
    df = pd.read_csv(path, sep="\t")
    return df.set_index("Sample")


def trimming_table(mq: pd.DataFrame, samples: list[str]) -> pd.DataFrame:
    """Q2: before/after trimming, one row per sample.

    The raw report is the row named like the sample, the trimmed one the row whose name
    starts with the sample name plus a suffix (e.g. Blood_PCR1 -> Blood_PCR1_posttrim).
    """
    rows = []
    for s in samples:
        if s not in mq.index:
            raise KeyError(f"no raw FastQC entry {s!r} in the MultiQC table ({list(mq.index)})")
        trimmed = [n for n in mq.index if n != s and n.startswith(s + "_")]
        if len(trimmed) != 1:
            raise KeyError(f"expected one trimmed FastQC entry for {s!r}, found {trimmed}")
        r, t = mq.loc[s], mq.loc[trimmed[0]]
        row = {
            "sample": s,
            "reads_raw": int(r["Total Sequences"]),
            "reads_trimmed": int(t["Total Sequences"]),
            "reads_kept_pct": round(100 * t["Total Sequences"] / r["Total Sequences"], 2),
            "read_length_raw": str(r["Sequence length"]).removesuffix(".0"),
            "read_length_trimmed": str(t["Sequence length"]).removesuffix(".0"),
            "mean_length_raw": round(float(r["avg_sequence_length"]), 1),
            "mean_length_trimmed": round(float(t["avg_sequence_length"]), 1),
            "gc_raw_pct": float(r["%GC"]),
            "gc_trimmed_pct": float(t["%GC"]),
            "duplication_raw_pct": round(100 - float(r["total_deduplicated_percentage"]), 1),
            "duplication_trimmed_pct": round(100 - float(t["total_deduplicated_percentage"]), 1),
        }
        for module, col in FASTQC_MODULES.items():
            a, b = str(r.get(col, "NA")).upper(), str(t.get(col, "NA")).upper()
            row[module] = a if a == b else f"{a} -> {b}"
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Q3/Q4 - Qualimap BamQC
# ----------------------------------------------------------------------------
def read_qualimap(path: str) -> dict:
    """Parse the numbers of Qualimap's genome_results.txt."""
    txt = Path(path).read_text(encoding="utf-8", errors="replace")

    def num(pattern, cast=float, default=float("nan")):
        m = re.search(pattern, txt)
        return cast(m.group(1).replace(",", "")) if m else default

    res = {
        "sample": Path(path).parent.name,
        "dir": Path(path).parent,
        "reads_in_bam": num(r"number of reads = ([\d,]+)", int, 0),
        "mapped_reads": num(r"number of mapped reads = ([\d,]+)", int, 0),
        "mapped_pct": num(r"number of mapped reads = [\d,]+ \(([\d.]+)%\)"),
        "mean_coverage": num(r"mean coverageData = ([\d.]+)X"),
        "std_coverage": num(r"std coverageData = ([\d.]+)X"),
        "breadth_1x_pct": num(r"There is a ([\d.]+)% of reference with a coverageData >= 1X"),
        "breadth_10x_pct": num(r"There is a ([\d.]+)% of reference with a coverageData >= 10X"),
        "mean_mapq": num(r"mean mapping quality = ([\d.]+)"),
        "error_rate": num(r"general error rate = ([\d.]+)"),
        "mismatches": num(r"number of mismatches = ([\d,]+)", int, 0),
        "insertions": num(r"number of insertions = ([\d,]+)", int, 0),
        "deletions": num(r"number of deletions = ([\d,]+)", int, 0),
        "duplication_rate_pct": num(r"duplication rate = ([\d.]+)%"),
        "gc_pct": num(r"GC percentage = ([\d.]+)%"),
        "reference_length": num(r"number of bases = ([\d,]+) bp", int, 0),
    }
    res["unmapped_reads"] = res["reads_in_bam"] - res["mapped_reads"]
    return res


def mapping_table(qm: dict, samples: list[str]) -> pd.DataFrame:
    """Q3/Q4: how good was the mapping, one row per sample."""
    rows = []
    for s in samples:
        q = qm[s]
        rows.append(
            {
                "sample": s,
                "reads_in_bam": q["reads_in_bam"],
                "mapped_reads": q["mapped_reads"],
                "mapped_pct": q["mapped_pct"],
                "unmapped_reads": q["unmapped_reads"],
                "mean_coverage_x": round(q["mean_coverage"], 1),
                "std_coverage_x": round(q["std_coverage"], 1),
                "breadth_of_coverage_1x_pct": q["breadth_1x_pct"],
                "breadth_of_coverage_10x_pct": q["breadth_10x_pct"],
                "mean_mapping_quality": round(q["mean_mapq"], 2),
                "error_rate_pct": round(100 * q["error_rate"], 2),
                "mismatches": q["mismatches"],
                "insertions": q["insertions"],
                "deletions": q["deletions"],
                "duplication_rate_pct": q["duplication_rate_pct"],
                "gc_pct": q["gc_pct"],
            }
        )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Q5 - FreeBayes VCF
# ----------------------------------------------------------------------------
def gt_class(gt: str) -> str:
    """'0/0' -> hom_ref, '0/1' -> het, '1/1' -> hom_alt, './.' -> missing."""
    alleles = re.split(r"[/|]", gt)
    if "." in alleles or gt == ".":
        return "missing"
    if len(set(alleles)) == 1:
        return "hom_ref" if alleles[0] == "0" else "hom_alt"
    return "het"


def read_vcf(path: str) -> tuple[list[str], list[dict], str]:
    """Minimal VCF reader: sample names, one dict per record, FreeBayes command line."""
    samples: list[str] = []
    records: list[dict] = []
    commandline = ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("##"):
                if line.startswith("##commandline="):
                    commandline = line.split("=", 1)[1].strip().strip('"')
                continue
            f = line.rstrip("\n").split("\t")
            if line.startswith("#CHROM"):
                samples = f[9:]
                continue
            if len(f) < 10:
                continue
            info = {}
            for kv in f[7].split(";"):
                k, _, v = kv.partition("=")
                info[k] = v if v else True
            fmt = f[8].split(":")
            rec = {
                "chrom": f[0],
                "pos": int(f[1]),
                "ref": f[3],
                "alt": f[4],
                "qual": float(f[5]) if f[5] != "." else float("nan"),
                "type": info.get("TYPE", "."),
                "calls": {},
            }
            for s, val in zip(samples, f[9:]):
                d = dict(zip(fmt, val.split(":")))
                gt = d.get("GT", ".")
                dp = int(d["DP"]) if d.get("DP", ".") not in (".", "") else 0
                ao = sum(int(x) for x in d.get("AO", "0").split(",") if x not in (".", ""))
                rec["calls"][s] = {
                    "GT": gt,
                    "class": gt_class(gt),
                    "DP": dp,
                    "AO": ao,
                    "AF": ao / dp if dp else float("nan"),
                }
            records.append(rec)
    return samples, records, commandline


def snp_table(vcf_samples: list[str], records: list[dict], samples: list[str]) -> tuple[pd.DataFrame, dict]:
    """Q5: SNPs per sample, heterozygous vs homozygous.

    Same counting as the course's awk script: a "SNP site" is a VCF record with
    INFO TYPE=snp (FreeBayes also writes candidate sites where every sample is 0/0);
    a sample "has" the SNP when its genotype is not 0/0.
    """
    by_norm = {norm_sample(s): s for s in vcf_samples}
    snp_sites = [r for r in records if r["type"] == "snp"]
    rows = []
    for s in samples:
        vs = by_norm.get(s)
        if vs is None:
            raise KeyError(f"sample {s!r} not found in the VCF (samples: {vcf_samples})")
        het = sum(r["calls"][vs]["class"] == "het" for r in snp_sites)
        hom = sum(r["calls"][vs]["class"] == "hom_alt" for r in snp_sites)
        het_all = sum(r["calls"][vs]["class"] == "het" for r in records)
        hom_all = sum(r["calls"][vs]["class"] == "hom_alt" for r in records)
        rows.append(
            {
                "sample": s,
                "total_snps": het + hom,
                "heterozygous": het,
                "homozygous": hom,
                "variants_all_types": het_all + hom_all,
                "heterozygous_all_types": het_all,
                "homozygous_all_types": hom_all,
            }
        )

    def any_non_ref(r):
        return any(c["class"] in ("het", "hom_alt") for c in r["calls"].values())

    type_counts = pd.Series([r["type"] for r in records]).value_counts().to_dict()
    overview = {
        "records_in_vcf": len(records),
        "type_counts": type_counts,
        "snp_sites_in_vcf": len(snp_sites),
        "sites_variant_in_any_sample": sum(any_non_ref(r) for r in records),
        "snp_sites_variant_in_any_sample": sum(any_non_ref(r) for r in snp_sites),
    }
    return pd.DataFrame(rows), overview


def variant_sites_table(vcf_samples: list[str], records: list[dict], samples: list[str]) -> pd.DataFrame:
    """Sites that are non-reference in >= 1 sample, with each sample's genotype and
    alternate-allele fraction (what the IGV VCF track shows, as a table)."""
    by_norm = {norm_sample(s): s for s in vcf_samples}
    rows = []
    for r in records:
        if not any(c["class"] in ("het", "hom_alt") for c in r["calls"].values()):
            continue
        row = {"pos": r["pos"], "ref": r["ref"], "alt": r["alt"], "type": r["type"], "qual": round(r["qual"])}
        for s in samples:
            c = r["calls"][by_norm[s]]
            row[s] = f"{c['GT']} ({c['AF']:.2f})"
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Figures: copies of the plots made by MultiQC and Qualimap
# ----------------------------------------------------------------------------
def collect_figures(multiqc_plot: str, qm: dict, samples: list[str], figdir: Path) -> dict:
    """Copy the tool-made PNGs into <outdir>/figures/ and return {label: relative path}."""
    figdir.mkdir(parents=True, exist_ok=True)
    figures = {}
    if multiqc_plot and Path(multiqc_plot).exists():
        dest = figdir / MULTIQC_FIGURE
        shutil.copyfile(multiqc_plot, dest)
        figures["MultiQC - FastQC per-base sequence quality, raw and trimmed"] = f"{FIGURE_DIR}/{dest.name}"
    for s in samples:
        for plot in QUALIMAP_PLOTS:
            src = qm[s]["dir"] / "images_qualimapReport" / f"{plot}.png"
            if not src.exists():
                print(f"warning: {src} not found", file=sys.stderr)
                continue
            dest = figdir / f"qualimap_{s}_{plot}.png"
            shutil.copyfile(src, dest)
            label = plot.replace("genome_", "").replace("_", " ")
            figures[f"Qualimap - {s} - {label}"] = f"{FIGURE_DIR}/{dest.name}"
    return figures


# ----------------------------------------------------------------------------
# Markdown report
# ----------------------------------------------------------------------------
def write_report(path, samples, trim_df, map_df, snp_df, sites_df, overview, commandline, figures, igv_report):
    modules = list(FASTQC_MODULES)
    status_df = trim_df.set_index("sample")[modules].T.reset_index().rename(columns={"index": "FastQC module"})
    reads_df = trim_df[["sample", "reads_raw", "reads_trimmed", "reads_kept_pct",
                        "read_length_raw", "read_length_trimmed", "mean_length_raw", "mean_length_trimmed"]]
    map_cols = ["sample", "mapped_reads", "mapped_pct", "unmapped_reads", "mean_coverage_x",
                "breadth_of_coverage_1x_pct", "mean_mapping_quality", "error_rate_pct", "duplication_rate_pct"]
    types = ", ".join(f"{k}: {v}" for k, v in sorted(overview["type_counts"].items()))
    out = Path(path)
    igv_link = Path(igv_report).resolve().relative_to(out.parent.resolve().parent).as_posix() if igv_report else None

    def figs(prefix):
        return [f"![{k}]({v})" for k, v in figures.items() if k.startswith(prefix)]

    lines = [
        "# mtDNA variant calling - summary",
        "",
        f"Samples: {', '.join(samples)}. Tables and figures come from the reports of MultiQC",
        "(FastQC raw vs trimmed), Qualimap (mapping) and FreeBayes / IGV (variants).",
        "",
        "## Q2 - Quality of untrimmed vs trimmed reads (FastQC via MultiQC)",
        "",
        "Source: `06_multiqc/multiqc_report.html` (table `multiqc_data/multiqc_fastqc.txt`).",
        "",
        df_to_markdown(reads_df),
        "",
        "FastQC module status, raw -> trimmed (a single value means the status did not change):",
        "",
        df_to_markdown(status_df),
        "",
        *figs("MultiQC"),
        "",
        "## Q3/Q4 - Quality of the mapping (Qualimap BamQC on the de-duplicated BAMs)",
        "",
        "Source: `05_qualimap/<sample>/qualimapReport.html` (`genome_results.txt`). Unmapped reads",
        "were removed before this step (`samtools view -F 4`), so 100 % of the reads in each BAM",
        "are mapped by construction; coverage, mapping quality and error rate are the informative metrics.",
        "",
        df_to_markdown(map_df[map_cols]),
        "",
        *figs("Qualimap"),
        "",
        "## Q5 - Variants (FreeBayes joint call, viewed in IGV)",
        "",
        f"- FreeBayes command: `{commandline or 'n/a'}`",
        f"- Records in the VCF: {overview['records_in_vcf']} ({types})",
        f"- SNP sites in the VCF (INFO TYPE=snp, incl. candidate sites that are 0/0 in every sample): {overview['snp_sites_in_vcf']}",
        f"- Sites that are non-reference in at least one sample: {overview['sites_variant_in_any_sample']}"
        f" (of which SNPs: {overview['snp_sites_variant_in_any_sample']})",
        f"- IGV view of every variant (reference, VCF track, 4 BAM pileups): [{Path(igv_report).name}]({igv_link})" if igv_report else "",
        "",
        "Per sample (SNP sites only; the *_all_types columns also count indels/complex variants).",
        "The samples come from one individual, so 'heterozygous' calls of the diploid model are",
        "heteroplasmic sites (mixed mtDNA populations), not true heterozygosity.",
        "",
        df_to_markdown(snp_df),
        "",
        "Genotype (alternate allele fraction) of each sample at the variant sites:",
        "",
        df_to_markdown(sites_df),
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")


# ----------------------------------------------------------------------------
# Entry points
# ----------------------------------------------------------------------------
def run(multiqc_table, multiqc_plot, qualimap, vcf, outdir, samples=None, igv_report=None):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = {k: str(outdir / v) for k, v in OUTPUT_FILES.items()}

    mq = read_multiqc_fastqc(multiqc_table)
    qm = {q["sample"]: q for q in map(read_qualimap, qualimap)}
    vcf_samples, records, commandline = read_vcf(vcf)
    samples = list(samples) if samples else [s for s in mq.index if not any(s.startswith(o + "_") for o in mq.index if o != s)]
    missing = [s for s in samples if s not in qm]
    if missing:
        raise KeyError(f"Qualimap: no result for sample(s) {missing}; found {sorted(qm)}")

    trim_df = trimming_table(mq, samples)
    map_df = mapping_table(qm, samples)
    snp_df, overview = snp_table(vcf_samples, records, samples)
    sites_df = variant_sites_table(vcf_samples, records, samples)

    trim_df.to_csv(out["trimming"], index=False)
    map_df.to_csv(out["mapping"], index=False)
    snp_df.to_csv(out["snps"], index=False)
    figures = collect_figures(multiqc_plot, qm, samples, outdir / FIGURE_DIR)
    write_report(out["report"], samples, trim_df, map_df, snp_df, sites_df, overview, commandline, figures, igv_report)

    with pd.option_context("display.width", 200, "display.max_columns", 30):
        print("Q2 - trimming:\n", trim_df.iloc[:, :8].to_string(index=False), "\n")
        print("Q4 - mapping:\n", map_df.iloc[:, :10].to_string(index=False), "\n")
        print("Q5 - SNPs:\n", snp_df.to_string(index=False), "\n")
        print("VCF overview:", overview)
        print(f"{len(figures)} figures copied to {outdir / FIGURE_DIR}/")
    print(f"Summary written to {outdir}/")


def _expand(paths):
    found = []
    for p in paths:
        matches = sorted(glob.glob(p))
        found.extend(matches or [p])
    return found


def main_cli(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--multiqc-table", required=True, help="MultiQC's multiqc_data/multiqc_fastqc.txt")
    ap.add_argument("--multiqc-plot", default=None, help="MultiQC-exported PNG of the per-base quality plot")
    ap.add_argument("--qualimap", nargs="+", required=True, help="Qualimap genome_results.txt files")
    ap.add_argument("--vcf", required=True, help="FreeBayes multi-sample VCF")
    ap.add_argument("--igv-report", default=None, help="HTML made by igv-reports (linked in summary.md)")
    ap.add_argument("--outdir", default="08_summary")
    ap.add_argument("--samples", nargs="*", help="sample order (default: raw entries of the MultiQC table)")
    a = ap.parse_args(argv)
    run(a.multiqc_table, a.multiqc_plot, _expand(a.qualimap), a.vcf, a.outdir, a.samples, a.igv_report)


if "snakemake" in globals():  # executed by Snakemake through the `script:` directive
    sm = globals()["snakemake"]
    run(
        str(sm.input.multiqc_table),
        str(sm.input.multiqc_plot),
        list(sm.input.qualimap),
        str(sm.input.vcf),
        Path(str(sm.output.report)).parent,
        list(sm.params.samples),
        str(sm.input.igv),
    )
elif __name__ == "__main__":
    main_cli()
