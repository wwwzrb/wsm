import json
from bs4 import BeautifulSoup as bs
import urllib
import os


seeds = set()
maxDeep = 4
visited = set()
count = 0
mydir = "tempUrl4"
logFile = "log4.txt"

URL = "https://www.qidian.com"

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
            newTxtPath = "%s/temp4_%d_%d" % (mydir, count, tlen)
            saveUrl(newTxtPath)
            
        except Exception as exp:
            var = "Error: save temp url error.\r\n"
            output(var + str(exp))
    pass

# Generate seeds for "https://www.qidian.com/"
def generateSeeds(url, deep):
    
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
        down = urllib.urlopen(url).read()
        soup = bs(down.decode('utf-8'))
        urlInfo = soup.find_all("a")
        for lable in urlInfo:
            info = lable.get("href")
            if not info:
                continue
            try:
                tUrl = info #
                if info.startswith("http"):
                    tUrl = info
                elif info.startswith("//"):
                    tUrl = "https:" + info
                elif info.startswith("/"):
                    tUrl = URL + info

                if tUrl in visited:
                    continue

                if "book.qidian.com/info/" in info:
                    if not info in seeds:
                        AddToSeeds(tUrl)

                generateSeeds(tUrl, deep + 1)
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
    dst = "url4.txt"
    url = "https://www.qidian.com/"
    generateSeeds(url, 0)
    saveUrl(dst)

main()

