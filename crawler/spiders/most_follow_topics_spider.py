#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import json
import urlparse

import scrapy
from pybloomfilter import BloomFilter


class MostFollowTopicsSpider(scrapy.spiders.Spider):
    name = "MostFollowTopicsSpider"
    allowed_domains = ["zhihu.com"]
    start_urls = ['https://www.zhihu.com/topic/19776749/organize/entire']

    topic_bloom_filter = BloomFilter(500000, 0.001, 'topic.bloom')

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }

    def parse(self, response):
        url = response.request.url
        if response.request.method == 'GET':
            index = len('https://www.zhihu.com/topic/')
            try:
                topic_id = int(response.url[index:index+8])
            except:
                raw_input('wrong...wait!')
                yield scrapy.Request(url=response.url, callback=self.parse)
            topic_name = response.css('h1.zm-editable-content::text').extract_first()
            followers = int(response.css('div.zm-topic-side-followers-info strong::text').extract_first()) or 0

            self.topic_bloom_filter.add(topic_id)
            yield {
                'topic_id': topic_id,
                'topic_name': topic_name,
                'followers': followers,
            }
            print('[%s] %s: %s' % (topic_id, topic_name, followers))

            self.xsrf = response.css('input[name=_xsrf]::attr(value)').extract_first()
            yield scrapy.FormRequest(response.url, formdata={'_xsrf': self.xsrf},
                                     callback=self.parse)
        elif response.request.method == 'POST':
            js = json.loads(response.text)
            for topic_object_list in js['msg'][1]:
                topic_object = topic_object_list[0]
                if topic_object[0] == 'topic':
                    if topic_object[2] not in self.topic_bloom_filter:
                        yield scrapy.Request('https://www.zhihu.com/topic/%s/organize/entire'%topic_object[2],
                                             callback=self.parse)
                    else:
                        print('repeat')
                elif topic_object[0] == 'load':
                    print('more!!')
                    url = urlparse.urlparse(response.url).path + '?child=%s&parent=%s'%(topic_object[2], topic_object[3])
                    url = response.urljoin(url)
                    yield scrapy.FormRequest(url, formdata={'_xsrf': self.xsrf}, callback=self.parse)

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        return [scrapy.Request(url=captcha_url, headers=self.header, callback=self.parser_captcha)]

    def parser_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
        captcha = raw_input("please input the captcha\n>")
        return scrapy.FormRequest(url='https://www.zhihu.com/#signin', headers=self.header, callback=self.login, meta={
            'captcha': captcha
        })

    def login(self, response):
        xsrf = response.xpath("//input[@name='_xsrf']/@value").extract_first()
        if xsrf is None:
            return ''
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            "_xsrf": xsrf,
            "phone_num": '13987654321',
            "password": 'password',
            "captcha": response.meta['captcha']
        }
        return [scrapy.FormRequest(url=post_url, formdata=post_data, headers=self.header, callback=self.check_login)]

    # 验证返回是否成功
    def check_login(self, response):
        js = json.loads(response.text)
        if 'msg' in js and js['msg'] == u'登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url=url, headers=self.header, dont_filter=True)
        else:
            print('login failed')
            print(js['msg'])
