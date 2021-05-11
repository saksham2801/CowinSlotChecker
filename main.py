import datetime as dt2
import json
import os
import smtplib
import ssl
import time
from datetime import datetime

import flask
import requests
from tabulate import tabulate

context = ssl.SSLContext()
context.load_cert_chain('cert.pem', 'key.pem')

message_all = {}


def send_alert(center_arr, session_arr):
    global message_all
    print("You'll Receive the Email soon!!")
    message = [['Center Address', 'Center id', 'Center name', 'Center pincode', 'Center lat', 'Center long', 'fee_type', \
                'date', 'available_capacity', 'min_age_limit', 'vaccine', 'slots']]
    subject = "Vaccine avalability alert @ "
    for i in range(len(center_arr)):
        center_id = str(center_arr[i]['center_id'])
        center_name = str(center_arr[i]['name'])
        center_add = str(center_arr[i]['address'])
        center_pincode = str(center_arr[i]['pincode'])
        if center_pincode == "244001":
            subject += "Moradabad"
        else:
            subject += "Bangalore - " + center_pincode
        center_lat = str(center_arr[i]['lat'])
        center_long = str(center_arr[i]['long'])
        fee_type = str(center_arr[i]['fee_type'])
        date = str(session_arr[i]['date'])
        available_capacity = str(session_arr[i]['available_capacity'])
        min_age_limit = str(session_arr[i]['min_age_limit'])
        vaccine = str(session_arr[i]['vaccine'])
        slots = "   <----->   ".join(session_arr[i]['slots'])
        temp_msg = [center_add, center_id, center_name, center_pincode, center_lat, center_long, fee_type, date,
                    available_capacity, min_age_limit, vaccine, slots]
        message.append(temp_msg)

    message = str(tabulate(message))
    message = "Subject : {}\n\n{}".format(subject, message)
    print(message)
    if center_pincode in message_all and message_all[center_pincode] == message:
        print("Same Email will be sent")
        return
    message_all[center_pincode] = message
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "saksham2801@gmail.com"
    receiver_email = ["saksham.gfg@gmail.com", "kashmehrotra@gmail.com"]
    password = "vbvafngdyupigmgl"
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        print("Email Sent!!!")


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/")
def hello():
    return "Hello, World!"


def main():
    port = int(os.environ.get('PORT', 33507))
    app.run(ssl_context=context, port=port)
    pincode_to_age = {'560087': 18, '560037': 18, '560103': 18, '560035': 18, '244001': 45, '132103': 18}
    # pincode_to_age = {'244001': 45}
    # , '244901': 45
    available_capacity = 0
    num_of_days = 15
    while (True):
        for pin, age_limit in pincode_to_age.items():
            center_arr = []
            session_arr = []
            for i in range(num_of_days):
                d = (datetime.today() + dt2.timedelta(days=i)).strftime('%d-%m-%Y')
                url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=' + pin + '&date=' + d
                headers = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
                }
                print("Hitting the URL for " + str(i) + " times !!!")
                res = requests.get(url, headers=headers)
                try:
                    res_json = json.loads(res.text)
                    if 'centers' not in res_json:
                        continue
                    for center in res_json['centers']:
                        if 'sessions' not in center:
                            continue
                        for session in center['sessions']:
                            if 'min_age_limit' in session and int(session['min_age_limit']) == age_limit and \
                                    'available_capacity' in session and \
                                    int(session['available_capacity']) > available_capacity:
                                center_arr.append(center)
                                session_arr.append(session)
                    print(res_json)
                    # await asyncio.sleep(5)
                except:
                    print(res)
                time.sleep(5)
            print("Length of Response : ", len(center_arr))
            if len(center_arr) > 0:
                send_alert(center_arr, session_arr)
            else:
                print("No Slots found for next " + str(num_of_days) + " days")
        # await asyncio.sleep(20)
        time.sleep(20)


main()
# asyncio.run(main())
