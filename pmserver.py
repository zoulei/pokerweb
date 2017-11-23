#server entry, this file designate specific module to serve specific url

from flask import Flask
from flask import request

import logging
import logging.config
import DBOperater

import requestfoldstrategy
import collecthands

from flask import  render_template, redirect, url_for, send_from_directory
from werkzeug import secure_filename

import os

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
@app.route('/upload', methods=['POST'])
def upload():
    return collecthands.uploadNameImg(request)

@app.route('/uploadhandsinfo', methods=["POST"])
def uploadhandsinfo():
    return collecthands.uploadHandsInfo(request)

@app.route('/gameseq')
def gameseq():
    return collecthands.gameseq()

@app.route('/joingame/<int:seq>')
def joingame(seq):
    return collecthands.joingame(seq)

@app.route('/collectgamelist')
def collectgamelist():
    return collecthands.collectgamelist()

@app.route('/completegamecollect/<int:seq>')
def completegamecollect(seq):
    return collecthands.completegamecollect(seq)

@app.route('/uploadhandsurl/<path:handsurl>')
def uploadhandsurl(handsurl):
    return collecthands.uploadhandsurl(handsurl)

if __name__ == '__main__':
    #logging.info("start server")
    app.run(host='0.0.0.0',port = 80,debug = True)
