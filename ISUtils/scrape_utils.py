from bs4 import BeautifulSoup, element
import xml.etree.ElementTree as ET
import re, json

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

def hasISLabelClass(tag):
	if tag.name == "span":
		if tag.has_attr('class') and 'IS_label' in tag.attrs['class']:
			return True
	
	return False

def isISDataRoot(tag):
	if tag.name == "div":
		if tag.has_attr('class') and 'IS_data_holder' in tag.attrs['class']:
			return True
	
	return False

def buildRegex(tag):
	pattern = '(.+)'
	if type(asTrueValue(tag.get_text())) == int:
		pattern = '(\d+)'
	
	return tag.attrs['id'].replace("IS_start_", ""), pattern