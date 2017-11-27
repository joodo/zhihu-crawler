#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import re

import scrapy
from scrapy.utils.markup import remove_tags

from zhihu.items import Answer


def get_date(s):
    clean_s = re.findall(r'\d{4}-\d{2}-\d{2}', s)[-1]
    d = datetime.strptime(clean_s, '%Y-%m-%d')
    return d

class MostLikeAnswersSpider(scrapy.spiders.Spider):
    name = "MostLikeAnswersSpider"
    allowed_domains = ["zhihu.com"]
    start_urls = ['https://www.zhihu.com/topic/19776749/top-answers']

    def parse(self, response):
        for item in response.css(".feed-item"):
            date_tag = item.css('a.answer-date-link')
            last_updated_tag = date_tag.css('::text').extract_first()
            created_tag = date_tag.css('::attr(data-tooltip)').extract_first()
            if not created_tag:
                created_tag = last_updated_tag
            yield {
                'url': item.css('link::attr(href)').extract_first(),
                'question': item.css('h2>a::text').extract_first(),
                'answer': remove_tags(item.css('textarea.content::text').extract_first()),
                'created': get_date(created_tag),
                'last_updated': get_date(last_updated_tag),
                'likes': int(item.css('span.js-voteCount::text').extract_first()),
            }

        next_href = response.css('.zm-invite-pager span:last-of-type>a::attr(href)').extract_first()
        print(next_href)
        if next_href:
            yield response.follow(next_href, callback=self.parse)
