#!/usr/bin/env python

# pyvatsim.py

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.python import log
from twisted.python.log import FileLogObserver, startLogging, addObserver, msg
from vatsimhash import VatHasher
import sys

class VatsimClient(LineReceiver):
    """Vatsim Client protocol"""
    cid = ""
    password = ""
    realname = ""

    callsign = "ZAU_OBS"

    #lat = '33.9425'
    #lon = '-118.408056'

    #lat = "38.375833"
    #lon =  "-81.593056"

    lat ="41.786111"
    lon =  "-87.7525"
    def sendRawResponse(self,rawResponse):
        log.msg(">> %s" % rawResponse)
        self.sendLine(rawResponse)

    def sendResponse(self, controlCode, response):
        self.sendRawResponse("%s%s:%s"% (controlCode,self.callsign,response))
    
    def sendDirectResponse(self, controlCode, dest, response):
        rawResponse = '%s%s:%s:%s' % (controlCode,self.callsign,dest,response)
        #log.msg( ">> %s" % rawResponse
        self.sendRawResponse(rawResponse)

    def serverResponseBuilder(self, controlCode, response):
        response = ":".join(response)
        self.sendDirectResponse(controlCode,"SERVER",response)

    def connectionMade(self):
        pass

    def lineReceived(self, line):
        controlCode = line[:3]
        splitLine = line[3:].split(':')
        log.msg( "<< %s: %s" % (controlCode, splitLine))
        if '$DI' in controlCode:
            if 'CLIENT' in splitLine[1]:
                self.vathash = VatHasher(splitLine[3])
                log.msg(self.vathash.serverSalt)
                response = []
                response.append("2110")
                response.append("vSTARS")
                response.append("1")
                response.append("0")
                response.append(self.cid)
                response.append("462CEBA3")
                self.serverResponseBuilder("$ID",response)
                self.sendDirectResponse('#AA','SERVER','%s:%s:%s:1:100' % (self.realname,self.cid,self.password))
                self.sendDirectResponse('$CQ','SERVER','$CQZFW_OBS:SERVER:ATC')
                self.sendDirectResponse('$CQ','SERVER','IP')
                self.sendRawResponse("%s%s:99998:0:150:1:%s:%s:0"%("%",self.callsign,self.lat,self.lon))
        elif '#TM' in controlCode:
            if len(splitLine) > 2:
                log.msg( "%s: %s" % (splitLine[0],splitLine[2]))
        elif '$CR' in controlCode:
            if 'IP' in splitLine[2]:
                self.sendDirectResponse('$CR','SERVER','CAPS:VERSION=1:ATCINFO=1')
        elif '$ZC' in controlCode:
            response = []
            #log.msg( self.vathash.serverSalt
            response.append(self.vathash.hash(splitLine[2]))
            self.serverResponseBuilder('$ZR',response)
        elif '#DP' in controlCode:
            self.sendRawResponse("%s%s:99998:0:150:1:%s:%s:0"%("%",self.callsign,self.lat,self.lon))
        elif '@N' in controlCode:
            log.msg( "MOVEPACKET:%s" % (":".join(splitLine)))


class VatsimClientFactory(ClientFactory):
    """Vatsim Client Factory"""
    protocol = VatsimClient

    def clientConnectionFailed(self, connector, reason):
        log.msg('connection failed:', reason.getErrorMessage())
        reactor.stop()
    def clientConnectionLost(self, connector, reason):
        log.msg('connection lost:', reason.getErrorMessage())
        reactor.stop()

def main():
    factory = VatsimClientFactory()
    log.startLogging(sys.stdout)
    #log.addObserver(log.FileLogObserver(open("trace.log",'w')))
    addObserver(FileLogObserver(open("trace.log",'w')).emit)
    reactor.connectTCP('USA-E.vatsim.net',6809, factory)
    reactor.run()

if __name__ == '__main__':
    main()
        
