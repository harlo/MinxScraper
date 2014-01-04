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
			self.conf = json.loads(f.read())['M2X']
			f.close()
		except:
			self.conf = {}
			return
		
		try:
			self.is_active = self.conf['is_active']
		except KeyError as e:
			print "is_active not yet set for M2X.  using False as default"
			self.is_active = False
			
		self.url = "http://api-m2x.att.com/v1/feeds/%s" % self.conf['feed_id']
		self.header = {
			"X-M2X-KEY" : self.conf['api_key'],
			"Content-type" : "application/json",
			"Accept-Encoding" : "gzip, deflate",
			"User-Agent" : "python-m2x/%s" % version
		}
		self.timestamp_format = TIMESTAMP_FORMAT['iso8601']
	
	def updateConfig(self, config):
		self.conf = super(M2XDB, self).updateConfig("M2X", config)
		return True
	
	def update(self, stream, asset):
		if self.is_active:
			try:
				r = requests.post(
					"%s/streams/%s/values" % (self.url, stream), 
					data=json.dumps({ 'values' : [asset]}),
					headers=self.header
				)
			except requests.exceptions.ConnectionError as e:
				print e
				return False
		
			print r.headers
			print r.status_code
			print r.content

			return r.status_code in STATUS_OK

		return False
	
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
		