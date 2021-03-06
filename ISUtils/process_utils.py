import os, sys, signal, re, json

def getConf(from_path):
	this_dir = os.path.join(from_path, os.pardir)
	par_dir = os.path.join(this_dir, os.pardir)
	
	return os.path.abspath(os.path.join(par_dir, "conf.json"))

def getScrapers(from_path):
	scrapers = []
	for root, dir, files in os.walk(from_path):
		for file in files:
			if re.match(r'conf\.json', file) is not None:
				f = open(os.path.join(root, file), 'rb')
				try:
					scraper = json.loads(f.read())
					del scraper['elements']
					del scraper['rootElement']
					scrapers.append(scraper)
				except:
					pass

				f.close()
	
	if len(scrapers) > 0:
		return scrapers
		
	return None

def startDaemon(log_file, pid_file):
	print "DAEMONIZE"
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError, e:
		print e.errno
		sys.exit(1)
	
	os.chdir("/")
	os.setsid()
	os.umask(0)
	
	try:
		pid = os.fork()
		if pid > 0:
			f = open(pid_file, 'w')
			f.write(str(pid))
			f.close()
			
			sys.exit(0)
	except OSError, e:
		print e.errno
		sys.exit(1)
	
	si = file('/dev/null', 'r')
	so = file(log_file, 'a+')
	se = file(log_file, 'a+', 0)
	
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

def stopDaemon(pid_file):
	pid = False
	try:
		f = open(pid_file, 'r')
		try:
			pid = int(f.read().strip())
		except ValueError as e:
			print "NO PID AT %s" % pid_file
	except IOError as e:
		print "NO PID AT %s" % pid_file
		
	if pid:
		print "STOPPING DAEMON on pid %d" % pid
		try:
			os.kill(pid, signal.SIGTERM)
			return True
		except OSError as e:
			print "could not kill process at PID %d" % pid

	return False