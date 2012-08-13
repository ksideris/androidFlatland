
#!/usr/bin/env python

"""AsyncClient.py: asynchronous networking client"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"



import socket,pickle,time,string,sys
try:
    from  game.clientEnvironment import *
except:
    pass

SHOW_STATISTICS =False
ID = 0


class UDPClient():
    def __init__(self,client):
        self.myclient = client
        
    def MakeRequest(self,pid,team,action,position):
        #global ID
        #ID  = pid
        start =time.time()
        message = str(self.address)+'&'+str(60000+pid+1)+'&'+str(pid)+'&'+str(team)+'&'+str(action)
        #print message,action
        if position<>None: 
                message+='&'+str(position[0])+','+str(position[1])
        message+='&'+str(time.time())
        #print message
        #client = HTTPClient(self.client,self.server_address,self.server_port, message)
        #asyncore.loop()
    
        
        try:
            data, addr = self.sockin.recvfrom( 1024 ) # buffer size is 1024 bytes
            #print "received data:", data
            self.myclient.deSerialize(data)
        except:
            print "Unexpected error:", sys.exc_info()[0]

        self.sockout.sendto( message , (self.server_address,self.server_port)  )
        if(SHOW_STATISTICS):
            print 'Time Taken:',time.time()-start

   
    
    def start(self,serv_addr,serv_port,pid):
        
        self.server_address = serv_addr
        self.server_port =   serv_port
        
	self.sockin = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
	host = socket.gethostname()
        print socket.gethostbyname(host)
	self.address = socket.gethostbyname(host)
	self.sockin.bind( ( self.address,60000+pid+1) )

        self.sockin.setblocking(False)
        self.sockout = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP

if __name__ == '__main__':
    s=UDPClient(None)
    s.start('127.0.0.1',80,2)
    while(True):
        s.MakeRequest(2,1,1,(0,1))
