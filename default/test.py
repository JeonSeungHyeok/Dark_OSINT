#!/usr/bin/env python3

from requests_tor import RequestsTor

requests = RequestsTor(tor_ports=(9050,),tor_cport=9051)

url = "https://protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion/"

r = requests.get(url)

print(r.text)
