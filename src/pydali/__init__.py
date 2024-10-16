''' 
 PyDALI module to encapsulate DALI agent process management
 
 Licensed with Apache Public License
 by AAAI Research Group
 Department of Information Engineering and Computer Science and Mathematics
 University of L'Aquila, ITALY
 http://www.disim.univaq.it
'''

from dircache import listdir

__author__ = 'giodegas'

import glob, os, sys
import shutil, errno
from time import sleep
from pysicstus import SicstusProlog, write2file

# ------- Static functions

def copyFolder(src, dst):
    for top, dirs, files in os.walk(src):
        for f in files:
            shutil.copyfile(top + '/' + f, dst + '/' + f)

def cleanFolder(dirName):
    if os.path.isdir(dirName):
        shutil.rmtree(dirName+'/')


DALI_HOME = '../interpreter'
SERVER_DALI = DALI_HOME + '/active_server_wi.pl'
ACTIVE_USER = DALI_HOME + '/active_user_wi.pl'
ACTIVE_DALI = DALI_HOME + '/active_dali_wi.pl'


class Agent:

    def __init__(self,name, myPath='temp'):
        self.name = name

        self.path = myPath
        self.prepConf(None)
        self.Prolog = SicstusProlog(name)

    def setSource(self,src):
        self.source = src

    def setSourceFile(self,fname):
        content = ""
        with open(fname, 'r') as content_file:
            content = content_file.read()
        self.setSource(content)

    def setBasedir(self, basedir):
        self.basedir = basedir
        self.Prolog.setBasedir(basedir)

    def addConfString(self,data,sep=','):
        if type(data)==type('') or type(data)== type(u''):
            self.confString += data + sep
        else:
            s= str(list(data))
            s = s.replace('"','')
            self.confString += s + sep

    def prepConf(self,goal):
        self.fname = '_agent_'+self.name
        if goal:
            self.fname += '_'+goal
        self.fname = self.path+'/'+self.fname
        self.flag1 = "'no'"
        self.lang = "italian"
        shutil.copyfile(DALI_HOME+'/communication.con', self.path+'/'+self.name + '_comm.con')
        self.communication = "['"+ self.path+'/'+self.name + "_comm']"
        self.commFipa = ("'"+DALI_HOME+"/communication_fipa'", "'"+DALI_HOME+"/learning'", "'"+DALI_HOME+"/planasp'")
        self.flag2 = "'no'"
        self.onto = "'"+DALI_HOME+"/onto/dali_onto.txt'"
        self.confPath = self.path+'/'+self.name+'.txt'

    def makeConf(self):
        self.confString = "agent("
        self.addConfString("'"+self.fname+"'")
        self.addConfString(self.name)
        self.addConfString(self.flag1)
        self.addConfString(self.lang)
        self.addConfString(self.communication)
        self.addConfString(self.commFipa)
        self.addConfString(self.flag2)
        self.addConfString(self.onto, ',[]).')
        self.agentGoal = "start0('"+self.confPath+"')"
        return self.confString

    def start(self, goal=None):
        assert(len(self.source)>0)
        self.prepConf(goal)  # goal viene sovrascritto da start0(..)
        write2file(self.fname+'.txt', self.source)
        write2file(self.path+"/"+self.name+'.txt',self.makeConf())
        self.Prolog.spawn()
        self.Prolog.consultFile(ACTIVE_DALI, self.agentGoal, debug=True, blocking=True)

    def debugOut(self):
        return self.Prolog.debugOut()

    def waitFor(self, msg, debug=False):
        idx = self.Prolog.waitFor(msg, debug)
        if debug:
            print idx

    def isAlive(self):
        return self.Prolog.isAlive()

    def terminate(self):
        self.Prolog.terminate()
        sleep(1)

    def pul(self, goal=None):
	write2file(self.path+"/"+self.name+'.txt',self.makeConf())
	self.Prolog.spawn()
	self.Prolog.consultFile(ACTIVE_DALI, self.agentGoal, debug=True, blocking=True)


    def readMove(self):
	a = self.Prolog.readAll()
	b = string.replace(a, "(", " ")
	c = string.replace(b, ")", " ")
	d = string.replace(c, "[", " ")
	e = string.replace(d, "]", " ")
	f = string.replace(e, ",", " ")
	s = string.split(f)
	print s 


    def readMsg(self):
	a = self.Prolog.readAll()
	b = string.replace(a, "(", " ")
	c = string.replace(b, ")", " ")
	d = string.replace(c, ",", " ")
	e = string.replace(d, "_", " ")
	s = string.split(e)
	return s 


class LindaAgent(Agent):

    def __init__(self):
        Agent.__init__(self,'_LindaAgent',DALI_HOME)

    def start(self):
        self.Prolog.spawn()
        self.Prolog.consultFile(SERVER_DALI,"go(3010,'"+DALI_HOME+"/server.txt')",debug=True, blocking=False)

class UserAgent(Agent):

    def __init__(self):
        Agent.__init__(self,'_UserAgent', DALI_HOME)

    def start(self):
        self.Prolog.spawn()
        self.Prolog.consultFile(ACTIVE_USER, "utente", debug=True, blocking=False)

    def send(self, toAgent, fromAgent, message, debug=False):
        self.Prolog.send(toAgent+'.','|: ', debug=True)
        self.Prolog.send(fromAgent+'.','|: ', debug=True)
        self.Prolog.send(message+'.', '|: ', debug=True)
        if debug:
            print 'sent message <',message,'> to agent <',toAgent,'> from agent <',fromAgent,'>'
            print self.Prolog.debugOut()

class MAS:
    state = 0
    stateMessage = {
        0:"MAS Stopped",
        1:"MAS is not found!!!!",
        2:"MAS is empty!!!!"
    }
    errorState = 0

    def __init__(self, name, myPath=None):

        self.name = name
        if not myPath:
            self.path = './' + self.name + '/mas'
        else:
            self.path = myPath

        if not os.path.isdir(self.path):
            self.errorState = 1
            self.state = 1
            print "MAS don't found!!!!"
        else:
            self.MAS = []
            self.name2agent = {}

            self.work = './' + self.name + '/work'
            self.log = './' + self.name + '/log'
            self.conf = './' + self.name + '/conf'

            self.clean()

            self.prepareWork()

            self.build()
            print self.MAS.__len__()
            if self.MAS.__len__() == 0:
                self.errorState = 1
                self.state = 2
                print "MAS is empty!!!!"



    def build(self):
        print "Agent for MAS:", self.name;
        setdir = set()
        for top, dirs, files in os.walk(self.path):
	    files.sort()
            for f in files:
                if top.endswith('mas'):
                    fs = f.split('.')
                    if fs[1]=='txt' and top.endswith('mas'):
                        agentName = fs[0][2:]
                        print '\t', agentName,f
                        a = Agent(agentName,'./' + self.work)
                        a.setSourceFile(top + '/' + f)
                        a.setBasedir(self.work)
                        self.add(a)
                    else:
                        shutil.copyfile(top + '/' + f,  self.work + '/' + f)
                else:
                    trovato = False
                    for tempdir in setdir:
                        if  top.startswith(tempdir):
                            trovato = True
                    if not trovato: setdir.add(top)
        for dir in setdir:
            workdir = dir.replace("mas", "work");
            # shutil.copytree(dir, workdir)

    def add(self, newAgent, startGoal=None):
        assert(isinstance(newAgent, Agent))
        newAgent.agentGoal = startGoal
        self.MAS.append(newAgent)
        self.name2agent[newAgent.name] = newAgent

    def clean(self):
        # clean temporary files
        cleanFolder(self.work)
        cleanFolder('./util/')

    def prepareWork(self):
        if not os.path.isdir(self.work):
            os.makedirs(self.work)
        if not os.path.isdir(self.conf):
            os.makedirs(self.conf)
        if not os.path.isdir('./util'):
            os.makedirs('./util')

    def start(self, debug=False, startTo=None, startMsg=None ):
        if len(self.MAS)>0:
            print 'Starting ',self.name,'MAS'
            # server LINDA
            self.lindaAgent = LindaAgent()
            self.lindaAgent.start()
            # user agent
            self.userAgent = UserAgent()
            self.userAgent.start()
            print 'starting...'
            b = None
            for a in self.MAS:
                print a.name
                if a.name == 'iikeeper_agent':
                    b = a
		print '(agent,goal): ',a.name,a.agentGoal
                a.start(a.agentGoal)
                #sleep(4)
            print 'MAS started'
        else:
            print "No agents defined in MAS"

    def terminate(self):
        for a in self.MAS:
            a.terminate()
        self.userAgent.terminate()
        self.lindaAgent.terminate()
        print 'MAS terminated'

    def error(self):
        return self.errorState

    def errorMessage(self):
        return self.stateMessage[self.state]
