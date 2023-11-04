# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class WatchItem(scrapy.Item):
    """
    Scrapy item for storing information about watches scraped from a website.

    Attributes:
        image_urls: A field to store a list of image URLs associated with the watch.
        images: A field to store the information of the downloaded watch images (populated by Scrapy's image pipeline).
        metadata: A field to store various metadata and specifications of the watch, such as price and features.
    """
    image_urls = scrapy.Field()
    images = scrapy.Field()
    metadata = scrapy.Field()
