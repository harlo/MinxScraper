import time, json, os
from vars import TIMESTAMP_FORMAT
__metaclass__ = type

class Database():
	def __init__(self, **args):
		print "Initing database api..."
	
	def get(self, **args):
		print "getting asset by id"
	
	def delete(self, **args):
		print "deleting asset by id"
	
	def update(self, **args):
		print "updating/creating asset on feed"
	
	def create(self, **args):
		print "creating asset on feed"
	
	def indexExists(self, **args):
		print "checking to see if feed exists on database"
	
	def createIndex(self, **args):
		print "creating a new index on database"
	
	def updateConfig(self, db_name, config):
		print "updating sync properties for this database"
		from ISUtils.process_utils import getConf
		
		f = open(getConf(os.path.abspath(__file__)), 'rb')
		c = json.loads(f.read())
		f.close()
		
		for key in config.keys():
			c[db_name][key] = config[key]
		
		f = open(getConf(os.path.abspath(__file__)), 'wb+')
		f.write(json.dumps(c))
		f.close()
		
		return c[db_name]
	
	def parseTimestamp(self, timestamp):
		print "parsing timestamp %s according to %d" % (timestamp, self.timestamp_format)
		t = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
		
		if self.timestamp_format == TIMESTAMP_FORMAT['milliseconds']:
			timestamp = int(time.mktime(t))
		elif self.timestamp_format == TIMESTAMP_FORMAT['iso8601']:
			timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", t)
		
		print timestamp
		return timestamp