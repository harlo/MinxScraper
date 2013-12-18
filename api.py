import logging, os, signal, json, sys

import tornado.ioloop
import tornado.web
import tornado.httpserver

from conf import API_PORT, EXT_ID
from ISModels.schema import Schema

log_format = "%(asctime)s %(message)s"

class Res():
	def __init__(self):
		self.result = 403
	
	def emit(self):
		return self.__dict__

class MainHandler(tornado.web.RequestHandler):
	def parseRequest(self):
		print "parsing this request"
	
	def validateRequest(self):
		if self.request.headers['Origin'] == "chrome-extension://%s" % EXT_ID:
			return True
		
		return False
		
	def get(self):
		res = Res()
		
		print "GET"
		
		self.finish(res.emit())
	
	def post(self):
		res = Res()
		
		if not self.validateRequest():
			self.finish(res.emit())
			return
		
		try:
			s = json.loads(self.request.body)['manifest']
		except ValueError as e:
			print e
			self.finish(res.emit())
			return
		
		url = s['url']
		del s['url']
		
		schema = Schema(url, create=True, **s)
		schema.save()
		schema.activate()
		
		self.finish(res.emit())
	
	def put(self):
		res = Res()
		
		print "PUT"
		
		self.finish(res.emit())
	
	def delete(self):
		res = Res()
		
		print "DELETE"
		
		self.finish(res.emit())

def terminationHandler(signal, frame):
	sys.exit(0)
	
routes = [
	(r'/', MainHandler)
]

api = tornado.web.Application(routes)
signal.signal(signal.SIGINT, terminationHandler)

if __name__ == "__main__":
	log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	log_file = os.path.join(log_dir, "api_log.txt")
	
	logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)
	logging.info("API Started.")
	
	server = tornado.httpserver.HTTPServer(api)
	server.bind(API_PORT)
	server.start(5)
	
	tornado.ioloop.IOLoop.instance().start()