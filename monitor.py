from concurrent.futures import ThreadPoolExecutor
from json import load
from logging import INFO, basicConfig, getLogger
from os import listdir
from pprint import pprint

from bs4 import BeautifulSoup
from gmailconnector.send_sms import Messenger
from requests import get
from yfinance import Ticker

basicConfig(level=INFO, datefmt='%b-%d-%Y %H:%M:%S',
            format='%(asctime)s - %(levelname)s - %(funcName)s - Line: %(lineno)d - %(message)s')
logger = getLogger('monitor.py')


def analyze(ticker: str, max_threshold: float, min_threshold: float):
    """Analyzes the ticker value from finance.yahoo.com and compares with the max and min price value.

    Args:
        ticker: Ticker value for the cryptocurrency.
        min_threshold: Minimum value below which a notification has to be triggered.
        max_threshold: Maximum value beyond which a notification has to be triggered.

    """
    raw_data = Ticker(ticker=ticker).info
    price = raw_data['regularMarketPrice']
    open_value = raw_data['regularMarketOpen']
    if difference := price - open_value:
        if difference < 0:
            result = 'decreased'
            difference = - difference
        else:
            result = 'increased'
    else:
        result = 'currently no change. Last change:'
    prev_result = f"Opening price: {open_value}"
    curr_result = f"Current price: ${price}"
    result = f"{ticker} has {result} ${round(difference, 8)} for today."
    logger.info(curr_result)
    logger.info(prev_result)
    logger.info(result)
    message = None
    if price < min_threshold:
        message = f'Less than ${min_threshold}.'
    elif price > max_threshold:
        message = f'More than ${max_threshold}.'
    if message:
        logger.info(message)
        logger.info(Messenger(
            gmail_user=gmail_user, gmail_pass=gmail_pass, phone_number=phone_number,
            subject=ticker, message=message + f"\n{curr_result} {prev_result}\n{result}"
        ).send_sms())


def get_all_cryptos(offset: int):
    """Update a global dictionary with all cryptocurrency ticker values, current price and ticker name.

    Args:
        offset: An offset value is passed to frame the URL as a paginator.

    """
    response = BeautifulSoup(get(
        url=f'https://finance.yahoo.com/cryptocurrencies?count=100&offset={offset}').text,
        parser="html.parser")
    class_ = {'class': 'Ovx(a) Ovx(h)--print Ovy(h) W(100%)'}
    raw_data = response.find_all('div', class_)[0]
    name_list = raw_data.find_all('a', href=True)[::2]  # picks only every 2nd element
    num_list = raw_data.find_all('span', {'class': 'Trsdu(0.3s)'})[::4]  # picks only every 4th element
    num_list = [each.text for each in num_list]
    for index, link in enumerate(name_list):
        title = link.get('title')
        ticker = link.get('href').split('?p=')[-1]
        cryptos[num_list[index]] = [ticker, title]  # updated dictionary with ticker, name and current price


if __name__ == '__main__':
    if 'params.json' not in listdir():
        exit('Script requires a json file (params.json) with credentials stored as key value pairs.')

    if not open('params.json').read():
        logger.error('Credentials file is empty.')
        phone_number, gmail_user, gmail_pass = None, None, None
    else:
        json_file = load(open('params.json'))
        phone_number = json_file.get('PHONE')
        gmail_user = json_file.get('GMAIL_USER')
        gmail_pass = json_file.get('GMAIL_PASS')

    env_vars = [phone_number, gmail_user, gmail_pass]

    if any(env_var is None for env_var in env_vars):
        exit("Your 'params.json' should appear as following:\n"
             "{\n"
             "\tPHONE: <phone_number>,\n"
             "\tGMAIL_USER: <sender_email_address>,\n"
             "\tGMAIL_PASS: <sender_id_password>,\n"
             "}")

    analyze(ticker='DOGE-USD', max_threshold=1, min_threshold=0.35)

    cryptos = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(get_all_cryptos, list(range(0, 500, 100)))
    pprint(cryptos)
