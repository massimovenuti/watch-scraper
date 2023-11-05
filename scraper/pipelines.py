from itemadapter import ItemAdapter
import scrapy
import pymongo


class ScraperPipeline:
    """
    Scrapy item pipeline for processing and storing scraped watch data in a MongoDB database.

    Attributes:
        collection_name: The name of the MongoDB collection where watch data will be stored.
        mongo_uri: The MongoDB server URI.
        mongo_port: The MongoDB server port.
        mongo_db: The name of the MongoDB database where data will be stored.
    """

    collection_name = "watches"

    def __init__(self, mongo_uri: str, mongo_port: int, mongo_db: str):
        """
        Initialize the pipeline with MongoDB connection information.

        Args:
            mongo_uri: The MongoDB server URI.
            mongo_port: The MongoDB server port.
            mongo_db: The name of the MongoDB database where data will be stored.
        """
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler):
        """
        Create a pipeline instance with settings from the Scrapy crawler.

        If not set in the settings, the default values for the MongoDB server port and the MongoDB database are
        respectively 27017 and 'items'.

        Args:
            crawler: The Scrapy crawler instance.

        Returns:
            ScraperPipeline: An instance of the pipeline with MongoDB connection settings.
        """
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_port=crawler.settings.get("MONGO_PORT", 27017),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider: scrapy.Spider):
        """
        Initialize the MongoDB client and database connection when the spider starts.

        Args:
            spider: The Scrapy spider instance.
        """
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider: scrapy.Spider):
        """
        Close the MongoDB client connection when the spider is finished.

        Args:
            spider: The Scrapy spider instance.
        """
        self.client.close()

    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        """
        Process and store the scraped item in the MongoDB database.

        Args:
            item: The item to be processed and stored.
            spider: The Scrapy spider instance.

        Returns:
            scrapy.Item: The processed item.

        The item is processed in order to include image paths and metadata to be inserted into the MongoDB collection.

        Example:
            Original item:
            {
                'image_urls': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
                'images': [
                    {'url': https://example.com/image1.jpg, 'path': 'full/path/to/image1.jpg', 'checksum': 'a1b2c3', 'status': 'downloaded'},
                    {'url': https://example.com/image2.jpg, 'path': 'full/path/to/image2.jpg', 'checksum': 'x4y5z6', 'status': 'downloaded'}
                ],
                'metadata': {'price': 1000, 'brand': 'Example Watch', 'model': '12345'}
            }

            Processed item:
            {
                'image_urls': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
                'image_paths': ['full/path/to/image1.jpg', 'full/path/to/image2.jpg'],
                'price': 1000,
                'brand': 'Example Watch',
                'model': '12345'
            }
        """
        # Reformat the item data to include image paths and metadata
        item = {
            "image_urls": item["image_urls"],
            "image_paths": [img["path"] for img in item["images"]],
            "thumb_paths": [img["path"].replace("full", "thumbs/small") for img in item["images"]],
            **item["metadata"],
        }

        # Insert the item into the MongoDB collection if it doesn't already exist
        if not self.db[self.collection_name].find_one({"image_paths": {"$in": item["image_paths"]}}):
            self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())

        return item
