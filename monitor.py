from re import findall

from bs4 import BeautifulSoup
from requests import get


def analyze(ticker, max_threshold: float, min_threshold: float):
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
    msg = f"The current price of {ticker} is: ${price}\n{ticker} share has {result} ${price_change[-2]}"
    message = None
    if result == 'currently no change. Last change:':
        pass
    elif price < min_threshold:
        message = f'{ticker} is currently less than ${min_threshold}.\n\n{msg}'
    elif price > max_threshold:
        message = f'{ticker} is currently more than ${max_threshold}.\n\n{msg}'
    print(message)
    print(f'https://robinhood.com/crypto/{ticker}')


if __name__ == '__main__':
    analyze(ticker='BTC-USD', max_threshold=37_000, min_threshold=30_000)
