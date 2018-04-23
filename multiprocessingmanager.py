# -*-coding:utf-8 -*-
from Constant import *
import multiprocessing
import os
import signal

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

if __name__ == "__main__":
    test()