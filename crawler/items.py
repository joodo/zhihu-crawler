# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Answer(scrapy.Item):
    url = scrapy.Field()
    question = scrapy.Field()
    answer = scrapy.Field()
    answer_date = scrapy.Field()
    like = scrapy.Field()

