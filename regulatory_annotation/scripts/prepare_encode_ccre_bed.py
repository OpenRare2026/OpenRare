#!/usr/bin/env python3
import argparse
import gzip
import re
import sys
from pathlib import Path

KNOWN_CLASSES = [
    'PLS', 'pELS', 'dELS', 'CA-CTCF', 'CA-H3K4me3', 'CA-TF', 'CA', 'TF',
    'CTCF-only', 'DNase-H3K4me3', 'DNase-only', 'Low-DNase'
]
CLASS_RE = re.compile(r'^(PLS|pELS|dELS|CA-CTCF|CA-H3K4me3|CA-TF|CA|TF|CTCF-only|DNase-H3K4me3|DNase-only|Low-DNase)([,_].*)?$')
ACCESSION_RE = re.compile(r'(EH38E\d+|EH37E\d+|EM10E\d+|EH\d+E\d+)')

def open_text(path):
    if str(path).endswith('.gz'):
        return gzip.open(path, 'rt')
    return open(path, 'rt')

def pick_class(fields):
    for f in fields[3:]:
        token = f.strip()
        if CLASS_RE.match(token):
            return token
    for f in fields[3:]:
        for cls in KNOWN_CLASSES:
            if cls in f:
                return cls
    return fields[9].strip() if len(fields) > 9 and fields[9].strip() else 'NA'

def pick_id(fields):
    for f in fields[3:]:
        m = ACCESSION_RE.search(f)
        if m:
            return m.group(1)
    return fields[3].strip() if len(fields) > 3 and fields[3].strip() else f'{fields[0]}:{fields[1]}-{fields[2]}'

def main():
    ap = argparse.ArgumentParser(description='Normalize ENCODE SCREEN cCRE BED to chrom/start/end/id/class.')
    ap.add_argument('input_bed')
    ap.add_argument('output_bed')
    ap.add_argument('--require-chr', action='store_true', help='Drop records whose chromosome does not start with chr.')
    args = ap.parse_args()

    n_in = n_out = 0
    classes = {}
    with open_text(args.input_bed) as inp, open(args.output_bed, 'w') as out:
        for line in inp:
            if not line.strip() or line.startswith(('#', 'track', 'browser')):
                continue
            fields = line.rstrip('\n').split('\t')
            if len(fields) < 3:
                continue
            chrom, start, end = fields[0], fields[1], fields[2]
            n_in += 1
            if args.require_chr and not chrom.startswith('chr'):
                continue
            try:
                int(start); int(end)
            except ValueError:
                continue
            ccre_id = pick_id(fields)
            ccre_class = pick_class(fields)
            out.write(f'{chrom}\t{start}\t{end}\t{ccre_id}\t{ccre_class}\n')
            n_out += 1
            classes[ccre_class] = classes.get(ccre_class, 0) + 1

    sys.stderr.write(f'input_records\t{n_in}\noutput_records\t{n_out}\n')
    for cls, count in sorted(classes.items(), key=lambda x: (-x[1], x[0])):
        sys.stderr.write(f'class\t{cls}\t{count}\n')

if __name__ == '__main__':
    main()
