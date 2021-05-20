from imessage_reader import fetch_data
import datetime
import cloudscraper
import requests
import json

class BOOK:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json", "Accept-Language": "hi_IN",'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'})
        self.s = cloudscraper.create_scraper(sess=self.session)

    def getOTP(self):
        fd = fetch_data.FetchData()
        messagesTuples = fd.get_messages()
        keys = ("from", "message", "date", "type")
        messages = [dict(zip(keys, values)) for values in messagesTuples]
        for item in messages:
            for k, v in item.items():
                if k == "date":
                    item[k] = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        messages.sort(key=lambda k : k['date'], reverse=True)
        return messages[0]["message"]

    def generateOTP(self, mobile):
        data = json.dumps({"mobile":mobile})
        res = self.s.post("https://cdn-api.co-vin.in/api/v2/auth/generateOTP", data=data)
        return res.json()

    def verifyOTP(self, txnId, OTP):
        data = json.dumps({"otp":OTP,"txnId":txnId})
        res = self.s.post("https://cdn-api.co-vin.in/api/v2/auth/confirmOTP", data=data)
        return res.json()['token']

    def checkAvailability(self, pincode, date):
        res = self.s.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}&vaccine=COVAXIN".format(pincode, date))
        return res.json()['centers']

    def getDate(self, numDays=1):
        return (datetime.datetime.now() + datetime.timedelta(days=numDays)).strftime("%d-%m-%Y")

    def main(self):
        date = self.getDate()
        centersFound = self.checkAvailability(201015, date)
        txnId = self.generateOTP(7042652557)
        print(txnId)
        OTP = self.getOTP()
        print(OTP)
        token = self.verifyOTP(txnId, OTP)
        print(token)




        """
        {
        "centers": [
            {
            "center_id": 1234,
            "name": "District General Hostpital",
            "name_l": "",
            "address": "45 M G Road",
            "address_l": "",
            "state_name": "Maharashtra",
            "state_name_l": "",
            "district_name": "Satara",
            "district_name_l": "",
            "block_name": "Jaoli",
            "block_name_l": "",
            "pincode": "413608",
            "lat": 28.7,
            "long": 77.1,
            "from": "09:00:00",
            "to": "18:00:00",
            "fee_type": "Free",
            "vaccine_fees": [
                {
                "vaccine": "COVISHIELD",
                "fee": "250"
                }
            ],
            "sessions": [
                {
                "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "date": "31-05-2021",
                "available_capacity": 50,
                "available_capacity_dose1": 25,
                "available_capacity_dose2": 25,
                "min_age_limit": 18,
                "vaccine": "COVISHIELD",
                "slots": [
                    "FORENOON",
                    "AFTERNOON"
                ]
                }
            ]
            }
        ]
        }
        """

b = BOOK()
b.main()