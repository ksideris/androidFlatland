
#!/usr/bin/env python

"""server.py: The core networking module. Transmits the serialized state to the clients-phones and reads their states.

"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"




import logging

import pickle,time,sys #TODO change to cPickle for speed
import shelve,os,socket

SERVERDATA= 'ServerState.db'
CLIENTDATA= 'ClientState.db'




class UDPServer():

        
        
    def start(self,UDP_IP,UDP_PORT):
                
                

                
                self.sockin = socket.socket( socket.AF_INET, # Internet
                                      socket.SOCK_DGRAM ) # UDP

                host = socket.gethostname()
                self.sockin.bind( ( socket.gethostbyname(host),UDP_PORT) )
                self.sockin.setblocking(False)
                self.sockout = socket.socket( socket.AF_INET, # Internet
                                      socket.SOCK_DGRAM ) # UDP

                
                if os.path.exists(CLIENTDATA):
                    os.remove(CLIENTDATA)
    
                while True:
                    try:
                        data, addr = self.sockin.recvfrom( 1024 ) # buffer size is 1024 bytes
                        #print "received message:", data," from ",addr
                        #print (data.split('&')[0],data.split('&')[1])
                        
        
                        serv_db = shelve.open(SERVERDATA)

                        try:

                            ServerState = serv_db['data']['string']             
                            
                            self.sockout.sendto( ServerState,(data.split('&')[0],int(data.split('&')[1])) )
                            #self.sockout.sendto( 'Hello',(data.split('$')[0],int(data.split('$')[1])) )
                        except:
                            pass
                            
                        finally:
                            serv_db.close()
                            
                        
                        
                        ClientState = data.split('&')[2]+'$'+data.split('&')[3]+'$'+data.split('&')[4]+'$'+data.split('&')[5]+'$'+data.split('&')[6]
                        
                       
                        client_db = shelve.open(CLIENTDATA)
                        try:
                            client_db[data.split('&')[2]] = {'time':time.time(),'string':ClientState}
                        finally:
                            client_db.close()


                    except:
                        pass



if __name__ == '__main__':
    s=Server()
    s.start('127.0.0.1',80)
