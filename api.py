import logging, os, signal, json, sys

import tornado.ioloop
import tornado.web
import tornado.httpserver

from conf import API_PORT, EXT_ID
from vars import STATUS_OK, STATUS_FAIL

from ISUtils.process_utils import getScrapers

from ISModels.schema import Schema

log_format = "%(asctime)s %(message)s"

def getConf():
	try:
		f = open(path_to_conf,'rb')
		conf_ = json.loads(f.read())
		f.close()
	except IOError as e:
		print e
		conf_ = {}
	
	return conf_

class Res():
	def __init__(self):
		self.result = STATUS_FAIL[0]
	
	def emit(self):
		return self.__dict__

class EngineHandler(tornado.web.RequestHandler):
	def initialize(self, action):
		self.action = action
		
	def post(self, action):
		res = Res()
		
		if action == "sync":			
			try:
				s = json.loads(self.request.body)
				db_name = s['database']
				del s['database']
			except ValueError as e:
				print e
				self.finish(res.emit())
				return
			except KeyError as e:
				print e
				self.finish(res.emit())
				return
			
			db = None
			if db_name == "M2X":
				from ISData.m2xdb import M2XDB
				db = M2XDB()
			
			if db is not None:
				db.updateConfig(s)
				res.result = STATUS_OK[0]	
		else:		
			activate = False
			if action == "start":
				activate = True
			
			for scraper in getScrapers(scraper_dir):
				s = Schema(scraper['url'])
				if s.is_active != activate:
					s.activate(activate=activate)
		
			res.result = STATUS_OK[0]
		
		self.finish(res.emit())

class ConfigHandler(tornado.web.RequestHandler):
	def get(self):
		res = Res()		
		res.result = STATUS_OK[0]
		
		conf_ = getConf()		
		sync = []
		for key in conf_:
			s = {
				'vars' : [],
				'database': key
			}
			
			for var in conf_[key].keys():
				if var == "is_active":
					s['is_active'] = conf_[key][var]
					continue
					
				s['vars'].append({
					'key' : var,
					'value' : conf_[key][var]
				})
				
			sync.append(s)
		
		res.data = {
			'sync' : sync,
			'scrapers' : getScrapers(scraper_dir)
		}
		
		self.finish(res.emit())
	
	def post(self):
		res = Res()
		
		try:
			s = json.loads(self.request.body)
		except ValueError as e:
			print e
			self.finish(res.emit())
			return
		
		id_ = s['id']
		del s['id']
		
		print "update config"
		
		f = open(os.path.join(scraper_dir, id_, "conf.json"), 'rb')
		schema = Schema(json.loads(f.read())['url'])
		f.close()
		
		should_activate = None
		for key in s.keys():
			if key == "is_active":
				should_activate = s[key]
				continue
			
			if type(s[key]) == dict:
				val = getattr(schema, key)
				
				for key_ in s[key].keys():
					val[key_] = s[key][key_]

				schema.setattr(key, val)			
			else:
				schema.setattr(key, s[key])
		
		schema.save()
		
		if should_activate is not None:
			print "with activation: %s!" % should_activate
			schema.activate(activate=should_activate)
			
		res.result = STATUS_OK[0]
		print res.emit()
		self.finish(res.emit())

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
				
		self.finish(schema.activate())
	
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
	(r'/', MainHandler),
	(r'/config', ConfigHandler),
	(r'/engine/(start|stop|sync)', EngineHandler, dict(action=None))
]

api = tornado.web.Application(routes)
signal.signal(signal.SIGINT, terminationHandler)

if __name__ == "__main__":
	log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
	scraper_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UserModels")
	path_to_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf.json")
	
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
	log_file = os.path.join(log_dir, "api_log.txt")
	
	logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)
	logging.info("API Started.")
	
	server = tornado.httpserver.HTTPServer(api)
	server.bind(API_PORT)
	server.start(5)
	
	tornado.ioloop.IOLoop.instance().start()