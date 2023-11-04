import scrapy
from .. import items


class ChronextSpider(scrapy.Spider):
    name = "chronext"
    start_urls = ["https://www.chronext.fr/acheter"]

    def parse(self, response):
        watch_page_links = response.css("div.product-list a")
        yield from response.follow_all(watch_page_links, self.parse_watch)

        pagination_links = response.css("li.pagination__item--next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_watch(self, response):
        # Parse images urls
        # Adapt urls to get desired resolution
        image_urls = [
            img.attrib["src"].replace("w=570", "w=1000") for img in response.css("div.product-stage__image-wrapper img")
        ]

        metadata = {}
        # Parse specifications
        for specification_wrapper in response.css("div.specification__wrapper"):
            specification_title = (
                specification_wrapper.css("div.specification__title *::text").get(default="").strip().lower()
            )
            specification_value = (
                specification_wrapper.css("div.specification__value *::text").get(default="").strip().lower()
            )

            if specification_title != "":
                metadata[specification_title] = specification_value
            else:
                if metadata.get("fonctions", None) is None:
                    metadata["fonctions"] = [specification_value]
                else:
                    metadata["fonctions"].append(specification_value)

        yield items.WatchItem(
            image_urls=image_urls,
            metadata=metadata
        )
