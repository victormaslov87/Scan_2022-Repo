import scrapy,json,os,platform,csv
from crawldata.functions import *
from datetime import datetime

class CrawlerSpider(scrapy.Spider):
    name = 'All_programs'
    DATE_CRAWL=datetime.now().strftime('%Y-%m-%d')
    #custom_settings={'LOG_FILE':'./log/'+name+'_'+DATE_CRAWL+'.log'}
    if platform.system()=='Linux':
        URL='file:////' + os.getcwd()+'/scrapy.cfg'
    else:
        URL='file:///' + os.getcwd()+'/scrapy.cfg'
    def start_requests(self):
        yield scrapy.Request('https://programs.dsireusa.org/api/v1/programs?start=0&length=250',callback=self.parse,dont_filter=True)
    def parse(self, response):
        DATA=json.loads(response.text)
        Data=DATA['data']
        for row in Data:
            slug=Get_Slug(row['name'])
            url='https://programs.dsireusa.org/system/program/detail/'+str(row['id'])+'/'+slug
            yield scrapy.Request(url,callback=self.parse_data,dont_filter=True)
        if DATA['meta']['offset']<DATA['meta']['total']:
            yield scrapy.Request('https://programs.dsireusa.org/api/v1/programs?start='+str(DATA['meta']['offset']+DATA['meta']['limit'])+'&length='+str(DATA['meta']['limit']),callback=self.parse,dont_filter=True)
    def parse_data(self, response):
        html=response.xpath('//div[@data-ng-controller="DetailsPageCtrl"]/@data-ng-init').get()
        html=((str(html).split('init(')[1]).strip())[:-1]
        row=json.loads(html)
        item={}
        item['id']=row['program']['id']
        item['Program Name']=row['program']['name']
        item['State/Territory']=row['program']['stateObj']['abbreviation']
        item['Category']=row['program']['categoryObj']['name']
        item['Policy Incentive Type']=row['program']['typeObj']['name']
        item['Implementing Sector']=row['program']['sectorObj']['name']
        item['State']=row['program']['stateObj']['name']
        item['Incentive Type']=row['program']['typeObj']['name']
        item['Website']=row['program']['websiteUrl']
        item['Administrator']=row['program']['administrator']
        item['Start Date']=row['program']['startDate']
        DT=[]
        if not isinstance(row['technologiesByEnergyCategory'],list):
            for V in row['technologiesByEnergyCategory'].values():
                for rs in V:
                    DT.append(rs['name'])
        if row['program']['additionalTechnologies']:
            DT.append(row['program']['additionalTechnologies'])
        item['Eligible Sector']=', '.join(DT)
        DT=[]
        for rs in row['sectors']:
            DT.append(rs['name'])
        item['Applicable Sectors']=', '.join(DT)
        item['Incentive Amount']=''
        for rs in row['details']:
            if rs['label']=="Incentive Amount":
                item['Incentive Amount']=cleanhtml(rs['value'])
        item['Expiration Date']=row['program']['endDate']
        yield(item)