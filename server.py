import sys
import time
import os
import psutil
import json
import ConfigParser
import logging

from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

os.environ["TZ"] = "Asia/Shanghai"
time.tzset()
config = ConfigParser.ConfigParser()

def logInfo(info):
	logger = logging.getLogger("wslog")
	logger.setLevel(logging.INFO)

	localtime = time.localtime(time.time())
	year   = time.strftime('%Y',localtime)
	month  = time.strftime('%m',localtime)
	day    = time.strftime('%d',localtime)
	logdir = config.get("path", "log")

	path1 = os.path.join(logdir, year)
	if os.path.exists(path1) == False:
		os.makedirs(path1)
	path2 = os.path.join(path1, month)
	if os.path.exists(path2) == False:
		os.makedirs(path2)
	
	fh = logging.FileHandler(os.path.join(path2, day))
	fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
	
	logger.addHandler(fh)
	logger.info(info)
	logger.removeHandler(fh)

class BroadcastServerProtocol(WebSocketServerProtocol):
	def onOpen(self):
		self.factory.register(self)

	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
	def __init__(self, url, debug = False, debugCodePaths = False):
		WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
		self.clients = []
		self.tick()

	def register(self, client):
		if not client in self.clients:
			print "registered client " + client.peerstr
			self.clients.append(client)
			logInfo("registered:"+client.peerstr)

	def unregister(self, client):
		if client in self.clients:
			print "unregistered client " + client.peerstr
			self.clients.remove(client)
			logInfo("unregistered:"+client.peerstr)

	def broadcast(self, msg):
		print "broadcasting message '%s' .." % msg
		for c in self.clients:
			c.sendMessage(msg)
			print "message sent to " + c.peerstr
			
	def tick(self):
		cpu_usage      = psutil.cpu_percent(interval=1, percpu=True)
		virtual_memory = psutil.virtual_memory()
		harddisk       = psutil.disk_usage('/')
		network        = psutil.network_io_counters()
		
		sys_info = json.dumps({
			'timestamp'	: time.time()*1000,
			'cpu'		: cpu_usage,
			'memory'	: [(virtual_memory[0]-virtual_memory[1])/(1024**2), virtual_memory[1]/(1024**2)],
			'harddisk'	: [harddisk[1]/(1024**3), (harddisk[0]-harddisk[1])/(1024**3)],
			'network'	: [network[0], network[1]]
		})
		self.broadcast(sys_info)
		reactor.callLater(0.1, self.tick)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'debug':
		debug = True
	else:
		debug = False

	ServerFactory = BroadcastServerFactory

	try:
		rp = os.path.realpath(__file__)
		config.read(os.path.dirname(os.path.dirname(rp))+"/config.ini")
		factory = ServerFactory("ws://localhost:"+config.get(os.path.splitext(os.path.basename(rp))[0], "port"), debug = debug, debugCodePaths = debug)
	except:
		exit()

	factory.protocol = BroadcastServerProtocol
	factory.setProtocolOptions(allowHixie76 = True)
	listenWS(factory)

	reactor.run()
