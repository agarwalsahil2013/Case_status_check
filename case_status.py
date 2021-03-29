from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import os
# from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client
#import pandas as pd
#from waitress import serve

account_sid = 'AC43f4b6512603af5076e79d030fcaf815' 
auth_token = 'd74f8fa60f804f609d9bcac3c407b04d' 
client = Client(account_sid, auth_token) 

url = "https://egov.uscis.gov/casestatus/landing.do"

options = Options()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
chrome_browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=options)

# chrome_browser = webdriver.Chrome('./chromedriver')
# chrome_browser.get(url)

def case_status_check(receipt_number,phone_num):
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

	# df = pd.read_csv('database.csv')
	# df['phone_number'] = df['phone_number'].astype(str)
	# phone_num = phone_num[1:]

	# if phone_num not in set(df['phone_number']): 
	# 	validation_request = client.validation_requests \
	#                            .create(
	#                                 friendly_name=receipt_number,
	#                                 phone_number=phone_num
	#                             )

	if update_case == "Case Was Received":
		message = client.messages.create(  
                              messaging_service_sid='MG9f8f8674445c2faab902051a9604ea65', 
                              body = f"Your case status is same as '{update_case}'",      
                              to=phone_num 
                          )
		return "Message sent successfully...."
	else:
		message = client.messages.create(  
                              messaging_service_sid='MG9f8f8674445c2faab902051a9604ea65', 
                              body = f"HURRAY!! \nCongratulations, your case status has changed to '{update_case}'",      
                              to=phone_num 
                          )
		return "Message sent successfully......."



