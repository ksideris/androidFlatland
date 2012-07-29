

#!/usr/bin/env python

"""SimpleClient.py: simple http client.NOT USED anymore
"""

__author__      = "Konstantinos Sideris"
__copyright__   = "Copyright 2012, UCLA game lab"



import httplib,pickle,time,sys
import libs.shelve as shelve
SHOW_STATISTICS =False
ID = 0
CLIENTLOCALDATA = 'ClientLocalData.db'

class SimpleClient():

    def MakeRequest(self,pid,team,action,position):
        player_id=1
        try:
            ID  = pid
            start =time.time()
            message = '/?id='+str(pid)+'&team='+str(team)+'&action='+str(action)
            if position<>None: 
                message+='&pos='+str(position[0])+','+str(position[1])
            message+='&time='+str(time.time())
            conn = httplib.HTTPConnection(self.server_address+':'+self.server_port)
            conn.request("GET",  message)
            
            s = conn.getresponse()
            data =s.read()
            print data
            localdb = shelve.open(CLIENTLOCALDATA.split('.')[0]+str(ID)+'.'+CLIENTLOCALDATA.split('.')[1])
            try:
                localdb['data']={'time':time.time(),'string':data}
            finally:
                localdb.close()
                
            
            if(SHOW_STATISTICS):
                print 'Time Taken:',time.time()-start
            
        except Exception:
			print 'Exception in Simple Client:', sys.exc_info()[0]

    def start(self,serv_addr,serv_port):
        self.server_address = serv_addr
        self.server_port =   serv_port
