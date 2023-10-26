from airflow.models import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

from sqlalchemy import create_engine
from datetime import datetime
from os import path, getenv, remove
import logging
import gzip
import requests

DAG_ARGS = {
    "schedule_interval": None,
    "tags": ['imdb', 'ratings', 'dataset', 'extract', 'load'],
    "default_args": {
        "owner": "KehlRafael",
        "start_date": datetime(year=2023, month=1, day=1, hour=0, minute=0),
        "depends_on_past": False,
    },
    "params": {
        "rewrite_files": Param(default=False, type="boolean"),
        "db_conn_var": Param(default='AIRFLOW__CORE__SQL_ALCHEMY_CONN', type="string")
    },
    "catchup": False,
    "max_active_runs": 1,
    "render_template_as_native_obj": True
}

# Mounted in the `docker-compse.yml` file
DATA_FOLDER = "/opt/airflow/data"
SQL_FOLDER = "/opt/airflow/sql"

logger = logging.getLogger('airflow.task')


def remove_suffix(string:str, suffix:str):
    """Simple function to remove a suffix from a string"""
    if string.endswith(suffix):
        return string[:-len(suffix)]
    return string


def unzip_dataset(zipped_file:str, unzipped_file:str, chunk_size:int=8192):
    """Unzips a gzip file to the `unzipped_file` path"""
    with gzip.open(zipped_file, 'rb') as zipped, open(unzipped_file, 'wb') as unzipped:
        while True:
            block = zipped.read(chunk_size)
            if not block:
                break
            else:
                unzipped.write(block)


def download_datasets(rewrite_files:bool=False):
    """Downloads and unzips dataset to the `DATA_FOLDER` if they were not already"""
    datasets_url = [
        "https://datasets.imdbws.com/title.basics.tsv.gz",
        "https://datasets.imdbws.com/title.episode.tsv.gz",
        "https://datasets.imdbws.com/title.ratings.tsv.gz"
    ]
    for url in datasets_url:
        zipped_file = f"{DATA_FOLDER}/{url.split('/')[-1]}"
        unzipped_file = remove_suffix(f"{DATA_FOLDER}/{url.split('/')[-1]}", '.gz')
        if not rewrite_files and path.exists(unzipped_file):
            logger.info(f'Dataset "{unzipped_file}" already downloaded and will not be rewritten.')
        else:
            logger.info(f'Downloading dataset from "{url}"...')
            # Download as stream to not use too much RAM
            with requests.get(url, stream=True) as r:
                with open(zipped_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
            logger.info('Download successful, unzipping dataset...')
            unzip_dataset(zipped_file,unzipped_file)
            logger.info('Removing compressed dataset...')
            remove(zipped_file)


def clean_sql_command(command:str):
    """Simple function to avoid common issues when reading SQL files to execute"""
    if len(command.replace("\n", "")) == 0:
        return ""
    clean_command = command.replace("%", "%%")
    return clean_command


def run_sql_file(filepath:str, connection_var:str, split_char:str=';'):
    """Reads a file and executes it in a single transaction using the given connection string"""
    connection_string = getenv(connection_var)
    logger.info(f'Reading file "{filepath}"...')
    with open(filepath, 'r') as file:
        sql_commands = file.read()
    sql_commands = sql_commands.split(split_char)

    logger.info("Connecting to given connection string and executing file...")
    engine = create_engine(connection_string)
    with engine.begin() as conn:
        for command in sql_commands:
            clean_command = clean_sql_command(command)
            if clean_command:
                conn.execute(clean_command)


with DAG('extract_and_load_datasets', **DAG_ARGS) as dag:
    begin = DummyOperator(
        task_id='begin'
    )

    download = PythonOperator(
        task_id='download_datasets',
        python_callable=download_datasets,
        op_kwargs={
            "rewrite_files": "{{ params.rewrite_files }}"
        }
    )

    setup = PythonOperator(
        task_id='setup_tables',
        python_callable=run_sql_file,
        op_kwargs={
            "filepath": f"{SQL_FOLDER}/setup_imdb_tables.sql",
            "connection_var": "{{ params.db_conn_var }}",
        }
    )

    ingest = PythonOperator(
        task_id='ingest_datasets',
        python_callable=run_sql_file,
        op_kwargs={
            "filepath": f"{SQL_FOLDER}/ingest_imdb_tables.sql",
            "connection_var": "{{ params.db_conn_var }}",
        }
    )

    end = DummyOperator(
        task_id='end'
    )

    begin >> [download, setup] >> ingest >> end
