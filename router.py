import sys, os

from ISModels.schema import Schema

usage_prompt = """

MinxScraper!
				
Usage:
-[add|get|set|sync|-activate|-deactivate] [url] [auth=true|false][period=3m|4h][method=get|post]

"""

if __name__ == "__main__":	
	if len(sys.argv) < 2:
		sys.exit(usage_prompt)
	
	root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UserModels")
	if not os.path.exists(root_dir):
		os.makedirs(root_dir)	
	
	tasks = []
	for a in xrange(1, len(sys.argv)):
		if sys.argv[a].startswith("-"):
			task = [sys.argv[a]]

			m = a + 1
			while not m >= len(sys.argv):
				if sys.argv[m].startswith("-"):
					break
				else:
					task.append(sys.argv[m])
					m += 1
				

			tasks.append(task)
	
	for task in tasks:
		params = {}
		
		for t in xrange(2, len(task)):
			param = task[t].split("=")
			if len(param) != 2:
				continue
			
			params[param[0]] = param[1]
		
		create = False
		if task[0] == "-add":
			create = True

		is_ = Schema(task[1], create=create, **params)
		
		if task[0] == "-add":
			activation = is_.activate()
			if activation['result'] == True:
				sys.exit("\nSchema %s added and activated.\n" % is_._id)
			else:
				sys.exit("\nSchema %s added but could not be activated:\n%s\n" % (
					is_._id, activation['reason']
				))
		elif task[0] == "-activate":
			activation = is_.activate()
			if activation['result'] == True:
				sys.exit("\nSchema %s activated.\n" % is_._id)
			else:
				sys.exit("\nSchema %s could not be activated:\n%s\n" % (
					is_._id, activation['reason']
				))
		elif task[0] == "-deactivate":
			is_.activate(activate=False)
			sys.exit("\nSchema %s deactivated.\n" % is_._id)
		elif task[0] == "-set":
			is_.save()
			sys.exit("\nSchema %s modified:\n%s\n" % (is_._id, params))
		elif task[0] == "-get":
			sys.exit("\n%s\n" % is_.emit())
		elif task[0] == "-sync":
			is_.sync()
			sys.exit("\nSyncing %s\n" % is_._id)