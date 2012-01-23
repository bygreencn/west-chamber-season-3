'''
    PyGProxy helps you access Google resources quickly!!!
    Go through the G.F.W....
    gdxxhg AT gmail.com 110602
'''

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from httplib import HTTPResponse
import re, socket, struct, threading, os, traceback, sys, select, urlparse, signal, urllib, json

grules = []
PROXY_SERVER = "http://opliruqi.appspot.com/"
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
    "qq.com",
    "soso.com",
    "weibo.com",
    "youku.com",
    "tudou.com",
    "ft.net"
    ]

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer): pass
class ProxyHandler(BaseHTTPRequestHandler):
    remote = None
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

        print "ip rules: %d" % len(gipWhiteList)
        for r in gipWhiteList:
            ran,m2 = r.split("/");
            dip = struct.unpack('!I', socket.inet_aton(ip))[0]
            dran = struct.unpack('!I', socket.inet_aton(ran))[0]
            shift = 32 - int(m2)
            if (dip>>shift) == (dran>>shift):
                print ip + " (" + host + ") is in China, matched " + (r)
                return False
        return True

    def getip(self, host):
        for r in grules:
            if r[1].match(host) is not None:
                print ("Rule resolve: " + host + " => " + r[0])
                return r[0]
        if re.match(r'^([0-9]+\.){3}[0-9]+$', host) is None:
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
                packedIp = socket.inet_aton(ip)
                print struct.unpack('!I', packedIp)
                if struct.unpack('!I', packedIp)[0] in fakeIp:
                    print ("Fake IP " + host + " => " + ip)
                else:
                    print ("DNS system resolve: " + host + " => " + ip)
                    return ip
            except:
                ip = ""
            
            import DNS
            reqObj = DNS.Request()
            response = reqObj.req(name=host, qtype="A", protocol="tcp", server="168.95.1.1")
            #print response.answers
            #response.show()
            for a in response.answers:
                if a["name"] == host:
                    print ("DNS remote resolve: " + host + " => " + a["data"])
                    return a["data"]
            print ("DNS resolve failed: " + host)
            return host
        return host
    def proxy(self):
        try:
            print self.requestline
            self.supportCrLfPrefix = True
            port = 80
            host = self.headers["Host"]
            if host.find(":") != -1:
                port = int(host.split(":")[1])
                host = host.split(":")[0]
            # Remove http://[host]
            path = self.path[self.path.find(host) + len(host):]
            connectHost = self.getip(host)
            if self.remote is None or self.lastHost != self.headers["Host"]:
                self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.remote.connect((connectHost, port))
                if self.enableInjection(host, connectHost): 
                    self.remote.send("\r\n\r\n")
            self.lastHost = self.headers["Host"]
            while True:
                # Send requestline
                self.remote.send(" ".join((self.command, path, self.request_version)) + "\r\n")
                # Send headers
                self.remote.send(str(self.headers) + "\r\n")
                # Send Post data
                if(self.command=='POST'):
                    self.remote.send(self.rfile.read(int(self.headers['Content-Length'])))
                response = HTTPResponse(self.remote, method=self.command)
                response.begin()
                if response.status == 400 and self.supportCrLfPrefix == True:
                    while response.read(8192): pass
                    self.supportCrLfPrefix = False
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
            print exc_value
            traceback.print_tb(exc_traceback)
            (scm, netloc, path, params, query, _) = urlparse.urlparse(self.path)
            if (scm.upper() != "HTTP"):
                self.wfile.write("HTTP/1.1 500 Server Error " + scm.upper() + "\r\n")
            elif (netloc == urlparse.urlparse(PROXY_SERVER)[1]):
                self.wfile.write("HTTP/1.1 500 Server Error, Cannot connect to proxy " + "\r\n")
            else:
                status = "HTTP/1.1 302 Found"
                self.wfile.write(status + "\r\n")
                self.wfile.write("Location: " + PROXY_SERVER + self.path[7:] + "\r\n")
            
            self.connection.close()
    
    def do_GET(self):
        socket.setdefaulttimeout(18)
        self.proxy()
    def do_POST(self):
        socket.setdefaulttimeout(None)
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


def start():
    # do the UNIX double-fork magic, see Stevens' "Advanced   
    # Programming in the UNIX Environment" for details (ISBN 0201563177)  
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
        s = urllib.urlopen('http://liruqi.sinaapp.com/mirror.php?u=aHR0cDovL3NtYXJ0aG9zdHMuZ29vZ2xlY29kZS5jb20vc3ZuL3RydW5rL2hvc3Rz')
        for line in s.readlines():
            line = line.strip()
            if line[:1] == "#": continue
            d = line.split()
            if (len(d) != 2): continue
            #remove long domains, and redirect by proxy for short domains
            if len(d[1]) > 24 or len(d[1])<6:
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
        s = urllib.urlopen('http://liruqi.sinaapp.com/exclude-ip.json')
        gipWhiteList = json.loads( s.read() )
        print "load %d ip range rules" % len(gipWhiteList);
        s.close()
    except:
        print "load ip-range config fail"

    print "Loaded", len(grules), " dns rules."
    localPort = 1998
    #if (len(sys.argv) > 1):
    #    localPort = int(sys.argv[1])
    print "Set your browser's HTTP proxy to 127.0.0.1:%d"%(localPort)
    server = ThreadingHTTPServer(("0.0.0.0", localPort), ProxyHandler)
    try: server.serve_forever()
    except KeyboardInterrupt: exit()
    
if __name__ == "__main__":
    if (len(sys.argv)<2 or sys.argv[1] == "start"):
        # 
        # http://stackoverflow.com/questions/82831/how-do-i-check-if-a-file-exists-using-python
        try:
            open(PID_FILE).close()
            print "pid exists: " + open(PID_FILE).read()
        except IOError as e:
            start()
        exit(0)
    if (sys.argv[1] == "stop"):
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
    
