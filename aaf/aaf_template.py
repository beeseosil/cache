# Scheduler, Webserver, MetadataDb, Executor, Worker (of DAGs)
## LocalExecutor, CeleryExecutor, KubernatesExcutor
## Tasks are stored as script file in designated directories

# Airflow

with Task(
    'taskname',
    default_args={},
    schedule='on_demand',
    start_date=pendulum.datetime(2025,1,1,tz='UTC')
) as task:
    def extract(**kwargs):
        pass
    
    def transform_q(**kwargs):
        pass

    def transform_w(**kwargs):
        pass

    extract_task=PythonOperater(task_id,Callable)
    transform_q_task=PythonOperater(task_id,Callable)
    transform_w_task=PythonOperater(task_id,Callable)
