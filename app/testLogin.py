import urllib
import urllib2
import pprint
import json

def postHttp():
    url = "http://192.168.112.111/requestfoldstrategy"

    postdata = {"username": "zl","pwd":"12345"}

    postdata = urllib.urlencode(postdata)
    request = urllib2.Request(url,postdata)
    response=urllib2.urlopen(request)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint( json.loads(response.readline()))

if __name__ == "__main__":
    postHttp()