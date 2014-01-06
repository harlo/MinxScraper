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

def hasISFuzzClass(tag):
	if tag.name == "span":
		if tag.has_attr('class') and 'IS_fuzzed' in tag.attrs['class']:
			return True
	
	return False

def isISDataRoot(tag):
	if tag.name == "div":
		if tag.has_attr('class') and 'IS_data_holder' in tag.attrs['class']:
			return True
	
	return False
	
def sanitizeStr(str):
	str = str.replace('\t',"")
	str = str.replace('\n', "")
	str = str.replace('\r', "")
	return str

def sanitizeForRegex(str):
	# remove whitespace
	str = sanitizeStr(str)
	str = str.replace('<br/>',"")
	str = str.replace('(', '\(')
	str = str.replace(')', '\)')
	str = str.replace('-', '\-')
	
	return str.strip()

def doubleSanitizeForRegex(str):
	str = sanitizeForRegex(str)
	
	str = str.replace('+', '\+')
	str = str.replace('?', '\?')
	str = str.replace('.', '\.')
	
	return str.strip()
	
def determinePattern(str):
	pattern = '.+'
	if type(asTrueValue(str)) == int:
		pattern = '\d+'
	
	return pattern

def isEmptyRegex(regex):
	empty_regex = '\.\*[\s| ]*\(\.\+\)[\s| ]*\.\*'
	rx = re.findall(re.compile(empty_regex), regex)
	
	print "\n\nCHECKING \'%s\' FOR MEANINGLESS REGEX:" % regex
	print rx
	
	if len(rx) > 0:
		return True

	return False

def buildRegex(tag):
	if type(tag) == element.Tag:
		txt = tag.get_text()
	else:
		txt = str(tag)
		
	print "\n\nTAG/TXT FROM REGEX:"
	print txt
		
	pattern = "(" + determinePattern(txt) + ")"
	
	parent = "".join(str(e) for e in tag.parent.contents)
	segments = [doubleSanitizeForRegex(e) for e in parent.split(str(tag))]
	pattern = ('.*' + segments[0] + pattern + segments[1] + '.*')
	
	if isEmptyRegex(pattern):
		pattern = "(.*)"
	
	return tag.attrs['id'].replace("IS_start_", ""), pattern