import argparse
import web
import subprocess
urls = (
    '/search/(.+)', 'index',
    '/detail', 'detail',
    '/title/(.+)', 'Title',
    '/author/(.+)', 'Author',
    '/genre/(.+)', 'genre',
    '/', 'search'
)

use_elasticsearch = True

class search:

    def GET(self):
        render = web.template.render('templates/')
        return render.search()


class index:

    def GET(self, query):
        data_input = web.input()
        page = 0
        if "page" in data_input:
            page = int(data_input["page"])
        render = web.template.render('templates/')
        anses = []
        num_pages = 0
        # print 'query content:', query
        if use_elasticsearch:
            # importing libraries for Elasticsearch
            from elasticsearch import Elasticsearch
            from elasticsearch_dsl import Search, document, field, connections, Q
            from elasticsearch_dsl.connections import connections
            from booktype import Book

            es = Elasticsearch()
            es.indices.create(index='book-index', ignore=[400, 404])
            connections.create_connection(hosts=['localhost'], timeout=20)
            connections.add_connection('book', es)
            # print(connections.get_connection().cluster.health())
            s = Search(using=es, index='book-index').doc_type('book').query(Q('match', title=query.strip()) | Q('match', description=query.strip()) | Q("match", userreviews_userReview=query.strip()) | Q("match", type=query.strip()))
            ## This damn statement took half an hour from me! Nowhere in the documentation indicated that this statement should be before s.execute()
            s = s[page*10 : page * 10 + 10]
            response = s.execute()
            # print 'total number of hits: ', response.hits.total
            num_pages = (response.hits.total / 10) + 1
            for res in response:
                authors = zip(res.authors_name, res.authors_url)

                anses.append({'title':res.title, 'description': res.description.encode('utf-8'), 'url': res.url, 'cover':res.cover, 'authors':authors, 'types':res.type})
        else:
            try:
                anse = anses[0]
            except Exception as exp:
                print "get anses error"

        return render.index(anses, query, num_pages)

class detail:
    def GET(self):
        render = web.template.render('templates/')
        details = []
        data_input = web.input()
        query_author=""
        query_title=""
        if "author" in data_input:
            query_author = data_input["authors"]
        query_title=data_input["title"]


        if use_elasticsearch:
            # importing libraries for Elasticsearch
            from elasticsearch import Elasticsearch
            from elasticsearch_dsl import Search, document, field, connections, Q
            from elasticsearch_dsl.connections import connections
            from booktype import Book

            es = Elasticsearch()
            es.indices.create(index='book-index', ignore=[400, 404])
            connections.create_connection(hosts=['localhost'], timeout=20)
            connections.add_connection('book', es)
            # print(connections.get_connection().cluster.health())
            #s = Search(using=es, index='book-index').doc_type('book').query(Q('match', title=query.strip()) | Q('match', description=query.strip()) | Q("match", userreviews_userReview=query.strip()))
            s = Search(using=es).index('book-index').doc_type('book').query(
                Q('match', title=query_title) | Q('match', authors_name=query_author))
            ## This damn statement took half an hour from me! Nowhere in the documentation indicated that this statement should be before s.execute()
            response = s.execute()
            userreviews_userName=["None"]
            userreviews_userURL=["#"]
            userreviews_userReview=["None"]
            userreviews_userReviewDate=["None"]
            # print 'total number of hits: ', response.hits.total
            for res in response:
                authors = zip(res.authors_name, res.authors_url)
                try:
                    reviews = zip(res.userreviews_userName, res.userreviews_userURL,
                              res.userreviews_userReview, res.userreviews_userReviewDate)
                except:
                    reviews=zip(userreviews_userName,userreviews_userURL,userreviews_userReview,userreviews_userReviewDate)

                details.append({'title': res.title, 'description': res.description.encode('utf-8'), 'url': res.url, 'cover':res.cover, 'authors':authors, 'reviews': reviews, 'types': res.type})
                break
        else:
            try:
                detail = details[0]
            except Exception as exp:
                print "get detail error"

        return render.details(details)

class genre:
    def GET(self, query):
        data_input = web.input()
        page = 0
        if "page" in data_input:
            page = int(data_input["page"])
        render = web.template.render('templates/')
        anses = []
        num_pages = 0
        # print 'query content:', query
        if use_elasticsearch:
            # importing libraries for Elasticsearch
            from elasticsearch import Elasticsearch
            from elasticsearch_dsl import Search, document, field, connections, Q
            from elasticsearch_dsl.connections import connections
            from booktype import Book

            es = Elasticsearch()
            es.indices.create(index='book-index', ignore=[400, 404])
            connections.create_connection(hosts=['localhost'], timeout=20)
            connections.add_connection('book', es)
            # print(connections.get_connection().cluster.health())
            s = Search(using=es, index='book-index').doc_type('book').query(Q("match", type=query.strip()))
            ## This damn statement took half an hour from me! Nowhere in the documentation indicated that this statement should be before s.execute()
            s = s[page * 10: page * 10 + 10]
            response = s.execute()
            # print 'total number of hits: ', response.hits.total
            num_pages = (response.hits.total / 10) + 1
            for res in response:
                authors = zip(res.authors_name, res.authors_url)
                anses.append({'title': res.title, 'description': res.description.encode('utf-8'), 'url': res.url,
                              'cover': res.cover, 'authors': authors, 'types': res.type})
        else:
            try:
                anse = anses[0]
            except Exception as exp:
                print "get genre error"


        return render.genre(anses, query, num_pages)

class Title:
    def GET(self, query):
        data_input = web.input()
        page = 0
        if "page" in data_input:
            page = int(data_input["page"])
        render = web.template.render('templates/')
        anses = []
        num_pages = 0
        # print 'query content:', query
        if use_elasticsearch:
            # importing libraries for Elasticsearch
            from elasticsearch import Elasticsearch
            from elasticsearch_dsl import Search, document, field, connections, Q
            from elasticsearch_dsl.connections import connections
            from booktype import Book

            es = Elasticsearch()
            es.indices.create(index='book-index', ignore=[400, 404])
            connections.create_connection(hosts=['localhost'], timeout=20)
            connections.add_connection('book', es)
            # print(connections.get_connection().cluster.health())
            s = Search(using=es, index='book-index').doc_type('book').query(Q("match", title=query.strip()))
            ## This damn statement took half an hour from me! Nowhere in the documentation indicated that this statement should be before s.execute()
            s = s[page * 10: page * 10 + 10]
            response = s.execute()
            # print 'total number of hits: ', response.hits.total
            num_pages = (response.hits.total / 10) + 1
            for res in response:
                authors = zip(res.authors_name, res.authors_url)
                anses.append({'title': res.title, 'description': res.description.encode('utf-8'), 'url': res.url,
                              'cover': res.cover, 'authors': authors, 'types': res.type})
        else:
            try:
                anse = anses[0]
            except Exception as exp:
                print "get genre error"


        return render.index(anses, query, num_pages)


class Author:
    def GET(self, query):
        data_input = web.input()
        page = 0
        if "page" in data_input:
            page = int(data_input["page"])
        render = web.template.render('templates/')
        anses = []
        num_pages = 0
        # print 'query content:', query
        if use_elasticsearch:
            # importing libraries for Elasticsearch
            from elasticsearch import Elasticsearch
            from elasticsearch_dsl import Search, document, field, connections, Q
            from elasticsearch_dsl.connections import connections
            from booktype import Book

            es = Elasticsearch()
            es.indices.create(index='book-index', ignore=[400, 404])
            connections.create_connection(hosts=['localhost'], timeout=20)
            connections.add_connection('book', es)
            # print(connections.get_connection().cluster.health())
            s = Search(using=es, index='book-index').doc_type('book').query(Q("match", authors_name=query.strip()))
            ## This damn statement took half an hour from me! Nowhere in the documentation indicated that this statement should be before s.execute()
            s = s[page * 10: page * 10 + 10]
            response = s.execute()
            # print 'total number of hits: ', response.hits.total
            num_pages = (response.hits.total / 10) + 1
            for res in response:
                authors = zip(res.authors_name, res.authors_url)
                anses.append({'title': res.title, 'description': res.description.encode('utf-8'), 'url': res.url,
                              'cover': res.cover, 'authors': authors, 'types': res.type})
        else:
            try:
                anse = anses[0]
            except Exception as exp:
                print "get genre error"


        return render.index(anses, query, num_pages)

if __name__ == "__main__":
    """
    main entry of the searching module
    """
    if use_elasticsearch:
        'Searching using Elasticsearch index.'
    else:
        'Searching using Lucene index.'
    app = web.application(urls, globals())
    app.run()
