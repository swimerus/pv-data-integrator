from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.decorators import task, dag
from airflow.utils.task_group import TaskGroup

from datetime import datetime, timedelta
import json
import os

from modules.energa.scrapper import Scrapper
from modules.energa.file_processor import FileProcessor

from modules.db.model import EnergaData, PvSource
from modules.db.controller import Controller

from modules.utils import util


def _day_processable_branch_func(**kwargs):
    ti = kwargs['ti']
    from_date = ti.xcom_pull(task_ids='get_next_date')
    print(f'from_date={from_date}')
    to_date = ti.xcom_pull(task_ids='get_last_date')
    print(f'to_date={to_date}')

    if from_date < to_date:
        return 'scrapping_tasks.scrape_energa'
    else:
        return 'skip_task'


def _scraped_data_valid_branch_func(**kwargs):
    ti = kwargs['ti']
    is_data_valid = ti.xcom_pull(
        task_ids='scrapping_tasks.validate_scraped_data')
    print(f'is_data_valid={is_data_valid}')

    if is_data_valid:
        return 'scrapping_tasks.processing_data_tasks.transform_excel_to_json'
    else:
        return 'scrapping_tasks.cleanup'


def _delete_org_files():
    path = f'{util.get_config_param("file_dir")}/energa/org_files'
    files = os.listdir(path)
    files = util.filter_files_by_extension(files=files, extension='xls')
    for file in files:
        os.remove(f'{path}/{file}')


@dag(
    dag_id='pv_energa_pipeline',
    start_date=datetime(2022, 5, 28),
    schedule_interval=None
)
def task_flow():

    start_task = EmptyOperator(
        task_id='start'
    )

    @task
    def get_next_date():
        db_ctrl = Controller(data_list=[EnergaData()])
        date = db_ctrl.get_last_process_date()
        return date.strftime('%Y-%m-%d')

    @task
    def get_last_date():
        to_date = datetime.now()-timedelta(days=4)
        return to_date.strftime('%Y-%m-%d')

    @task
    def scrape_energa(**kwargs):
        ti = kwargs['ti']
        from_date = ti.xcom_pull(task_ids='get_next_date')
        print(f'from_date={from_date}')
        to_date = ti.xcom_pull(task_ids='get_last_date')
        print(f'to_date={to_date}')

        scrapper = Scrapper()
        scrapper.scrape_summary()
        scrapper.scrape_details(from_date=from_date, to_date=to_date)

    @task
    def transform_excel_to_json():
        fp = FileProcessor()
        fp.transform_to_json()

    @task
    def find_files_to_proceed():
        path = f'{util.get_config_param("file_dir")}/energa'
        files = os.listdir(path)
        files = util.filter_files_by_extension(files=files, extension='json')

        return [file for file in files if file != 'summary.json']

    @task
    def move_proceeded_files_to_archive(**kwargs):
        ti = kwargs['ti']
        filenames = ti.xcom_pull(
            task_ids='scrapping_tasks.processing_data_tasks.find_files_to_proceed')
        print(f'filenames={filenames}')

        path = f'{util.get_config_param("file_dir")}/energa'
        archive_path = f'{path}/archive'

        for filename in filenames:
            os.replace(f'{path}/{filename}', f'{archive_path}/{filename}')

    @task
    def insert_data_to_db(**kwargs):
        ti = kwargs['ti']
        filenames = ti.xcom_pull(
            task_ids='scrapping_tasks.processing_data_tasks.find_files_to_proceed')
        print(f'filenames={filenames}')

        path = f'{util.get_config_param("file_dir")}/energa'
        for filename in filenames:
            with open(f'{path}/{filename}', 'r') as file:
                t = file.readlines()
                data = json.loads(t[0])

                pv_source = PvSource(
                    source=data['source'], collect_time=util.timestamp_to_time(data['scrape_time']))
                energy_type = data['energy_type']

                energa_data_list = []
                for d in data['data']:
                    energa_data = EnergaData(time=d['collectTime'], energy_type=energy_type,
                                             zone_1=d['Strefa 1 [kWh]'], zone_2=d['Strefa 2 [kWh]'], zone_3=d['Strefa 3 [kWh]'])
                    energa_data_list.append(energa_data)

                db_ctrl = Controller(pv_source=pv_source,
                                     data_list=energa_data_list)
                db_ctrl.save()

    @task
    def delete_org_files():
        _delete_org_files()

    @task
    def validate_scraped_data(**kwargs):
        path = f'{util.get_config_param("file_dir")}/energa/org_files'
        files = os.listdir(path)
        files = list(util.filter_files_by_extension(
            files=files, extension='xls'))

        if len(files) % 2 != 0 or len(files) == 0:
            return False

        return True

    @task
    def cleanup():
        _delete_org_files()

    is_next_day_processable = BranchPythonOperator(
        task_id='is_next_day_processable',
        provide_context=True,
        trigger_rule='all_success',
        python_callable=_day_processable_branch_func)

    skip_task = EmptyOperator(
        task_id='skip_task'
    )

    end_task = EmptyOperator(
        task_id='end',
        trigger_rule='none_failed_or_skipped'
    )

    with TaskGroup(group_id='scrapping_tasks') as scrapping_tasks:

        is_scraped_data_valid = BranchPythonOperator(
            task_id='is_scraped_data_valid',
            provide_context=True,
            python_callable=_scraped_data_valid_branch_func)

        with TaskGroup(group_id='processing_data_tasks') as processing_data_tasks:
            transform_excel_to_json() >> find_files_to_proceed() >> insert_data_to_db(
            ) >> move_proceeded_files_to_archive() >> delete_org_files()

        scrape_energa() >> validate_scraped_data() >> is_scraped_data_valid >> [
            processing_data_tasks, cleanup()]

    start_task >> [get_next_date(), get_last_date()] >> is_next_day_processable >> [
        scrapping_tasks, skip_task] >> end_task


dag = task_flow()
