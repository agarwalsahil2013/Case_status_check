import pandas as pd
from case_status import case_status_check
from apscheduler.schedulers.blocking import BlockingScheduler

def some_job():
	df = pd.read_csv('database.csv')
	for i in range(len(df['datetime'])):
		rn = df['receipt_number'][i]
		pn = df['phone_number'][i]
		return case_status_check(rn,pn)

scheduler = BlockingScheduler()
scheduler.add_job(some_job, 'cron', day_of_week = 'mon-fri', hour=10)
#scheduler.add_job(some_job, 'interval', seconds=15)
scheduler.start()
