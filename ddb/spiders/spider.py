import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DdbItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'

class DdbSpider(scrapy.Spider):
	name = 'ddb'
	base = "https://www.db.com/api/content/limit/15/offset/{}/render/false/type/json/query/%20+((categories:adHocRelease%20categories:event1%20categories:mediaRelease%20categories:news%20categories:research)%20&&%20(categories:art%20categories:awards%20categories:banking%20categories:boardsAndCommittees%20categories:bonds%20categories:brexit%20categories:capitalMarkets%20categories:careers%20categories:certificates%20categories:company1%20categories:corporateClients%20categories:corporateCulture%20categories:corporateFinance%20categories:corporateGovernance%20categories:corporateResponsibility1%20categories:crPortalHome%20categories:cryptocurrency%20categories:culture%20categories:digitalBankingServices%20categories:digitalisation%20categories:diversity%20categories:economy%20categories:economystories%20categories:educationBornToBe%20categories:employeeEngagement%20categories:employer1%20categories:ethicsConduct%20categories:finance%20categories:financialPerformance%20categories:financialResults%20categories:financing%20categories:fintech%20categories:fullServiceBank%20categories:ghpHome%20categories:globalReach%20categories:greenBonds%20categories:history%20categories:homeMarket%20categories:hrDevelopment%20categories:industry%20categories:initialPublicOfferingsIpos%20categories:innovation1%20categories:innovationCulture%20categories:interview%20categories:investmentFund%20categories:investorRelations%20categories:irHome%20categories:managementLeadership%20categories:markets%20categories:mergersAcquisitionsMA%20categories:microfinance%20categories:personnelAnnouncements%20categories:productsServices%20categories:realEstate%20categories:renewableEnergy%20categories:renminbi%20categories:researchEuropeanIntegration%20categories:researchGermany%20categories:researchGlobalFinancialMarkets%20categories:researchSocietyNaturalResources%20categories:researchTechnologyInnovation%20categories:retirementProvision%20categories:smallBusinesses%20categories:socialResponsibility%20categories:society%20categories:sports%20categories:startups%20categories:strategy%20categories:sustainability%20categories:sustainableInvestmentStrategiesEsg%20categories:sustainableProducts%20categories:technology%20categories:topVersion%20categories:transactionBanking%20categories:urbanDevelopment%20categories:wealthManagement))%20%20+C03News.publishDate:%5B20150101000000%20to%2020211231235959%5D%20+conhost:8e29bc28-e0f6-40f1-930a-6258631a0985%20+languageId:1%20+deleted:false%20/orderby/C03News.publishDate%20desc"
	offset = 0
	start_urls = [base.format(offset)]

	def parse(self, response):
		data = json.loads(response.text)

		for index in range(len(data['contentlets'])):
			links = data['contentlets'][index]['urlMap']
			yield response.follow(links, self.parse_post)

		if not len(data['contentlets']) == 0:
			self.offset += 15
			yield response.follow(self.base.format(self.offset), self.parse, dont_filter=True)

	def parse_post(self, response):

		date = response.xpath('//div[@class="meta-bar"]/span[last()]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('(//div[@class="rich-text"])[1]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=DdbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
