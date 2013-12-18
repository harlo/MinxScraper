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
		
		if self.timestamp_format == TIMESTAMP_FORMAT['milliseconds']:
			pass
		elif self.timestamp_format == TIMESTAMP_FORMAT['iso8601']:
			pass
		
		return timestamp