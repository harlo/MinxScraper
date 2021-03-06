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
					replacement = determinePattern(node.string)
					
					if as_test:
						print "\n\nFUZZ NODE PARENT AND TEXT"
						print parent_
					
					if node.previousSibling is not None:
						print node.previousSibling
						
						try:
							node.previousSibling.replaceWith(
								node.previousSibling + replacement)
						except TypeError as e:
							print e
							print "\n\nMODIFYING PARENT AS TEXT NODE"
							
							parent_parent = BeautifulSoup(
								"<div></div>").find_all('div')[0]
							parent_parent.append(parent_)

							rx = '<span class="IS_fuzzed">%s</span>' % node.string
							parent_ = str(parent_parent.contents[0]).replace(
								rx, replacement)
					else:
						# create a previous sibling as text (replacement)
						# previous sibling is text.
						sibling = BeautifulSoup().new_string(replacement)
						node.insert_before(sibling)

					node.extract()
					
					if as_test:
						print parent_
				
				if as_test:
					print "\n\nTEMPLATE:"
					print scrape_doc
				
				if self.contentType in CONTENT_TYPE_XML:
					pathToBody = el['xmlPath'][::-1][1:]
					
					if as_test:
						print "\n\nXML PATH:"
						print pathToBody
						
					for i, p in enumerate(pathToBody):
						nodes = nodes.findall(p)[0]
						if i == len(pathToBody) - 1:
							target_node_found = True
							target_node = BeautifulSoup(nodes.text)
					
				elif self.contentType in CONTENT_TYPE_HTML:
					pathToBody = el['pathToBody'][::-1]
					
					if as_test:
						print "\n\nHTML PATH:"
						print pathToBody
						
					for i, p in enumerate(pathToBody):
						if as_test and target_node is not None:
							print "\n\nNODE TYPES:"
							for b in target_node:
								print type(b)
							print "\n"
						
						try:
							target_node = nodes[p]
							nodes = [e for e in nodes[p].contents if type(e) == element.Tag]
						except IndexError as e:
							print e
							print i, p
							print "only have %d nodes.  Last:\n" % len(nodes)
							print nodes[len(nodes) - 1]					
							
							if as_test:
								pass
								
								
								'''
								print BeautifulSoup(
									"".join([str(e) for e in target_node])).prettify()
								pass
								'''
								
							break
				
						if p == el['pathToBody'][0]:	
							target_node_found = True

				if target_node is None or not target_node_found:
					if as_test:
						print "\n\nTARGET NODE NOT FOUND"
						
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
				
					if as_test:
						print "\n\nPATH TO NODE TOP:"
						print path_to_node_top
				
					if self.contentType in CONTENT_TYPE_XML:
						path_to_node_top = path_to_node_top[::-1][:-1]
					elif self.contentType in CONTENT_TYPE_HTML:
						path_to_node_top = path_to_node_top[1:-1]
					
					if as_test:
						print "\n\nTARGET NODE FROM LIVE HTML"
						print target_node
				
					inner_target_node = None
					inner_target_node_found = False
				
					if as_test:
						print "\n\nTARGET NODE NAME"
						print target_node.name
					
					nodes = [e for e in target_node.contents if type(e) == element.Tag]
					if len(nodes) == 0:
						nodes = BeautifulSoup(target_node.contents[0])
						inner_target_node = nodes
						inner_target_node_found = True
						
					print "\n\nNODES:"
					print nodes
				
					if inner_target_node is None and not inner_target_node_found:
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
								if i == len(path_to_node_top) -1:					
									inner_target_node_found = True
									break
		
					if inner_target_node is not None and inner_target_node_found:
						if as_test:
							print "\n\nINNER TARGET NODE:"
							print inner_target_node
					
						regex = buildRegex(node)
						
						inner_target_content = " ".join(
							[str(s) for s in inner_target_node.contents]
						)
						
						if as_test:
							print "\n\nINNER TARGET CONTENT:"
							print inner_target_content
						
						print "\n\nREGEX:"
						print regex
						match = re.findall(
							re.compile(regex[1]), sanitizeStr(inner_target_content))
						if len(match) >= 1:
							result['matches'] += 1
							result['data'].append({
								regex[0] : match[0].strip()
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
		
		print "\n\nSCRAPE RESULT:"
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