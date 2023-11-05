from typing import Iterable
import scrapy
from .. import items
import re


class ChronextSpider(scrapy.Spider):
    """
    Scrapy spider for crawling and scraping watches information from the Chronext website.
    """

    name = "chronext"

    # Trim to keep only digits in a text. Usefull to parse price.
    trim = re.compile(r"[^\d.,]+")  

    # Attributes to preload every pages of the products pagination
    watches_per_page = 24
    n_pages = 264
    url = "https://www.chronext.fr/acheter?s%5Bef5bfee0-c7d4-470e-82e2-39d397cb3750%5D%5Boffset%5D={}"

    # Settings to control parsing
    desired_img_width = 1000
    specs_to_ignore = ["expédition", "emballage", "documents"]  # Unnecessary specs that don't need to be saved

    def start_requests(self) -> Iterable[scrapy.Request]:
        """
        Generate initial requests to begin the scraping process.

        Returns:
            Iterable[scrapy.Request]: An iterable of Scrapy Request objects to start the scraping process.
        """
        for i in range(self.n_pages + 1):
            yield scrapy.Request(self.url.format(i * self.watches_per_page))

    def parse(self, response: scrapy.http.Response):
        """
        Parse the current products page and follow links to watches specification pages.

        Args:
            response: The response object representing the current products page.

        Yields:
            scrapy.Request: Requests to follow watches specification pages.
        """
        watch_page_links = response.css("div.product-list a:first-of-type")
        yield from response.follow_all(watch_page_links, self.parse_watch_page)

    def parse_watch_page(self, response: scrapy.http.Response):
        """
        Parse a watch specification page, extracting image URLs and watch specifications.

        Args:
            response: The response object representing a watch specification page.

        Yields:
            items.WatchItem: Watch information with image URLs and metadata.
        """

        # Parse images urls and adapt them to get desired resolution
        image_urls = [
            img.attrib["src"].replace("w=570", f"w={self.desired_img_width}")
            for img in response.css("div.product-stage__image-wrapper img")
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
                # Ignore unwanted specs
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

        # Parse price by keeping only digits
        price_str = response.css("div.price::text").get()
        metadata["price"] = float(self.trim.sub("", price_str))

        yield items.WatchItem(image_urls=image_urls, metadata=metadata)
