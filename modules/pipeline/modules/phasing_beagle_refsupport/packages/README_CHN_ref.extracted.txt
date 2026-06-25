CHN reference panel
===================
Source: 1000 Genomes 30x GRCh38 phased panel
Subset: CHB + CHS + CDX, 359 samples
Purpose: Beagle phasing reference panel
Coordinates: GRCh38
Chromosome naming: chr1-chr22
Naming: 1000G.CHN.chrN.phased.vcf.gz plus .tbi or .csi index

Extract:
  tar -xzf CHN_ref_1000G_CHN_359_GRCh38_phased.tar.gz

Verify:
  cd CHN_ref
  md5sum -c CHN_ref.md5
