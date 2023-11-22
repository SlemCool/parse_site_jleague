import codecs

import mmh3
import requests

proxy = {"http": "http://199.229.254.129:4145", "https": "http://199.229.254.129:4145"}
response = requests.get(
    "https://www.jleague.co/static/icons/favicon.f435a6b5e7ad.ico",
    proxies=proxy,
)
favicon = codecs.encode(response.content, "base64")
hash = mmh3.hash(favicon)
print(hash)
