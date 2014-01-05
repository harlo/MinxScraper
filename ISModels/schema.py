import hashlib, os, json, requests, time, re
from multiprocessing import Process
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, element
from vars import CONTENT_TYPE_XML

from asset import Asset

from ISUtils.scrape_utils import isISDataRoot, hasISLabelClass, hasISFuzzClass, buildRegex, asTrueValue, sanitizeStr, determinePattern
from ISUtils.process_utils import startDaemon, stopDaemon

from vars import STATUS_OK, STATUS_FAIL, CONTENT_TYPE_XML, CONTENT_TYPE_HTML

class Schema(Asset):
	def __init__(self, url, create=False, as_test=False, **args):
		super(Schema, self).__init__()
		
		self.url = url
		self._id = hashlib.sha1(self.url).hexdigest()
		
		this_dir = os.path.join(os.path.abspath(__file__), os.pardir)
		par_dir = os.path.join(this_dir, os.pardir)
		user_models_dir = os.path.join(par_dir, "UserModels")
		
		self.path = os.path.abspath(os.path.join(user_models_dir, self._id))
		
		if not as_test:
			if not os.path.exists(self.path):
				if create:
					os.makedirs(self.path)
					self.save()
				else:
					return
			else:
				self.inflate()
		
		self.inflate(inflate=args)
		
	def buildHeaders(self):
		h = {}
		for header in self.headers:
			h[header['name']] = header['value']
		return h
	
	def getEntries(self):
		entries = []
		for root, dir, files in os.walk(self.path):
			for file in files:
				if re.match(r'^[a-zA-Z0-9]{40}.json', file):
					f = open(os.path.join(self.path, file), 'rb')
					entries.append(((json.loads(f.read())), file))
					f.close()
		
		return entries
	
	def syncEntries(self):
		from conf import SYNC_TYPES
		if len(SYNC_TYPES) == 0: return
		
		for entry in self.getEntries():
			has_synched = True
			try:
				for e in entry[0]['data']:
					for key in e.keys():
						value = {
							'value' : e[key]
						}
					
						for sync_type in SYNC_TYPES:
							db = None
						
							if sync_type == "elasticsearch":
								from ISData.elasticsearch import Elasticsearch
								db = Elasticsearch()
							elif sync_type == "m2x":
								from ISData.m2xdb import M2XDB
								db = M2XDB()
						
							if db is not None:
								value['at'] = db.parseTimestamp(entry[0]['timestamp'])
								if not db.indexExists(key):
									if not db.createIndex(key):
										return
								
								has_synched = db.create(key, value)
							else:
								has_synched = False
			except KeyError as e:
				print e
				has_synched = False
							
			if has_synched:
				os.remove(os.path.join(self.path, entry[1]))
						
	def scrape(self, as_test=False):
		result = {
			'result' : STATUS_FAIL[0],
			'matches' : 0,
			'data' : []
		}
		
		if not hasattr(self, "contentType"):
			result['error'] = "no content type!"
			print result
			return result

		if not hasattr(self, "rootElement"):
			result['error'] = "no root element!"
			print result
			return result
	
		params = None
		urls = [self.url]
		
		if not as_test:
			if self.config['IS_config_iterate_url'] != self.url:
				for front, s,v,e, back in re.findall(
					r'(.*)(\[%[s|n]\])(.*)(\[/%[s|n]\])(.*)', self.config['IS_config_iterate_url']):
					operator = re.findall(r'\[%([s|n])\]', s)[0]
					if operator == "n":
						r = [int(d) for d in v.split(",")]
						for d in xrange(r[0], r[1]):
							urls.append(front + str(d) + back)			
					elif operator == "s":
						for d in v.split(","):
							urls.append(front + d + back)
		
		for url in urls:
			print "TRYING URL %s" % url
			if self.method == "GET":
				r = requests.get(url, params=params, headers=self.buildHeaders())
			elif self.method == "POST":
				r = requests.post(url, params=params, headers=self.buildHeaders())
			
			if not r.status_code in STATUS_OK:
				result['result'] = STATUS_FAIL[1]
				result['error'] = "request failed. try again later"
			
				print result
				return result
		
			result['timestamp'] = r.headers['date']
		
			if self.contentType in CONTENT_TYPE_XML:
				doc = ET.fromstring(r.content)
				nodes = doc
			
			elif self.contentType in CONTENT_TYPE_HTML:
				doc = BeautifulSoup(r.content).find(self.rootElement)		
				nodes = [e for e in doc.contents if type(e) == element.Tag]
			
			target_node = None
		
			for el in self.elements:
				scrape_doc = list(
					BeautifulSoup(el['innerHtml'])
						.find(isISDataRoot).children
				)[0]
				scrape_nodes = scrape_doc.find_all(hasISLabelClass, recursive=True)
				if len(scrape_nodes) == 0:
					continue
				
				target_node_found = False
			
				if self.contentType in CONTENT_TYPE_XML:
					to_keep = []
					for p in [e for e in scrape_doc.contents if type(e) == element.Tag]:
						try:
							if "text" in p.attrs['class']:
								to_keep.extend([str(e) for e in p.contents if e != ""])
						except KeyError as e:
							print e
							pass
				
					scrape_doc = BeautifulSoup("".join(to_keep))
					scrape_nodes = scrape_doc.find_all(hasISLabelClass, recursive=True)
			
				#replace the fuzznodes
				fuzz_nodes = scrape_doc.find_all(hasISFuzzClass, recursive=True)
				for node in fuzz_nodes:
					parent_ = node.parent
					node.previousSibling.replaceWith(node.previousSibling + determinePattern(node.string))
					node.extract()
				
				if self.contentType in CONTENT_TYPE_XML:
					pathToBody = el['xmlPath'][::-1][1:]
					for i, p in enumerate(pathToBody):
						nodes = nodes.findall(p)[0]
						if i == len(pathToBody) - 1:
							target_node_found = True
							target_node = BeautifulSoup(nodes.text)
					
				elif self.contentType in CONTENT_TYPE_HTML:
					for p in el['pathToBody'][::-1]:
						try:
							target_node = nodes[p]
							nodes = [e for e in nodes[p].contents if type(e) == element.Tag]
						except IndexError as e:
							print e
							break
				
						if p == el['pathToBody'][0]:	
							target_node_found = True
	
				if target_node is None or not target_node_found:	
					continue
			
				for node in scrape_nodes:	
					path_to_node_top = []
					parent = node.parent
					sibling = node
												
					while parent is not None:
						sibling_path = 0
						for p in [e for e in parent.contents if type(e) == element.Tag]:
							if p == sibling:
								path_to_node_top.append(sibling_path)
								break
							sibling_path += 1

						sibling = parent
						parent = parent.parent
				
					#print path_to_node_top
				
					if self.contentType in CONTENT_TYPE_XML:
						path_to_node_top = path_to_node_top[::-1][:-1]
					elif self.contentType in CONTENT_TYPE_HTML:
						path_to_node_top = path_to_node_top[1:-1]
					
					#print path_to_node_top
				
		
					inner_target_node = None
					inner_target_node_found = False
				
					nodes = [e for e in target_node.contents if type(e) == element.Tag]
				
					for i, p in enumerate(path_to_node_top):
						'''
						print i, p
						print BeautifulSoup("".join([str(e) for e in nodes])).prettify()
						print [e.name for e in nodes]
						print "\n*********\n"
						'''
				
						try:
							inner_target_node = nodes[p]
							nodes = [e for e in nodes[p].contents if type(e) == element.Tag]
							if i == len(path_to_node_top) -1:
								inner_target_node_found = True
						except IndexError as e:
							print e, i, p
							if i == len(path_to_node_top) -1:					
								inner_target_node_found = True
								break
		
					if inner_target_node is not None and inner_target_node_found:
						#print inner_target_node
					
						regex = buildRegex(node)
						print regex
						inner_target_content = " ".join(
							[str(s) for s in inner_target_node.contents]
						)
					
						match = re.findall(re.compile(regex[1]), inner_target_content)
						if len(match) >= 1:
							result['matches'] += 1
							result['data'].append({
								regex[0] : match[0]
							})

			result['result'] = STATUS_OK[0]
			if result['matches'] == 0:
				del result['data']
		
			if not as_test:
				scrape_result = json.dumps(result)
				scrape_hash = hashlib.sha1(scrape_result).hexdigest()
			
				f = open(os.path.join(self.path, "%s.json" % scrape_hash), 'wb+')
				f.write(scrape_result)
				f.close()				
		
		print result
		return result
	
	def sync(self, period):
		startDaemon(
			os.path.join(self.path, "log.txt"), 
			os.path.join(self.path, "pid.txt")
		)
		while True:
			self.scrape()
			self.syncEntries()
			time.sleep(period)
	
	def activate(self, activate=True):
		self.is_active = activate
		result = {
			'result' : STATUS_OK[0]
		}
		
		if activate:
			period = 0
			try:
				period = int(self.config['IS_config_period']) * 60 * 1000
				if self.config['IS_config_period_mult'] == "h":
					period *= 60
				elif self.config['IS_config_period_mult'] == "d":
					period *= 60 * 24
			
			except KeyError as e:
				result['result'] = STATUS_FAIL[0]
				result['error'] = e
			
			if period == 0:	
				self.save()
				return result
			
			p = Process(target=self.sync, args=(period,))
			p.start()
		else:
			stopDaemon(os.path.join(self.path, "pid.txt"))
		
		self.save()
		return result