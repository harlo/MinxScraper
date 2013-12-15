import hashlib, os, json, requests, time, re
from bs4 import BeautifulSoup
from asset import Asset

class Schema(Asset):
	def __init__(self, url, create=False, **args):
		super(Schema, self).__init__()
		
		self.url = url
		self._id = hashlib.sha1(self.url).hexdigest()
		
		this_dir = os.path.join(os.path.abspath(__file__), os.pardir)
		par_dir = os.path.join(this_dir, os.pardir)
		user_models_dir = os.path.join(par_dir, "UserModels")
		
		self.path = os.path.abspath(os.path.join(user_models_dir, self._id))
		
		if not os.path.exists(self.path):
			if create:
				os.makedirs(self.path)
				self.save()
			else:
				return
		else:
			self.inflate()
			
		self.inflate(inflate=args)
	
	def scrape(self):
		data = None
		print "Scraping %s" % self.url
				
		if hasattr(self, "data"):
			data = self.data
			print json.loads(data)
		
		if self.method == "get":
			r = requests.get(self.url, params=json.dumps(data))
		elif self.method == "post":
			print "as post: %s" % ("%s?%s" % (self.url, data))
			r = requests.post(self.url, data=json.dumps(data))
		
		if r.status_code != 200:
			return (None, r.status_code)
		
		if hasattr(self, "dataType"):
			dataType = self.dataType
		else:
			dataType = "html"
		
		parse_content = r.content
		from ISUtils.soup_utils import parse
		
		if dataType == "html":
			if hasattr(self, "mapping"):
				pass
	
		elif dataType == "xml":
			import xml.etree.ElementTree as ET
			from ISUtils.soup_utils import xmlDrill
			
			doc = ET.fromstring(r.content)
			if hasattr(self, "mapping"):
				mapping = self.mapping.split(".")
				
				obj = doc
				for m in mapping:
					if m.startswith("["):
						idx = int(m[1:-1])
						if idx == 0:
							parse_content = obj.text
						else:
							parse_content = obj[idx].text
					else:
						obj = xmlDrill(obj, m, 0)				
			
		data, result = parse(parse_content, os.path.join(self.path, "mapping.html"))
		if result == 200:
			data_dump = os.path.join(self.path, "%s.json" % hashlib.sha1(json.dumps(data) + "_" + str(time.time())).hexdigest())
			
			f = open(data_dump, 'wb+')
			f.write(json.dumps({'data': data}))
			f.close()
	
	def activate(self, activate=True):
		self.is_active = activate
		res = {
			'result' : True
		}
		
		if activate:
			from ISUtils.activation import activate
			if hasattr(self, "period"):
				activate(self)
			else:
				self.is_active = False
				res = {
					'result' : False,
					'reason' : "No sync period.  Please set the sync period by running \n\n-set [url] period=[sync period]\n\nand running -activate [url]"
				}
		else:
			from ISUtils.activation import deactivate
			deactivate(self.path)
		
		self.save()
		return res
	
	def sync(self):
		from ISUtils.sync_utils import Sync
		sync = Sync()
		
		for root, dir, files in os.walk(self.path):
			for file in files:				
				if re.match(r'[conf\.json|mapping\.html|pid\.txt|log\.txt]', file):
					continue
				
				sync.syncData(os.path.join(self.path, file))
		