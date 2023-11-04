# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScraperPipeline:
    def process_item(self, item, spider):
        # Modify image url with desired resolution
        

        # image can be accessed in item["image"]
        # metadata can be accessed in item["metadata"]
        return item
