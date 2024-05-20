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


def run_elt_script():
    script_path = "/opt/airflow/elt_script/scraper.py"
    result = subprocess.run(["python", script_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Script failed with error: {result.stderr}")
    else:
        print(result.stdout)


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
    auto_remove=True,
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
        "--full-refresh"
    ],
    auto_remove=True,
    docker_url="unix://var/run/docker.sock",
    network_mode="container:airflow-source_postgres-1",
    mounts=[
        Mount(source='/Users/karthiktalluri/Desktop/uk/Career/Liverpool/Projects/Airflow/scraper',
              target='/dbt', type='bind'),
        Mount(source='/Users/karthiktalluri/.dbt', target='/root', type='bind'),
    ],
    dag=dag
)

t1 >> t2