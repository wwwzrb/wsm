from __future__ import unicode_literals
import urllib
from bs4 import BeautifulSoup as bs
import codecs
from fuzzywuzzy import fuzz
import json
import os
from string import punctuation, digits
import time
import datetime

# Deal with Chinese problem [encoding problem]
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# http://www.goodreads.com
class Scraper:
    """
    Goodreads books URL scraper class
    This class will get a URL and will try to scrape it and return relevant information
    """

    soup = ''
    url = ''
    # relative weighting of partial_ratio matching score and normal matching score. Partial matching is weighed more than normal matching
    pr_ratio = 0.7

    def __init__(self, __url__):
        """
        Scraper class constructor
        Webpage will be downloaded and encoded as BeautifulSoup4 object 'soup'

        Parameters
        ----------
        __url__: str
                 URL to the book webpage
        """
        self.url = __url__
        down = urllib.urlopen(self.url).read()
        self.soup = bs(down.decode('utf-8'), "html.parser")

    def info(self, s):
        print s

    def getTitle(self):
        """
        Returns
        -------
        str: title of the book
        """
        title = ""
        try:
            title = self.soup.find("h1", "bookTitle").text.strip()
        except Exception as exp:
            var = "getTitle() Error in class Scraper:\r\n" + str(exp)
            self.info(var)
        return title

    def getAuthors(self):
        """
        Returns
        -------
        list(dict): a list of dict items containing author name and author page URL
                            {'name', 'url'}
        """
        authors = []
        try:
            for a in self.soup.find_all("a", "authorName"):
                authors.append({"name":a.text.strip(), "url":a.get("href")})
        except Exception as exp:
            var = "getAuthors() Error in class Scraper:\r\n" + str(exp)
            self.info(var)
        return authors

    def getDescription(self):
        """
        Returns
        -------
        str: description of the book
        """
        ds = ""
        try:
            descs = self.soup.find("div", attrs={"id":"description"}).find_all("span")
            ds = descs[-1].text.strip()
        except Exception as exp:
            var = "getDescription() Error in class Scraper:\r\n" + str(exp)
            self.info(var)
        return ds

    def getNumbers(self):
        """
        Get average rating, total number of reviews and total number of ratings
        Returns
        -------
        dict: returns a dict object {"average": float, "ratings": int, "reviews": int}
        """
        nums = {}
        try:
            var = self.soup.find("span", "average")
            nums["average"] = float(var.text)
            varb = self.soup.find("div", attrs={"id" : "bookMeta"})

            tmp1 = varb.find("span", "votes")
            tmp2 = varb.find("span", "count")
            nums["ratings"] = int(tmp1.get("title"))
            nums["reviews"] = int(tmp2.get("title"))

            # varc = varb.find_all("a", "gr-hyperlink")
            # var = varc[0].find("span", "votes")
            # nums["ratings"] = int(var.get("title"))
            # var = varc[1].find("span", "count")
            # nums["reviews"] = int(var.get("title"))

        except Exception as exp:
            var = "getNumbers() Error in class Scraper:\r\n" + str(exp)
            self.info(var)

        return nums

    def getCoverPhotoURL(self):
        """
        Returns
        -------
        str: cover image url
        """
        url = ""
        try:
            url = self.soup.find("img", attrs={"id":"coverImage"}).get("src")
        except Exception as exp:
            var = "getCoverPhotoURL() Error in class Scraper:\r\n" + str(exp)
            self.info(var)
        return url

    def getReviews(self):
        """
        Get user reviews of the first page (reviews of other pages may be added later)

        Returns
        -------
        list(dict): a list of user reviews as a list of dicts of the form {"userURL", "userName", "userReviewDate", "userReview"}
        """
        revs = self.soup.find("div", attrs={"id":"reviews"}).find_all("div", "friendReviews")
        reviews = []
        try:
            for rev in revs:
                review = {}
                review["userURL"] = 'http://www.goodreads.com' + rev.find("div", "review").find("a", "user").get("href")
                review["userName"] = rev.find("div", "review").find("a", "user").text
                review["userReviewDate"] = rev.find("a", "reviewDate").text
                try:
                    textConts = rev.find("div", "reviewText").find("span", "readable").find_all("span")
                    review["userReview"] = textConts[-1].text.strip()
                except:
                    continue
                reviews.append(review)
        except Exception as exp:
            var = "getReviews() Error in class Scraper:\r\n" + str(exp)
            self.info(var)
        return reviews

    def getBookLinks(self):
        """
        Gets all the hyperlinks to Goodreads books in this webpage
        These links will be fed back to the crawler frontline queue
        Also there are the outgoing links that will be used for PageRank
        These links won't contain links related to the current URL, similar URLs will be filtered out using fuzzy string matching
        Returns
        -------
        links: list(str)
               a list of urls of the form 'http://www.goodreads.com/book/show/*'
        """
        links = []
        try:
            for link in self.soup.find_all("a"):
                l = link.get("href")
                if l:
                    if l.startswith("/book/show"):
                        if l.find('?') > 0:
                            l = l[:l.find('?')]
                        l = 'http://www.goodreads.com' + l
                    elif l.startswith("http://www.goodreads.com/book/show"):
                        if l.find('?') > 0:
                            l = l[:l.find('?')]
                    else:
                        continue
                    if not l in links:
                        links.append(l)
        except Exception as exp:
            var = "getBookLinks() Error in class Scraper:\r\n" + str(exp)
            self.info(var)
        return links

    def getBookType(self):
        """
        book type

        """
        bookTypes = []

        try:
            vars = self.soup.find("div", "rightContainer")
            vars = vars.find_all("div", "stacked")
            vars = vars[1]  # slacked
            vars = vars.find("div")
            vars = vars.find("div", "bigBoxBody").find_all("div")[0]
            vars = vars.find_all("div", "elementList")
            for i in range(len(vars)):
                if i > 4 :
                    break
                var = vars[i]
                var = var.find("div", "left").find("a").text.strip()
                bookTypes.append(var)
        except Exception as exp:
            var = "getBookType() Error in class Scraper:\r\n" + str(exp)
            self.info(var)

        return bookTypes

    def getJSON(self):
        """
        This will return a JSON string of the information scraped from this url
        The main object will be a dictionary and its element might themselves be objects, dictionaries, lists or anything else

        Returns
        -------
        js: str
            JSON string representation of scraped information
            Top-level object will be dictionary of this form:
            "title": str -> book title
            "authors": list(dict{"name", "url"}) -> book authors
            "description": str -> description of the book
            "average": float -> average rating of the book
            "ratings": int -> total number of user ratings for this book
            "reviews": int -> total number of user reviews for this book
            "cover": str -> URL to the photo cover
            "userreviews" -> list(dict{"userURL", "userName", "userReview", "userReviewDate"}) -> user reviews for this book
            "url": str -> this book's URL
            "outlinks" : list(str): a filtered list of outgoing URLs to other books on Goodreads website

        """
        obj = {}
        # obj["title"] = self.getTitle()
        # obj["authors"] = self.getAuthors()
        # obj["description"] = self.getDescription()
        # nums = self.getNumbers()
        # obj["average"] = nums["average"]
        # obj["ratings"] = nums["ratings"]
        # obj["reviews"] = nums["reviews"]
        # obj["cover"] = self.getCoverPhotoURL()
        # obj["userreviews"] = self.getReviews()
        obj["url"] = self.url
        # obj["outlinks"] = self.getBookLinks()

        
        tmp = ''
        try:
            tmp = self.getTitle()
        except Exception as exp:
            print "self.getTitle() failed!"
        obj["title"] = tmp
        try:
            obj["authors"] = self.getAuthors()
        except Exception as exp:
            print "self.getAuthors() failed!"

        try:
            obj["description"] = self.getDescription()
        except Exception as exp:
            print "self.getDescription() failed!"

        try:
            nums = self.getNumbers()
        except Exception as exp:
            print "self.getNumbers() failed!"

        tmp = 1
        try:
            tmp = nums["average"]
        except Exception as exp:
            print "nums[\"average\"] failed!"
        obj["average"] = tmp

        tmp = 1  
        try:
            tmp = nums["ratings"]
        except Exception as exp:
            print "nums[\"ratings\"] failed!"
        obj["ratings"] = tmp

        tmp = 1
        try:
            tmp = nums["reviews"]
        except Exception as exp:
            print "nums[\"reviews\"] failed!"
        obj["reviews"] = tmp
        try:
            obj["cover"] = self.getCoverPhotoURL()
        except Exception as exp:
            print "self.getCoverPhotoURL() failed!"
            
        try:
            obj["userreviews"] = self.getReviews()
        except Exception as exp:
            print "self.getReviews() failed!"
        
        try:
            obj["outlinks"] = self.getBookLinks()
        except Exception as exp:
            print "self.getBookLinks() failed!"

        tmp = []
        try:
            tmp = self.getBookType()
        except Exception as exp:
            print "self.getBookType() failed!"
        obj["type"] = tmp
        
        return json.dumps(obj)

    def writeJSON(self, addr):
        """
        This will write the JSON output as a json file in addr directory.
        File name will be the title of the book
        """
        js = self.getJSON()
        filename = self.getTitle().decode('utf-8')
        ignoreDict = {ord(c): None for c in (punctuation + digits + ' ' + '\n')}
        filename = filename.translate(ignoreDict)
        print 'writing json file: ', filename
        with open(os.path.join(addr, filename + '.json'), "w") as f:
            f.write(js)


# http://www.17k.com/
class Scraper_17k:
    """
    books URL scraper class
    This class will get a URL and will try to scrape it and return relevant information
    """

    soup = ''
    url = ''
    # relative weighting of partial_ratio matching score and normal matching score. Partial matching is weighed more than normal matching
    pr_ratio = 0.7
    bookId = 0

    def __init__(self, __url__):
        """
        Scraper class constructor
        Webpage will be downloaded and encoded as BeautifulSoup4 object 'soup'

        Parameters
        ----------
        __url__: str
                 URL to the book webpage
        """
        self.url = __url__
        try:
            arr = __url__.split("/")
            tmp = arr[-1]
            arr1 = tmp.split(".")
            self.bookId = arr1[0]
        except Exception as exp:
            var = "__init__() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)

        down = urllib.urlopen(self.url).read()
        self.soup = bs(down.decode('utf-8'),"html.parser")

    def info(self, s):
        print s

    def getTitle(self):
        """
        Returns
        -------
        str: title of the book
        """
        title = ""
        try:
            var = self.soup.find("div", "Info Sign").find("h1").find("a")
            title = var.text.strip()
        except Exception as exp:
            var = "getTitle() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)

        return title

    def getAuthors(self):
        """
        Returns
        -------
        list(dict): a list of dict items containing author name and author page URL
                            {'name', 'url'}
        """
        authors = []
        try:
            var = self.soup.find("div", "author").find("a", "name")
            authors.append({"name":var.text.strip(), "url" : "http://www.17k.com" + var.get("href")})
        except Exception as exp:
            var = "getAuthors() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)

        return authors

    def getDescription(self):
        """
        Returns
        -------
        str: description of the book
        """

        descs = ""
        try:
            var = self.soup.find("div", "Info Sign").find("dl", "Tab").find("dd").find("div", "cont").find("a")
            descs = var.text.strip()
        except Exception as exp:
            var = "getDescription() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)
        
        return descs

    def getNumbers(self):
        """
        Get average rating, total number of reviews and total number of ratings
        Returns
        -------
        dict: returns a dict object {"average": float, "ratings": int, "reviews": int}
        """
        nums = {}
        nums["average"] = -1.0   # No this attibute
        nums["ratings"] = -1     # No this attibute
        nums["reviews"] = -1     # No this attibute

        tmpUrl = "http://api.ali.17k.com/v2/book/" + str(self.bookId) + "/stat_info?app_key=3362611833"
        
        try:
            # var = self.soup.find("em", attrs={"id" : "howmuchreadBook"})
            # var = self.soup.find("em", "blue")
            # nums["reviews"] = int(var.text.strip())
            #  Unknow how to get
            rawData = urllib.urlopen(tmpUrl).read()
            rawData = rawData.decode('utf-8')
            rawJson = json.loads(rawData, encoding='utf-8')
            nums["reviews"] = rawJson["data"]["click_info"]["total_count"]
           
        except Exception as exp:
            var = "getNumbers() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)

        return nums

    def getCoverPhotoURL(self):
        """
        Returns
        -------
        str: cover image url
        """
        url = ""
        try:
            url = self.soup.find("img", "book").get("src")
        except Exception as exp:
            var = "getCoverPhotoURL() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)
        return url

    def getReviews(self):
        """
        Get user reviews of the first page (reviews of other pages may be added later)

        Returns
        -------
        list(dict): a list of user reviews as a list of dicts of the form {"userURL", "userName", "userReviewDate", "userReview"}
        """
        reviews = []
        try:
            # revs = self.soup.find("div", "comment")
            # revs = self.soup.find_all("script")
            # turl = "http://comment.17k.com/topic_list?bookId=2819588&commentType=all&order=1&page=1&pagesize=20&callback=Q._91_8094_10&jsonp=Q._91_8094_10"
            turl = "http://comment.17k.com/topic_list?bookId=" + str(self.bookId)
            # turl = "http://comment.17k.com/topic/2801193"
            commentRaw = urllib.urlopen(turl).read()
            commentRaw1 = commentRaw.decode('utf-8')
            # with open("temp.txt", "wb") as f:
            #     f.write(ss)
            idx = commentRaw1.find(u"{")
            commentRaw2 = ""
            if idx > 0:
                commentRaw2 = commentRaw1[idx: -1]
            else:
                commentRaw2 = commentRaw1
            rawJsons = json.loads(commentRaw2, encoding='utf-8')
            comments = rawJsons["page"]["result"]

            for rev in comments:
                review = {}
                try:
                    review["userURL"] = "http://user.17k.com/" + str(rev["marks"]["userId"]) 
                    review["userName"] = rev["marks"]["nikeName"] 
                    review["userReview"] = rev["summary"]
                    
                    rawTime = rev["creationDate"]
                    rawTime = str(rawTime)
                    rawTime = rawTime[0: 10]
                    rawTime = int(rawTime)
                    locTime = time.localtime(rawTime)
                    newTime = time.strftime("%Y-%m-%d", locTime)
                    review["userReviewDate"] = unicode(newTime, "utf-8")
                except Exception as exp1:
                    var = "getReviews() Error in class Scraper_17k:\r\n" + str(exp1)
                    self.info(var)
                reviews.append(review)
        except Exception as exp:
            var = "getReviews() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)

        return reviews

    def getBookLinks(self):
        """
        Gets all the hyperlinks to Goodreads books in this webpage
        These links will be fed back to the crawler frontline queue
        Also there are the outgoing links that will be used for PageRank
        These links won't contain links related to the current URL, similar URLs will be filtered out using fuzzy string matching
        Returns
        -------
        links: list(str)
               a list of urls of the form 'http://www.goodreads.com/book/show/*'
        """

        outlinkUrl = [
            "http://www.17k.com/rankingtop/06_vipclick/06_vipclick_mm_top_book_index_10_pc.html",
            "http://www.17k.com/rankingtop/06_vipclick/06_vipclick_man_top_book_index_10_pc.html",
            "http://www.17k.com/rankingtop/06_vipclick/06_vipclick_cool_top_book_index_10_pc.html",
        ]

        links = []

        try:
            for i in range(len(outlinkUrl)):
                data = urllib.urlopen(outlinkUrl[i]).read()
                tmpSo = bs(data.decode('utf-8'),"html.parser")
                for link in tmpSo.find_all("a"):
                    l = link.get("href")
                    if l:
                        if not l.startswith("http://www.17k.com/book/"):
                            continue
                        # pr = fuzz.partial_ratio(l, self.url)
                        # r = fuzz.ratio(l, self.url)
                        # match_score = self.pr_ratio * pr + (1 - self.pr_ratio) * r
                        # if r < 80 and pr < 100:
                        #     links.append(l)
                        if not l in links:
                            links.append(l)
        except Exception as exp:
            var = "getBookLinks() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)
        return links

    def getBookType(self):
        """
        book type

        """
        bookTypes = []

        try:
            var = self.soup.find("div", "Info Sign").find("dl", "Tab")
            var = var.find("dd").find_all("div", "cont")[1]
            var = var.find("table").find("tbody")
            var = var.find_all("tr")[0]
            var = var.find_all("td")[1]
            var = var.find("a").text
            bookTypes.append(var)
        except Exception as exp:
            var = "getBookType() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)

        return bookTypes

    def getJSON(self):
        """
        This will return a JSON string of the information scraped from this url
        The main object will be a dictionary and its element might themselves be objects, dictionaries, lists or anything else

        Returns
        -------
        js: str
            JSON string representation of scraped information
            Top-level object will be dictionary of this form:
            "title": str -> book title
            "authors": list(dict{"name", "url"}) -> book authors
            "description": str -> description of the book
            "average": float -> average rating of the book
            "ratings": int -> total number of user ratings for this book
            "reviews": int -> total number of user reviews for this book
            "cover": str -> URL to the photo cover
            "userreviews" -> list(dict{"userURL", "userName", "userReview", "userReviewDate"}) -> user reviews for this book
            "url": str -> this book's URL
            "outlinks" : list(str): a filtered list of outgoing URLs to other books on Goodreads website

        """
        obj = {}
        # obj["title"] = self.getTitle()
        # obj["authors"] = self.getAuthors()
        # obj["description"] = self.getDescription()
        # nums = self.getNumbers()
        # obj["average"] = nums["average"]
        # obj["ratings"] = nums["ratings"]
        # obj["reviews"] = nums["reviews"]
        # obj["cover"] = self.getCoverPhotoURL()
        # obj["userreviews"] = self.getReviews()
        obj["url"] = self.url
        # obj["outlinks"] = self.getBookLinks()

        tmp = []
        try:
            tmp = self.getBookType()
        except Exception as exp:
            print "self.getBookType() failed!"
        obj["type"] = tmp

        tmp = ''
        try:
            tmp = self.getTitle()
        except Exception as exp:
            print "self.getTitle() failed!"
        obj["title"] = tmp
        try:
            obj["authors"] = self.getAuthors()
        except Exception as exp:
            print "self.getAuthors() failed!"

        try:
            obj["description"] = self.getDescription()
        except Exception as exp:
            print "self.getDescription() failed!"

        try:
            nums = self.getNumbers()
        except Exception as exp:
            print "self.getNumbers() failed!"

        tmp = 1
        try:
            tmp = nums["average"]
        except Exception as exp:
            print "nums[\"average\"] failed!"
        obj["average"] = tmp

        tmp = 1  
        try:
            tmp = nums["ratings"]
        except Exception as exp:
            print "nums[\"ratings\"] failed!"
        obj["ratings"] = tmp

        tmp = 1
        try:
            tmp = nums["reviews"]
        except Exception as exp:
            print "nums[\"reviews\"] failed!"
        obj["reviews"] = tmp
        try:
            obj["cover"] = self.getCoverPhotoURL()
        except Exception as exp:
            print "self.getCoverPhotoURL() failed!"
            
        try:
            obj["userreviews"] = self.getReviews()
        except Exception as exp:
            print "self.getReviews() failed!"
        
        try:
            obj["outlinks"] = self.getBookLinks()
        except Exception as exp:
            print "self.getBookLinks() failed!"

        return json.dumps(obj)

    def writeJSON(self, addr):
        """
        This will write the JSON output as a json file in addr directory.
        File name will be the title of the book
        """
        try:

            js = self.getJSON()
            filename = self.getTitle()
            filename = filename.decode('utf-8')
            ignoreDict = {ord(c): None for c in (punctuation + digits + ' ' + '\n')}
            filename = filename.translate(ignoreDict)
            print 'writing json file: ', filename
            with open(os.path.join(addr, filename + '.json'), "w") as f:
                f.write(js)

        except Exception as exp:
            var = "writeJSON() Error in class Scraper_17k:\r\n" + str(exp)
            self.info(var)
