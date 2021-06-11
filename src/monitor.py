from concurrent.futures import ThreadPoolExecutor
from json import load
from logging import INFO, basicConfig, getLogger
from os import listdir
from pprint import pprint
from re import findall
from smtplib import SMTP, SMTPException

from bs4 import BeautifulSoup
from requests import get

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
    scrapped = BeautifulSoup(get(f'https://finance.yahoo.com/quote/{ticker}').text, "html.parser")
    class_name = {'class': 'D(ib) smartphone_Mb(10px) W(70%) W(100%)--mobp smartphone_Mt(6px)'}
    raw_data = scrapped.find_all('div', class_name)[0]
    price = float(raw_data.find('span').text.replace(',', ''))
    price_change = findall(r"\d+\.\d+", str(raw_data))
    result = None
    if 'At close' in str(raw_data):
        result = 'currently no change. Last change:'
    elif 'negativeColor' in str(raw_data):
        result = 'decreased'
    elif 'positiveColor' in str(raw_data):
        result = 'increased'
    logger.info(f"The current price of {ticker} is: ${price}\n{ticker} share has {result} ${price_change[-2]}")
    message = None
    if price < min_threshold:
        message = f'{ticker} is currently less than ${min_threshold}.'
    elif price > max_threshold:
        message = f'{ticker} is currently more than ${max_threshold}.'
    if message:
        logger.info(message)
        notify(subject=ticker, body=message)


def notify(subject: str, body: str):
    """Notification is triggered when the case status, is other than 'Case Was Received'.

    Notifies via text message through SMS gateway of destination number.

    Args:
        body: Receives the content as argument `body` to send an SMS notification.
        subject: Receives the title as argument `subject` to send an SMS notification.

    """
    try:
        to = f"{phone_number}@tmomail.net"
        message = (f"From: {email_sender}\n" + f"To: {to}\n" + f"Subject: {subject}\n" + "\n\n" + body)
        server = SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user=email_sender, password=email_password)
        server.sendmail(email_sender, to, message)
        server.quit()
        server.close()
        logger.info('SMS notification has been sent.')
    except SMTPException as error:
        if 'Username and Password not accepted' in str(error):
            logger.error(error)
            exit(1)
        else:
            logger.error('Failed to send SMS. Please check the GMAIL_USER and GMAIL_PASS in params.json.')
            logger.critical('Logon to https://myaccount.google.com/lesssecureapps and turn ON less secure apps.')
            exit(error)


def get_all_cryptos(offset: int):
    """Update a global dictionary with all cryptocurrency ticker values, current price and ticker name.

    Args:
        offset: An offset value is passed to frame the URL as a paginator.

    """
    response = BeautifulSoup(get(url=f'https://finance.yahoo.com/cryptocurrencies?count=100&offset={offset}').text,
                             "html.parser")
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
    if 'params.json' not in listdir('src'):
        exit('Script requires a json file (params.json) with credentials stored as key value pairs.')

    if not open('src/params.json').read():
        logger.error('Credentials file is empty.')
        phone_number, email_sender, email_password = None, None, None
    else:
        json_file = load(open('src/params.json'))
        phone_number = json_file.get('PHONE')
        email_sender = json_file.get('GMAIL_USER')
        email_password = json_file.get('GMAIL_PASS')

    env_vars = [phone_number, email_sender, email_password]

    if any(env_var is None for env_var in env_vars):
        exit("Your 'params.json' should appear as following:\n"
             "{\n"
             "\tPHONE: <phone_number>,\n"
             "\tGMAIL_USER: <sender_email_address>,\n"
             "\tGMAIL_PASS: <sender_id_password>,\n"
             "}")

    analyze(ticker='BTC-USD', max_threshold=37_000, min_threshold=30_000)

    cryptos = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(get_all_cryptos, list(range(0, 500, 100)))
    pprint(cryptos)
