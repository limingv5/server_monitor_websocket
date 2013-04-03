import sys
import time
import os
import psutil
import json

from twisted.internet import reactor

from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS

os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

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

   def tick(self):
      cpu_usage      = psutil.cpu_percent(interval=1, percpu=True)
      virtual_memory = psutil.virtual_memory()
      harddisk       = psutil.disk_usage('/')
      network        = psutil.network_io_counters()

      self.broadcast(json.dumps({
         'timestamp':time.time()*1000,
         'cpu':cpu_usage,
         'memory':[(virtual_memory[0]-virtual_memory[1])/(1024**2), virtual_memory[1]/(1024**2)],
         'harddisk':[harddisk[1]/(1024**3), (harddisk[0]-harddisk[1])/(1024**3)],
         'network':[network[0], network[1]]
      }))
      reactor.callLater(0.1, self.tick)

   def register(self, client):
      if not client in self.clients:
         print "registered client " + client.peerstr
         self.clients.append(client)

   def unregister(self, client):
      if client in self.clients:
         print "unregistered client " + client.peerstr
         self.clients.remove(client)

   def broadcast(self, msg):
      print "broadcasting message '%s' .." % msg
      for c in self.clients:
         c.sendMessage(msg)
         print "message sent to " + c.peerstr


if __name__ == '__main__':
   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      debug = True
   else:
      debug = False

   ServerFactory = BroadcastServerFactory

   factory = ServerFactory("ws://localhost:9000",
                           debug = debug,
                           debugCodePaths = debug)

   factory.protocol = BroadcastServerProtocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   reactor.run()
