# 知乎爬虫

爬取点赞数最多的回答、关注数最多的话题。

技术栈：

- Scrapy（爬虫）
- Jieba（分词，用于爬取结果的词频分析）
- Bloom Filter（用于过滤重复的话题）
- webpack
- mongodb
- node.js
- express
- mustache

## 运行

### 爬虫

```
scrapy crawl [spider_name] --nolog
```

`spider_name`: MostFollowTopicsSpider 或 MostLikeAnswersSpider

### Web

```
cd web
node server/main.js
```

