#!/usr/bin/env python3
#coding=utf-8

#============================#
#Program:获取各高校的历年录取分数线
#Date:2019.06.10
#Author:liheng
#Version:V1.0
#============================#

__author__ = 'liheng'

import re
import requests
from lxml import etree
from time import sleep
import random

import json
import string
import smtplib

import os


#===========================================#
#1°通过网址:http://college.gaokao.com/schpoint/a22/s1/,确定在河南省进行录取的一本高校,理科,的页数
#2°遍历每一页上的高校,获取其录取分数详情网址,获得其相应的录取分数等信息,并保存

class GetScore(object):
    '''

    '''

    def __init__(self):
        '''

        '''
        self.headers = \
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36"
            }
        self.user_agent = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]


    def gethtml(self,weburl):
        '''
        获取指定网页内容并返回
        :param weburl: 指定url
        :return: 网页内容
        '''
        try:
            webheader = {"User-Agent": random.choice(self.user_agent)}
            res = requests.get(url=weburl,
                               headers=webheader,
                               timeout=2)  # 设置全局超时时间
            res.close()

            if res.status_code != 200:
                return None
            else:
                return res.content.decode('gb2312')

        except Exception as e:
            print(e)
            return None

    def getScoolPageNum(self,html):
        '''
        获取符合要求的网页页面数量
        :param html: 网页内容
        :return: 符合要求的页面数量
        '''

        p = re.compile(r'li id="qx">1/(.*?)页',re.S)
        content = re.findall(p,html)
        if content:
            num = int(content[0])
        else:
            num = 0

        return num

    def getPageSchoolListUrl(self,url):
        '''
        获取每一页上各个学校关于录取信息的网址
        :param url: 需要获取学校信息的页面url
        :return: 该页面上的各个学校录取信息的url
        '''
        lists = None

        html = self.gethtml(url)
        if html:
            lists = re.findall('<li>录取分数线：<span class="blue"><a href="(.*?)" target=', html, re.S)
        return lists

    def getSchoolScoreInfo(self,schoolScoreUrl):
        '''
        通过网页获取某以学校的录取信息,年份	最低	最高	平均	录取人数.
        仅返回2016年及以后的数据
        :param schoolScoreUrl:
        :return:[str(学校名称 年份 最低 最高 平均 录取人数),...]
        '''
        list = []
        html = self.gethtml(schoolScoreUrl)
        if html:
            selector = etree.HTML(html)
            school_name = selector.xpath('//div[@class="cont_l in"]/p/font[1]/text()')[0] #学校名称
            area = selector.xpath('//div[@class="cont_l in"]/p/font[2]/text()')[0] #招生地区
            s_type = selector.xpath('//div[@class="cont_l in"]/p/font[3]/text()')[0] #文理科


            if selector.xpath('//div[@class="cont_l in"]/div[@class="ts"]'):
                #print("无数据")
                list = []
            elif selector.xpath('//div[@class="cont_l in"]/div[@id="pointbyarea"]/table/tr'):
                # 有数据，采集
                for each_info in selector.xpath('//div[@class="cont_l in"]/div[@id="pointbyarea"]/table/tr'):
                    if each_info.xpath('td[1]/text()'):
                        year = each_info.xpath('td[1]/text()')[0]
                    else:
                        year = ''
                    if each_info.xpath('td[2]/text()'):
                        min = each_info.xpath('td[2]/text()')[0]
                    else:
                        min = ''
                    if each_info.xpath('td[3]/text()'):
                        max = each_info.xpath('td[3]/text()')[0]
                    else:
                        max = ''
                    if each_info.xpath('td[4]/text()'):
                        ave = each_info.xpath('td[4]/text()')[0]
                    else:
                        ave = ''
                    if each_info.xpath('td[5]/text()'):
                        num = each_info.xpath('td[5]/text()')[0]
                    else:
                        num = ''
                    if each_info.xpath('td[6]/text()'):#录取批次
                        admission_type = each_info.xpath('td[6]/text()')[0]
                    else:
                        admission_type = ''

                    #if year != '':
                    if year != '' and int(year)>=2016 and admission_type=='第一批':
                        list.append('%s\t%s\t%s\t%s\t%s\t%s' % (school_name,year,min,max,ave,num))
                        #print(list[-1])

        return list



    def getmessage(self,html):
        '''

        :param html:
        :return:
        '''
        p = re.compile(r'javascript:setpk(.*?);\">', re.S)
        # 对内容进行正则匹配
        message = re.findall(p, html)  # 返回正则匹配的结果
        return message











if __name__ == '__main__':
    page_url = 'http://college.gaokao.com/schpoint/a22/s1/b100/'
    file = open('./schoolScore.txt','w')

    GetScore = GetScore()

    #1°获取页面数量
    html = GetScore.gethtml(page_url)
    pageNum = GetScore.getScoolPageNum(html)#页面数量
    print(pageNum)

    pageNum = 1
    #2°构造每一页的网址,http://college.gaokao.com/schpoint/a22/s1/b100/p5/
    for i in range(1,pageNum+1):
        page_url = "{0}p{1}/".format(page_url,i)

        #3°获取每一页上的学校列表
        schoolList = GetScore.getPageSchoolListUrl(page_url)


        #4°获取该页上的每一个学校信息
        for schoolUrl in schoolList:
            print("正在获取{} ...".format(schoolUrl))
            schoolScoreInfoList = GetScore.getSchoolScoreInfo(schoolUrl)
            for perYear in schoolScoreInfoList:
                #print(perYear)
                file.write(perYear[0]+'\n')

        sleep(0.2)#停顿0.2s




    file.close()




