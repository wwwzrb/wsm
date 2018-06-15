from Queue import Queue
import threading
import time
from SetQueue import SetQueue
from scraper2 import Scraper
# from scraper2 import Scraper_17k as Scraper
import argparse
import glob
import json
# jsons_dir = 'JSONs' # address to save JSON files
# jsons_dir = "NewJsons"
jsons_dir = "NewJsons2"
import loadSeeds

crawledQ = SetQueue()
frontlineQ = SetQueue()


seeds = [
    # "http://www.goodreads.com/book/show/3241368-the-little-prince-letter-to-a-hostage",
    # "http://www.goodreads.com/book/show/29938349-de-pourpre-et-de-soie"
    "http://www.goodreads.com/book/show/25434438-the-dressmaker-s-war"
    # "http://novel.tingroom.com/shuangyu/2013/",
    # "http://www.17k.com/book/2819588.html",
]

class crawlerThread(threading.Thread):
    def __init__(self, threadID, timeout, crawl_delay):
        """
        Constructor for the crawler thread class
        """
        threading.Thread.__init__(self)
        self.ID = threadID
        self.timeout = timeout
        self.delay = crawl_delay
        print 'Thread', threadID, ' created at ', time.ctime(time.time())

    def run(self):
        print 'Thread', self.ID, ' starting at ', time.ctime(time.time())
        crawl(self.timeout, self.delay, self.ID)
        print 'Thread', self.ID, ' exiting at ', time.ctime(time.time())

def crawl(timeout, crawl_delay, threadID):
    """
    This method will do the crawling on a URL. In a (almost-)never-ending loop, it will try to get a URL out of the frontline queue, it will crawl it and add new URLs to the frontline queue.

    Parameters
    ----------
    timeout: time object
             this is the timeout time, past which crawling will be stopped
    crawl_delay: int
                timeout between two crawling attempts
    threadID: int, str
              this is the ID of the thread that is using this method. for logging purposes only.
    """
    while True:
        if time.time() > timeout:
            break
        if frontlineQ.empty():
            time.sleep(crawl_delay)
            continue
        url = frontlineQ.get()
        try:
            print 'Thread', threadID, ' scraping ', url
            sc = Scraper(url)
            sc.writeJSON(jsons_dir)
            outgoings = sc.getBookLinks()
            crawledQ.put(url)
            for u in outgoings:
                if not crawledQ.contains(u):
                    frontlineQ.put(u)
        except:
            crawledQ.put(url)
        frontlineQ.task_done()
        time.sleep(crawl_delay/2)

def generateSeeds():
    with open("url2.txt", "r") as fr:
        while True:
            line = fr.readline()
            if not line:
                break
            line = line[:-2]
            seeds.append(line)

def initializeFrontline():
    """
    This method will initialize the frontline queue and also frontline list.
    It can be modified to resume crawling after the last crawl operation.
    At the moment, the latter feature is not implemented.
    """
    # seeds = 'http://www.goodreads.com/book/show/3241368-the-little-prince-letter-to-a-hostage'
    # seeds = "https://www.qidian.com/"
    # seeds = "https://book.qidian.com/info/1011848994"
    # seeds = ""
    for i in range(len(seeds)):
        frontlineQ.put(seeds[i])

    all_jsons_dir = glob.glob(jsons_dir + '/*.json')
    if len(all_jsons_dir) > 0:
        for jdir in all_jsons_dir:
            with open(jdir, 'r') as f:
                jsn = json.load(f)
                crawledQ.put(jsn['url'])
                for outl in jsn['outlinks']:
                    if not crawledQ.contains(outl):
                        frontlineQ.put(outl)
    print crawledQ.qsize(), ' urls crawled already.'
    print 'initial frontline queue contains ', frontlineQ.qsize(), ' urls.'

def main(thread_cnt = 5, crawl_delay = 20, timeout=2):
    """
    crawler module.
    Parameters
    ----------
    thread_cnt: int
                number of threads to use for crawling
    crawl_delay: int
                seconds between two crawling attempts, for each thread
    timeout: int
                crawling duration, after which crawling will be halted. In minutes
    """
    timeout = time.time() + timeout * 60
    # generateSeeds()
    initializeFrontline()
    threads = []
    print 'creating threads'
    for i in range(thread_cnt):
        t = crawlerThread(i, timeout, crawl_delay)
        threads.append(t)

    print 'starting threads'

    for i in range(thread_cnt):
        threads[i].start()

    for i in range(thread_cnt):
        threads[i].join()

    print 'Exiting main thread'

if __name__ == '__main__':
    """
    Main entry for the crawling module. Arguments for number of threads, delay between two crawl attempts and crawling duration are required.
    """
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-t", "--threads", type=int, help="Number of threads")
    # parser.add_argument("-d", "--delay", type=int, help="Delay between every two crawl attempts in seconds")
    # parser.add_argument("-e", "--timeout", type=int, help="Crawling duration, after which crawling will be stopped. In minutes")
    # args = parser.parse_args()
    # if (not args.threads) or (not args.delay) or (not args.timeout):
    #     parser.print_help()
    #     exit()
    # main(args.threads, args.delay, args.timeout)

    seedFile = "url2.txt"
    seeds = loadSeeds.load(seedFile)

    # main(1, 2, 10)
    main(5, 2, 100)
