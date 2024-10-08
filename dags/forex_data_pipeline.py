import datetime as dt
import json

import pandas as pd
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook

# default arguments for the dag, this are applied to the TASK
DEFAULT_ARG = {
    "owner": "felipehdez",
    "email_on_failure": True,
    "email_on_retry": False,
    "email": "juanfelipehdezm@gmail.com",
    "retries": 2,
    # minutes to wait before retrying
    "retry_delay": dt.timedelta(minutes=1),
    "email_on_failure": True,
    "email_on_retry": False
}


def download_rates():
    """
    It downloads the json file from the url and writes it to a file
    """

    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=COP&apikey=EHCCX9LJ1T4XQV4E'
    r = requests.get(url)
    data = json.loads(r.text)["Realtime Currency Exchange Rate"]
    # as we are using docker we must provide the path like this
    with open("/opt/airflow/dags/files/rates.json", "w") as outfile:
        j = json.dumps(data, indent=4)
        outfile.write(j)


def processing_json_file():
    """
    It reads a json file, converts it to a dataframe, renames the columns, and then sends it to a csv
    file.
    """

    with open("/opt/airflow/dags/files/rates.json", "r") as file:
        data = json.load(file)
        proper_data = {k: v.split(",") for k, v in data.items()}

        df_rates = pd.DataFrame(proper_data)
        df_rates = df_rates.iloc[:, :7]
        df_rates.rename(columns={"1. From_Currency Code": "From_Currency_Code",
                                 "2. From_Currency Name": "From_Currency_Name",
                                 "3. To_Currency Code": "To_Currency_Code",
                                 "4. To_Currency Name": "To_Currency_Name",
                                 "5. Exchange Rate": "Exchange_Rate",
                                 "6. Last Refreshed": "Last_Refreshed",
                                 "7. Time Zone": "Time_Zone"}, inplace=True)
        # sending the data to the CS, it will APPEND the new data
        df_rates.to_csv("/opt/airflow/dags/files/rates.csv",
                        header=False, index=False, mode="a")


def store_ratings():
    """
    It copies the contents of the file /opt/airflow/dags/files/rates.csv into the table forex_ratings
    """
    hook = PostgresHook(postgres_conn_id="forex_db")
    hook.copy_expert(
        sql="COPY forex_ratings FROM stdin WITH DELIMITER AS ','",
        filename="/opt/airflow/dags/files/rates.csv"
    )

    # iniating the dag object
with DAG("forex_data_pipeline", start_date=dt.datetime(2022, 11, 7),
        schedule="@daily", default_args=DEFAULT_ARG, catchup=False,
        dagrun_timeout=dt.timedelta(minutes=5)) as dag:

    """
    ###forex_data_pipeline
    This dag will read an API, tranform the data and load the data into a SQL database.
    The info is the exchange currency between COP and USA
    """

    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        # this connection is created on arflow UI
        http_conn_id="forex_api",
        endpoint="/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=COP&apikey=EHCCX9LJ1T4XQV4E",
        response_check=lambda response: "Rate" in response.text,
        # frecuency in which the sensor check if the condition is match (in these case 5 segs)
        poke_interval=5,
        # after 20 segs or running the record it will stop checking
        timeout=20
    )

    downloading_rates = PythonOperator(
        task_id="downloading_rates",
        python_callable=download_rates
    )

    is_forex_rates_file_available = FileSensor(
        task_id="is_forex_rates_file_available",
        # on airflow UI we create the path where to look for the file
        fs_conn_id="forex_path",
        filepath="rates.json",
        poke_interval=5,
        timeout=20
    )

# Creating a table in the database.
    create_forexRates_database = PostgresOperator(
        task_id="create_forexRates_database",
        postgres_conn_id="forex_db",
        sql="""

            DROP TABLE IF EXISTS forex_ratings;

            CREATE TABLE IF NOT EXISTS forex_ratings (
                From_Currency_Code TEXT NOT NULL,
                From_Currency_Name TEXT NOT NULL,
                To_Currency_Code TEXT NOT NULL,
                To_Currency_Name TEXT NOT NULL,
                Exchange_Rate NUMERIC(6,2),
                Last_Refreshed TIMESTAMP NOT NULL,
                Time_Zone TEXT NOT NULL
            );
        """,
        queue="high_cpu"

    )

    process_json_file = PythonOperator(
        task_id="process_json_file",
        python_callable=processing_json_file
    )

    store_ratings = PythonOperator(
        task_id="store_ratings",
        python_callable=store_ratings
    )

    # DEPENDENCIES
    is_forex_rates_available >> downloading_rates >> is_forex_rates_file_available >> process_json_file >> store_ratings

    create_forexRates_database >> store_ratings
