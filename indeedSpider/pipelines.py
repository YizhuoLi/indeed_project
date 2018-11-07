# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
import pymysql
from indeedSpider.models.es_types import IndeedType
from elasticsearch_dsl.connections import connections
es = connections.create_connection(IndeedType)


class IndeedspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonExporterPipeline(object):
    # 此处为调用scrapY提供的JSON export导出JSON文件
    def __init__(self):
        self.file = open('indeedExport.json', 'wb')  # 此处WB表示二进制格式，并且用了open的原因是下一步还是要解码，就懒得管了
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect('localhost', 'root', '12345678', 'IndeedSpider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = 'INSERT INTO data_science(job_title, company_name, job_location, job_summary, job_salary, job_href, job_star, job_review) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (item["job_title"], item["company_name"], item["job_location"], item["job_summary"], item["job_salary"], item["job_href"], item["job_star"], item["job_review"])
        print(insert_sql)
        self.cursor.execute(insert_sql)
        self.conn.commit()
        return item


def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set() #使用set去重
    suggests = []
    for text, weight in info_tuple:
        if text: # 判断text是否存在
            # 调用es的analyzer接口分析字符串
            words = es.indices.analyze(index=index, body={"analyzer": "ik_max_word", "text": "{0}".format(text)},  params={'filter':['lowercase']})
            # analyzed_words = set([r["token"] for r in words if len(r["token"])>1 ]) #判断大于1是因为通常一个字是没什么含义的，但英文不同，所以在此不写>1试一下
            analyzed_words = set([r["token"] for r in words["tokens"]])  # tokens是es中，parse了内容之后的label
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests


class ElasticsearchPipeline(object):
    #将数据写入es中
    def process_item(self, item, spider):
        #将item转化为es的数据
        indeedData = IndeedType()

        indeedData.job_salary = item['job_salary']
        indeedData.job_summary = item['job_summary']
        indeedData.job_location = item['job_location']
        indeedData.job_title = item['job_title']
        indeedData.company_name = item['company_name']
        indeedData.job_href = item['job_href']
        indeedData.job_star = item['job_star']
        indeedData.job_review = item['job_review']

        indeedData.suggest = gen_suggests("indeed", ((indeedData.job_title, 10), (indeedData.job_location, 9), (indeedData.company_name, 8)))

        indeedData.save()

        return item
