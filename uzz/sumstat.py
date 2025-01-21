
import os
import dask.dataframe as df
import pandas as pd

result_prefix='result'
root_path='/home/yuninze/res/work'
feature_path='/home/yuninze/res/work/phenotype/phenotype-zscore.csv.tsv'

phenotype='ad'
p_threshold=1e-0

plink_rerun=True

if plink_rerun:
  print(f'...Attempting to rerun plink2 for {phenotype}')
  os.system(f'''
  plink2 --bfile '{root_path}/kchip_120' \
    --linear \
    --pheno '{feature_path}' --pheno-name {phenotype} --1 \
    --covar '{feature_path}' --covar-name sex age \
    --out '{os.path.join(root_path,result_prefix)}'
  ''')

linear_column_dtype={
  '#CHROM': 'u4',
  'POS': 'u4',
  'ID': 'object',
  'REF': 'object',
  'ALT': 'object',
  'PROVISIONAL_REF?': 'object',
  'A1': 'object',
  'OMITTED': 'object',
  'A1_FREQ': 'f4',
  'TEST': 'object',
  'OBS_CT': 'u4',
  'BETA': 'f4',
  'SE': 'f4',
  'T_STAT': 'f4',
  'P': 'f4',
  'ERRCODE': 'object'
}

logit_column_dtype={
  '#CHROM': 'object',
  'POS': 'u4',
  'ID': 'object',
  'REF': 'object',
  'ALT': 'object',
  'PROVISIONAL_REF?': 'object',
  'A1': 'object',
  'OMITTED': 'object',
  'A1_FREQ': 'f4',
  'FIRTH?': 'object',
  'TEST': 'object',
  'OBS_CT': 'object',
  'OR': 'f4',
  'LOG(OR)_SE': 'f4',
  'Z_STAT': 'f4',
  'P': 'f4',
  'ERRCODE': 'object'
}

gene=df.read_csv(
  os.path.join(
    root_path,
    f'{result_prefix}.{phenotype}.glm.linear'
  ),
  sep='\t',
  dtype=linear_column_dtype
)

gene_info=gene.loc[gene.ERRCODE=='.']

gene_info_sign=gene_info.loc[gene_info.P <= p_threshold]

gene_info_additive=gene_info_sign.loc[gene_info_sign.TEST=='ADD']

gene_info_neat=gene_info_additive.drop(
  ['PROVISIONAL_REF?','ERRCODE'],
  axis=1
)

out_filename=os.path.join(
  root_path,
  f'{phenotype}-glm-linear-{p_threshold}.feather'
)

gene_info_neat.compute().pipe(
  pd.DataFrame.reset_index,
  drop=True
).pipe(
  pd.DataFrame.to_feather,
  path=out_filename,
  compression='zstd',
  compression_level=9
)

print(f'...{out_filename}')
