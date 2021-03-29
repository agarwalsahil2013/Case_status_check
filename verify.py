from authy.api import AuthyApiClient
from flask import Flask, render_template, request, redirect, url_for, session, Response
from case_status import case_status_check
import csv
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'super-secret'

api = AuthyApiClient(app.config['AUTHY_API_KEY'])

def write_to_csv(data):
	with open('database.csv', newline='', mode = "a") as database:
		phone_number = data['phone_number']
		country_code = data['country_code']
		receipt_number = data['receipt_number']
		date_time = data['datetime']
		final_phone = "+"+country_code+phone_number
		csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		csv_writer.writerow([receipt_number, final_phone, date_time])

@app.route("/", methods=["GET", "POST"])
def phone_verification():
	if request.method == "POST":
		datab = pd.read_csv('database.csv')
		datab['phone_number'] = datab['phone_number'].astype(str)
		data = request.form.to_dict()
		receipt_number = request.form.get("receipt_number")
		country_code = request.form.get("country_code")
		phone_number = request.form.get("phone_number")
		method = request.form.get("method")

		session['receipt_number'] = receipt_number
		session['country_code'] = country_code
		session['phone_number'] = phone_number
		session['data'] = data

		final_ph_num = country_code+phone_number
		if final_ph_num in set(datab['phone_number']):
			return redirect(url_for("verified_user"))
		else:
			api.phones.verification_start(phone_number, country_code, via=method)
			return redirect(url_for("verify"))

	return render_template('phone_verification.html')

@app.route("/verified_user")
def verified_user():
	cn_code = session.get('country_code')
	ph_num = session.get("phone_number")
	rec_num = session.get('receipt_number')
	final_ph_no = "+"+cn_code+ph_num
	result = case_status_check(rec_num, final_ph_no)
	return Response(f"This <b>{final_ph_no}</b> number is already verified !!!<br/> We are sending your status on your registered phone number......<br/><b>{result}</b>")
	
@app.route("/verify", methods=["GET", "POST"])
def verify():
	if request.method == "POST":
		token = request.form.get("token")

		receipt_number = session.get("receipt_number")
		phone_number = session.get("phone_number")
		country_code = session.get("country_code")
		data = session.get("data")

		verification = api.phones.verification_check(phone_number, country_code, token)

		final_ph_no = "+"+country_code+phone_number
		output_message = case_status_check(receipt_number, final_ph_no)

		if verification.ok():
			now = datetime.now() # current date and time
			date_time = now.strftime("%d/%m/%Y, %H:%M")
			data['datetime'] = date_time

			write_to_csv(data)
			return	output_message

	return render_template("verify.html")

if __name__ == '__main__':
    app.run(debug=True)