from concurrent.futures import ThreadPoolExecutor
from logging import INFO, basicConfig, getLogger
from os import environ, path
from pprint import pprint

from bs4 import BeautifulSoup
from dotenv import load_dotenv
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
    result = f"{ticker} has {result} ${float(round(difference, 4))} for today."
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
        if all([gmail_user, gmail_pass, phone_number]):
            response = Messenger(gmail_user=gmail_user, gmail_pass=gmail_pass, phone_number=phone_number,
                                 subject=ticker, message=f"{message}\n{curr_result} {prev_result}\n{result}").send_sms()
            if response.ok:
                logger.info('SMS notification has been sent.')
            else:
                logger.error(response.json())
        else:
            logger.warning('Please store the env vars for PHONE, GMAIL_USER and GMAIL_PASS to enable notifications.')


def get_all_cryptos(offset: int):
    """Update a global dictionary with all cryptocurrency ticker values, current price and ticker name.

    Args:
        offset: An offset value is passed to frame the URL as a paginator.
    """
    response = BeautifulSoup(get(
        url=f'https://finance.yahoo.com/cryptocurrencies?count=100&offset={offset}').text,
        parser="html.parser", features="lxml")
    class_ = {'class': 'Ovx(a) Ovx(h)--print Ovy(h) W(100%)'}
    name_list = response.find_all('div', class_)[0].find_all('a', href=True)[::2]  # picks only every 2nd element
    [cryptos.update({link.get('href').split('?p=')[-1]: link.get('title')}) for link in name_list]


if __name__ == '__main__':
    if path.isfile('.env'):
        load_dotenv(dotenv_path='.env', override=True, verbose=True)

    phone_number = environ.get('PHONE')
    gmail_user = environ.get('GMAIL_USER')
    gmail_pass = environ.get('GMAIL_PASS')

    analyze(ticker='DOGE-USD', max_threshold=1, min_threshold=0.35)

    cryptos = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(get_all_cryptos, list(range(0, 500, 100)))
    pprint(cryptos)
