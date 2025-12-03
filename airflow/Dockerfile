FROM apache/airflow:3.0.6-python3.12

USER airflow
COPY ../pyproject.toml /opt/airflow/pyproject.toml
COPY ../uv.lock /opt/airflow/uv.lock
WORKDIR /opt/airflow
RUN uv sync
