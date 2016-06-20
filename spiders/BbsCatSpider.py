# coding=utf-8

import mysql
import MySQLdb
import scrapy
import sys
import json
import re
import const
from byrbbs.items import ByrbbsItem
from const import DB_CONFIG
class BbsCatSpider(scrapy.Spider):
    name = 'bbscat'
    allowed_domains = const.ALLOW_DOMAINS
    cookiejar = {}
    pat = r'href="(/\w+/\w+)" title="(.*)"\s*>'
    db = None
    headers = const.HEADERS
    start_urls = ['http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-0','http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-1','http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-2','http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-3', 'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-4', 'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-5', 'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-6', 'http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-7','http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-8','http://bbs.byr.cn/section/ajax_list.json?uid=bill220&root=sec-9']

    def parse(self,response):
        item = ByrbbsItem()
	body = response.body_as_unicode()
        data = json.loads(body.encode('utf-8'))
        for panel in data:
           ma = re.search(self.pat, panel['t'], re.I);
           url = ma.group(1);
           title = ma.group(2);
	   self.store_data({'url': url, 'name': title.encode('utf8')})

    def start_requests(self):
        self.db = mysql.MySQL(DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['passwd'], DB_CONFIG['db'], DB_CONFIG['port'], DB_CONFIG['charset'], DB_CONFIG['timeout'], '')
	return [scrapy.FormRequest("http://bbs.byr.cn/user/ajax_login.json",
                formdata = const.LOGIN_DATA,
                meta = {'cookiejar':1},
                headers = self.headers,
                callback=self.logged_in)]
    def logged_in(self,response):
	self.cookiejar = response.meta['cookiejar']
	for url in self.start_urls:
	    yield scrapy.Request(url,meta={'cookiejar':response.meta['cookiejar']},headers=self.headers,callback=self.parse)
    def store_data(self, data):
        sql = "insert into sect(url, name) values ('%s', '%s')" % (MySQLdb.escape_string(data['url']), MySQLdb.escape_string(data['name']))
        self.db.update(sql);
