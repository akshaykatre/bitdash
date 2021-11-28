import json
import bitstamp
import bitstamp.client

details = open("login.json", "rb")
login = json.load(details)

trading_client = bitstamp.client.Trading(username=login['username'], key=login['api_key'], secret=login['secret_key'])

