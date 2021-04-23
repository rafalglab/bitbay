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
    bitbay = Bitbay(api_key='a3ea51d9-ba72-4e2e-abf3-bc9ff8cbc7d4', api_secret='4592deeb-f1d7-4555-8743-36388ff7c4eb')
    how_many = 1
    print("================================")
    print(" ")
    print(time.asctime(time.localtime(time.time())))
    how_many += 1
    # Setup parameters load from setup.txt file. JSON format.

    setup_parameters = load_params()

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
