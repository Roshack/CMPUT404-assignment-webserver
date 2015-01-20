#  coding: utf-8 
import SocketServer
import os
import datetime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Rob Hackman
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):
    requestString = ""
    data = []
    pathStart = "./www"
    response = ""
    notFoundBody = "<h2>Document not found</h2>\r\n"
    notFoundBody += "You asked for a document that doesn't exist. That is so sad.\r\n"
    notFoundBody += "</body></html>"    
    notFoundString = "HTTP/1.1 404 Not Found\r\n" 
    notFoundString += "Date: %s\r\n"% datetime.datetime.now()		
    notFoundString += "Content-Type: text/html\r\n"
    notFoundString += "Content-Length: %d\r\n" % len(notFoundBody)
    notFoundString += "\r\n"
    notFoundString += notFoundBody
    
    forbiddenBody = "<h2>HOW DARE YOU</h2>\r\n"
    forbiddenBody += "You asked for a document THAT YOU HAVE ABSOLUTELY NO RIGHT TO LOOK AT! BEGONE!\r\n"
    forbiddenBody += "</body></html>"  
    forbiddenString = "HTTP/1.1 403 Forbidden\r\n" 
    forbiddenString += "Date: %s\r\n"% datetime.datetime.now()		
    forbiddenString += "Content-Type: text/html\r\n"
    forbiddenString += "Content-Length: %d\r\n" % len(forbiddenBody)
    forbiddenString += "\r\n"
    forbiddenString += forbiddenBody    
    
    def handle(self):
        self.requestString = self.request.recv(1024).strip()
        self.data = self.requestString.split("\r\n")
        check = self.checkRequest()
        
    def checkRequest(self):
        # Check that we are handling an appropriate get request
        checkOne = self.data[0].split()
        for i in range(len(checkOne)):
            checkOne[i] = checkOne[i].strip()
        if len(checkOne) != 3:
            return -1
        if checkOne[0] != "GET":
            return -1
        if checkOne[2] != "HTTP/1.1":
            return -1
        # If we get here we are handling a proper get request so
        # let's try to find what the user is asking for!
        self.handleGet(checkOne[1])
    
    def handleGet(self, target):
        print("Looking for %s" % target)
        if (target[-1] != "/"):
            if (self.findFile(target) == 1):
                return 1
            elif (self.dirExists(target + "/") == 1):
                self.redirect(target + "/")
                return 2
            else:
                return self.NotFound(target)
        else:
            #okay we're looking for a directory
            if (self.dirExists(target) == 1):
                if (self.getDir(target) == -1):
                    self.NotFound(target)
            else:
                return self.NotFound(target)
    def findFile(self,target):
        absPath = os.path.abspath(self.pathStart)
        absSize = len(absPath)
        if (len(os.path.abspath(self.pathStart+target)) < absSize):
            self.request.sendall(self.notFoundString)
            return 1
        if (os.path.abspath(self.pathStart+target)[0:absSize] != absPath):
            self.request.sendall(self.notFoundString)
            return 1            
        if (os.path.isfile(self.pathStart+target)):
            theType = target.split(".")[1].strip()
            
            theFile = open(self.pathStart+target,"r")
            contents = theFile.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Date: %s\r\n" % datetime.datetime.now()
            response += "Server: rhackmanServer\r\n"
            response += "Content-Type: text/%s\r\n" % theType
            print(theType)
            print("Content-Type: text/%s\r\n" % theType)
            response += "Content-Length: %d\r\n" % len(contents)       
            response += "\r\n"
            response += contents
            self.request.sendall(response)    
            return 1
        else:
            return -1
    
    def dirExists(self,target):
        if (os.path.isdir(self.pathStart + target)):
            return 1
        return 0
    
    def getDir(self,target):
        # retrieve and return a dir for the request
        print("Get dir: " + target + "index.html")
        return self.findFile(target + "index.html")
        
    def redirect(self,target):
        response = "HTTP/1.1 302 Found\r\n"
        response += "Location: %s\r\n" % target
        print("Sending redirect")
        print(response)
        self.request.sendall(response)
    
    def NotFound(self,target):
        print("404 for " + target)
        self.request.sendall(self.notFoundString)
        
        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
