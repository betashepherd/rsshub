# -*- coding: utf-8 -*-
import json
import logging
import scrapy
import feedparser
import random
import mysql.connector
import functools
import datetime
import os


class CnbetaSpider(scrapy.Spider):
    name = "cnbeta"

    start_urls = ["https://rss.cnbeta.com.tw"]

    proxy_list = ['61.160.202.82:80', '202.117.115.6:80']

    # Can pass some URLs on the commandline:
    # $ scrapy runspider rssspider.py -a 'urls=http://some.url/,https://some.other.url'
    def __init__(self, *args, **kwargs):
        if kwargs.get('urls'):
            urls = kwargs.pop('urls', [])
            if urls:
                self.start_urls = urls.split(',')

        super(CnbetaSpider, self).__init__(*args, **kwargs)
        self.db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
        )

    def process_request(self, request, spider):
        pass

    def start_requests(self):
        urls = []
        for url in self.start_urls:
            request = scrapy.Request(url)
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy
            urls.append(scrapy.Request(url))
        return urls

    def parse_feed(self, feed):
        """ Parse RSS/Atom feed using feedparser
        """
        data = feedparser.parse(feed)
        if data.bozo:
            logging.error('Bozo feed data. %s: %r',
                          data.bozo_exception.__class__.__name__,
                          data.bozo_exception)
            if (hasattr(data.bozo_exception, 'getLineNumber') and
                    hasattr(data.bozo_exception, 'getMessage')):
                line = data.bozo_exception.getLineNumber()
                logging.error('Line %d: %s', line, data.bozo_exception.getMessage())
                segment = feed.split('\n')[line - 1]
                logging.info('Body segment with error: %r', segment)
            # could still try to return data. not necessarily completely broken
            return None
        return data

    def parse_bak(self, response):
        cursor = self.db.cursor()

        # parse downloaded content with feedparser (NOT re-downloading with feedparser)
        feed = self.parse_feed(response.body)
        if feed:
            # grab some feed elements
            # - https://pythonhosted.org/feedparser/common-rss-elements.html
            # - https://pythonhosted.org/feedparser/common-atom-elements.html

            # ns = feed.namespaces
            feed_title = feed.feed.title
            feed_link = feed.feed.link
            feed_desc = feed.feed.description

            print(response.url)

            for entry in feed.entries:
                # have content?
                content = entry.get('content')
                if content:
                    # content = content[0]
                    content = content[0]['value']

                # item = {
                #     # global feed data
                #     'feed_title': feed_title,
                #     'feed_link': feed_link,
                #     'feed_description': feed_desc,
                #     #
                #     # item entry data
                #     'url': response.url,
                #     'link': entry.link,
                #     'title': entry.title,
                #     'description': entry.description,
                #     # 'date': entry.published,
                #     # 'date': entry.published_parsed,
                #     'date': entry.updated_parsed,
                #
                #     # optional
                #     'content': content,
                #     'type': entry.get('dc_type'),
                # }
                #
                # print(json.dumps(item))
                #
                # print(response.url)

                db_item = {
                    'link': entry.link,
                    'title': entry.title,
                    'summary': entry.description,
                    'content': "",
                }

                # Check if the link already exists in the database
                cursor.execute("SELECT link FROM news WHERE link = %s", (db_item['link'],))
                result = cursor.fetchone()
                if result:
                    logging.info("Link already exists, skipping: %s", db_item['link'])
                    continue

                self.parse_link()
                columns = ', '.join(db_item.keys())
                placeholders = ', '.join(['%s'] * len(db_item))
                sql = "INSERT INTO news (%s) VALUES (%s)" % (columns, placeholders)
                values = tuple(db_item.values())

                cursor.execute(sql, values)
                # yield item

        self.db.commit()
        cursor.close()

    def parse_page(self, response, db_item):
        cursor = self.db.cursor()
        news_detail = response.xpath('//*[@id="artibody"]').get()
        db_item['content'] = news_detail
        db_item['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db_item['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        columns = ', '.join(db_item.keys())
        placeholders = ', '.join(['%s'] * len(db_item))
        sql = "INSERT INTO news (%s) VALUES (%s)" % (columns, placeholders)
        values = tuple(db_item.values())
        cursor.execute(sql, values)
        self.db.commit()
        cursor.close()

    def parse(self, response):
        cursor = self.db.cursor()

        # parse downloaded content with feedparser (NOT re-downloading with feedparser)
        feed = self.parse_feed(response.body)
        if feed:
            # grab some feed elements
            # - https://pythonhosted.org/feedparser/common-rss-elements.html
            # - https://pythonhosted.org/feedparser/common-atom-elements.html

            # ns = feed.namespaces
            feed_title = feed.feed.title
            feed_link = feed.feed.link
            feed_desc = feed.feed.description

            for entry in feed.entries:
                # have content?
                content = entry.get('content')
                if content:
                    # content = content[0]
                    content = content[0]['value']

                db_item = {
                    'link': entry.link,
                    'title': entry.title,
                    'summary': entry.description,
                    'content': "",
                }

                # Check if the link already exists in the database
                cursor.execute("SELECT link FROM news WHERE link = %s", (db_item['link'],))
                result = cursor.fetchone()
                if result:
                    logging.info("Link already exists, skipping: %s", db_item['link'])
                    continue

                parse_page_function = functools.partial(self.parse_page, db_item=db_item)
                yield scrapy.Request(entry.link, callback=parse_page_function)
