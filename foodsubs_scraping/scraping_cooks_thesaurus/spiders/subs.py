import scrapy


class SubsSpider(scrapy.Spider):
    name = "subs"

    def start_requests(self):
        urls = [
            'http://www.foodsubs.com',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        prefix = 'http://www.foodsubs.com/'
        page = "_".join(response.url.split("/")[-2:])
        filename = 'scraped_pages/subs_%s.html' % page

        with open(filename, 'wb') as f:
           f.write(response.body)
        self.log('Saved file %s' % filename)

        for link in response.css('a::attr(href)').getall():
            if link[-4:] == 'html' and link[:4] != 'http':
                nextpage = prefix+link
                yield scrapy.Request(nextpage, callback=self.parse)

