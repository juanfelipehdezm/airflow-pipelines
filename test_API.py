import requests

url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=COP&apikey=EHCCX9LJ1T4XQV4E'
r = requests.get(url)
data = r.json()

print(data)
