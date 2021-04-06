# Importing libraries
from authy.api import AuthyApiClient
from flask import Flask, render_template, request, redirect, url_for, session, Response
from case_status import case_status_check
import pandas as pd
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Flask configuration
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'super-secret'

# Calling twilio authentication key
api = AuthyApiClient(app.config['AUTHY_API_KEY'])

# Use to switch between localhost and heroku server
ENV = 'prod'

if ENV == 'dev':
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:18jan1995@localhost/OPT_Case_Database'
else:
	app.debug = False
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://eyhavmcpguroqq:ed96c37ad6bc86ddd10e9f8fc8cc05e580382b887e342c319790d933f4b6ac76@ec2-52-7-115-250.compute-1.amazonaws.com:5432/der9vn9qndvuda'

# Ignore warnings related to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Declaring database
db = SQLAlchemy(app)

# Creating tables and columns
class Feedback(db.Model):
	__tablename__='feedback'
	receipt_number = db.Column(db.String(200), unique=True)
	country_code = db.Column(db.VARCHAR(5))
	phone_number = db.Column(db.Numeric(15), primary_key=True)
	datetime = db.Column(db.VARCHAR(25))

	def __init__(self,receipt_number, country_code, phone_number,datetime):
		self.receipt_number = receipt_number
		self.country_code = country_code
		self.phone_number = phone_number
		self.datetime = datetime			

# Home page
@app.route("/", methods=["GET", "POST"])
def phone_verification():
	"""
	Accepts user's receipt and phone number. Checks if it already exists or not.
	If not then request a verfication code to register for the service.
	"""
	if request.method == "POST":
		#data = request.form.to_dict()
		receipt_number = request.form.get("receipt_number")
		country_code = request.form.get("country_code")
		phone_number = request.form.get("phone_number")
		method = request.form.get("method")

		# Check whether user is new or existed
		if receipt_number == '' or phone_number == '':
			return render_template('phone_verification.html', message="Please fill out those fields")
		else:
		#datab = pd.read_csv('s3://case-number-database//database.csv')
		#datab['phone_number'] = datab['phone_number'].astype(str)

			session['receipt_number'] = receipt_number
			session['country_code'] = country_code
			session['phone_number'] = phone_number
			#session['data'] = data

			#final_ph_num = country_code+phone_number
			#if final_ph_num in set(datab['phone_number']):
			if db.session.query(Feedback).filter(Feedback.phone_number == phone_number).count() != 0:
				return redirect(url_for("verified_user"))
			else:
				api.phones.verification_start(phone_number, country_code, via=method)
				return redirect(url_for("verify"))

	return render_template('phone_verification.html')

# If user already exist in the database
@app.route("/verified_user")
def verified_user():
	"""
	If already exist in our database then send the instant notification to
	the registered phone number of case status.
	"""
	cn_code = session.get('country_code')
	ph_num = session.get("phone_number")
	rec_num = session.get('receipt_number')
	final_ph_no = "+"+cn_code+ph_num
	result = case_status_check(rec_num, final_ph_no)
	return render_template('result_verified_user.html', final_ph_no=final_ph_no, result=result) 
	
# If new user registered
@app.route("/verify", methods=["GET", "POST"])
def verify():
	"""
	Check whether user entered correct OTP or not. If yes, register
	that number with receipt number in the database.
	"""
	if request.method == "POST":
		token = request.form.get("token")

		receipt_number = session.get("receipt_number")
		phone_number = session.get("phone_number")
		country_code = session.get("country_code")
		#data = session.get("data")

		verification = api.phones.verification_check(phone_number, country_code, token)

		final_ph_no = "+"+country_code+phone_number

		# Check if the OTP entered correctly
		if verification.ok():
			output_message = case_status_check(receipt_number, final_ph_no)
			now = datetime.now() # current date and time
			date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
			#data['datetime'] = date_time

			data = Feedback(receipt_number, country_code, phone_number, date_time)
			db.session.add(data)
			db.session.commit()
			#write_to_csv(data)
			return	render_template('result_verify.html', final_ph_no=final_ph_no, output_message=output_message)
			
	return render_template("verify.html")

if __name__ == '__main__':
    app.run(debug=True)