from datetime import datetime, timedelta
import json
import os

from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.decorators import task, dag
from airflow.utils.task_group import TaskGroup

from modules.fusion_solar.data_retriever import DataRetriever

from modules.db.model import PvSource, FusionSolarData
from modules.db.controller import Controller
from modules.utils import util


def branch_func(**kwargs):
    ti = kwargs['ti']
    from_date = ti.xcom_pull(task_ids='get_next_date')
    print(f'from_date={from_date}')

    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    now = datetime.now()

    if from_date < now - timedelta(days=1):
        return 'data_collection_tasks.get_data_from_fusion_solar'
    else:
        return 'skip_task'


def insert_data_to_db(filename):

    if isinstance(filename, list):
        for file in filename:
            print(f'{file} in a loop')
            insert_data_to_db(file)
    else:
        print(f'inserting {filename}')
        with open(f'/opt/airflow/files/fusion_solar/{filename}', 'r') as file:
            t = file.readlines()
            data = json.loads(t[0])

            pv_source = PvSource(
                source=data['source'], collect_time=data['gatheringDate'], fs_station_code=data['stationCode'])

            fs_data_list = []
            for d in data['data']:
                fs = FusionSolarData(
                    time=d['collectTime'], inverter_power=d['inverterPower [kWh]'], power_profit=d['powerProfit [kWh]'])
                fs_data_list.append(fs)

            db_ctrl = Controller(pv_source=pv_source,
                                 data_list=fs_data_list)
            db_ctrl.save()


@dag(
    dag_id='pv_fs_pipeline',
    start_date=datetime(2022, 5, 28),
    schedule_interval=None
)
def task_flow():

    start_task = EmptyOperator(
        task_id='start'
    )

    @task
    def get_data_from_fusion_solar(**kwargs):
        ti = kwargs['ti']
        from_date = ti.xcom_pull(task_ids='get_next_date')
        print(f'from_date={from_date}')

        date_from = datetime.strptime(from_date, '%Y-%m-%d')

        dr = DataRetriever()
        filename = dr.get_station_kpi_hour_and_save(date_from)

        return filename

    @task
    def insert_fs_data(**kwargs):
        ti = kwargs['ti']
        filename = ti.xcom_pull(
            task_ids='data_collection_tasks.get_data_from_fusion_solar')
        print(f'filename={filename}')

        insert_data_to_db(filename)

    @task
    def get_next_date():
        db_ctrl = Controller(data_list=[FusionSolarData()])
        date = db_ctrl.get_last_process_date()+timedelta(days=1)
        return date.strftime('%Y-%m-%d')

    @task
    def find_files_to_proceed():
        path = f'{util.get_config_param("file_dir")}/fusion_solar'
        files = os.listdir(path)
        files = util.filter_files_by_extension(files=files, extension='json')

        return [file for file in files]

    @task
    def move_proceeded_files_to_archive(**kwargs):
        ti = kwargs['ti']
        filenames = ti.xcom_pull(
            task_ids='data_collection_tasks.find_files_to_proceed')
        print(f'filenames={filenames}')

        path = f'{util.get_config_param("file_dir")}/fusion_solar'
        archive_path = f'{path}/archive'

        for filename in filenames:
            os.replace(f'{path}/{filename}', f'{archive_path}/{filename}')

    @task
    def delete_org_files():
        path = f'{util.get_config_param("file_dir")}/fusion_solar/org_files'
        files = os.listdir(path)
        files = util.filter_files_by_extension(files=files, extension='json')
        for file in files:
            os.remove(f'{path}/{file}')

    is_next_day_processable = BranchPythonOperator(
        task_id='is_next_day_processable',
        provide_context=True,
        python_callable=branch_func)

    skip_task = EmptyOperator(
        task_id='skip_task'
    )

    end_task = EmptyOperator(
        task_id='end',
        trigger_rule='none_failed_or_skipped'
    )

    with TaskGroup(group_id='data_collection_tasks') as data_collection_tasks:
        get_data_from_fusion_solar() >> insert_fs_data() >> find_files_to_proceed(
        ) >> move_proceeded_files_to_archive() >> delete_org_files()

    start_task >> get_next_date() >> is_next_day_processable >> [
        data_collection_tasks, skip_task] >> end_task


dag = task_flow()
