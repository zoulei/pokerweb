# -*- coding:utf-8 -*-
import time

class Timer:
    DEFAULTID = "default timer"
    def __init__(self):
        self.reset()

    def reset(self):
        self.m_elapsed = {}
        self.m_starttime = {}

    def start(self, identifier = DEFAULTID):
        if identifier not in self.m_starttime:
            self.m_starttime[identifier] = time.time()

    def stop(self, identifier = DEFAULTID):
        if identifier not in self.m_starttime:
            return
        if identifier not in self.m_elapsed:
            self.m_elapsed[identifier] = 0
        self.m_elapsed[identifier] += time.time() - self.m_starttime[identifier]
        del self.m_starttime[identifier]

    def stopall(self):
        for identifier in self.m_starttime.keys():
            self.stop(identifier)

    def getelapsedtime(self, identifier = DEFAULTID):
        if identifier in self.m_starttime:
            # 该目标还在计时
            return time.time() - self.m_starttime[identifier] + self.m_elapsed.get(identifier,0)
        else:
            return self.m_elapsed.get(identifier,0)

    def printdata(self, identifier = None):
        if identifier is None:
            for key, value in self.m_elapsed.items():
                print key,":",value
        else:
            print identifier,":",self.m_elapsed.get(identifier,0)

    def printpcgdata(self, identifier = None):
        total = sum(self.m_elapsed.values())
        if identifier is None:
            for key, value in self.m_elapsed.items():
                print key,":",value * 1.0 / total
        else:
            print identifier,":",self.m_elapsed.get(identifier,0) * 1.0 / total