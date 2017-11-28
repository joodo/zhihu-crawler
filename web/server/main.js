var fs = require('fs');

var Mustache = require('mustache');

var MongoClient = require('mongodb').MongoClient;

var Moment = require('moment');

var express = require('express');
var app = express();

var baseHtml = fs.readFileSync('public/base.html').toString();

var database;
var pageData = {
    'top-answer-list': {
        'title': '点赞最多的回答',
        'th': [ '点赞数', '问题', '回答日期', '最后修改日期', '链接' ],

        'collection': 'MostLikeAnswersSpiderItems',
        'sort': {'likes': -1},
        'fields': [
            '{{ likes }}',
            '{{ question }}',
            '{{ #formatDate }}{{ created }}{{ /formatDate }}',
            '{{ #formatDate }}{{ last_updated }}{{ /formatDate }}',
            '<a href="https://www.zhihu.com{{ url }}">详细</a>'
        ]
    },
    'top-answer-question-analyse': {
        'title': '点赞最多的回答的问题词频',
        'th': [ '词', '计数' ],
        'hint': '已去除连词、叹词、拟声词、介词、量词、代词、处所词、助词、标点符号、语气词',

        'collection': 'MostLikeAnswersSpiderAnalyseQuestion',
        'sort': {'count': -1},
        'fields': [
            '{{ word }}',
            '{{ count }}'
        ]
    },
    'top-answer-answer-analyse': {
        'title': '点赞最多的回答的词频',
        'th': [ '词', '计数' ],
        'hint': '已去除连词、叹词、拟声词、介词、量词、代词、处所词、助词、标点符号、语气词',

        'collection': 'MostLikeAnswersSpiderAnalyseAnswer',
        'sort': {'count': -1},
        'fields': [
            '{{ word }}',
            '{{ count }}'
        ]
    },
    'top-follow-topic': {
        'title': '关注人数最多的话题',
        'th': [ '话题', '关注人数', '链接' ],

        'collection': 'MostFollowTopicsSpider',
        'sort': {'followers': -1},
        'fields': [
            '{{ topic_name }}',
            '{{ followers }}',
            '<a href="https://www.zhihu.com/topic/{{ topic_id }}">详细</a>'
        ]
    }
}

app.use(express.static('public/js'), {maxAge:1000*60*60});
app.get('/*', function(request, response) {
    var view = pageData[request.params[0]]
    if (!view || view === '' || view === 'index') {
        response.send(Mustache.render(baseHtml, {
            'title': '把咖脸撕哭',
            'hint': '↑↑↑ 点击菜单查看数据 ↑↑↑'
        }))
        return;
    }

    var page = parseInt(request.query.page || 1)
    view['pagination'] = createPagination(page);

    var skip = 20*(page-1)
    var collection = database.collection(view.collection);
    collection.find().sort(view.sort).skip(skip).limit(20).toArray(function(err, result) {
        response.send(Mustache.render(Mustache.render(baseHtml, view), {
            'result': result,
            'formatDate': function() {
                return function(text, render) {
                    return Moment(render(text)).format('YYYY-MM-DD');
                }
            }
        }))
    });
})

function createPagination(page) {
    var i;
    var pagination = new Array();
    if (page > 1) {
        pagination.push({
            'page': 1,
            'text': '第一页'
        })
        pagination.push({
            'page': page-1,
            'text': '上一页'
        })
    }
    for (i = Math.max(1, page-5); i < page; i++) {
        pagination.push({
            'page': i,
            'text': i
        })
    }
    pagination.push({
        'page': page,
        'text': page,
        'active': true
    })
    for (i = page+1; i < page+5; i++) {
        pagination.push({
            'page': i,
            'text': i
        })
    }
    pagination.push({
        'page': page+1,
        'text': '下一页'
    })
    return pagination;
}

var server = app.listen(8080, function() {
    var key;
    var i;

    for (key in pageData) {
        pageData[key]['tbody'] = '{{#result}}<tr>';
        for (i in pageData[key]['fields']) {
            pageData[key]['tbody'] += '<td>'+pageData[key]['fields'][i]+'</td>';
        }
        pageData[key]['tbody'] += '</tr>{{/result}}';
    }
    MongoClient.connect('mongodb://127.0.0.1:27017/items', function(err, db) {
        console.log("连接成功！");
        database = db;
    });
});
