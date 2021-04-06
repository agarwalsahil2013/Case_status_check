# Importing libraries
import psycopg2
from case_status import case_status_check
#from apscheduler.schedulers.blocking import BlockingScheduler

# Use to switch between localhost and heroku server
ENV = "prod"

if ENV == "dev":
	con = psycopg2.connect(database="OPT_Case_Database", user="postgres", password="18jan1995", host='localhost')
else:
	con = psycopg2.connect(database="der9vn9qndvuda", user="eyhavmcpguroqq", password="ed96c37ad6bc86ddd10e9f8fc8cc05e580382b887e342c319790d933f4b6ac76", host='ec2-52-7-115-250.compute-1.amazonaws.com', port=5432)

# Extracting data from postgresql database
cur = con.cursor()
cur.execute("SELECT receipt_number,country_code,phone_number, datetime from FEEDBACK")
rows = cur.fetchall()

def some_job():
	"""
	Check's each receipt and phone number present in the database and
	sends a notification on their phone number.
	"""
	for row in rows:
		receipt_number = row[0]
		phone_number = row[2]
		return case_status_check(receipt_number, phone_number)

some_job()
con.close()
# Scheduling the task on localhost machine.
# scheduler = BlockingScheduler()
# scheduler.add_job(some_job, 'cron', day_of_week = 'mon-fri', hour=10)
#scheduler.add_job(some_job, 'interval', seconds=15)
#scheduler.start()

