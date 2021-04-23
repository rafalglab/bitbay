import time
import requests
import json
import uuid
import hashlib
import hmac
import json
from bitbay import Bitbay

def load_params():
    with open('setup.txt') as f:
        data = f.read()
    setup_par = json.loads(data)
    print(setup_par)
    f.close()
    return setup_par


if __name__ == '__main__':
    bitbay_req = Bitbay(api_key='a3ea51d9-ba72-4e2e-abf3-bc9ff8cbc7d4', api_secret='4592deeb-f1d7-4555-8743-36388ff7c4eb')
    how_many = 1
    order_buy = {}
    order_sell = {}
    while how_many < 300:
        print("================================")
        print(" ")
        print(time.asctime(time.localtime(time.time())))
        how_many += 1
        # Setup parameters load from setup.txt file. JSON format.

        setup_parameters = load_params()

        # print(bitbay_req.get_ticker('PLN')['rate'])

        pln_balance = bitbay_req.get_curr_balance('PLN')
        btc_balance = bitbay_req.get_curr_balance('BTC')
        pln_btc_rate = float(bitbay_req.get_ticker("BTC-PLN")['rate'])   
        btc_sell = pln_btc_rate * setup_parameters["BTC_SELL_RATE"]
        btc_buy = pln_btc_rate * setup_parameters["BTC_BUY_RATE"]
        btc_to_sell = btc_balance * setup_parameters["BTC_SELL_AMOUNT_RATE"]
        btc_to_buy = btc_balance * setup_parameters["BTC_BUY_AMOUNT_RATE"]

        # print("balance PLN: " + str(pln_balance))
        # print("balance BTC: " + str(btc_balance))
        # print("pln-btc rate: " + str(pln_btc_rate))
        # print("sprzedaz: " + str(btc_sell))
        # print("kupno: " + str(btc_buy))
        # print("btc_to_buy: " + str(btc_to_buy))
        # print("btc_to_sell: " + str(btc_to_sell))
        # print(bitbay_req.get_balance()['balances'])
        

        order_buy = bitbay_req.create_order('BTC-PLN', amount=round(btc_to_buy, 6), rate=int(btc_buy), offerType='buy', mode='limit')
        order_sell = bitbay_req.create_order('BTC-PLN', amount=round(btc_to_sell, 6), rate=int(btc_sell), offerType='sell', mode='limit')
        print(order_buy)
        print(order_sell)

        print("End of iteration: " + str(how_many)) 

        time.sleep(600)
        cancel_buy = bitbay_req.cancel_order('BTC-PLN', order_buy["offerId"], 'buy', round(btc_to_buy, 6))
        cancel_sell = bitbay_req.cancel_order('BTC-PLN', order_sell["offerId"], 'sell', round(btc_to_sell))
        

        