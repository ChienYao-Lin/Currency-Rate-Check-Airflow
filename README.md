# Currency Rate Check with Airflow
This is a simple airflow app that remind me the currency rate (TWD/AUD) with email. The rate will be recorded in local postgresSQL database.


## Deployment
### Deploy with conda
> Install PostgreSQL and create database and new user
```bash
brew install postgresql
brew services start postgresql
psql postgres
CREATE ROLE new_user WITH LOGIN PASSWORD 'pwd';
CREATE DATABASE airflow_db;
\q
psql -d airflow_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO new_user;
\q
```
> Install pgAdmin to manipulate our database
```bash
brew install --cask pgadmin4
```
> Connect your local database with pgAdmin
1. Right-click on ‘Servers’ and select Create => Server
2. Give it an easy name in general tab
3. Fill the other settings as the following image
![](https://github.com/ChienYao-Lin/currency_rate_check_airflow/blob/main/images/pgAdmin_sever_setting.png)

> Create new table to store the currency rate with pgAdmin Query Tool
```bash
CREATE TABLE audtotwd(
	id SERIAL,
	price REAL,
	datetime DATE,
	PRIMARY KEY (id)
	);
```
![](https://github.com/ChienYao-Lin/currency_rate_check_airflow/blob/main/images/pgAdmin_query_tool.png)

> Create Environment
```bash
conda create -n airflow python=3.9
conda activate airflow
```

> Install postgresSQL package for python
```bash
pip install psycopg2
```

> Install crawler package 
```bash
pip install bs4
```

> Follow Apache Airflow [Quick Start](https://airflow.apache.org/docs/apache-airflow/stable/start/local.html)) to install Airflow
```bash
export AIRFLOW_HOME=~/airflow
AIRFLOW_VERSION=2.2.3
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

> Configure airflow setting
```bash
vim ~/airflow/airflow.cfg
```

```bash
......

sql_alchemy_conn = postgresql+psycopg2://newuser:pwd@localhost:5432/airflow_db

......

load_examples = False

......

[smtp]

# If you want airflow to send emails on retries, failure, and you want to use
# the airflow.utils.email.send_email_smtp function, you have to configure an
# smtp server here
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
# Example: smtp_user = airflow
smtp_user = airflow
# Example: smtp_password = airflow
smtp_password = airflow
smtp_port = 25
smtp_mail_from = airflow@gmail.com
smtp_timeout = 30
smtp_retry_limit = 5

```

> Gmail setting
1. Before using Airflow to access your google email, we will need to turn on "Allow Less Secure Apps"
(https://myaccount.google.com/lesssecureapps)
2. Check that IMAP Access is also turned on in your GMAIL settings
(https://support.google.com/mail/answer/7126229)

> DAG configuration

There are also some variables you can set in ~/dags/audtwd.py
```bash
# set the currency rate
target_rate = 20
# set the local time zone
tz = "Australia/Melbourne"
# send notification to this email
to_email = "your_email"
# email messages
email_messages = """ <a href="https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/exchange-rate-chart?Currency=AUD/TWD">E.SUN BANK</a> """
```

> Start Deploy
```bash
airflow db init
airflow users create \
    --username admin \
    --firstname Chienyao \
    --lastname Lin \
    --role Admin \
    --email email@gmail.com

airflow webserver --port 8080

airflow scheduler
```

















