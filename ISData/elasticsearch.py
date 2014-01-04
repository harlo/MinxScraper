import requests, json, hashlib
from database import Database

from ISModels import Asset
from vars import TIMESTAMP_FORMAT

class Elasticsearch(Database):
	def __init__(self):
		super(Elasticsearch, self).__init__()
		
		try:
			f = open(getConf(os.path.abspath(__file__)), 'rb')
			els_conf = json.loads(f.read())['ELS']
			f.close()
		except:
			els_conf = {
				'port' : 9200,
				'root_name' : "minx"
			}
			
		port = els_conf['port']
		root_name = els_conf['root_name']
		
		try:
			self.is_active = els_conf['is_active']
		except KeyError as e:
			print "is_active not yet set for Elasticsearch.  using False as default"
			self.is_active = False
		
		self.url = "http://localhost:%d/%s/" % (port, root_name)
		self.timestamp_format = TIMESTAMP_FORMAT['milliseconds']
	
	def get(self, river, _id):
		try:
			r = requests.get("%s%s/%s" % (self.url, river, _id))
		except requests.exceptions.ConnectionError as e:
				print e
				return None

		result = json.loads(r.text)
		
		try:
			if result['exists']:
				return result['_source']
		except KeyError as e:
			print e
		
		return None
	
	def delete(self, river, _id):
		try:
			r = requests.delete("%s%s/%s" % (self.url, river, _id))
		except requests.exceptions.ConnectionError as e:
				print e
				return False

		result = json.loads(r.text)
		
		try:
			return result['ok']
		except KeyError as e:
			print r.text
		
		return False
	
	def update(self, river, asset, _id):
		if self.is_active:
			try:
				r = requests.put("%s%s/%s" % (self.url, river, _id), data=json.dumps(asset))
			except requests.exceptions.ConnectionError as e:
					print e
					return False

			print r.text
			result = json.loads(r.text)
		
			try:
				return result['ok']
			except KeyError as e:
				print r.text

		return False
	
	def create(self, river, asset, _id=None):
		if _id is None:
			_id = hashlib.sha1(json.dumps(asset)).hexdigest()
		return self.update(river, asset, _id)
	
	def indexExists(self, river):
		try:
			r = requests.get("%s%s" % (self.url, river))
		except requests.exceptions.ConnectionError as e:
				print e
				return False
		
		try:
			result = json.loads(r.text)
		except ValueError as e:
			print r.text
			return False
		
		print r.text
		return False
	
	def createIndex(self, mappings=None, reindex=True):
		if reindex:
			try:
				r = requests.delete(self.url)
			except requests.exceptions.ConnectionError as e:
				print e
				return False
				
			result = json.loads(r.text)
			
			try:
				if result['error']:
					pass
			except KeyError as e:
				print r.text
		
		if mappings is not None:
			mappings = json.dumps({
				"mappings" : mappings
			})
		
		try:
			r = requests.put(self.url, data=mappings)
		except requests.exceptions.ConnectionError as e:
				print e
				return False

		result = json.loads(r.text)
		
		try:
			return result['ok']
		except:
			print r.text
		
		return False