import scrapy
import calendar
import datetime
import sys

from Crawlers.XSMN.XSMN.items import XsmnItem
from scrapy.spiders import CrawlSpider


class SxmnSpider(CrawlSpider):
    name = 'xsmn'
    allowed_domains = ['xskt.com.vn']

    start_urls = []

    now = datetime.datetime.now()
    if now.hour < 19:
        now -= datetime.timedelta(days=1)
    start_urls.append('http://xskt.com.vn/ket-qua-xo-so-theo-ngay/mien-nam-xsmn/'
                      '{0}-{1}-{2}.html'.format(now.day, now.month, now.year))

    def parse(self, response):
        xs_item = XsmnItem()
        tmp_data = {}
        data_resp = scrapy.Selector(response)

        xs_item['xs_info'] = [
            # Thứ
            data_resp.xpath("//table[@id='MN0']/tr/th[1]/a/text()").extract_first(),
            # Ngày tháng
            data_resp.xpath("//table[@id='MN0']/tr/th[1]/text()").extract_first(),
            self.now.year
        ]

        for i in range(2, 5):
            # Các tỉnh trong bảng xổ số
            tmp_location = data_resp.xpath("//table[@id='MN0']/tr/th[{0}]/a/text()".format(i)).extract_first()
            if tmp_location is None:
                continue
            tmp_data[tmp_location] = {}

            for j in range(2, 11):
                # Cột các giải từ giải 8 đến giải đặc biệt
                tmp_giai = data_resp.xpath("//table[@id='MN0']/tr[{0}]/td[1]/text()".format(j)).extract_first()
                # Các số trúng thưởng trong cột theo tỉnh
                tmp_number = data_resp.xpath("//table[@id='MN0']/tr[{0}]/td[{1}]//text()".format(j, i)).extract()
                tmp_data[tmp_location][tmp_giai] = ", ".join(tmp_number)

        xs_item['xs_data'] = tmp_data

        yield xs_item


