import time
import requests
import json
import uuid
import hashlib
import hmac
import json

URL = "https://api.bitbay.net/rest"


class Bitbay():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.secret_key = api_secret

    def query_private(self, method, url, req={}):
        t = int(time.time())
        if method == 'GET':
            message = self.api_key + str(t)
        else:
            if req:
                postdata = json.dumps(req)
            else:
                postdata = ""
            message = self.api_key + str(t) + postdata

        message = message.encode('utf-8')
        signature = hmac.new(self.secret_key.encode('utf-8'), message, hashlib.sha512).hexdigest()
        headers = {
            'API-Key': self.api_key,
            'API-Hash': signature,
            'operation-id': self.getUUID(),
            'Request-Timestamp': str(t),
            'Content-Type': 'application/json'
        }

        if method == 'GET':
            r = requests.request(method, url, headers=headers, params=json.dumps(req))
        else:
            r = requests.request(method, url, headers=headers, data=postdata)
        rep = r.json()
        return rep

    def getUUID(self):
        # 16 bytes
        return str(uuid.uuid4())

    """
    ### Trading
    """
    def create_order(self, symbol, amount, rate=None, price=None, offerType='buy', mode='limit', postOnly=True, fillOrKill=False, firstBalanceId=None, secondBalanceId=None):
        """
        New order
        :param symbol:          BTC-PLN
        :param amount:
        :param rate:
        :param price:
        :param offerType:       buy / sell
        :param mode:            limit / market
        :param postOnly:
        :param fillOrKill:
        :param firstBalanceId:
        :param secondBalanceId:
        :return:
        """
        if mode == 'limit':
            request = {"amount": amount, "rate": rate, "offerType": offerType, "mode": mode, "postOnly": postOnly, "filllOrKill": fillOrKill, "firstBalanceId": firstBalanceId, "secondBalanceId": secondBalanceId}
        else:
            request = {"amount": amount, "price": price, "offerType": offerType, "mode": mode, "postOnly": postOnly, "filllOrKill": fillOrKill, "firstBalanceId": firstBalanceId, "secondBalanceId": secondBalanceId}
        response = self.query_private("POST", URL + "/trading/offer/%s" % symbol, req=request)
        return response

    def get_active_orders(self, symbol=None):
        """
        :param symbol:
        :return:
        """
        if symbol:
            response = self.query_private("GET", URL + "/trading/offer/%s" % symbol)
        else:
            response = self.query_private("GET", URL + "/trading/offer")

        return response

    def cancel_order(self, symbol, offer_id, offer_type, price):
        """
        cancel an existing order
        :param symbol:
        :param offer_id:
        :param offer_type:
        :param price:
        :return:
        """
        response = self.query_private("DELETE", URL + "/trading/offer/%s/%s/%s/%s" % (symbol, offer_id, offer_type, price))
        return response

    def get_config(self, symbol):
        response = self.query_private("GET", URL + "/trading/config/%s" % symbol)
        return response

    def change_config(self, symbol, first, second):
        """g
        Change wallet
        :param symbol:
        :param first:       UUID of wallet for first currency.
        :param second:      UUID of wallet for second currency.
        :return:
        """
        request = {"first": first, "second": second}
        response = self.query_private("POST", URL + "/trading/config/%s" % symbol, req=request)
        return response

    """
    # Deposit/Withdraw
    """
    def get_deposit_address(self, wallet_id):
        response = self.query_private("GET", URL+"/payments/crypto-address/%s" % wallet_id)
        return response

    def generate_deposit_address(self, wallet_id, currency="BTC"):
        request = {"currency": currency}
        response = self.query_private("POST", URL+"/payments/crypto-address/%s" % wallet_id, req=request)
        return response

    def get_address_history(self, wallet_id):
        response = self.query_private("GET", URL+"/payments/crypto-address/all/balance/%s" % wallet_id)
        return response

    def withdraw(self, wallet_id, address, amount, comment=""):
        request = {"address": address, "amount": amount, "comment": comment}
        response = self.query_private("POST", URL + "/payments/withdrawal/%s" % wallet_id, req=request)
        return response

    # FIAT
    def get_igoria_deposit(self, symbol):
        """
        :param symbol: e.g. ETC PLN
        :return:
        """
        response = self.query_private("GET", URL + "/payments/deposit/igoria_deposit/%s/customs" % symbol)
        return response

    def fiat_withdraw(self, wallet_id, symbol, address, amount, name):
        """
        :param wallet_id:
        :param symbol:
        :return:
        """
        request = {"address": address, "amount": amount, "name":name}
        response = self.query_private("GET", URL + "/payments/withdrawal/%s/igoria_withdrawal/%s/start" % (wallet_id, symbol), req=request)
        return response

    """
    ### History
    """
    def get_trade_transactions(self, markets, rateFrom, rateTo, fromTime, toTime, userAction, nextPageCursor):
        """
        :param markets:
        :param rateFrom:
        :param rateTo:
        :param fromTime:
        :param toTime:
        :param userAction: buy/sell
        :param nextPageCursor:  start
        :return:
        """
        request = {"markets": markets, "rateFrom": rateFrom, 'rateTo': rateTo, "fromTime": fromTime, "toTime": toTime, "userAction": userAction, "nextPageCursor": nextPageCursor}

        response = self.query_private("GET", URL + "/trading/history/transactions", req=request)
        return response

    def get_operation_transactions(self, balancesId, balanceCurrencies, fromTime, toTime, fromValue, toValue, balanceTypes, types, sort):
        request = {"balancesId": balancesId, "balanceCurrencies": balanceCurrencies, "fromTime": fromTime, "toTime": toTime, "fromValue": fromValue, "toValue": toValue,
                   "balanceTypes": balanceTypes, "types": types, "sort": sort}
        response = self.query_private("GET", URL + "/balances/BITBAY/history", req=request)
        return response

    """
    ### WALLET
    """
    def get_balance(self, symbol=None):
        if symbol:
            response = self.query_private("GET", URL + "/balances/BITBAY/balance/%s" % symbol)
        else:
            response = self.query_private("GET", URL + "/balances/BITBAY/balance")
        return response
    
    def get_curr_balance(self, symbol):
        table = self.get_balance()['balances']
        for currency in table:
            if currency['name'] == symbol:
                return currency['availableFunds']
        return 'None'

    def create_wallet(self, currency, type, name):
        """
        :param currency:
        :param type:
        :param name:
        :return:
        """
        request = {"currency": currency, "type": type, "name": name}
        response = self.query_private("POST", URL + "/balances/BITBAY/balance", req=request)
        return response

    def change_wallet_name(self, wallet_id, name):
        request = {"name": name}
        response = self.query_private("PUT", URL + "/balances/BITBAY/balance/%s" % wallet_id, req=request)
        return response

    def internal_transfer(self, source_id, destination_id, currency, funds):
        request = {"currency": currency, "funds": funds}
        response = self.query_private("POST", URL + "/balances/BITBAY/balance/transfer/%s/%s" % (source_id, destination_id), req=request)
        return response

    def fiat_cantor(self, currency1, currency2):
        """
        Currency rate
        :param currency1:
        :param currency2:
        :return:
        """
        response = self.query_private("GET", URL + "/fiat_cantor/rate/%s/%s" % (currency1, currency2))
        return response

    def fiat_exchange(self, currency1BalanceId, currency2BalanceId, currency1, currency2, amount, rate):
        request = {"currency1BalanceId": currency1BalanceId, "currency2BalanceId": currency2BalanceId, "currency1": currency1, "currency2": currency2, "amount": amount, "rate": rate}
        response = self.query_private("POST", URL + "/fiat_cantor/exchange", req=request)
        return response

    def fiat_history(self, page, limit, markets):
        """
        Return historical data of performed exchanges.
        :param page:
        :param limit:
        :param markets:
        :return:
        """
        request = {"page": page, "limit": limit, "markets": markets}
        response = self.query_private("GET", URL + "/fiat_cantor/history", req=request)
        return response

    """
    Market data API
    """

    def get_symbols(self):
        r = requests.get(URL + '/trading/ticker', verify=True, )
        rep = r.json()
        return list(rep['items'].keys())

    # symbol - BTC-PLN
    def get_orderbook(self, symbol):
        r = requests.get(URL + "/trading/orderbook/%s" % (symbol), verify=True, )
        rep = r.json()
        return rep

    def get_trades(self, symbol, limit=None, fromTime=None):
        """
        :param symbol:
        :param limit:
        :param fromTime:
        :return:
        """
        if limit and fromTime:
            r = requests.get(URL + "/trading/transactions/%s?limit=%s&fromTime=%s" % (symbol, limit, fromTime), verify=True, )
        elif limit:
            r = requests.get(URL + "/trading/transactions/%s?limit=%s" % (symbol, limit), verify=True, )
        elif fromTime:
            r = requests.get(URL + "/trading/transactions/%s?fromTime=%s" % (symbol, fromTime), verify=True, )
        else:
            r = requests.get(URL + "/trading/transactions/%s" % (symbol), verify=True, )
        rep = r.json()
        return rep

    def get_kline(self, symbol, seconds, start=None, end=None):
        """
        :param symbol:
        :param seconds:
        :param start:
        :param end:
        :return:
        """
        if start and end:
            url = URL + '/trading/candle/history/%s/%s?from=%s&to=%s' % (symbol, seconds, start, end)
        else:
            url = URL + '/trading/candle/history/%s/%s' % (symbol, seconds)

        r = requests.get(url, verify=True, )
        rep = r.json()
        return rep

    def get_stats(self, symbol=None):
        """
        :param symbol:
        :return:
        """
        if symbol:
            r = requests.get(URL + '/trading/stats/%s' % symbol, verify=True, )
            rep = r.json()
            return rep['stats']
        else:
            r = requests.get(URL + '/trading/stats', verify=True, )
            rep = r.json()
            return rep['items']

    def get_ticker(self, symbol=None):
        """
        get the ticker
        :param symbol:
        :return:
        """
        if symbol:
            r = requests.get(URL + '/trading/ticker/%s' % symbol, verify=True, )
            rep = r.json()
            # print(rep)
            return rep['ticker']
        else:
            r = requests.get(URL + '/trading/ticker', verify=True, )
            rep = r.json()
            return rep['items']


if __name__ == '__main__':
    bitbay = Bitbay(api_key='a3ea51d9-ba72-4e2e-abf3-bc9ff8cbc7d4', api_secret='4592deeb-f1d7-4555-8743-36388ff7c4eb')
    how_many = 1
    order_buy = {}
    order_sell = {}
    while how_many < 300:
        print("================================")
        print(" ")
        print(time.asctime(time.localtime(time.time())))
        how_many += 1
        # Setup parameters load from setup.txt file. JSON format.
        with open('setup.txt') as f:
            data = f.read()
        setup_parameters = json.loads(data)
        print(setup_parameters)
        f.close()

        # private methods
        #if (bitbay.get_balance())['status'] == 'Ok':
        #    print(bitbay.get_balance())
        #else:
        #    print('Get balance: ' + str((bitbay.get_balance())['errors']))
        # order = bitbay.create_order('BTC-USD', amount=1, rate=100, offerType='buy', mode='limit')
        # print(order)
        # print(bitbay.get_balance()['status'])
        # result = bitbay.cancel_order('BTC-USD', '82ca35da-6eeb-4f30-91bb-165fdcf4d8b2', 'buy', 4000);
        # print(result)
        # print(bitbay.get_active_orders())

        # status = (bitbay.get_trade_transactions(markets=['BTC-PLN'], rateFrom='10', rateTo='20', fromTime=None, toTime=None, userAction='Buy', nextPageCursor="start"))['status']
        # print(status)

        # print(bitbay.get_trade_transactions(markets=['BTC-PLN'], rateFrom='10', rateTo='20', fromTime=None, toTime=None, userAction='Buy', nextPageCursor="start"))
        # Market Data
        # print(bitbay.get_symbols())
        # print(bitbay.get_ticker("BTC-PLN")['rate'])
        # print(bitbay.get_orderbook('BTC-PLN'))
        # print(bitbay.get_kline(symbol="BTC-USD", seconds=600))
        # print(bitbay.get_trades("BTC-PLN"))
        # print(bitbay.get_balance())
        # table = bitbay.get_balance()['balances']
        # print(len(table))
        # for currency in table:
        #     if currency['name'] == 'PLN':
        #         pln_balance = currency['availableFunds']
        pln_balance = bitbay.get_curr_balance('PLN')
        btc_balance = bitbay.get_curr_balance('BTC')
        pln_btc_rate = float(bitbay.get_ticker("BTC-PLN")['rate'])   
        btc_sell = pln_btc_rate * setup_parameters["BTC_SELL_RATE"]
        btc_buy = pln_btc_rate * setup_parameters["BTC_BUY_RATE"]
        btc_to_sell = btc_balance * setup_parameters["BTC_SELL_AMOUNT_RATE"]
        btc_to_buy = btc_balance * setup_parameters["BTC_BUY_AMOUNT_RATE"]

        print("balance PLN: " + str(pln_balance))
        print("balance BTC: " + str(btc_balance))
        print("pln-btc rate: " + str(pln_btc_rate))
        print("sprzedaz: " + str(btc_sell))
        print("kupno: " + str(btc_buy))
        print("btc_to_buy: " + str(btc_to_buy))
        print("btc_to_sell: " + str(btc_to_sell))
        #print(bitbay.get_balance()['balances'])
        

        order_buy = bitbay.create_order('BTC-PLN', amount=round(btc_to_buy, 6), rate=int(btc_buy), offerType='buy', mode='limit')
        order_sell = bitbay.create_order('BTC-PLN', amount=round(btc_to_sell, 6), rate=int(btc_sell), offerType='sell', mode='limit')
        print(order_buy)
        print(order_sell)

        print("End of iteration: " + str(how_many))

        for currency in setup_parameters["CURRENCIES"].keys():
            print(currency)
            curr_zakup = float(setup_parameters["CURRENCIES"][currency])
            curr_aktualny_kurs = float(bitbay.get_ticker(currency)['rate'])
            curr_zmiana = (curr_aktualny_kurs / curr_zakup - 1) * 100
            # print("Zakup: " + str(curr_zakup))
            print("Aktualny kurs: " + str(curr_aktualny_kurs))
            print("Zmiana kursu: %.2f" % curr_zmiana + "%")
            print("-------------------------------")
            # print(" ")    

        time.sleep(600)
        cancel_buy = bitbay.cancel_order('BTC-PLN', order_buy["offerId"], 'buy', round(btc_to_buy, 6))
        cancel_sell = bitbay.cancel_order('BTC-PLN', order_sell["offerId"], 'sell', round(btc_to_sell))
        

        