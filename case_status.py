# Importing libraries
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import os
from twilio.rest import Client
#import pandas as pd
#from waitress import serve
# from webdriver_manager.chrome import ChromeDriverManager

# Twilio authentication
account_sid = 'YOUR TWILIO SID' 
auth_token = 'YOUR TWILIO TOKEN NUMBER' 
client = Client(account_sid, auth_token) 

# USCIS case status check url
url = "https://egov.uscis.gov/casestatus/landing.do"

# Chrome browser configurations
options = Options()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
chrome_browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=options)
#chrome_browser = webdriver.Chrome('./chromedriver', options=options)
chrome_browser.get(url)


def case_status_check(receipt_number,phone_num):
	"""
	This code receives user's receipt and phone number to find the status
	of their application and sends an instant notification on their number.
	"""
	chrome_browser.get(url)
	case_num = chrome_browser.find_element_by_xpath('//input[@type="text"]')
	submit_button = chrome_browser.find_element_by_xpath('//input[@type="submit"]') 
	case_num.clear()
	case_num.send_keys(receipt_number)
	time.sleep(2)

	submit_button.click()
	time.sleep(2)

	case_status = chrome_browser.find_element_by_xpath('//div[@class="rows text-center"]/h1')
	update_case = case_status.text

	# Register user's number on Twilio
	# if phone_num not in set(df['phone_number']): 
	# 	validation_request = client.validation_requests \
	#                            .create(
	#                                 friendly_name=receipt_number,
	#                                 phone_number=phone_num
	#                             )

	if update_case == "Case Was Received":
		message = client.messages.create(  
                              messaging_service_sid='MG9f8f8674445c2faab902051a9604ea65', 
                              body = f"Your case number of {receipt_number} has same status as '{update_case}'",      
                              to=phone_num 
                          )
		return "Message sent successfully...."
	else:
		message = client.messages.create(  
                              messaging_service_sid='MG9f8f8674445c2faab902051a9604ea65', 
                              body = f"HURRAY!! \nCongratulations, your case number {receipt_number} has changed status to '{update_case}'",      
                              to=phone_num 
                          )
		return "Message sent successfully......."
