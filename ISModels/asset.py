import copy, sys, os, json

__metaclass__ = type

emit_omits = ['emit_omits', 'path']

class Asset():
	def __init__(self, extra_omits=None):
		self.emit_omits = copy.deepcopy(emit_omits)
		if extra_omits is not None:
			self.emit_omits.extend(extra_omits)
	
	def emit(self, exclude=None):
		emit = {}
		for key, value in self.__dict__.iteritems():
			if not key in self.emit_omits:
				if type(value) is unicode:
					emit[key] = str(value)
				else:
					emit[key] = value
				
		if exclude is not None:
			for e in exclude:
				try:
					del emit[e]
				except KeyError as e:
					pass
		
		return emit
	
	def save(self):
		conf = open(os.path.join(self.path, "conf.json"), 'wb+')
		conf.write(json.dumps(self.emit()))
		conf.close()
	
	def inflate(self, inflate=None):
		if inflate is None:
			conf = open(os.path.join(self.path, "conf.json"), 'rb')
			inflate = json.loads(conf.read())
			conf.close()
			
		for key, value in inflate.iteritems():
			setattr(self, key, value)