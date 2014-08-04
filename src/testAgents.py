__author__ = 'giodegas'

from time import sleep
import pydali as pd

lindaServer = pd.LindaAgent()
lindaServer.start()
userAgent = pd.UserAgent()
userAgent.start()

ag1 = pd.Agent('test')
ag1.setSource(" :- tell('pippo.txt'),write('ciaociao'),told, writeLog('gone!'). ")
ag1.start()
print 'agent 1 started'

userAgent.send('test','user','send_message(go,user)',debug=True)
sleep(5)
print 'Are agents still alive?', ag1.isAlive(), userAgent.isAlive()
ag1.terminate()
userAgent.terminate()
print 'Agents terminated.'
sleep(2)
print 'Are agents still alive?', ag1.isAlive(), userAgent.isAlive()

