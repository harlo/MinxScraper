import time
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
	
	def parseTimestamp(self, timestamp):
		print "parsing timestamp %s according to %d" % (timestamp, self.timestamp_format)
		t = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
		
		if self.timestamp_format == TIMESTAMP_FORMAT['milliseconds']:
			timestamp = int(time.mktime(t))
		elif self.timestamp_format == TIMESTAMP_FORMAT['iso8601']:
			timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", t)
		
		print timestamp
		return timestamp