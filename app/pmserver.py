#server entry, this file designate specific module to serve specific url

from flask import Flask
from flask import request

import logging
import DBOperater

import requestfoldstrategy
import collecthands

from werkzeug import secure_filename

#configrate logging
# logging.config.dictConfig({
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
#         },
#     },
#     'handlers': {
#         'default': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'formatter': 'verbose',
#             'filename': '/home/zoul15/nginxwebsite/myapp.log',
#             'maxBytes': 204800,
#             'backupCount': 3,
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['default'],
#             'level': 'INFO',
#         },
#         'sqlalchemy': {
#             'handlers': ['default'],
#             'level': 'INFO',
#         },
#     }
# })

app = Flask(__name__)

#connect to mongoDB
DBOperater.Connect()

@app.route("/requestfoldstrategy",methods=["POST"])
def requestfoldstrategy_():
    return str(requestfoldstrategy.requestfoldstrategy(request))

@app.route("/test")
def test():
    return "success"

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/index')
def index():
    return open("index.html").read()
    #return render_template('index.html')

# Route that will process the file upload

@app.route('/uploadhandsinfo', methods=["POST"])
def uploadhandsinfo():
    return collecthands.uploadHandsInfo(request)

@app.route('/gameseq/<path:phoneid>')
def gameseq(phoneid):
    return collecthands.gameseq(phoneid)

@app.route('/joingame/<int:seq>/<path:phoneid>')
def joingame(seq,phoneid):
    return collecthands.joingame(seq, phoneid)

@app.route('/collectgamelist/<path:phoneid>')
def collectgamelist(phoneid):
    return collecthands.collectgamelist(phoneid)

@app.route('/collectgamehandidx/<int:seq>/<path:phoneid>')
def collectgamehandidx(seq,phoneid):
    return collecthands.collectgamehandidx(seq, phoneid)

@app.route('/completegamecollect/<int:seq>')
def completegamecollect(seq):
    return collecthands.completegamecollect(seq)

# @app.route('/uploadhandsurl/<string:club>/<int:room>/<int:handstotal>/<int:handidx>/<path:handsurl>')
# def uploadhandsurl(club, room, handstotal, handidx, handsurl):
#     return collecthands.uploadhandsurl(club, room, handstotal, handidx, handsurl)

@app.route('/uploadhandsurl/<string:club>/<int:room>/<path:handsurl>')
def uploadhandsurl(club, room, handsurl):
    return collecthands.uploadhandsurl(club, room, handsurl)

@app.route('/checkroom/<string:club>/<int:room>/<string:identifier>')
def checkroom(club, room, identifier):
    return collecthands.checkroom(club, room, identifier)

@app.route('/joinedroom/')
def fetchjoinedroom():
    return collecthands.fetchjoinedroom()

@app.route('/joinroom/<int:roomid>')
def joinroom(roomid):
    return collecthands.joinroom(roomid)

@app.route('/uploadsuccess/')
def fetchuploadsuccess():
    return collecthands.fetchuploadsuccess()

@app.route('/cleanroom/')
def cleanroom():
    return collecthands.cleanroom()

@app.route('/exitroom/<int:roomid>')
def exitroom(roomid):
    return collecthands.exitroom(roomid)

@app.route('/enterroom/<int:roomid>')
def enterroom(roomid):
    return collecthands.enterroom(roomid)

if __name__ == '__main__':
    #logging.info("start server")
    app.run(host='0.0.0.0',port = 80,debug = True)
