# asnd
## Usage
### Using command line
`chaos -silent -d telegram.org | dnsx -silent -a -resp-only | sort -u | python ./main.py`

### Example output
```
=====  ======================  ===============  ================  ==========================
  ASN  ORG                     IP               Network           Location
=====  ======================  ===============  ================  ==========================
15169  GOOGLE                  216.58.211.243   216.58.192.0/19   N/A, United States
=====  ======================  ===============  ================  ==========================
16509  AMAZON-02               18.184.99.30     18.184.0.0/15     Frankfurt am Main, Germany
=====  ======================  ===============  ================  ==========================
59930  Telegram Messenger Inc  149.154.175.16   149.154.172.0/22  Amsterdam, The Netherlands
59930  Telegram Messenger Inc  149.154.175.114  149.154.172.0/22  Amsterdam, The Netherlands
59930  Telegram Messenger Inc  149.154.175.209  149.154.172.0/22  Amsterdam, The Netherlands
=====  ======================  ===============  ================  ==========================
62014  Telegram Messenger Inc  149.154.170.96   149.154.168.0/22  Amsterdam, The Netherlands
62014  Telegram Messenger Inc  149.154.171.116  149.154.168.0/22  Amsterdam, The Netherlands
62014  Telegram Messenger Inc  149.154.171.236  149.154.168.0/22  Amsterdam, The Netherlands
62014  Telegram Messenger Inc  149.154.171.237  149.154.168.0/22  Amsterdam, The Netherlands
=====  ======================  ===============  ================  ==========================
62041  Telegram Messenger Inc  95.161.64.2      95.161.64.0/20    N/A, Antigua and Barbuda
62041  Telegram Messenger Inc  95.161.64.10     95.161.64.0/20    N/A, Antigua and Barbuda
62041  Telegram Messenger Inc  149.154.162.40   149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.162.186  149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.162.203  149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.162.204  149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.163.169  149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.164.3    149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.164.125  149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.167.57   149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.167.99   149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.167.124  149.154.160.0/21  London, United Kingdom
62041  Telegram Messenger Inc  149.154.167.220  149.154.160.0/21  London, United Kingdom
=====  ======================  ===============  ================  ==========================
```