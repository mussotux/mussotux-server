''' 
Author : Deepak Pant 
Name   : Chat Server
'''
print 'LOADING CONFIGURATION FILES'
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("config.ini")
print 'LOADING MODULES........... '
import time
print 'loading Time                                    [Done]'
from twisted.internet.protocol import Factory , Protocol
print "loading Protol , Factory                        [Done]"
time.sleep(.5)
from twisted.protocols.basic import LineReceiver
print 'loading LineReceiver                            [Done]'
time.sleep(.5)
from twisted.internet import  reactor ,ssl
print 'loading Reactor  , SSL                          [Done]'
time.sleep(.5)
import MySQLdb
print 'loading MySQL Database                          [Done]'
time.sleep(.5)

time.sleep(.5)
import thread
import threading
print 'Loading Thread,Threading                        [Done]'
time.sleep(.5)
import logging
print 'Loading Logger                                  [Done]'
time.sleep(.5)
time.sleep(2)
print '                                         [Modules Loaing Completed]'
logging.basicConfig(filename='example.log',level=logging.INFO)
def ConfigSectionMap(section,option):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

groups={}
Config=ConfigSectionMap("server",'port')
PORT=Config['port']
mysql_sock=Config['mysql_sock']
servername=Config['servername']
encryption=Config['encryption']







def addGroup(index,group):
	groups[index]=group
	return index
	
	
def genIndex():
    return len(groups)

def addMember(no,con):
	groups[no].append(con)
	return
def printH(a,b):
    while 1:	
	print "thread"
	time.sleep(2)

class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"
	self.data = ""

    def connectionMade(self):
        logging.info("new User Connected ")
        #self.sendLine("connection made .. Provide Credentails <username><space><password>")
	
    def showFriendlist(self,a,b):
	logging.info("showfriendList Thread started for %s"%self.name)
	line=""
	for name in self.data['friends']:
	    line=line+name+","
        self.sendLine("USERLIST::%s" %line)
	logging.info("Userlist sent for %s"%self.name)
	time.sleep(2)
	

    def connectionLost(self, reason):
        if self.users.has_key(self.name):
            del self.users[self.name]

    def userListLineFormat(self):
	line=""
	for name in self.data['friends']:
	   line=line+name+","
	return line
	
    def lineReceived(self, line):
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
	print name
        if(self.checkLogin(name,'name')):
	    logging.info("new user %s Loggedin Successfully " %name)
            self.sendLine(" ")
            self.name = name
            self.users[name] = self
            self.state = "CHAT"
	    try:
		thread.start_new_thread( self.showFriendlist, ("Thread-1",2) )
	    except:
		logging.warning("showFriendlist Thread Couldnot Be started")
        else:
	    logging.info("login failed")
            self.sendLine("sorry invalid Credentials")

    def handle_CHAT(self, message):
        parsedMessage=message.split('::')
	headerText=parsedMessage[0]
	if headerText == 'ADDNEWGROUP':
	    username=parsedMessage[1]
	    groupId=addGroup(genIndex(),[str(self.name),str(username)])
	    logging.info("New Gorup %d created by User %s in pair with %s" %(groupId,self.name,username))
	    lineText="GID::"+str(groupId)
	    self.sendLine(lineText)
        if headerText == 'ADDMEMBER':
	    groupId=int (parsedMessage[1])
	    username=parsedMessage[2]
            addMember(groupId,username)
	 
	  
	if headerText == 'MSG':
	    groupId=int(parsedMessage[1])
            message=str("< %s >"%self.name+parsedMessage[2])
	    for name in groups[groupId]:
		for keyname,protocol in self.users.iteritems():
		    if name == keyname and protocol != self:
			protocol.sendLine(message)
      
        if message =='quit':
	    if self.users.has_key(self.name):
            	del self.users[self.name]
		self.factory.users.remove(self)
		print self.name +' has quit'
    
    def checkLogin(self,username,password):
        db = MySQLdb.connect("localhost","root","","chat",unix_socket=mysql_sock )
        cursor = db.cursor()
        sql = "select * from users where username='%s' " %username
        try:
            cursor.execute(sql)
            resultCount = int(cursor.rowcount)
            if resultCount == 1:
		result=cursor.fetchone()
		data={'name':result[1]}
		friends=[]
		res=result[3].split(',')
		for x in res:
		   sql="select username from users where id='%d'"%(int(x))
		   cursor.execute(sql)
		   username=cursor.fetchone()
		   friends.append(username[0])
		data['friends']=friends
		self.data=data
		return True
	    else:
 		return False
            
        except:
            print "error occured"

  

class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)

if encryption!='ssl':
	reactor.listenTCP(int(PORT), ChatFactory())
	print "----------- STARTING SSL DISABLED SERVER.----------"
else:
	factory = Factory()
	factory.protocol = ChatFactory()
	time.sleep(1)
	reactor.listenSSL(8001,factory,ssl.DefaultOpenSSLContextFactory('server.key','server.crt'))
	print '----------- STARTING SSL ENABLED SERVER.----------'
print '''
 

 ###     ###    ####   ###    #######    #########                    _____
#####   #####   ####   ###    ##         #########                   /@___@\\
###  ###  ###   ####   ###      ####     ###   ###              ____[\\`   '/]____
###   #   ###   ####   ###         ##    ###   ###             /\\ #\\ \\_____/ /# /\\
###       ###   ####   ###     	    ##   ###   ###            /  \\# \\_.---._/ #/  \\
###       ###   ####   ###          ##   #########           /   /|\\  |   |  /|\\   \\
###       ###   ##########     #######   #########          /___/ | | |   | | | \\___\\
                                                            |  |  | | |---| | |  |  |
   ###########    ####   ###   ####      ####               |__|  \\_| |_#_| |_/  |__|
   ###########    ####   ###    ####    ####                //\\\\  <\\ _//^\\\\_ />  //\\\\
       ###        ####   ###      #### ####                 \||/  |\//// \\\\\\\\/|  \\||/
       ###        ####   ###         ###                          |   |   |   |
       ###        ####   ###      #### ####                       |---|   |---|
       ###        ####   ###    #####   ####                      |---|   |---|
       ###        ##########   ####      #####                    |___|   |___|
                                                                  /   \\   /   \\
                  					         |_____| |_____|
                                                                 |HHHHH| |HHHHH|
        
'''
time.sleep(1)
print '------------SERVER STARTED ON PORT %s--------------       '%PORT
reactor.run()
print "-------------TERMINATTING SERVER--------------------- "

