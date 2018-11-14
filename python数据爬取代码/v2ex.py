#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-17 11:11:46
# Project: v2ex

from pyspider.libs.base_handler import *
import re
import random
import MySQLdb


class Handler(BaseHandler):
    crawl_config = {
    }
    
    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'nowcoder', 'wenda', charset='utf8')
    
    def add_question(self, title, content):
        try:
            cursor = self.db.cursor()
            sql = 'insert into question(title, content, user_id, created_date, comment_count) values ("%s","%s",%d, %s, 0)' % (title, content, random.randint(1, 10) , 'now()');
            print sql
            cursor.execute(sql)
            self.db.commit()
        except Exception, e:
            print e
            self.db.rollback()
        
    

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://v2ex.com', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http://v2ex.com/?tab="]').items():
            self.crawl(each.attr.href, callback=self.tab_page)
   
    @config(age=10 * 24 * 60 * 60)
    def tab_page(self, response):
        for each in response.doc('a[href^="http://v2ex.com/go/"]').items():
            self.crawl(each.attr.href, callback=self.board_page)
    
    @config(priority=2)
    def board_page(self, response):
        for each in response.doc('a[href^="http://v2ex.com/t/"]').items():
            url = each.attr.href
            if url.find('#reply') > 0:
                url = url[0:url.find('#')]
            self.crawl(url, callback=self.detail_page)
        for each in response.doc('a.page_normal').items():
            self.crawl(each.attr.href, callback=self.board_page)

    @config(priority=20)
    def detail_page(self, response):
        title = response.doc('h1').text()
        content = response.doc('div.topic_content').html()
        self.add_question(title, content)
        return {
            'url': response.url,
            'title': title,
            'content': content
        }
