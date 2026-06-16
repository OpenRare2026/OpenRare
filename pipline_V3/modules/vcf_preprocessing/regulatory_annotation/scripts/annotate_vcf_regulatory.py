#!/usr/bin/env python3
import argparse
import bisect
import gzip
import sys
from collections import defaultdict
from datetime import date

INFO_HEADERS = [
    '##INFO=<ID=REG_CCRE_ID,Number=.,Type=String,Description="ENCODE SCREEN cCRE identifiers overlapping this variant interval">',
    '##INFO=<ID=REG_CCRE_CLASS,Number=.,Type=String,Description="ENCODE SCREEN cCRE classes overlapping this variant interval">',
    '##INFO=<ID=REG_CCRE_COUNT,Number=1,Type=Integer,Description="Number of ENCODE SCREEN cCRE intervals overlapping this variant interval">',
    '##INFO=<ID=REG_CCRE_SOURCE,Number=1,Type=String,Description="Regulatory annotation source version">',
]

def open_text(path):
    if path == '-':
        return sys.stdin
    if path.endswith('.gz'):
        return gzip.open(path, 'rt')
    return open(path, 'rt')

def load_bed(path):
    by_chrom = defaultdict(list)
    with open_text(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith(('#', 'track', 'browser')):
                continue
            f = line.rstrip('\n').split('\t')
            if len(f) < 5:
                raise SystemExit(f'BED requires at least 5 columns: {line[:120]}')
            chrom, start, end, ccre_id, ccre_class = f[:5]
            start_i = int(start)
            end_i = int(end)
            if end_i <= start_i:
                continue
            by_chrom[chrom].append((start_i, end_i, ccre_id, ccre_class))
    index = {}
    for chrom, rows in by_chrom.items():
        rows.sort(key=lambda x: (x[0], x[1], x[2]))
        starts = [r[0] for r in rows]
        max_len = max(r[1] - r[0] for r in rows)
        index[chrom] = (rows, starts, max_len)
    return index

def uniq(values):
    seen = set()
    out = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out

def overlap(index, chrom, start, end):
    if chrom not in index:
        return []
    rows, starts, max_len = index[chrom]
    i = bisect.bisect_left(starts, end) - 1
    lower_start = start - max_len
    hits = []
    while i >= 0 and rows[i][0] >= lower_start:
        r_start, r_end, ccre_id, ccre_class = rows[i]
        if r_start < end and r_end > start:
            hits.append((r_start, r_end, ccre_id, ccre_class))
        i -= 1
    hits.sort(key=lambda x: (x[0], x[1], x[2]))
    return hits

def add_info(info, key, value):
    if info == '.' or info == '':
        return f'{key}={value}'
    return f'{info};{key}={value}'

def main():
    ap = argparse.ArgumentParser(description='Annotate VCF variants with ENCODE SCREEN cCRE overlaps.')
    ap.add_argument('--vcf', required=True, help='Input VCF, optionally .gz')
    ap.add_argument('--bed', required=True, help='Normalized 5-column BED: chrom start end ccre_id ccre_class')
    ap.add_argument('--source', default='ENCODE_SCREEN_v4_GRCh38')
    ap.add_argument('--stats', help='Write summary TSV')
    args = ap.parse_args()

    index = load_bed(args.bed)
    total = annotated = 0
    class_counts = defaultdict(int)
    existing_info = set()
    pending_headers = []

    with open_text(args.vcf) as fh:
        for line in fh:
            if line.startswith('##INFO=<ID='):
                existing_info.add(line.split('ID=', 1)[1].split(',', 1)[0])
                pending_headers.append(line)
                continue
            if line.startswith('##'):
                pending_headers.append(line)
                continue
            if line.startswith('#CHROM'):
                for h in pending_headers:
                    sys.stdout.write(h)
                for h in INFO_HEADERS:
                    info_id = h.split('ID=', 1)[1].split(',', 1)[0]
                    if info_id not in existing_info:
                        sys.stdout.write(h + '\n')
                sys.stdout.write(line)
                break
        else:
            raise SystemExit('Input does not look like a VCF: missing #CHROM header')

        for line in fh:
            if not line.strip() or line.startswith('#'):
                sys.stdout.write(line)
                continue
            total += 1
            f = line.rstrip('\n').split('\t')
            if len(f) < 8:
                sys.stdout.write(line)
                continue
            chrom = f[0]
            pos = int(f[1])
            ref = f[3]
            start = pos - 1
            end = start + max(1, len(ref))
            hits = overlap(index, chrom, start, end)
            if hits:
                annotated += 1
                ids = uniq([h[2] for h in hits])
                classes = uniq([h[3] for h in hits])
                for c in classes:
                    class_counts[c] += 1
                info = f[7]
                info = add_info(info, 'REG_CCRE_ID', ','.join(ids))
                info = add_info(info, 'REG_CCRE_CLASS', ','.join(classes))
                info = add_info(info, 'REG_CCRE_COUNT', str(len(hits)))
                info = add_info(info, 'REG_CCRE_SOURCE', args.source)
                f[7] = info
                sys.stdout.write('\t'.join(f) + '\n')
            else:
                sys.stdout.write(line)

    if args.stats:
        with open(args.stats, 'w') as out:
            out.write('metric\tvalue\n')
            out.write(f'source\t{args.source}\n')
            out.write(f'run_date\t{date.today().isoformat()}\n')
            out.write(f'total_variants\t{total}\n')
            out.write(f'variants_with_ccre_overlap\t{annotated}\n')
            out.write(f'variants_without_ccre_overlap\t{total - annotated}\n')
            for cls, count in sorted(class_counts.items(), key=lambda x: (-x[1], x[0])):
                out.write(f'class:{cls}\t{count}\n')

if __name__ == '__main__':
    main()
