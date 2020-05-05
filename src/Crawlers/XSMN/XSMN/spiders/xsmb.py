import scrapy
import calendar
import datetime

from scrapy.spiders import CrawlSpider
from ..items import XsmnItem


class SxmbSpider(CrawlSpider):
    name = 'xsmb'
    allowed_domains = ['xskt.com.vn']

    start_urls = []
    now = datetime.datetime.now()
    if now.hour < 19:
        now -= datetime.timedelta(days=1)
    start_urls.append('http://xskt.com.vn/ket-qua-xo-so-theo-ngay/mien-bac-xsmb/'
                      '{0}-{1}-{2}.html'.format(now.day, now.month, now.year))

    def parse(self, response):
        xs_item = XsmnItem()
        tmp_data = {}
        data_resp = scrapy.Selector(response)

        xs_item['xs_info'] = [
            # Thứ
            data_resp.xpath("//table[@id='MB0']/tr/th[1]/h3/a[2]/text()").extract_first(),
            # Ngày tháng
            data_resp.xpath("//title/text()").extract_first()[44:],
            self.now.year
        ]

        # Các tỉnh trong bảng xổ số
        tmp_location = 'Miền Bắc'
        tmp_data[tmp_location] = {}

        for j in range(11, 1, -1):
            if j == 9 or j == 6:
                continue
            # Cột các giải từ giải 8 đến giải đặc biệt
            tmp_giai = data_resp.xpath("//table[@id='MB0']/tr[{0}]/td[1]/text()".format(j)).extract_first()
            # Các số trúng thưởng trong cột theo tỉnh
            tmp_number = data_resp.xpath("//table[@id='MB0']/tr[{0}]/td[2]//text()".format(j)).extract()

            tmp_data[tmp_location][tmp_giai] = ", ".join(tmp_number)

        xs_item['xs_data'] = tmp_data

        yield xs_item
