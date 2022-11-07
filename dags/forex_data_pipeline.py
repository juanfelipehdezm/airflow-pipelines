from airflow import DAG
import datetime as dt
from airflow.providers.http.sensors.http import HttpSensor

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

    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        # this connection is created on arflow UI
        http_conn_id="forex_api",
        endpoint="/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=COP&apikey=EHCCX9LJ1T4XQV4E",
        response_check=lambda response: "rates" in response.text,
        # frecuency in which the sensor check if the condition is match (in these case 5 segs)
        poke_interval=5,
        # after 20 segs or running the record it will stop checking
        timeout=20
    )
