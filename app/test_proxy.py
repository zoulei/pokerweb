import urllib2
import requests
from fake_useragent import UserAgent
from requests.auth import HTTPBasicAuth
import json

def get_url_content(url, session_id, create = False):
    ua = UserAgent()
    i_headers = {
        "User-Agent": str(ua.random),
        "X-Crawlera-cookies": "disable",
        "accept-encoding": "gzip, deflate, br",
        "X-Crawlera-Session": session_id
    }
    # if create:
    #     i_headers["X-Crawlera-Session"] = "create"
    i_headers = {
        "User-Agent": str(ua.random)
    }
    response = requests.get(url, headers=i_headers, allow_redirects=False)
    i_headers = {
        "User-Agent": str(ua.random),
        "X-Crawlera-cookies": "disable",
        "accept-encoding": "gzip, deflate, br",
        "X-Crawlera-Session": session_id
    }
    if 'Location' in response.headers:
        print response.headers
        proxyMeta = "http://6398bdb3f1ec4a079b57f48bc32b9556:@proxy.crawlera.com:8011/"
        proxies = {"http": proxyMeta, "https": proxyMeta}
        response = requests.get(url, headers=i_headers, proxies=proxies, verify="./zyte-smartproxy-ca.crt")
        print "length : ", len(response.content)
        if len(response.content) < 1000:
            print response.content
            if len(response.content) > 100:
                print "headers : ", response.headers
    else:
        print "??????????????????????????"
    return len(response.content)

def create_sessions():
    resopnse = requests.post("http://proxy.zyte.com:8011/sessions/", auth=HTTPBasicAuth('6398bdb3f1ec4a079b57f48bc32b9556', ''))
    print resopnse.headers
    return resopnse.headers["X-Crawlera-Session"]

def delete_sessions(session_id):
    response = requests.delete('http://proxy.zyte.com:8011/sessions/' + session_id, auth=HTTPBasicAuth('6398bdb3f1ec4a079b57f48bc32b9556', ''))

def get_sessions():
    response = requests.get('http://proxy.zyte.com:8011/sessions', auth=HTTPBasicAuth('6398bdb3f1ec4a079b57f48bc32b9556', ''))
    return json.loads(response.content)

def test():
    f = open("./data/test_url")
    idx = 0
    session_id = create_sessions()
    for line in f:
        idx += 1
        line = line.strip()
        while True:
            length = get_url_content("http://" + line, session_id)
            print "sessions : ", session_id
            if length < 1000:
                delete_sessions(session_id)
                session_id = create_sessions()
            if length > 1000:
                break
            print "========================= idx : ", idx
            pass

if __name__=="__main__":
    # get_url_content("https://ipv4.icanhazip.com")
    # get_url_content("http://i.i3tj.com/u5PYut")
    test()
    # print get_sessions()
    # create_sessions()