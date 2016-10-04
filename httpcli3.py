import sys
import urlparse
import httplib
from HTMLParser import HTMLParser
import time
from pprint import pprint

#in [1]
def basename(path):
    """Get base name from the given path"""
    if path in ('', '/'):
        return 'index.html'
    index = path.rfind('/')
    if index == -1:    # not found
        return 'index.html'
    else:
        return path[index+1:]

def parse_url(url):
    parsed = urlparse.urlsplit(url)
    if parsed.query:
        selector = parsed.path + '?' + 'base.query'    
    else:
        selector = parsed.path
    return parsed.netloc, selector, basename(parsed.path)

#in [2]
begin = time.time()
base_url = "http://mclab.hufs.ac.kr/test/index.html"  
base_netloc, base_selector, base_name = parse_url(base_url)
conn = httplib.HTTPConnection(base_netloc)
conn.debuglevel = 1  # print details only for debugging

#in [3]
conn.request("GET", base_selector)

#in [4]
def handle_response(conn, filename):
    """Get HTTP response and save it as given filename
    All the response status except 200 are ignored"""
    res = conn.getresponse()
    if res.status == 200:    # OK
        
        f = open(filename,'wb')
        obj = res.read(res.getheader('Content-Length'))
        f.write(obj)
        f.close()
        
        if 'text/html' in res.getheader('Content-Type') :
            return obj    
        else:
            return None   # no need to peek inside
    print '%s %s' %(res.status, res.reason)
    return None    # Error

base_html = handle_response(conn, base_name)

if not base_html:
    sys.exit("No html contents exists")

#in [5]
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag not in ('img', 'script'): return
        for attr in attrs:
            if attr[0] == 'src':
                srcs.append(attr[1])

parser = MyHTMLParser()   
srcs = []
parser.feed(base_html)
print('srcs from base html:')
pprint(srcs)

srcs_dict = {}

for src in srcs:
    url = urlparse.urljoin(base_url,src)
    netloc, selector, name = parse_url(url)
    if netloc in srcs_dict.keys():
        srcs_dict[netloc].append((selector,name))
    else:
        srcs_dict[netloc] = [(selector,name)]
    
pprint(srcs_dict)

#in [6]
for obj in srcs_dict[base_netloc]:
    conn.request('GET', obj[0])
    handle_response(conn, obj[1])
conn.close()

del srcs_dict[base_netloc]

for netloc in srcs_dict.keys():
    conn = httplib.HTTPConnection(netloc)
    for obj in srcs_dict[netloc]:
        conn.request('GET', obj[0])
        handle_response(conn, obj[1])
    conn.close()
    
elapsed = time.time() - begin
print "Elapsed time: %.3f sec" %(elapsed)
