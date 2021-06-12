# Cryptocurrency Monitor
Python scripts to monitor cryptocurrencies.
- `yfinance` - Get currency information using yahoo finance [API](https://pypi.org/project/yfinance/)
- `requests` - Get all cryptocurrencies from [yahoo finance](https://finance.yahoo.com/)
- `BeautifulSoup` - Extract tag values from html response
- `SMTP` - Send SMS notification using Simple Mail Transfer Protocol

### Commit:
`pip install -U sphinx==4.0.2`<br>
`pip install pre-commit==2.13.0`<br>
`pre-commit run --all-files`

### Requirements
[params.json](README.md)<br>
[requirements.txt](src/requirements.txt)

### Docker
`docker build -t crypto .`<br>
`docker run crypto`

<h6>
Note: DO NOT use <code>alpine</code> for docker as the build dependencies from 
<a href="https://pypi.org/simple/pandas/">simple/pandas</a> fail due to missing pre-req.<br>
Alternative is to use <code>slim</code> or install the modules directly from <code>alpine</code> 
<a href="https://pkgs.alpinelinux.org/packages?name=*pandas">repository</a>
</h6>

### Runbook:
https://thevickypedia.github.io/crypto-monitor/
