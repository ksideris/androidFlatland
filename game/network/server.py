
#!/usr/bin/env python

"""server.py: The core networking module. Transmits the serialized state to the clients-phones and reads their states.

"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"




import logging
from tornado.simple_httpclient import SimpleAsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
import pickle,time,sys #TODO change to cPickle for speed
import shelve,os

SERVERDATA= 'ServerState.db'
CLIENTDATA= 'ClientState.db'



class GameStateTransmitter(RequestHandler):
    
    
    
    def get(self):
        args= self.request.arguments
        
        serv_db = shelve.open(SERVERDATA)

        try:

            ServerState = serv_db['data']['string']             
            self.write(ServerState)
            self.flush()
            self.finish()
        except:
            pass
            
        finally:
            serv_db.close()
            
        
        
        ClientState = args['id'][0]+'$'+args['team'][0]+'$'+args['action'][0]+'$'+args['pos'][0]+'$'+args['time'][0]
        
       
        client_db = shelve.open(CLIENTDATA)
        try:
            client_db[args['id'][0]] = {'time':time.time(),'string':ClientState}
        finally:
            client_db.close()
            
        

class Server():

	def start(self,server_address,server_port):
                if os.path.exists(CLIENTDATA):
                    os.remove(CLIENTDATA)
	
		app = Application([('/', GameStateTransmitter)])
		app.listen(server_port, address=server_address)
	   
		IOLoop.instance().start()


if __name__ == '__main__':
	s=Server()
	s.start('192.168.1.103','80')
