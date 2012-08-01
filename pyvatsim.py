#!/usr/bin/env python

# pyvatsim.py

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from vatsimhash import VatHasher

class VatsimClient(LineReceiver):
    """Vatsim Client protocol"""

    def sendRawResponse(self,rawResponse):
        self.sendLine(rawResponse)

    def sendResponse(self, controlCode, dest, response):
        rawResponse = '%s%s:%s:%s' % (controlCode,self.callsign,dest,response)
        print ">> %s" % rawResponse
        self.sendRawResponse(rawResponse)

    def serverResponseBuilder(self, controlCode, response):
        response = ":".join(response)
        self.sendResponse(controlCode,"SERVER",response)

    def connectionMade(self):
        self.callsign = "ZFW_OBS"
        pass

    def lineReceived(self, line):
        controlCode = line[:3]
        splitLine = line[3:].split(':')
        print "<< %s: %s" % (controlCode, splitLine)
        if '$DI' in controlCode:
            if 'CLIENT' in splitLine[1]:
                cid = ""
                password = ""
                self.vathash = VatHasher(splitLine[3])
                print self.vathash.serverSalt
                response = []
                response.append("2110")
                response.append("vSTARS")
                response.append("1")
                response.append("0")
                response.append(cid)
                response.append("462CEBA3")
                self.serverResponseBuilder("$ID",response)
                self.sendResponse('#AA','SERVER','Reginald Beardsley:%s:%s:1:100' % (cid,password))
                self.sendResponse('$CQ','SERVER','$CQZFW_OBS:SERVER:ATC')
                self.sendResponse('$CQ','SERVER','IP')
                self.sendRawResponse("%ZFW_OBS:99998:0:150:1:0.00000:0.00000:0")
        elif '#TM' in controlCode:
            if len(splitLine) > 2:
                print "%s: %s" % (splitLine[0],splitLine[2])
        elif '$CR' in controlCode:
            if 'IP' in splitLine[2]:
                self.sendResponse('$CR','SERVER','CAPS:VERSION=1:ATCINFO=1')
        elif '$ZC' in controlCode:
            response = []
            #print self.vathash.serverSalt
            response.append(self.vathash.hash(splitLine[2]))
            self.serverResponseBuilder('$ZR',response)

class VatsimClientFactory(ClientFactory):
    """Vatsim Client Factory"""
    protocol = VatsimClient

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()
    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

def main():
    factory = VatsimClientFactory()
    reactor.connectTCP('USA-E.vatsim.net',6809, factory)
    reactor.run()

if __name__ == '__main__':
    main()
        
