# Scheduler, Webserver, MetadataDb, Executor, Worker (of DAGs)
## LocalExecutor, CeleryExecutor, KubernatesExcutor
## Tasks are stored as script file in designated directories

# Airflow


from airflow.models.dag import DAG
from airflow.decorators import task

from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from airflow.models.baseoperator import chain

import textwrap

with DAG(
    'taskname',
    description='',
    default_args={},
    schedule=timedelta(hours=1),
    start_date=pendulum.datetime(2025,1,1,tz='UTC'),
    tags=['test']
) as task:

    def task_placeholder():
        t0=EmptyOperator(
            task_id=0,
            task_display_name='Grouped Empty Task'
        )

        @task(task_display_name='A Placeholder Task')
        def task_in_task_placeholder():
            return
        
        task_placeholder >> task_in_task_placeholder()

    t1=BashOperator(
        task_id='t1',
        bash_command='cd /home/yuninze/res && ls -lah',
        retries=3
    )

    t2=BashOperator(
        task_id='t2',
        bash_command='sudo lsof -i -P -n',
        retries=0
    )

    t3=PythonOperator(
        task_id='t3',
        callable="print('x')",
        retries=0
    )

    t1.doc_md=textwrap.dedent('''
        #### Test

        -a

        ```sql
            select * from something order by id
        ```

        -qwer, asdf, zxcv
        
        [img](https://imgs.xkcd.com/comics/fixing_problems.png)
    ''')

    t1 >> [t2, t3]

    def extract(**kwargs):
        pass
    
    def transform_q(**kwargs):
        pass

    def transform_w(**kwargs):
        pass

    extract_task=PythonOperator(task_id,Callable)
    transform_q_task=PythonOperator(task_id,Callable)
    transform_w_task=PythonOperator(task_id,Callable)

    extraction_tasks=[
        e1,e2,e3
    ]
    chain(*extraction_tasks)

    transform_tasks=[
        t1,t2,t3
    ]
    chain(*transform_tasks)

    chain(extraction_tasks, transform_tasks)
