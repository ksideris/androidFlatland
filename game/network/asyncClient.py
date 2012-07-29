
#!/usr/bin/env python

"""AsyncClient.py: asynchronous networking client"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"




import asyncore, socket,pickle,time,string
import libs.shelve as shelve
SHOW_STATISTICS =False
ID = 0
CLIENTLOCALDATA = 'ClientLocalData.db'
message =''
class HTTPClient(asyncore.dispatcher):

    def __init__(self, host,port, path):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, int(port)) )
        self.buffer = 'GET %s HTTP/1.0\r\n\r\n' % path

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
	global ID,message
	s= self.recv(100000)
	if(len(s)>0):
            if(s[:4]<>'HTTP'):
                message+=s
            else:
                if(len(message)>0):
                
                    localdb = shelve.open(CLIENTLOCALDATA.split('.')[0]+str(ID)+'.'+CLIENTLOCALDATA.split('.')[1])
                    try:
                        localdb['data']={'time':time.time(),'string':message}
                    finally:
                        localdb.close()
                    message=''    
                bodyIndex =  string.index(s, "\r\n\r\n") +4
                message += s[bodyIndex:]        
            #print message           
		    
    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


class AsyncClient():

    def MakeRequest(self,pid,team,action,position):
        global ID
        ID  = pid
        start =time.time()
        message = '/?id='+str(pid)+'&team='+str(team)+'&action='+str(action)
        #print message,action
        if position<>None: 
                message+='&pos='+str(position[0])+','+str(position[1])
        message+='&time='+str(time.time())
        #print message
        client = HTTPClient(self.server_address,self.server_port, message)
        asyncore.loop()
    
        
        if(SHOW_STATISTICS):
            print 'Time Taken:',time.time()-start

   
    
    def start(self,serv_addr,serv_port):
        
        self.server_address = serv_addr
        self.server_port =   serv_port
