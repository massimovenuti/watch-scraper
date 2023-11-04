import scrapy
from .. import items
import re


class ChronextSpider(scrapy.Spider):
    """
    Scrapy spider for crawling and scraping watch product information from the Chronext website.
    """

    name = "chronext"
    start_urls = ["https://www.chronext.fr/acheter"]
    specs_to_ignore = ["expédition", "emballage", "documents"]  # Unnecessary specs that don't need to be saved
    number_trim = re.compile(r"[^\d.,]+")  # Trim to keep only numbers in a text. Usefull to parse price.

    def parse(self, response: scrapy.http.Response):
        """
        Parse the main page and follow links to watch product pages and pagination.

        Args:
            response: The response object representing the main page.

        Yields:
            scrapy.Request: Requests to follow watch product pages and pagination.
        """
        # Parse every watches product page from the current page
        watch_page_links = response.css("div.product-list a")
        yield from response.follow_all(watch_page_links, self.parse_watch_page)

        # Parse next pages from the pagination
        pagination_links = response.css("li.pagination__item--next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_watch_page(self, response: scrapy.http.Response):
        """
        Parse a watch product page, extracting image URLs and watch specifications.

        Args:
            response: The response object representing a watch product page.

        Yields:
            items.WatchItem: Watch product information with image URLs and metadata.
        """

        # Parse images urls and adapt urls to get desired resolution
        image_urls = [
            img.attrib["src"].replace("w=570", "w=1000") for img in response.css("div.product-stage__image-wrapper img")
        ]

        metadata = {}

        # Parse watch specifications
        for specification_wrapper in response.css("div.specification__wrapper"):
            # Watch specs are displayed with the format title / value
            specification_title = (
                specification_wrapper.css("div.specification__title *::text").get(default="").strip().lower()
            )
            specification_value = (
                specification_wrapper.css("div.specification__value *::text").get(default="").strip().lower()
            )

            if specification_title in self.specs_to_ignore:
                # Ignore unnecessary specs
                continue
            elif specification_title == "":
                # Watch functions case (e.g. luminous hands, chronograph)
                # They are not displayed with a title, we gather them within the field 'fonctions'
                if metadata.get("fonctions", None) is None:
                    metadata["fonctions"] = [specification_value]
                else:
                    metadata["fonctions"].append(specification_value)
            else:
                metadata[specification_title] = specification_value

        # Parse price
        price_str = response.css("div.price::text").get()
        # Keep only numbers
        metadata["price"] = float(self.number_trim.sub("", price_str))

        yield items.WatchItem(image_urls=image_urls, metadata=metadata)
