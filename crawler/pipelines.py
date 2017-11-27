# -*- coding: utf-8 -*-

from pprint import pprint

import pymongo
import jieba.posseg as pseg
import jieba


class PrintPipeline(object):
    def process_item(self, item, spider):
        pprint(item)
        return item


class MostLikeAnswerPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.analyse = {
            'question': {},
            'answer': {},
        }

    def close_spider(self, spider):
        analyse_coll = self.db[spider.name + 'AnalyseQuestion']
        analyse_coll.insert_many([{'word': word, 'count': self.analyse['question'][word]} for word in self.analyse['question']])
        analyse_coll = self.db[spider.name + 'AnalyseAnswer']
        analyse_coll.insert_many([{'word': word, 'count': self.analyse['answer'][word]} for word in self.analyse['answer']])

        self.client.close()

    def process_item(self, item, spider):
        self.db[spider.name + 'Items'].insert_one(dict(item))

        words = pseg.cut(item['question'], HMM=False)
        for word, flag in words:
            # 连词、叹词、拟声词、介词、量词、代词、处所词、助词、标点符号、语气词
            if flag[0] in ('c', 'e', 'o', 'p', 'q', 'r', 's', 'u', 'w', 'x', 'y'):
                continue
            if word in self.analyse['question']:
                self.analyse['question'][word] += 1
            else:
                self.analyse['question'][word] = 1

        words = pseg.cut(item['answer'], HMM=False)
        for word, flag in words:
            # 连词、叹词、拟声词、介词、量词、代词、处所词、助词、标点符号、语气词
            if flag[0] in ('c', 'e', 'o', 'p', 'q', 'r', 's', 'u', 'w', 'x', 'y'):
                continue
            if word in self.analyse['answer']:
                self.analyse['answer'][word] += 1
            else:
                self.analyse['answer'][word] = 1

        return item


class MostFollowTopicsPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
