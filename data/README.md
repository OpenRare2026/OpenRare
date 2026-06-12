# PharmGKB / ClinPGx local data

Place the ClinPGx download under this directory:

```
data/pharmGKB/
├── PrimaryData/
│   └── genes.zip
└── AnnotationData/
    ├── summaryAnnotations.zip
    ├── guidelineAnnotations.json.zip
    └── pathways-tsv.zip
```

Download from [ClinPGx Downloads](https://www.clinpgx.org/downloads) or copy an existing tree.  
Set `PHARMGKB_DATA_DIR=./data/pharmGKB` in `.env` (default).

This folder is gitignored because the zips are large.
