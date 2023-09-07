import hmac
import hashlib
import json
import requests
import time
from threading import Thread
from luno_python.client import Client as cl
from binance.client import Client


class CryptoCom:
    BASE_URL = "https://api.crypto.com/v2/"

    def __init__(self):
        with open("keys.json")as keys:
            data = json.load(keys)
            self.API_KEY = data['crypto.com']["api_key"]
            self.SECRET_KEY = data['crypto.com']["secret_key"]

    def get_candlestick(self, instrument, period):
        data = requests.get(
            self.BASE_URL+"public/get-candlestick?instrument_name="+instrument+"&timeframe="+period)
        data = json.loads(data.text)
        return data['result']["data"][-1]

    def get_crypto_balance(self, currency):
        req = {
            "id": 11,
            "method": "private/get-account-summary",
            "api_key": self.API_KEY,
            "params": {
                "currency": currency,  # omit this to get all currencies
            },
            "nonce":  int(time.time() * 1000)
        }

        paramString = ""

        if "params" in req:
            for key in sorted(req['params']):
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = req['method'] + str(req['id']) + \
            req['api_key'] + paramString + \
            str(req['nonce'])

        req['sig'] = hmac.new(
            bytes(str(self.SECRET_KEY), 'utf-8'),
            msg=bytes(sigPayload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        data = requests.post(self.BASE_URL+'private/get-account-summary',
                             json=req, headers={'Content-Type': "application/json"})
        data = data.json()
        print(data)
        # return round(float(data['result']['accounts'][0]['balance']), 2)

    def test(self):
        que = Queue.Queue()
        t = Thread(target=lambda q, arg1: q.put(
            self.get_candlestick(arg1)), args=(que, "VET_USDT", "1m"))
        t.start()
        result = que.get()
        print(result)

    def get_account_summary(self):
        vetP = float(self.get_candlestick("VET_USDT", "1m")['h'])
        croP = float(self.get_candlestick("CRO_USDT", "1m")['h'])
        dotP = float(self.get_candlestick("DOT_USDT", "1m")['h'])
        shibP = float(self.get_candlestick("SHIB_USDT", "1m")['h'])

        vetQ = self.get_crypto_balance("VET")
        croQ = self.get_crypto_balance("CRO")
        # dotQ = self.get_crypto_balance("DOT")
        # shibQ = self.get_crypto_balance("SHIB")

        print("CRYPTO.COM SUMMARY")
        print('***********************************')
        print("SYMBOL       PRICE       USDT VALUE")
        print('')
        print("  VET       "+str(vetP)+"       "+str(round((vetP*vetQ), 2)))
        print("  CRO       "+str(croP)+"        "+str(round((croP*croQ), 2)))
        print("  DOT       "+str(dotP)+"        "+str(round((dotP*dotQ), 2)))
        print("  SHIB                     "+str(round(shibP*shibQ, 2)))


class Luno:

    def __init__(self):
        with (open("keys.json")) as keys:
            data = json.load(keys)
            self.API_KEY = data['luno']["api_key"]
            self.SECRET_KEY = data['luno']["secret_key"]

        self.conn = cl(api_key_id=self.API_KEY, api_key_secret=self.SECRET_KEY)

    def get_price(self, currency):
        try:
            res = self.conn.get_ticker(pair=currency)
            return round(float(res['ask']), 2)
        except Exception as e:
            print(e)
            print("penis")

    def get_balance(self):
        try:
            result = self.conn.get_balances()
            return result
        except Exception as e:
            print(e)
            print("penis")

    def get_account_summary(self):
        ltcP = self.get_price("LTCZAR")
        ethP = self.get_price("ETHZAR")

        ethB = float(self.get_balance()['balance'][1]['balance'])
        ltcB = float(self.get_balance()['balance'][2]['balance'])

        total = round((ethB*ethP)+(ltcP*ltcB), 2)
        print()
        print("LUNO SUMMARY")
        print('***********************************')
        print("SYMBOL       PRICE       Rand VALUE")
        print('')
        print("  ETH       "+str(ethP)+"        "+str(round((ethB*ethP), 2)))
        print("  LTC       "+str(ltcP)+"         "+str(round((ltcP*ltcB), 2)))
        print('-----------------------------------')
        print("                          R"+str(total))


class Binance:
    def __init__(self):
        with open("keys.json")as keys:
            data = json.load(keys)
            self.API_KEY = data['binance']["api_key"]
            self.SECRET_KEY = data['binance']["secret_key"]
        self.client = Client(self.API_KEY, self.SECRET_KEY)

    def get_balance(self, currency):
        result = self.client.get_asset_balance(asset=currency)
        return round(float(result['free']), 2)

    def get_price(self, currency):
        price = self.client.get_symbol_ticker(symbol=currency)['price']
        return (float(price))

    def get_account_summary(self):
        crvQ = self.get_balance("CRV")
        crvP = self.get_price("CRVUSDT")

        print()
        print("BINANCE SUMMARY")
        print('***********************************')
        print("SYMBOL       PRICE       USDT VALUE")
        print('')
        print("  CRV        "+str(crvP)+"         "+str(round((crvP*crvQ), 2)))
        print('')


if __name__ == "__main__":
    b = Binance()
    b.get_account_summary()
    # c = CryptoCom()
    # c.get_account_summary()
    l = Luno()
    l.get_account_summary()
