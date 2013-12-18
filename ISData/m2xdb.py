import requests, json, hashlib, os
from requests.exceptions import HTTPError

from m2x.client import M2XClient
from m2x import version

from database import Database

from ISModels import Asset
from vars import TIMESTAMP_FORMAT, STATUS_OK
from ISUtils.process_utils import getConf

class M2XDB(Database):
	def __init__(self):
		super(M2XDB, self).__init__()
		
		try:
			f = open(getConf(os.path.abspath(__file__)), 'rb')
			m2x_conf = json.loads(f.read())['M2X']
			f.close()
		except:
			return
		
		self.url = "http://api-m2x.att.com/v1/feeds/%s" % m2x_conf['feed_id']
		self.header = {
			"X-M2X-KEY" : m2x_conf['api_key'],
			"Content-type" : "application/json",
			"Accept-Encoding" : "gzip, deflate",
			"User-Agent" : "python-m2x/%s" % version
		}
		self.timestamp_format = TIMESTAMP_FORMAT['iso8601']
			
	def update(self, stream, asset):
		try:
			r = requests.put(
				"%s/streams/%s" % (self.url, stream), 
				data=json.dumps(asset),
				headers=self.header
			)
		except requests.exceptions.ConnectionError as e:
			print e
			return False
		
		print r.headers
		print r.status_code
		print r.content

		return r.status_code in STATUS_OK
	
	def create(self, stream, asset):
		return self.update(stream, asset)
	
	def indexExists(self, stream):
		print "%s/streams/%s" % (self.url, stream)
		try:
			r = requests.get("%s/streams/%s" % (self.url, stream), headers=self.header)
		except requests.exceptions.ConnectionError as e:
			print e
			return False
		
		print r.status_code
		print r.content
		
		return r.status_code in STATUS_OK
	
	def createIndex(self, stream, **params):
		try:
			r = requests.put(
				"%s/streams/%s" % (self.url, stream),
				data=json.dumps(params),
				headers=self.header
			)
		except requests.exceptions.ConnectionError as e:
			print e
			return False
		
		print r.status_code
		print r.content
		
		return r.status_code in STATUS_OK
		