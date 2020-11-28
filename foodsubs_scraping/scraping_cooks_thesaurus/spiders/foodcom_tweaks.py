import scrapy


class FoodcomTweaksSpider(scrapy.Spider):
    name = "crawl_food_substitutes"

    def start_requests(self):
        urls = [

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        prefix = ''
        page = "_".join(response.url.split("/")[3:])

        filename = 'sub_scraping/%s.html' % page

        with open(filename, 'wb') as f:
           f.write(response.body)
        self.log('Saved file %s' % filename)

