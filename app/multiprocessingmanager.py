# -*-coding:utf-8 -*-
from Constant import *
import multiprocessing
import os
import signal
import time

def process(func, para, threadnum = THREADNUM):
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = multiprocessing.Pool(threadnum)
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
        # result = self.m_pool.map_async(self.mainfunc, doclist)
        result = pool.map_async(func, para)
        result = result.get(99999999)  # Without the timeout this blocking call ignores all signals.
    except KeyboardInterrupt:
        pool.terminate()
        pool.close()
        pool.join()
        exit()
    else:
        pool.close()
    pool.join()
    return result

def mainfunc(paraele):
    return paraele

def test():
    result = process(mainfunc, range(10))
    for v in result:
        print v
    for v in result:
        print v

def testmainfunc(para):
    a = 0
    for key in para:
        a += para[key]
    time.sleep(60)
    return a

def test1():
    kvdict = dict(zip(range(100000000),range(100000000)))
    print "generate dict"
    time.sleep(60)
    print "sleep over"
    process(testmainfunc,[kvdict,]*1000)

if __name__ == "__main__":
    test1()