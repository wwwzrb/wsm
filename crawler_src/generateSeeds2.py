import json
from bs4 import BeautifulSoup as bs
import urllib
import urllib2
import os

# import socket
# socket.setdefaulttimeout(60)

seeds = set()
maxDeep = 3
visited = set()
count = 0
mydir = "tempUrl2"
logFile = "log2.txt"

URL = "http://www.goodreads.com"

def output(s):
    print s

def writeLog(s):
    global logFile
    try:
        with open(logFile, "w") as fw:
            fw.write(s + "\r\n")
    except Exception as exp:
        var = "Error: write log error.\r\n"  + str(exp)
        output(var)

def AddToSeeds(url):
    global count
    
    seeds.add(url)

    # epoch
    tlen = len(seeds)
    if tlen % 500 == 0:
        count += 1
        var = "Save temp url : times = %d"% (count)
        output(var)
        try:
            if not os.path.exists(mydir):
                os.makedirs(mydir)
            newTxtPath = "%s/temp2_%d_%d" % (mydir, count, tlen)
            saveUrl(newTxtPath)
            
        except Exception as exp:
            var = "Error: save temp url error.\r\n"
            output(var + str(exp))
    pass

# Generate seeds for "http://www.goodreads.com"
def generateSeeds2(url, deep):
    
    if "/" not in url:
        return
    var = "Current: url = %s  deep = %d" % (url, deep)
    output(var)
    var = "seeds size = %d" % len(seeds)
    output(var)
    if deep > maxDeep:
        return
    if url in visited:
        return
    visited.add(url)
    
    urlInfo = ""
    tUrl = ""
    info = ""

    try:
        # down = urllib.urlopen(url).read()
        down = urllib2.urlopen(url, timeout=60).read()
        soup = bs(down.decode('utf-8'))
        urlInfo = soup.find_all("a")
        for lable in urlInfo:
            
            try:
                info = lable.get("href")
                if not info:
                    continue
                if len(info) < 7:
                    continue
                tUrl = info #
                if "www.goodreads.com" not in info:
                    tUrl = URL + info
                if tUrl in visited:
                    continue
                if "/book/show/" in info:
                    if not info in seeds:
                        AddToSeeds(tUrl)
                generateSeeds2(tUrl, deep + 1)
            except Exception as exp1:
                var = "Error: " + str(exp1)
                writeLog(var)   

    except Exception as exp:
        var = "Error: url = %s  deep = %d\r\n" % (url, deep)
        var +=  str(exp)
        writeLog(var)

def saveUrl(dst):
    with open(dst, "w") as f:
        for link in seeds:
            f.write(link + "\r\n")

def main():
    dst = "url2.txt"
    url = "http://www.goodreads.com"
    generateSeeds2(url, 0)
    saveUrl(dst)

main()

