import json
from bs4 import BeautifulSoup as bs
import urllib


seeds = set()
maxDeep = 3


def output(s):
    print s



# Generate seeds for "http://www.17k.com/"
def generateSeeds2(url, deep):
    var = "Current: url = %s  deep = %d" % (url, deep)
    output(var)
    var = "seeds size = %d" % len(seeds)
    output(var)
    if deep > maxDeep:
        return
    try:
        down = urllib.urlopen(url).read()
        soup = bs(down.decode('utf-8'))
        urlInfo = soup.find_all("a")
        for lable in urlInfo:
            info = lable.get("href")
            # if (not info.startswith("http://www.17k.com/book/")) and (not info.startswith("http://all.17k.com/lib")):
            if not "17k" in info:
                continue
            if len(info) < 40:
                if not info in seeds:
                    seeds.add(info)
            else:
                generateSeeds2(info, deep + 1)

    except Exception as exp:
        var = "Error: url = %s  deep = %d" % (url, deep)
        print var
        print str(exp)


def saveUrl():        
    with open("url.txt", "w") as f:
        for link in seeds:
            f.write(link + "\r\n")

def main():
    url = "http://www.17k.com/"
    generateSeeds2(url, 0)
    saveUrl()

main()

