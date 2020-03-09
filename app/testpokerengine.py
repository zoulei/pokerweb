from urllib2 import urlopen

def testserver():
    ip = "http://192.168.0.11:8080"
    urllist = [
        "/init/8_2_1_0000_5_0_400_400_400_400_400_400_0_400_400_0_0_0_0_0_0_0_0_0_0",
        "/uploadhand/AS9S",
        "/update/5_call_4",
        "/update/4_fold_0",
        "/update/3_fold_0",
        "/update/2_fold_0",
        "/update/1_raise_20",
        "/update/9_fold_0",
        "/update/8_fold_0",
        "/update/6_call_20",
        "/update/5_call_20",
        "/newboard/AC8DKD",
        "/update/6_check_0",
        # "/update/5_check_0",
        # "/update/1_raise_40",
        # "/update/6_fold_0",
        # "/update/5_call_40",
        # "/newboard/2D",
        # "/update/5_check_0",
        # "/update/1_check_0",
        # "/newboard/3D",
        # "/update/5_check_0",
        # "/update/1_check_0",
    ]
    # urllist = [
    #     "/init/8_2_1_0000_5_0_400_400_400_400_400_400_0_400_400_0_0_0_0_0_0_0_0_0_0",
    #     "/uploadhand/AS9S",
    #     "/update/5_raise_399",
    # ]
    urllist = [ip + v for v in urllist]
    for handsurl in urllist:
        print handsurl
        htmldoc = urlopen(handsurl).read()
        print htmldoc

if __name__ == "__main__":
    testserver()