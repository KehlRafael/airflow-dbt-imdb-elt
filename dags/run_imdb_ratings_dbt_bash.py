from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator

from datetime import datetime

DAG_ARGS = {
    "schedule_interval": None,
    "tags": ['imdb', 'ratings', 'dataset', 'transform', 'dbt'],
    "default_args": {
        "owner": "KehlRafael",
        "start_date": datetime(year=2023, month=1, day=1, hour=0, minute=0),
        "depends_on_past": False,
    },
    "catchup": False,
    "max_active_runs": 1,
    "render_template_as_native_obj": True
}

# Mounted in the `docker-compse.yml` file
DBT_FOLDER = "/opt/airflow/dbt"
# Following AWS instructions on running dbt on MWAA
DBT_PROJECT = "imdb_ratings"
BASH_COMMAND = f"""cp -R {DBT_FOLDER} /tmp;\
cd /tmp/dbt/{DBT_PROJECT};\
dbt test --project-dir /tmp/dbt/{DBT_PROJECT}/ --profiles-dir .;\
dbt run --project-dir /tmp/dbt/{DBT_PROJECT}/ --profiles-dir .;\
cat /tmp/dbt/{DBT_PROJECT}/logs/dbt.log;
"""

with DAG(f'run_{DBT_PROJECT}_bash', **DAG_ARGS) as dag:
    begin = DummyOperator(
        task_id='begin'
    )

    run_dbt = BashOperator(
        task_id='run_dbt_project',
        bash_command=BASH_COMMAND
    )

    end = DummyOperator(
        task_id='end'
    )

    begin >> run_dbt >> end
