import os
import psycopg2
import requests
import pendulum
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup

from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.dummy_operator import DummyOperator

# set the currency rate
target_rate = 20
# set the local time zone
tz = "Australia/Melbourne"
# send notification to this email
to_email = "your_email"
# email messages
email_messages = """ <a href="https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/exchange-rate-chart?Currency=AUD/TWD">E.SUN BANK</a> """


local_tz = pendulum.timezone(tz)
default_args = {
    'owner': 'Cylin',
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}


# crawl the website to get the currency rate
def check_rate_info(**context):
    # currency rate page
    curr_page = "https://www.investing.com/currencies/aud-twd"
    url = curr_page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    targets = soup.find("span", {'data-test': 'instrument-price-last'})
    rate_info = float(targets.text)

    return rate_info

# insert the current rate into database
def insert_data(**context):
    DSN = """host=localhost
             dbname=airflow_db
             user=new_user 
             password=pwd 
             port=5432"""
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            print("Saving latest currency rate (TWD/AUD)..")
            rate_info = context['task_instance'].xcom_pull(task_ids='check_rate_info')
            query = """INSERT INTO audtotwd
                       (price, datetime) 
                       VALUES (%s, %s)"""
            cur.execute(query, (rate_info, date.today()))


# Check if the rate is greater than the target value
def decide_what_to_do(target_rate, **context):
    rate_info = context['task_instance'].xcom_pull(task_ids='check_rate_info')

    if rate_info >= target_rate:
        return 'send_notification'
    else:
        return 'no_do_nothing'



# Build the DAG 
with DAG('currency_rate_check', 
         default_args=default_args,
         description='A simple DAG that check the rate TWD/AUD',
         schedule_interval='0 12 * * 1-5',
         start_date=datetime(2022, 1, 17, 0, 0, tzinfo=local_tz)
) as dag:

    # define tasks

    insert_data = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data,
        provide_context=True
    )

    check_rate_info = PythonOperator(
        task_id='check_rate_info',
        python_callable=check_rate_info,
        provide_context=True
    )

    decide_what_to_do = BranchPythonOperator(
        task_id='currency_rate_check',
        op_args=[target_rate],
        python_callable=decide_what_to_do,
        provide_context=True
    )

    send_notification = EmailOperator(
        task_id='send_notification',
        to=to_email,
        subject='rate over ' + str(target_rate),
        html_content=email_messages,
        dag=dag
    )

    do_nothing = DummyOperator(task_id='no_do_nothing')

    # Define workflow
    check_rate_info >> insert_data >> decide_what_to_do
    decide_what_to_do >> send_notification
    decide_what_to_do >> do_nothing

