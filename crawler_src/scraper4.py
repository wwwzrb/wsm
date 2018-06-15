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
import cookielib  
import urllib2



# Deal with Chinese problem [encoding problem]
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# https://www.qidian.com/
class Scraper_QiDian:
    """
    books URL scraper class
    This class will get a URL and will try to scrape it and return relevant information
    """

    soup = ''
    url = ''
    authorId = ""
    bookId = ""
    cookie = ""

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
            self.bookId = tmp
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            resp = urllib2.urlopen(__url__);  
            for index, cookie in enumerate(cj):
                if "_csrfToken" == cookie.name:
                    self.cookie = cookie.value
                    break
            
        except Exception as exp:
            var = "__init__() Error in class Scraper_QiDian:\r\n" + str(exp)
            self.info(var)

        down = urllib.urlopen(self.url).read()
        self.soup = bs(down.decode('utf-8'))
        self.authorId = self.getAuthorId()
        

    def info(self, s):
        print s

    def getAuthorId(self):
        autId = ""

        try:
            var = self.soup.find("div", "author-photo").get("data-authorid").strip()
            autId = str(var)
        except Exception as exp:
            var = "getAuthorId() Error in class Scraper_QiDian:\r\n" + str(exp)
            self.info(var)

        return autId

    def getTitle(self):
        """
        Returns
        -------
        str: title of the book
        """
        title = ""
        try:
            var = self.soup.find("div", "book-info")
            var = var.find("h1")
            temp = var.find("em").text
            title = temp
        except Exception as exp:
            var = "getTitle() Error in class Scraper_QiDian:\r\n" + str(exp)
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
            var = self.soup.find("a", "writer")
            authors.append({"name":var.text.strip(), "url" : "https:" + var.get("href")})
        except Exception as exp:
            var = "getAuthors() Error in class Scraper_QiDian:\r\n" + str(exp)
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
            var = self.soup.find("p", "intro")
            descs = var.text.strip()
        except Exception as exp:
            var = "getDescription() Error in class Scraper_QiDian:\r\n" + str(exp)
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

       
        try:
            var1 = self.soup.find("cite", attrs={"id" : "score1"})
            var1 = var1.text.strip()
            var2 = self.soup.find("i", attrs={"id" : "score2"})
            var2 = var2.text.strip()
            var = "%s.%s" % (var1, var2)
            nums["ratings"] = float(var)

            # var = self.soup.find("p", attrs={"id" : "j_userCount"})
            # var = var.find("span").text.strip() # Can not get data
            # nums["reviews"] = int(var)
        
        except Exception as exp:
            var = "getNumbers() Error in class Scraper_QiDian:\r\n" + str(exp)
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
            url = self.soup.find("a", attrs={"id" : "bookImg"}).find("img").get("src")
            url = url[:-1]  # remove '\n'
        except Exception as exp:
            var = "getCoverPhotoURL() Error in class Scraper_QiDian:\r\n" + str(exp)
            self.info(var)
        return url

    def getReviews(self):
        """
        Get user reviews of the first page (reviews of other pages may be added later)

        Returns
        -------
        list(dict): a list of user reviews as a list of dicts of the form {"userURL", "userName", "userReviewDate", "userReview"}
        """
        # https://book.qidian.com/ajax/book/GetBookForum?_csrfToken=5EKKoKOZ5Vs2dlZyT9sPnMDLJiwOE8cW7t68UZ4k&authorId=4374001&bookId=3547179&chanId=1&pageSize=15

        # Ref: https://blog.csdn.net/t8116189520/article/details/80319339
        turl = "%s_csrfToken=%s&authorId=%s&bookId=%s&chanId=1&pageSize=15" % (
            "https://book.qidian.com/ajax/book/GetBookForum?",
            str(self.cookie),
            str(self.authorId),
            str(self.bookId)
        )
        reviews = []
        

        try:

            commentRaw = urllib.urlopen(turl).read()
            commentRaw1 = commentRaw.decode('utf-8')
            rawJsons = json.loads(commentRaw1, encoding='utf-8')
            comments = rawJsons["data"]["threadList"]

            for i in range(len(comments)):
                if i == 0:
                    continue
                review = {}
                rev = comments[i]
                try:
                    review["userURL"] = "https://my.qidian.com/user/" + str(rev["userId"])
                    review["userName"] = rev["userName"]
                    review["userReview"] = rev["content"]
                    review["userReviewDate"] = rev["dateTime"]
                except Exception as exp1:
                    var = "getReviews() Error in class Scraper_QiDian:\r\n" + str(exp1)
                    self.info(var)
                reviews.append(review)
        except Exception as exp:
            var = "getReviews() Error in class Scraper_QiDian:\r\n" + str(exp)
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
            
            data = self.soup.find_all("a")
            for var in data:
                var = var.get("href").strip()
                if "//book.qidian.com/info/" in var:
                    l = "https:" + var
                    links.append(l)
        except Exception as exp:
            var = "getBookLinks() Error in class Scraper_QiDian:\r\n" + str(exp)
            self.info(var)
        return links

    def getBookType(self):
        """
        book type

        """
        bookTypes = []

        try:
            data = self.soup.find("p", "tag")
            arr = data.find_all("a", "red")
            for i in range(len(arr)):
                if i > 4:
                    break
                var = arr[i]
                tmp = var.text.strip()
                bookTypes.append(tmp)
  
        except Exception as exp:
            var = "getBookType() Error in class Scraper_QiDian:\r\n" + str(exp)
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
            self.info("self.getTitle() failed!")
        obj["title"] = tmp
        
        try:
            obj["authors"] = self.getAuthors()
        except Exception as exp:
            self.info("self.getAuthors() failed!")

        try:
            obj["description"] = self.getDescription()
        except Exception as exp:
            self.info("self.getDescription() failed!")

        try:
            nums = self.getNumbers()
        except Exception as exp:
            self.info("self.getNumbers() failed!")

        tmp = 1
        try:
            tmp = nums["average"]
        except Exception as exp:
            self.info("nums[\"average\"] failed!")
        obj["average"] = tmp

        tmp = 1  
        try:
            tmp = nums["ratings"]
        except Exception as exp:
            self.info("nums[\"ratings\"] failed!")
        obj["ratings"] = tmp

        tmp = 1
        try:
            tmp = nums["reviews"]
        except Exception as exp:
            self.info("nums[\"reviews\"] failed!")
        obj["reviews"] = tmp
        try:
            obj["cover"] = self.getCoverPhotoURL()
        except Exception as exp:
            self.info("self.getCoverPhotoURL() failed!")
            
        try:
            obj["userreviews"] = self.getReviews()
        except Exception as exp:
            self.info("self.getReviews() failed!")
        
        try:
            obj["outlinks"] = self.getBookLinks()
        except Exception as exp:
            self.info("self.getBookLinks() failed!")

        tmp = []
        try:
            tmp = self.getBookType()
        except Exception as exp:
            self.info("self.getBookType() failed!")
        obj["type"] = tmp

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
            var = "writeJSON() Error in class Scraper_QiDian:\r\n" + str(exp)
            self.info(var)
