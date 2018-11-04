# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter
import pymysql


class IndeedspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonExporterPipeline(object):
    #此处为调用scrapY提供的JSON export导出JSON文件
    def __init__(self):
        self.file = open('indeedExport.json', 'wb')  #此处WB表示二进制格式，并且用了open的原因是下一步还是要解码，就懒得管了
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
        insert_sql = 'INSERT INTO data_science(job_title, company_name, job_location, job_summary, job_salary) VALUES ("%s", "%s", "%s", "%s", "%s")' % (item["job_title"], item["company_name"], item["job_location"], item["job_summary"], item["job_salary"])
        self.cursor.execute(insert_sql)
        self.conn.commit()
        return item
