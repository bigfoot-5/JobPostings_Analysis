from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount

from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator

from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

# build a docker image for running the web scraper


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# converts data from postgres database to excel spreadsheet
def db_to_excel():
    source_config = {
    'dbname' : 'source_db',
    'user' : 'postgres',
    'password': 'secret',
    'host': 'source_postgres',
    'port': '5433'
    }
    subprocess_env = dict(PGPASSWORD=source_config['password'])
    sql = "\COPY (select * from jobs_master) TO '/opt/airflow/elt_script/master.csv' DELIMITER ',' CSV HEADER;"
    remove_jobs= "delete from jobs;"
    for command in [sql, remove_jobs]:
        parser = [
        'psql',
        '-U', source_config['user'],
        '-h', source_config['host'],
        '-d', source_config['dbname'],
        '-c',
        command
        ]

    subprocess.run(parser, env=subprocess_env, check=True)

# dags for ETL process
dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='An ELT workflow with dbt',
    schedule_interval='0 12 * * *',
    start_date=datetime(2024, 5, 19),
    catchup=False,
)

t1 = DockerOperator(
    task_id='scraping_task',
    image='scraper',
    api_version='auto',
    auto_remove=False,
    command="python /opt/airflow/elt_script/scraper.py",
    docker_url='unix://var/run/docker.sock',
    network_mode='container:airflow-source_postgres-1',
    mounts=[Mount(source='/Users/karthiktalluri/Desktop/uk/Career/Liverpool/Projects/Airflow/elt_script',
                  target= '/opt/airflow/elt_script', type='bind')],
    mount_tmp_dir = False,
    dag=dag,
)
t2 = DockerOperator(
    task_id='dbt_run',
    image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
    command=[
        "run",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt",
    ],
    auto_remove=False,
    docker_url="unix://var/run/docker.sock",
    network_mode="container:airflow-source_postgres-1",
    mounts=[
        Mount(source='/Users/karthiktalluri/Desktop/uk/Career/Liverpool/Projects/Airflow/scraper',
              target='/dbt', type='bind'),
        Mount(source='/Users/karthiktalluri/.dbt', target='/root', type='bind'),
    ],
    dag=dag
)
t3 = PythonOperator(
    task_id='to_excel',
    python_callable=db_to_excel,
    dag=dag,
)

t1 >> t2 >> t3