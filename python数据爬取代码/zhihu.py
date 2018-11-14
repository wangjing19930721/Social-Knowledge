#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-19 14:21:53
# Project: zhihu

from pyspider.libs.base_handler import *
import random
import MySQLdb


class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v1',
        'headers': {
            'User-Agent': 'GoogleBot',
            'Host' : 'www.zhihu.com',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
    }
    
    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'nowcoder', 'wenda', charset='utf8')
    
    def add_question(self, title, content, comment_count):
        try:
            cursor = self.db.cursor()
            sql = 'insert into question(title, content, user_id, created_date, comment_count) values ("%s","%s",%d, %s, %d)' % (title, content, random.randint(1, 10) , 'now()', comment_count);
            #print sql
            cursor.execute(sql)
            qid = cursor.lastrowid
            self.db.commit()
            return qid
        except Exception, e:
            print e
            self.db.rollback()
        return 0
            
    def add_comment(self, qid, comment):
        try:
            cursor = self.db.cursor()
            sql = 'insert into comment(content, entity_type, entity_id, user_id, created_date) values ("%s",%d,%d, %d,%s)' % (comment, 1, qid, random.randint(1, 10) , 'now()');
            #print sql
            cursor.execute(sql)
            self.db.commit()
        except Exception, e:
            print e
            self.db.rollback()

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.zhihu.com/topic/19554298/top-answers?page=3', callback=self.index_page, validate_cert=False)
        self.crawl('https://www.zhihu.com/topic/19552330/top-answers?page=3', callback=self.index_page, validate_cert=False)
        

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a.question_link').items():
            self.crawl(each.attr.href, callback=self.detail_page, validate_cert=False)
        for each in response.doc('.zm-invite-pager span a').items():
            self.crawl(each.attr.href, callback=self.index_page, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        items = response.doc('div.zm-editable-content.clearfix').items()
        title = response.doc('span.zm-editable-content').text()
        html = response.doc('#zh-question-detail .zm-editable-content').html()
        if html == None:
            html = response.doc('#zh-question-detail .content.hidden').html()
            if html == None:
                html = ''
        content = html.replace('"', '\\"')
        print content

        qid = self.add_question(title, content, sum(1 for x in items))
        for each in response.doc('div.zm-editable-content.clearfix').items():
            self.add_comment(qid, each.html().replace('"', '\\"'))

        return {
            "url": response.url,
            "title": title,
            "content": content,
        }
