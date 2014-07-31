import sys
import math
import socket
import time
import select
import struct
import termstatus

class netGPIB:
    def __init__(self,ip,gpibAddr,eot='\004',debug=0):

        #End of Transmission character
        self.eot=eot
        # EOT character number in the ASCII table
        self.eotNum=struct.unpack('B',eot)[0]

        #Debug flag
        self.debug = debug

        self.ip = ip
        self.gpibAddr=gpibAddr

        #Connect to the GPIB-Ethernet converter
        netAddr=(ip, 1234)
        self.netSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.netSock.connect(netAddr)

        #Initialize the GPIB-Ethernet converter
        self.netSock.setblocking(0)
        self.netSock.send("++savecfg 0\n") # Don't write changes to flash
        self.netSock.send("++addr "+str(self.gpibAddr)+"\n")
        time.sleep(0.1)
        self.netSock.send("++eos 3\n")
        time.sleep(0.1)
        self.netSock.send("++mode 1\n")
        time.sleep(0.1)
        self.netSock.send("++auto 0\n")
        time.sleep(0.1)
        self.netSock.send("++ifc\n")
        time.sleep(0.1)
        self.netSock.send("++read_tmo_ms 3000\n")
        time.sleep(0.1)
        self.netSock.send("++eot_char "+str(self.eotNum)+"\n")
        self.netSock.send("++eot_enable 1\n")
        self.netSock.send("++addr "+str(self.gpibAddr)+"\n")
        
    def refresh(self):
        self.netSock.send("++savecfg 0\n") # Don't write changes to flash
        self.netSock.send("++addr "+str(self.gpibAddr)+"\n")
        time.sleep(0.1)
        self.netSock.send("++eos 3\n")
        time.sleep(0.1)
        self.netSock.send("++mode 1\n")
        time.sleep(0.1)
        self.netSock.send("++auto 0\n")
        time.sleep(0.1)
        self.netSock.send("++ifc\n")
        time.sleep(0.1)
        self.netSock.send("++read_tmo_ms 3000\n")
        time.sleep(0.1)
        self.netSock.send("++eot_char"+str(self.eotNum)+"\n")
        self.netSock.send("++eot_enable 1\n")
        self.netSock.send("++addr "+str(self.gpibAddr)+"\n")


    def getData(self, buf, sleep=0.1):
        data=""
        dlen=0
        if self.debug == True:
            progressInfo=termstatus.statusTxt("0 bytes received")
        while 1: # Repeat reading data until eot is found
            while 1:  # Read some data
                readSock, writeSock, errSock = select.select([self.netSock],[],[],3)
                if len(readSock) == 1:
                    data1 = readSock[0].recv(buf)
                    if self.debug == True:
                        dlen=dlen+len(data1)
                        progressInfo.update(str(dlen)+' bytes received')
                    break
                

            if data1[-1] == self.eot: #if eot is found at the end
                data = data + data1[:-1] #remove eot
                break
            else:
                data = data + data1
                time.sleep(0.1)

        if self.debug == True:
            progressInfo.end()
        return data
            
    def query(self,string,buf=100,sleep=0):
        self.netSock.send(string+"\n")
        time.sleep(sleep)
        self.netSock.send("++read eoi\n") #Change to listening mode
        return self.getData(buf)
    
    def command(self,string):
        self.netSock.send(string+"\n")
        time.sleep(0.1)

    def close(self):
        self.netSock.close()

    def setDebugMode(self, debugFlag):
        if debugFlag:
            self.debug=1
        else:
            self.debug=0


def gpibGetData(netSock, buf, eot, debug=0):
    data=""
    while 1: # Repeat reading data until eot is found
        while 1:  # Read some data
            readSock, writeSock, errSock = select.select([netSock],[],[],3)
            if len(readSock) == 1:
                data1 = readSock[0].recv(buf)
                if debug == True:
                    print(str(len(data1))+' bytes received')
                break

        if data1[len(data1)-1] == eot: #if eot is found at the end
            data = data + data1[0:len(data1)-1] #remove eot
            break
        else:
            data = data + data1
            time.sleep(1)

    return data

