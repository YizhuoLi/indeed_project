# -*- coding: utf-8 -*-
import scrapy
import requests
import bs4
from bs4 import BeautifulSoup
import time
from scrapy.http import Request
from indeedSpider.items import IndeedItem
import re

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['www.indeed.com/']
    start_urls = ['https://www.indeed.com/jobs?q=data+scientist&l=']

    def parse(self, response):
        max_results_per_city = 1000

        for start in range(0, max_results_per_city, 10):
            # page = 'http://www.indeed.com/jobs?q=data+scientist&l=' + str(city) + '&start=' + str(start)
            # page = 'https://www.indeed.com/jobs?q=data+scientist&start=' + str(start)
            # time.sleep(1)
            # yield Request(url=page, callback=self.parse_detail, dont_filter=True)

            city_set = ['Miami', 'New+York', 'Chicago', 'San+Francisco', 'Austin', 'Seattle',
                        'Los+Angeles', 'Philadelphia', 'Atlanta', 'Dallas', 'Pittsburgh',
                        'Portland', 'Phoenix', 'Denver', 'Houston', 'Washington+DC', 'Boulder']

            for city in city_set:
                for start in range(0, max_results_per_city, 10):
                        page = 'http://www.indeed.com/jobs?q=data+scientist&l=' + str(city) + '&start=' + str(start)
                        time.sleep(1)
                        yield Request(url=page, callback=self.parse_detail, dont_filter=True)
                        # test = requests.get(page).text
                        # if 'np>Next' not in test:
                        #     yield Request(url=page, callback=self.parse_detail, dont_filter=True)
                        #     break
                        # else:
                        #     yield Request(url=page, callback=self.parse_detail, dont_filter=True)

        pass

    def parse_detail(self, response):
        indeed_item = IndeedItem()
        soup = BeautifulSoup(response.text, "lxml", from_encoding="utf-8")
        jobList = soup.find_all(name="div", attrs={"class": "row"})
        for div in jobList:
            for a in div.find_all(name="a", attrs={"data-tn-element": "jobTitle"}):
                job_title = a["title"]  # appending job title to job_post
                job_href = str('https://www.indeed.com' + a["href"])
                indeed_item['job_title'] = job_title
                indeed_item['job_href'] = job_href
            company = div.find_all(name="span", attrs={"class": "company"})  # most company information is found here.
            if len(company) > 0:  # if there's at least one span tag with class:company, it'll contain the company name
                for b in company:
                    company_name = b.text.strip()  # appending company name to job_post
                    indeed_item['company_name'] =company_name
            else:  # if not, it'll be in a specialty tag of class:result-link-source
                sec_try = div.find_all(name="span", attrs={"class": "result-link-source"})
                for span in sec_try:
                    company_name = span.text  # appending company name to job_post
                    indeed_item['company_name'] = company_name
            for c in div.find_all('span', attrs={'class': 'location'}):  # find all span tags in entry with class = location
                job_location = c.string  # appending location name to job_post
                indeed_item['job_location'] = job_location
            # grabbing summary text
            d = div.findAll('span', attrs={'class': 'summary'})  # find all span tags in entry with class = summary
            for span in d:
                job_summary = span.text.strip()  # appending summary information to job post
                indeed_item['job_summary'] = job_summary
            # grabbing salary data
            try:
                # e = div.findAll('span', attrs={'class': 'no-wrap'})  # if salary info is in 'no-wrap' tag, grab it,
                # for span in e:
                #     job_salary = span.text
                #     indeed_item['job_salary'] = job_salary
                job_salary = div.find('span', attrs={'class': 'no-wrap'}).string.strip()
                indeed_item['job_salary'] = job_salary
            except:
                # try:
                #     div_two = div.find(name="div",
                #                        attrs={"class": "sjcl"})  # otherwise, look for div tags with class:sjcl
                #     div_three = div_two.find(
                #         "div")  # and then look for div tags within and grab text (which will be salary)
                #     job_salary = div_three.text.strip()
                #     indeed_item['job_salary'] = job_salary
                # except:
                job_salary = "Nothing_found"  # otherwise, note that nothing was found
                indeed_item['job_salary'] = job_salary
            #grabing job star rate data
            try:
                for f in div.find_all("span", attrs={"class": "rating"}):
                    job_star = (re.findall(r"width:(.*)px", f["style"])[0])  # appending job star rate to job_post
                    indeed_item['job_star'] = job_star
            except:
                job_star = 'No star'
                indeed_item['job_star'] = job_star
            #frabing job review num
            try:
                for g in div.find_all("span", attrs={"class": "slNoUnderline"}):
                    job_review = (re.findall(r"(.*) reviews", g.string.strip())[0])   # appending job review rate to job_post
                    indeed_item['job_review'] = job_review
            except:
                job_review = 'No review'
                indeed_item['job_review'] = job_review

            yield indeed_item


        pass
    #
    #完成后用sql对数据进行去重与计算
    # -- CREATE table data(select *
    # from (select distinct * from data_science as temp) temp)
    # -- select count(*) from data SELECT  9629
    # count(*) FROM data WHERE job_salary LIKE 'N%d';  8898
    #比较有趣的是，href不是distinct的，有href一样，但其他信息存在不同的
    #另外review存在大量的相似数据，感觉有点像假的
    #job显示在网页上的总数无法全部通过分类界面获得，最多获得1000条，所以要分城市进行抓取
    #create table data_distinct (select * from data3 where job_href in (select * from data2))
