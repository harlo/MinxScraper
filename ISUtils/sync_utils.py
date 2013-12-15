import json, hashlib, re, requests
from requests.exceptions import HTTPError

from m2x.client import M2XClient
from m2x import version
from conf import M2X_Conf

api_key = M2X_Conf['api_key']
feed_id = M2X_Conf['feed_id']
master_key = M2X_Conf['master_key']

root_url = "http://api-m2x.att.com/v1"
header = {
	"X-M2X-KEY" : api_key,
	"Content-type" : "application/json",
	"Accept-Encoding" : "gzip, deflate",
	"User-Agent" : "python-m2x/%s" % version
}

success = [204, 200, 201]
fail = [404, 403, 405]

def sanitizeName(name):
	name = name.replace(" ","_")
	name = name.replace("(", "")
	name = name.replace(")", "")
	return str(name).lower()

class Sync():
	def __init__(self, location=None):
		self.client = M2XClient(key=api_key)
		self.feed = None
	
		try:
			self.feed = self.client.feeds.details(feed_id)
		except HTTPError as e:
			return
			
	def postValue(self, stream, **args):
		url = "%s/feeds/%s/streams/%s" % (root_url, self.feed.id, stream)
		
		print "\n\n"
		print "posting new value to %s" % url
		print "values:\n%s" % args
		
		r = requests.put(url, data=json.dumps(args), headers=header)
		print r.content
		print r.headers
		print r.url
		
		print r.status_code in success
		print "\n\n"
		
		return r.status_code in success
	
	def getStream(self, name):
		url = "%s/feeds/%s/streams/%s" % (root_url, self.feed.id, name)
		
		print "\n\n"
		print "getting stream at %s" % url
		
		r = requests.get(url, headers=header)
		print r.content
		print r.headers
		print r.url
		
		print r.status_code in success
		print "\n\n"
		
		return r.status_code in success
		
			
	def createStream(self, name, **args):
		url = "%s/feeds/%s/streams/%s" % (root_url, self.feed.id, name)
		
		print "\n\n"
		print "creating stream at %s" % url
		
		print "with the following arguments:\n%s" % args		
		r = requests.put(url, data=json.dumps(args), headers=header)
		
		print r.content
		print r.headers
		print r.url
		
		print r.status_code in success
		print "\n\n"
		
		return r.status_code in success
		
	def syncData(self, data):
		if self.feed is None:
			return False

		try:
			f = open(data, 'rb')
			data = f.read()
			f.close()
		except IOError as e:
			return False
		
		for d in json.loads(data)['data']:
			for key, value in d.iteritems():
				has_value = re.findall(r'(\w+)_value', key)
				has_unit = re.findall(r'(\w+)_unit', key)
				
				stream_name = None
				stream_value = {}
				stream_unit = {}
				
				if len(has_value) == 1:
					stream_name = has_value[0]
					stream_value = {
						'value' : value
					}
				elif len(has_unit) == 1:
					stream_name = has_unit[0]
					stream_unit = {
						'unit' : {
							'label' : value,
							'symbol' : value
						}
					}
				
				if stream_name is None:
					continue
				
				if not self.getStream(sanitizeName(stream_name)):
					if not self.createStream(sanitizeName(stream_name), **stream_unit):
						continue
					
				if len(stream_value.keys()) > 0:
					self.postValue(stream_name, **stream_value)
		
		return True