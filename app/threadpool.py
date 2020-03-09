import signal
import multiprocessing
import Constant

class ThreadPool:
    def __init__(self, func, para, threadnum = Constant.THREADNUM):
        self.m_func = func
        self.m_para = para
        self.m_threadnum = threadnum

    def run(self):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = multiprocessing.Pool(self.m_threadnum)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            # result = self.m_pool.map_async(self.mainfunc, doclist)
            result = pool.map_async(self.m_func, self.m_para)
            result.get(99999999)  # Without the timeout this blocking call ignores all signals.
        except KeyboardInterrupt:
            pool.terminate()
            pool.close()
            pool.join()
            exit()
        else:
            pool.close()
        pool.join()
        return result.get()

    def getresult(self):
        return self.run()