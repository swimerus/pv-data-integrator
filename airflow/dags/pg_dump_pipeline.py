from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.decorators import task, dag

from datetime import datetime

from modules.utils import util


@dag(
    dag_id='pv_db_dump_pipeline',
    start_date=datetime(2022, 5, 28),
    schedule_interval=None
)
def task_flow():

    def get_bash_command():
        username = util.get_config_param("postgresql_username")
        password = util.get_config_param("postgresql_password")
        db_name = util.get_config_param("postgresql_database")
        server = util.get_config_param("postgresql_server")
        port = util.get_config_param("postgresql_port")

        now = datetime.now().strftime("%Y%m%d%H%M%S")

        pg_dump_command = f'PGPASSWORD="{password}" pg_dump -c -O -U {username} -d {db_name} -h {server} -p {port} --disable-dollar-quoting > /var/lib/postgresql/dumps/dump_{now}.sql'
        return pg_dump_command

    db_dump = BashOperator(
        task_id='db_dump',
        bash_command=get_bash_command()
    )

    db_dump


dag = task_flow()
