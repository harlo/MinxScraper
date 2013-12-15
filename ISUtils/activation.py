from process_utils import startDaemon, stopDaemon

def activate(schema):
	# if activated, double-fork this scraping process
	from time import sleep
	import re

	print "Activating on %s..." % schema.path
	period_manifest = re.findall(r'(^\d+)(\w)', schema.period)
	if len(period_manifest) == 0:
		return
	
	period_manifest = period_manifest[0]
	num = int(period_manifest[0])
	mult = period_manifest[1]
	
	period = num * 60 * 1000
	if mult == "h":
		period *= 60
	elif mult == "d":
		period *= 60 * 24
	
	schema.scrape()
	'''
	startDaemon(os.path.join(path, "log.txt"), os.path.join(path, "pid.txt"))
	
	while True:
		schema.scrape()
		
		sleep(period)
	'''

def deactivate(path):
	# if deactivated, pull up the pid file and kill
	print "Deactivating..."
	#stopDaemon(os.path.join(path, "pid.txt"))