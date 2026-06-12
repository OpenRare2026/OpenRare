curl -s -X POST http://172.27.206.112:7003/runs \
  -F file=@/mnt/workspace/xlw/phenotype_score/v3/test.P002.csv \
  -F hpo_file=@/mnt/workspace/xlw/phenotype_score/v3/hpo_Hackcase002.txt \
  -F hgvs=true
