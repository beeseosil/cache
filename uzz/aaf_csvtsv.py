# Airflow

from airflow.models.dag import DAG
from airflow.datasets import Dataset
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

from time import time
from os import path

with DAG(
  dag_id='csv2tsv',
  description='A csv2tsv parser',
  params=dict(
    file_path=Param(
      default='/home/yuninze/res/work',
      type='string',
      title='file_path',
      minLength=1,
      description='A file_path would be a base_path for the parser.'
    ),
    is_dirty=Param(
      default=True,
      type='boolean',
      title='is_dirty',
      description='Is dirty?'
    )
  ),
  default_args=dict(),
  tags=['mine']
) as dag:

  params=dag.params

  def get_params():
    if ~(params['file_path'].endswith('.csv')):
      raise ValueError('File Extension is unlikely csv')

    params['infile']=Dataset(params['file_path'], extra=dict(is_raw=True))
    infile_uris=path.split(params['infile'].uri)
    params['outfile']=Dataset(
      path.join(infile_uris[0], str(int(time())) + '-' + infile_uris[-1] + '.tsv'),
      extra=dict(is_raw=True)
    )

  def parse():
    # with open(infile,encoding="utf-8") as csvfile, open(outfile,newline="\n",encoding="utf-8",mode="w") as tsvfile:
    #   tsvfile_data=[]
    #   for line in csvfile:
    #     truncated_line=line.replace(",","\t").replace(" ","-")
    #     tsvfile_data.append(truncated_line)
        
    #   for line in tsvfile_data:
    #     if tsvfile_data.index(line)==0:
    #       line="\t".join([f"{q}" for q in line.split("\t")])
    #     tsvfile.write(line)
    
    return print(params['infile'].uri,'>>',params['outfile'].uri)

  q=PythonOperator(task_id='csv2tsv', python_callable=parse)
  w=BashOperator(task_id='revert', bash_command=f'echo ####')
  e=EmptyOperator(task_id='placeholder')
  
  q >> w >> e
