from bs4 import BeautifulSoup, element
import xml.etree.ElementTree as ET
import re, json, time

def asTrueValue(str_value):
	try:
		if str_value.startswith("[") and str_value.endswith("]"):
			vals = []
			for v_ in str(str_value[1:-1]).split(","):
				vals.append(AsTrueValue(v_))

			return vals
		if str_value.startswith("{") and str_value.endswith("}"):
			return json.loads(str_value)
		if str_value == "0":
			return int(0)
		if str_value == "true":
			return True
		if str_value == "false":
			return False
		if type(str_value) is unicode:
			return unicode.join(u'\n', map(unicode, str_value))
	except AttributeError:
		pass
	
	try:
		if int(str_value):
			return int(str_value)
	except ValueError:
		pass
		
	try:
		if float(str_value):
			return float(str_value)	
	except ValueError:
		pass
		
	return str_value

def cleanup(str):
	str = str.replace("\t", "")
	str = str.replace("\n", "")
	
	return str
	
def buildRegex(pattern):	
	refined_pattern = "".join([cleanup(str(el)) for el in pattern if cleanup(str(el)) != ""])
	parts = pattern.find_all(attrs= {
		'id' : re.compile(r'IS_start_.*')
	})
	
	labels = []
	print refined_pattern
	for p in parts:
		labels.append(p['id'].replace("IS_start_",""))
		val_type = type(asTrueValue(str(p.get_text())))
		comp = "(.+)"
		if val_type is int:
			comp = "(\d+)"
		
		refined_pattern = refined_pattern.replace(str(p), comp)
	
	refined_pattern = refined_pattern.replace('-', '\-')
	print refined_pattern
	return (refined_pattern, labels)

def parse(html, template):
	res = []	
	doc = BeautifulSoup(html)
	
	try:
		f = open(template, 'rb')
		mapping = BeautifulSoup(f.read())
		f.close()
	except IOError as e:
		return (None, 404)
	
	doc_root = mapping.contents[0]
	
	# for each data holder, get its sibling index and the upward path to doc_root		
	for dh in mapping.find_all(id="IS_data_holder"):
		path_from_parent = []
		pattern, labels = buildRegex(dh.find_all(id="IS_start_data_block")[0])
		
		parent = dh.parent
		sibling = dh
		
		while parent is not None:
			sibling_path = 0
			try:
				for p in [el for el in parent.contents if type(el) == element.Tag]:
					if p == sibling:
						path_from_parent.append(sibling_path)
						break
					
					sibling_path += 1
			
				sibling = parent
				parent = parent.parent
			except AttributeError as e:
				break		
				
		match_data = [el for el in doc.contents if type(el) == element.Tag][0].parent
		for p in path_from_parent[::-1]:
			els = [e for e in match_data.contents if type(e) == element.Tag]			
			match_data = els[p]
					
		sanitized = [cleanup(el) for el in match_data.contents if type(el) == element.NavigableString and cleanup(el) != ""]

		for m in sanitized:
			match = re.findall(re.compile(pattern), m)
			if len(match) >= 1:
				for m_ in match:
					match_ = list(m_)
					
					labels.append("timestamp")
					match_.append(time.time() * 1000)
					
					res.append(dict(zip(labels, match_)))
		
		return (res, 200)
			
def xmlDrill(obj, tag, idx):
	doc = obj.findall(tag)
	if type(doc) == list:
		return doc[idx]
	else:
		return doc