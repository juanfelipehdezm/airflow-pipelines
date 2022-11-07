from airflow import DAG
import datetime as dt

# default arguments for the dag, this are applied to the TASK
DEFAULT_ARG = {
    "owner": "felipehdez",
    "email_on_failure": True,
    "email_on_retry:": False,
    "email": "juanfelipehdezm@gmail.com",
    "retries": 2,
    # minutes to wait before retrying
    "retry_delay": dt.timedelta(minutes=5)
}

# iniating the dag object
with DAG("forex_data_pipeline", start_date=dt.datetime(2022, 11, 7),
         schedule_interval="@daily", default_args=DEFAULT_ARG, catchup=False) as dag:

    print("hola")
