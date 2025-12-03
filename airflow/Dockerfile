FROM apache/airflow:3.0.6-python3.12

USER airflow
COPY ./airflow/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ../pyproject.toml /opt/airflow/pyproject.toml
COPY ../uv.lock /opt/airflow/uv.lock
WORKDIR /opt/airflow
RUN uv sync
