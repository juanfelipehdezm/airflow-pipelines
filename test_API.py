import requests
import json

url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=COP&apikey=EHCCX9LJ1T4XQV4E'
r = requests.get(url)
data = json.loads(r.text)["Realtime Currency Exchange Rate"]
# print(data)

with open("rates2.json", "w") as outfile:
    j = json.dumps(data, indent=4)
    outfile.write(j)
