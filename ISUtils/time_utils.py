import time
from vars import TIMESTAMP_FORMAT

def parseTimestamp(timestamp, format):
	t = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
	
	if format == TIMESTAMP_FORMAT['milliseconds']:
		return int(time.mktime(t))
	elif format == TIMESTAMP_FORMAT['iso8601']:
		return time.strftime("%Y-%m-%dT%H:%M:%S", t)
	
	return timestamp
