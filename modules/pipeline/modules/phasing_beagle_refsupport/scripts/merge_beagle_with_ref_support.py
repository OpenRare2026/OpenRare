#!/usr/bin/env python3
import argparse
import gzip
import re
import sys
from collections import Counter


INFO_HEADERS = (
    '##INFO=<ID=BEAGLE_PHASED,Number=1,Type=Integer,Description="1 if GT was replaced by Beagle noimpute phased GT; 0 if original GT was retained">\n',
    '##INFO=<ID=CHN_REF_SUPPORT,Number=1,Type=String,Description="Support category in the supplied reference panel: POLYMORPHIC, MONOMORPHIC_REF, ALLELE_MISMATCH, NOT_IN_REF">\n',
    '##INFO=<ID=CHN_ALT_CARRIER_COUNT,Number=1,Type=Integer,Description="Number of reference samples carrying allele 1 at an exactly matched CHROM/POS/REF/ALT marker">\n',
    '##INFO=<ID=CHN_ALT_AC,Number=1,Type=Integer,Description="Allele 1 count in reference samples at an exactly matched CHROM/POS/REF/ALT marker">\n',
    '##INFO=<ID=PHASING_CONFIDENCE,Number=1,Type=String,Description="Confidence label based on Beagle output and reference ALT support: HIGH, LOW, UNPHASED">\n',
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge Beagle noimpute GTs into original patient sites."
    )
    parser.add_argument("--patient-vcf", required=True)
    parser.add_argument("--beagle-vcf", required=True)
    parser.add_argument("--ref-vcf", required=True)
    parser.add_argument("--output-vcf", required=True, help="Uncompressed output VCF")
    parser.add_argument("--chrom", required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--stats")
    return parser.parse_args()


def open_text(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "rt", encoding="utf-8")


def sample_index_from_header(path, sample_id):
    with open_text(path) as handle:
        for line in handle:
            if line.startswith("#CHROM"):
                samples = line.rstrip("\n").split("\t")[9:]
                if sample_id not in samples:
                    raise RuntimeError(f"{sample_id!r} is not present in {path}")
                return 9 + samples.index(sample_id)
    raise RuntimeError(f"#CHROM header not found in {path}")


def get_gt(fields, sample_column):
    if len(fields) <= sample_column:
        return None
    fmt = fields[8].split(":")
    if "GT" not in fmt:
        return None
    gt_index = fmt.index("GT")
    values = fields[sample_column].split(":")
    return values[gt_index] if gt_index < len(values) else None


def replace_gt(fields, sample_column, gt):
    if len(fields) <= sample_column:
        return False
    fmt = fields[8].split(":")
    if "GT" not in fmt:
        return False
    gt_index = fmt.index("GT")
    values = fields[sample_column].split(":")
    while len(values) <= gt_index:
        values.append(".")
    values[gt_index] = gt
    fields[sample_column] = ":".join(values)
    return True


def allele1_counts(gt):
    if not gt or gt in {".", "./.", ".|."}:
        return 0, 0
    count = sum(allele == "1" for allele in re.split(r"[|/]", gt))
    return int(count > 0), count


def append_info(info, annotations):
    replaced = {name for name, _ in annotations}
    values = [
        item
        for item in info.split(";")
        if item and item != "." and item.split("=", 1)[0] not in replaced
    ]
    values.extend(f"{name}={value}" for name, value in annotations)
    return ";".join(values) if values else "."


def main():
    args = parse_args()
    patient_sample_column = sample_index_from_header(args.patient_vcf, args.sample_id)
    beagle_sample_column = sample_index_from_header(args.beagle_vcf, args.sample_id)

    patient_keys = set()
    patient_positions = set()
    with open_text(args.patient_vcf) as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            key = (fields[0], fields[1], fields[3], fields[4])
            patient_keys.add(key)
            patient_positions.add((fields[0], fields[1]))

    exact_ref = {}
    reference_positions = set()
    reference_samples = None
    multiallelic_exact = 0
    with open_text(args.ref_vcf) as handle:
        for line in handle:
            if line.startswith("#CHROM"):
                reference_samples = len(line.rstrip("\n").split("\t")) - 9
                continue
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            position = (fields[0], fields[1])
            if position not in patient_positions:
                continue
            reference_positions.add(position)
            key = (fields[0], fields[1], fields[3], fields[4])
            if key not in patient_keys:
                continue
            carrier_count = 0
            alt_ac = 0
            fmt = fields[8].split(":")
            if "GT" in fmt:
                gt_index = fmt.index("GT")
                for sample_field in fields[9:]:
                    values = sample_field.split(":")
                    gt = values[gt_index] if gt_index < len(values) else "."
                    carrier, ac = allele1_counts(gt)
                    carrier_count += carrier
                    alt_ac += ac
            exact_ref[key] = (carrier_count, alt_ac)
            if "," in fields[4]:
                multiallelic_exact += 1

    if reference_samples != 359:
        print(
            f"WARNING {args.chrom}: expected 359 reference samples, "
            f"found {reference_samples}; continuing.",
            file=sys.stderr,
        )

    beagle_gt = {}
    with open_text(args.beagle_vcf) as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            key = (fields[0], fields[1], fields[3], fields[4])
            if key in patient_keys:
                gt = get_gt(fields, beagle_sample_column)
                if gt is not None:
                    beagle_gt[key] = gt

    support_counts = Counter()
    confidence_counts = Counter()
    beagle_counts = Counter()
    gt_counts = Counter()
    warning_count = 0
    records = 0

    with open_text(args.patient_vcf) as source, open(
        args.output_vcf, "wt", encoding="utf-8"
    ) as output:
        header_added = False
        for line in source:
            if line.startswith("##"):
                if not any(
                    line.startswith(f"##INFO=<ID={header.split('ID=', 1)[1].split(',', 1)[0]}")
                    for header in INFO_HEADERS
                ):
                    output.write(line)
                continue
            if line.startswith("#CHROM"):
                for header in INFO_HEADERS:
                    output.write(header)
                output.write(line)
                header_added = True
                continue
            if line.startswith("#"):
                output.write(line)
                continue

            fields = line.rstrip("\n").split("\t")
            key = (fields[0], fields[1], fields[3], fields[4])
            position = (fields[0], fields[1])
            beagle_phased = int(
                key in beagle_gt
                and replace_gt(fields, patient_sample_column, beagle_gt[key])
            )
            beagle_counts[beagle_phased] += 1

            if key in exact_ref:
                carriers, alt_ac = exact_ref[key]
                support = "POLYMORPHIC" if carriers else "MONOMORPHIC_REF"
            elif position in reference_positions:
                carriers, alt_ac = 0, 0
                support = "ALLELE_MISMATCH"
            else:
                carriers, alt_ac = 0, 0
                support = "NOT_IN_REF"
            support_counts[support] += 1

            if not beagle_phased:
                confidence = "UNPHASED"
            elif support == "POLYMORPHIC":
                confidence = "HIGH"
            else:
                confidence = "LOW"
                if support in {"ALLELE_MISMATCH", "NOT_IN_REF"}:
                    warning_count += 1
            confidence_counts[confidence] += 1

            fields[7] = append_info(
                fields[7],
                (
                    ("BEAGLE_PHASED", str(beagle_phased)),
                    ("CHN_REF_SUPPORT", support),
                    ("CHN_ALT_CARRIER_COUNT", str(carriers)),
                    ("CHN_ALT_AC", str(alt_ac)),
                    ("PHASING_CONFIDENCE", confidence),
                ),
            )
            gt = get_gt(fields, patient_sample_column)
            if gt and "|" in gt:
                gt_counts["phased"] += 1
            elif gt and "/" in gt:
                gt_counts["unphased"] += 1
            else:
                gt_counts["other"] += 1
            output.write("\t".join(fields) + "\n")
            records += 1

    if not header_added:
        raise RuntimeError(f"{args.chrom}: #CHROM header not found")

    stats_path = args.stats or args.output_vcf + ".stats.tsv"
    rows = (
        ("chrom", args.chrom),
        ("sample_id", args.sample_id),
        ("reference_samples", reference_samples),
        ("patient_records", records),
        ("BEAGLE_PHASED_1", beagle_counts[1]),
        ("BEAGLE_PHASED_0", beagle_counts[0]),
        ("CHN_REF_SUPPORT_POLYMORPHIC", support_counts["POLYMORPHIC"]),
        ("CHN_REF_SUPPORT_MONOMORPHIC_REF", support_counts["MONOMORPHIC_REF"]),
        ("CHN_REF_SUPPORT_ALLELE_MISMATCH", support_counts["ALLELE_MISMATCH"]),
        ("CHN_REF_SUPPORT_NOT_IN_REF", support_counts["NOT_IN_REF"]),
        ("PHASING_CONFIDENCE_HIGH", confidence_counts["HIGH"]),
        ("PHASING_CONFIDENCE_LOW", confidence_counts["LOW"]),
        ("PHASING_CONFIDENCE_UNPHASED", confidence_counts["UNPHASED"]),
        ("final_GT_phased", gt_counts["phased"]),
        ("final_GT_unphased", gt_counts["unphased"]),
        ("final_GT_other", gt_counts["other"]),
        ("multiallelic_exact_allele1_only", multiallelic_exact),
        ("warning_beagle1_nonexact_support", warning_count),
    )
    with open(stats_path, "wt", encoding="utf-8") as stats:
        stats.write("metric\tvalue\n")
        for metric, value in rows:
            stats.write(f"{metric}\t{value}\n")

    if multiallelic_exact:
        print(
            f"WARNING {args.chrom}: {multiallelic_exact} multiallelic exact markers "
            "were counted using allele 1 only.",
            file=sys.stderr,
        )
    if warning_count:
        print(
            f"WARNING {args.chrom}: {warning_count} BEAGLE_PHASED=1 markers had "
            "ALLELE_MISMATCH/NOT_IN_REF support and were labeled LOW.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
