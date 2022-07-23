import threading
import time
from flask import Flask
import signal

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.ioloop
import tornado.web
import tornado.options

static_joined_room = dict()

app = Flask(__name__)

@app.route('/exitroom/<int:roomid>')
def exitroom(roomid):
    mutex = threading.Lock()
    mutex.acquire()
    print("exitroom : ", roomid)
    del static_joined_room[roomid]
    mutex.release()
    return "1"

@app.route('/enterroom/<int:roomid>')
def enterroom(roomid):
    mutex = threading.Lock()
    mutex.acquire()
    print("enterroom : ", roomid)
    if roomid in static_joined_room and time.time() - static_joined_room[roomid] < 3600 * 24:
        mutex.release()
        return "2"
    else:
        static_joined_room[roomid] = time.time()
        mutex.release()
        return "1"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class MyApplication(tornado.web.Application):
    is_closing = False

    def signal_handler(self, signum, frame):
        # logging.info('exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            # clean up here
            tornado.ioloop.IOLoop.instance().stop()
            # logging.info('exit success')


application = MyApplication([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    signal.signal(signal.SIGINT, application.signal_handler)
    tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
    print('run...')
    IOLoop.instance().start()