import argparse

import requests
from pyquery import PyQuery as pq


req = requests.Session()
req.headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16', 'Accept' : 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5', 'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding' : 'gzip,deflate,sdch', 'Accept-Language' : 'en-US,en;q=0.8', 'Cache-Control' : 'max-age=0', 'Connection' : 'keep-alive', 'Host' : 'adminfo.ucsadm.oregonstate.edu', 'Referer' : 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_WWWLogin'}
cookie = {}


def login(sid, pin):
    req.headers['Referer'] = 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_WWWLogin'
    url = 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_ValLogin'
    res = req.get(url)
    res = req.post(url, {'sid' : sid, 'PIN' : pin})

    if pq(res.content)('title').text() == 'Login':
        return False
    return True


def select_term():
    req.headers['Referer'] = 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu'
    url = 'https://adminfo.ucsadm.oregonstate.edu/prod/bwskfreg.P_AltPin'
    res = req.get(url)

    if pq(res.content)('title').text() == 'Select Term':
        res = req.post(url, {'term_in': '201303'})
        if pq(res.content)('title').text() == 'Registration Pin Verification':
            return True
    elif pq(res.content)('title').text() == 'Registration Pin Verification':
        return True


def attempt_pin(pin):
    pass


def main(args):
    if not login(args.username, args.password):
        print "[ERR] Could not login."
        return
    else:
        if not select_term()
            print "[ERR] Could not select term."
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Striker On.')
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    args = parser.parse_args()
    main(args)
