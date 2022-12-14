# Goal
Main goal of this project is to consolidate data from Fusion Solar inverter and mojlicznik.energa-operator.pl and insert them into PostgreSQL to create dashboard in Grafana and enable further analysis. 

# Technology
* Python 
* Docker
* Apache Airflow
* PostgreSQL
* Grafana

# Data Pipelines
There are 3 data pipelines:
* **pv_energa_pipeline** for gatering data from mojlicznik.energa-operator.pl by scrapping using Selenium
![pv_energa_pipeline](./images/pv_energa_pipeline.png)
* **pv_fs_pipeline for** gathering data from FusionSolar API
![pv_fs_pipeline](./images/pv_fs_pipeline.png)
* **pv_db_dump_pipeline** which only purpose is creating cyclic dump of database

# Grafana Dashboard
![grafa_dashboard](./images/grafana_dashboard.png)