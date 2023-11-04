import scrapy


class ChronextSpider(scrapy.Spider):
    name = "chronext"
    start_urls = ["https://www.chronext.fr/acheter"]

    def parse(self, response):
        watch_page_links = response.css("div.product-list a")
        yield from response.follow_all(watch_page_links, self.parse_watch)

        pagination_links = response.css("li.pagination__item--next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_watch(self, response):
        item = {}

        # Get images urls, modified with desired resolution
        item["images_urls"] = [
            img.attrib["src"].replace("w=570", "w=1000") for img in response.css("div.product-stage__image-wrapper img")
        ]

        # Get specifications
        for specification_wrapper in response.css("div.specification__wrapper"):
            specification_title = specification_wrapper.css("div.specification__title *::text").get(default="").strip()
            specification_value = specification_wrapper.css("div.specification__value *::text").get(default="").strip()

            if specification_title != "":
                item[specification_title] = specification_value
            else:
                if item.get("Fonctions", None) is None:
                    item["Fonctions"] = [specification_value]
                else:
                    item["Fonctions"].append(specification_value)

        yield item
