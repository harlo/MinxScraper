import hashlib, os, json, requests, time, re
from bs4 import BeautifulSoup, element

from asset import Asset

from ISUtils.scrape_utils import isISDataRoot, hasISLabelClass, buildRegex, asTrueValue
from ISUtils.process_utils import startDaemon, stopDaemon

from vars import STATUS_OK, STATUS_FAIL, CONTENT_TYPE_XML, CONTENT_TYPE_HTML

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
		
	def buildHeaders(self):
		h = {}
		for header in self.headers:
			h[header['name']] = header['value']
		return h
	
	def scrape(self):
		result = {
			'result' : STATUS_FAIL[0],
			'matches' : 0,
			'data' : []
		}
		
		if not hasattr(self, "contentType"):
			result['error'] = "no content type!"
			return result
		else:
			print self.contentType

		if not hasattr(self, "rootElement"):
			result['error'] = "no root element!"
			return result
		else:
			print "root is %s" % self.rootElement
	
		params = None
		if self.method == "GET":
			r = requests.get(self.url, params=params, headers=self.buildHeaders())
		elif self.method == "POST":
			r = requests.post(self.url, params=params, headers=self.buildHeaders())
			
		if not r.status_code in STATUS_OK:
			result['result'] = STATUS_FAIL[1]
			result['error'] = "request failed. try again later"
			return result
		
		result['timestamp'] = r.headers['date']
		
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
				path_to_node_top = path_to_node_top[1:-1]
		
				inner_target_node = None
				inner_target_node_found = False
				nodes = [e for e in target_node.contents if type(e) == element.Tag]
				for i, p in enumerate(path_to_node_top):
					try:
						inner_target_node = nodes[p]
						nodes = [e for e in nodes[p].contents if type(e) == element.Tag]
					except IndexError as e:
						if i == len(path_to_node_top) -1:					
							inner_target_node_found = True
							break
		
				if inner_target_node is not None and inner_target_node_found:
					regex = buildRegex(node)
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
		
		scrape_result = json.dumps(result)
		scrape_hash = hashlib.sha1(scrape_result).hexdigest()

		f = open(os.path.join(self.path, "%s.json" % scrape_hash), 'wb+')
		f.write(scrape_result)
		f.close()				
		
		print result	
		return result
	
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
			
			'''
			startDaemon(
				os.path.join(self.path, "log.txt"), 
				os.path.join(self.path, "pid.txt")
			)
			while True:
				self.scrape()
				time.sleep(period)
			'''
			self.scrape()
		else:
			stopDaemon(os.path.join(self.path, "pid.txt"))
		
		self.save()
		return result