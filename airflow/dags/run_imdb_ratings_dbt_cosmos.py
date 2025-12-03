import os
from datetime import datetime

from cosmos import ProjectConfig, ProfileConfig, ExecutionConfig, DbtDag

DBT_PROJECT_PATH = "/opt/airflow/dbt/imdb_ratings"
DBT_EXECUTABLE_PATH = "/opt/airflow/.venv/bin/dbt"

DAG_ARGS = {
    "schedule": None,
    "tags": ['imdb', 'ratings', 'dataset', 'transform', 'dbt'],
    "default_args": {
        "owner": "KehlRafael",
        "start_date": datetime(2023, 1, 1),
        "depends_on_past": False,
    },
    "catchup": False,
    "max_active_runs": 1,
    "render_template_as_native_obj": True
}

project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH
)
profile_config = ProfileConfig(
    profile_name="imdb_ratings",
    target_name="dev",
    profiles_yml_filepath=os.path.join(DBT_PROJECT_PATH, "profiles.yml")
)
execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXECUTABLE_PATH
)

dbt_dag = DbtDag(
    dag_id="run_imdb_ratings_dbt_cosmos",
    project_config=project_config,
    profile_config=profile_config,
    execution_config=execution_config,
    **DAG_ARGS
)
