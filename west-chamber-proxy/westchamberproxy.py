#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    westchamberproxy by liruqi AT gmail.com
    Based on:
    PyGProxy helps you access Google resources quickly!!!
    Go through the G.F.W....
    gdxxhg AT gmail.com 110602
'''

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from httplib import HTTPResponse, BadStatusLine
import re, socket, struct, threading, os, traceback, sys, select, urlparse, signal, urllib, urllib2, json, platform, time
import config

grules = []

gConfig = config.gConfig

PID_FILE = '/tmp/python.pid'
gipWhiteList = []
domainWhiteList = [
    ".cn",
    ".am",
    ".pl",
    ".gl",
    "baidu.com",
    "mozilla.org",
    "mozilla.net",
    "mozilla.com",
    "wp.com",
    "qstatic.com",
    "serve.com",
    "qq.com",
    "qqmail.com",
    "soso.com",
    "weibo.com",
    "youku.com",
    "tudou.com",
    "ft.net",
    "ge.net",
    "phonenumber.com"
    ]

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer): pass
class ProxyHandler(BaseHTTPRequestHandler):
    remote = None
    dnsCache = {}
    now = 0

    def enableInjection(self, host, ip):
        global gipWhiteList;
        print "check "+host + " " + ip
        if (host == ip):
            print host + ": do not inject ip, maybe stream server or ws"
            return False
        for d in domainWhiteList:
            if host.endswith(d):
                print host + " in domainWhiteList: " + d
                return False
        for c in ip:
            if c!='.' and (c>'9' or c < '0'):
                print "recursive ip "+ip
                return True

        for r in gipWhiteList:
            ran,m2 = r.split("/");
            dip = struct.unpack('!I', socket.inet_aton(ip))[0]
            dran = struct.unpack('!I', socket.inet_aton(ran))[0]
            shift = 32 - int(m2)
            if (dip>>shift) == (dran>>shift):
                print ip + " (" + host + ") is in China, matched " + (r)
                return False
        return True

    def isIp(self, host):
        return re.match(r'^([0-9]+\.){3}[0-9]+$', host) != None

    def getip(self, host):
        if self.isIp(host):
            return host

        for r in grules:
            if r[1].match(host) is not None:
                print ("Rule resolve: " + host + " => " + r[0])
                return r[0]

        print "Resolving " + host
        self.now = int( time.time() )
        if host in self.dnsCache:
            if self.now < self.dnsCache[host]["expire"]:
                print "Cache: " + host + " => " + self.dnsCache[host]["ip"] + " / expire in %d (s)" %(self.dnsCache[host]["expire"] - self.now)
                return self.dnsCache[host]["ip"]

        if gConfig["SKIP_LOCAL_RESOLV"]:
            return self.getRemoteResolve(host, gConfig["REMOTE_DNS"])

        try:
            ip = socket.gethostbyname(host)
            fakeIp = {
                0x5d2e0859 : 1,
                0xcb620741 : 1,
                0x0807c62d : 1,
                0x4e10310f : 1,
                0x2e52ae44 : 1,
                0xf3b9bb27 : 1,
                0xf3b9bb1e : 1,
                0x9f6a794b : 1,
                0x253d369e : 1,
                0x9f1803ad : 1,
                0x3b1803ad : 1,
            }
            ChinaUnicom404 = {
                "202.106.199.37" : 1,
                "202.106.195.30" : 1,
            }
            packedIp = socket.inet_aton(ip)
            if struct.unpack('!I', packedIp)[0] in fakeIp:
                print ("Fake IP " + host + " => " + ip)
            elif ip in ChinaUnicom404:
                print ("ChinaUnicom404 " + host + " => " + ip + ", ignore");
            else:
                print ("DNS system resolve: " + host + " => " + ip)
                return ip
        except:
            print "DNS system resolve Error: " + host
            ip = ""
        return self.getRemoteResolve(host, gConfig["REMOTE_DNS"])

    def getRemoteResolve(self, host, dnsserver):
        print "remote resolve " + host + " by " + dnsserver
        import DNS
        reqObj = DNS.Request()
        response = reqObj.req(name=host, qtype="A", protocol="tcp", server=dnsserver)
        #response.show()
        #print "answers: " + str(response.answers)
        for a in response.answers:
            if a["name"] == host:
                print ("DNS remote resolve: " + host + " => " + str(a))
                if a['typename'] == 'CNAME':
                    return self.getip(a["data"])
                self.dnsCache[host] = {"ip":a["data"], "expire":self.now + a["ttl"]}
                return a["data"]
        print "authority: "+ str(response.authority)
        for a in response.authority:
            if a['typename'] != "NS":
                continue
            if type(a['data']) == type((1,2)):
                return self.getRemoteResolve(host, a['data'][0])
            else :
                return self.getRemoteResolve(host, a['data'])
        print ("DNS remote resolve failed: " + host)
        return host
    
    def netlog(self, path):
        print "FEEDBACK_LOG: " + path
        if "FEEDBACK_LOG_SERVER" in gConfig:
            try:
                urllib2.urlopen(gConfig["FEEDBACK_LOG_SERVER"] + path).close()
            except:
                pass
        print "end FEEDBACK_LOG" 
        
    def proxy(self):
        doInject = False
        print self.requestline
        port = 80
        host = self.headers["Host"]
        if host.find(":") != -1:
            port = int(host.split(":")[1])
            host = host.split(":")[0]
        errpath = ""

        try:
            redirectUrl = self.path
            while True:
                (scm, netloc, path, params, query, _) = urlparse.urlparse(redirectUrl)

                if (netloc not in gConfig["REDIRECT_DOMAINS"]):
                    break
                prefixes = gConfig["REDIRECT_DOMAINS"][netloc].split('|')
                found = False
                for prefix in prefixes:
                    prefix = prefix + "="
                    for param in query.split('&') :
                        if param.find(prefix) == 0:
                            print "redirect to " + urllib.unquote(param[len(prefix):])
                            redirectUrl = urllib.unquote(param[len(prefix):])
                            found = True
                            continue 
                if not found:
                    break

            if (host in gConfig["HSTS_DOMAINS"]):
                redirectUrl = "https://" + self.path[7:]

            #redirect 
            if (redirectUrl != self.path):
                status = "HTTP/1.1 302 Found"
                self.wfile.write(status + "\r\n")
                self.wfile.write("Location: " + redirectUrl + "\r\n")
                self.connection.close()
                return
            # Remove http://[host]
            path = self.path[self.path.find(netloc) + len(netloc):]
            connectHost = self.getip(host)
            
            self.lastHost = self.headers["Host"]

            while True:
                doInject = self.enableInjection(host, connectHost)
                if self.remote is None or self.lastHost != self.headers["Host"]:
                    self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print "connect to " + host + ":" + str(port)
                    self.remote.connect((connectHost, port))
                    if doInject: 
                        self.remote.send("\r\n\r\n")
                # Send requestline
                self.remote.send(" ".join((self.command, path, self.request_version)) + "\r\n")
                # Send headers
                self.remote.send(str(self.headers) + "\r\n")
                # Send Post data
                if(self.command=='POST'):
                    self.remote.send(self.rfile.read(int(self.headers['Content-Length'])))
                response = HTTPResponse(self.remote, method=self.command)
                badStatusLine = False
                msg = "http405"
                try :
                    response.begin()
                    print host + " response: %d"%(response.status)
                    msg = "http%d"%(response.status)
                except BadStatusLine:
                    print host + " response: BadStatusLine"
                    msg = "badStatusLine"
                    badStatusLine = True
                except:
                    raise

                if doInject and (response.status == 400 or response.status == 405 or badStatusLine):
                    self.remote.close()
                    self.remote = None
                    domainWhiteList.append(host)
                    errpath = (msg + "/host/" + host)
                    continue
                break
            # Reply to the browser
            status = "HTTP/1.1 " + str(response.status) + " " + response.reason
            self.wfile.write(status + "\r\n")
            h = ''
            for hh, vv in response.getheaders():
                if hh.upper()!='TRANSFER-ENCODING':
                    h += hh + ': ' + vv + '\r\n'
            self.wfile.write(h + "\r\n")
            while True:
                response_data = response.read(8192)
                if(len(response_data) == 0): break
                self.wfile.write(response_data)
        except:
            if self.remote:
                self.remote.close()
                self.remote = None

            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "error in proxy: ", self.requestline
            print exc_type
            print str(exc_value) + " " + host
            errpath = "unkown/host/" + host 
            if exc_type == socket.error:
                code, msg = str(exc_value).split('] ')
                code = code[1:].replace(" ", "")
                errpath = code + "/host/" + host + "/?msg=" + urllib.quote(msg)
            traceback.print_tb(exc_traceback)
            (scm, netloc, path, params, query, _) = urlparse.urlparse(self.path)
            status = "HTTP/1.1 302 Found"
            if (netloc != urlparse.urlparse( gConfig["PROXY_SERVER"] )[1]):
                self.wfile.write(status + "\r\n")
                redirectUrl = gConfig["PROXY_SERVER"] + self.path[7:]
                if host in gConfig["HSTS_ON_EXCEPTION_DOMAINS"]:
                    redirectUrl = "https://" + self.path[7:]

                self.wfile.write("Location: " + redirectUrl + "\r\n")
            else:
                status = "HTTP/1.1 302 Found"
                if (scm.upper() != "HTTP"):
                    msg = "schme-not-supported"
                else:
                    msg = "web-proxy-fail"
                errpath = ("error/host/" + host + "/?msg=" + msg)
                self.wfile.write(status + "\r\n")
                self.wfile.write("Location: http://liruqi.info/post/18486575704/west-chamber-proxy#" + msg + "\r\n")
            self.connection.close()
            print "client connection closed"

        if errpath != "":
            self.netlog(errpath)
    
    def do_GET(self):
        #some sites(e,g, weibo.com) are using comet (persistent HTTP connection) to implement server push
        #after setting socket timeout, many persistent HTTP requests redirects to web proxy, waste of resource
        #socket.setdefaulttimeout(18)
        self.proxy()
    def do_POST(self):
        #socket.setdefaulttimeout(None)
        self.proxy()

    def do_CONNECT(self):
        host, port = self.path.split(":")
        host = self.getip(host)
        self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("connect " + host + ":%d" % int(port))
        self.remote.connect((host, int(port)))

        Agent = 'WCProxy/1.0'
        self.connection.send('HTTP/1.1'+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%Agent)
        self._read_write()
        return

    # reslove ssl from http://code.google.com/p/python-proxy/
    def _read_write(self):
        BUFLEN = 8192
        time_out_max = 60
        count = 0
        socs = [self.connection, self.remote]
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                print ("select error")
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if in_ is self.connection:
                        out = self.remote
                    else:
                        out = self.connection
                    if data:
                        out.send(data)
                        count = 0
            if count == time_out_max:
                print ("select timeout")
                break


def start(fork):
    # do the UNIX double-fork magic, see Stevens' "Advanced   
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    
    if fork:
        try:   
            pid = os.fork()   
            if pid > 0:  
                # exit first parent  
                sys.exit(0)   
        except OSError, e:   
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)   
            sys.exit(1)  
        # decouple from parent environment  
        os.chdir("/")   
        os.setsid()   
        os.umask(0)   
        # do second fork  
        try:   
            pid = os.fork()   
            if pid > 0:
                sys.exit(0)   
        except OSError, e:   
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)   
            sys.exit(1)

        pid = str(os.getpid())
        print "start pid %s"%pid
        f = open(PID_FILE,'a')
        f.write(" ")
        f.write(pid)
        f.close()
    
    # Read Configuration
    try:
        s = urllib2.urlopen('http://liruqi.sinaapp.com/mirror.php?u=aHR0cDovL3NtYXJ0aG9zdHMuZ29vZ2xlY29kZS5jb20vc3ZuL3RydW5rL2hvc3Rz')
        for line in s.readlines():
            line = line.strip()
            line = line.split("#")[0]
            d = line.split()
            if (len(d) != 2): continue
            #remove long domains
            if len(d[1]) > 24:
                print "ignore "+d[1]
                continue
            print "read "+line
            regexp = d[1].replace(".", "\.").replace("*", ".*")
            try: grules.append((d[0], re.compile(regexp)))
            except: print "Invalid rule:", d[1]
        s.close()
    except:
        print "read onine hosts fail"
    
    try:
        global gipWhiteList;
        s = urllib2.urlopen('http://liruqi.sinaapp.com/exclude-ip.json')
        gipWhiteList = json.loads( s.read() )
        print "load %d ip range rules" % len(gipWhiteList);
        s.close()
    except:
        print "load ip-range config fail"

    print "Loaded", len(grules), " dns rules."
    print "Set your browser's HTTP proxy to 127.0.0.1:%d"%(gConfig["LOCAL_PORT"])
    server = ThreadingHTTPServer(("0.0.0.0", gConfig["LOCAL_PORT"]), ProxyHandler)
    try: server.serve_forever()
    except KeyboardInterrupt: exit()
    
if __name__ == "__main__":
    isWindows = (platform.system() == "Windows")
    if (len(sys.argv)<2 or sys.argv[1] == "start"):
        # 
        # http://stackoverflow.com/questions/82831/how-do-i-check-if-a-file-exists-using-python
        if not isWindows:
            try:
                open(PID_FILE).close()
                print "pid exists: " + open(PID_FILE).read()
                exit(0)
            except IOError as e:
                print "start new process..."
        start( (False == isWindows) )
        
    if (sys.argv[1] == "stop"):
        if isWindows:
            print "process control is not supported on Windows"
            exit(2)
        try:
            pid = open(PID_FILE).read()
            os.remove(PID_FILE)
            os.kill(int(pid), signal.SIGKILL)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print exc_type
            print exc_value
            traceback.print_tb(exc_traceback)
        exit(0)

    print "Usage: "+ sys.argv[0] + " start | stop"
    exit(1)
    
