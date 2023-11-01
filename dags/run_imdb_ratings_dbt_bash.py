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
RUN_COMMAND = f"""cp -R {DBT_FOLDER} /tmp;\
cd /tmp/dbt/{DBT_PROJECT};\
dbt run --project-dir /tmp/dbt/{DBT_PROJECT}/ --profiles-dir .;\
cat /tmp/dbt/{DBT_PROJECT}/logs/dbt.log;
"""
# We copy again to ensure the worker has the files.
# Important with multiple workers.
TEST_COMMAND = f"""cp -R {DBT_FOLDER} /tmp;\
cd /tmp/dbt/{DBT_PROJECT};\
dbt test --project-dir /tmp/dbt/{DBT_PROJECT}/ --profiles-dir .;\
cat /tmp/dbt/{DBT_PROJECT}/logs/dbt.log;
"""
# This command is copying the docs to the mounted path
# so we can run `dbt docs serve` locally. Ideally, we should
# upload these to S3 or a similar service, where we will then
# be able to host the static website.
DOCS_COMMAND = f"""cp -R {DBT_FOLDER} /tmp;\
cd /tmp/dbt/{DBT_PROJECT};\
dbt docs generate --project-dir /tmp/dbt/{DBT_PROJECT}/ --profiles-dir .;\
cp -R /tmp/dbt/imdb_ratings/target {DBT_FOLDER}/imdb_ratings;\
"""

with DAG(f'run_{DBT_PROJECT}_bash', **DAG_ARGS) as dag:
    begin = DummyOperator(
        task_id='begin'
    )

    run_dbt = BashOperator(
        task_id='run_dbt_project',
        bash_command=RUN_COMMAND
    )

    test_dbt = BashOperator(
        task_id='test_dbt_project',
        bash_command=TEST_COMMAND
    )

    generate_docs = BashOperator(
        task_id='generate_docs',
        bash_command=DOCS_COMMAND
    )

    end = DummyOperator(
        task_id='end'
    )

    begin >> run_dbt >> test_dbt >> generate_docs >> end
