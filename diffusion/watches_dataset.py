"""
This module defines a WatchesDataset class that loads data from a MongoDB collection,
prepares it for use with the Hugging Face 'datasets' library, and saves the resulting dataset to disk.
"""

import pymongo
from datasets import Dataset, Image
from os import path


class WatchesDataset:
    def __init__(
        self,
        mongo_uri: str,
        mongo_port: int,
        mongo_db: str,
        mongo_collection: str,
        image_dir: str,
    ) -> None:
        """
        Initialize the WatchesDataset object.

        Parameters:
        - mongo_uri: MongoDB URI.
        - mongo_port: MongoDB port.
        - mongo_db: MongoDB database name.
        - mongo_collection: MongoDB collection name.
        - image_dir: Directory path containing images.
        """
        self.client = pymongo.MongoClient(mongo_uri, mongo_port)
        self.db = self.client[mongo_db]
        self.collection = self.db[mongo_collection]
        self.image_dir = image_dir
        self.ds = Dataset.from_dict(self.load()).cast_column("image", Image())
        self.client.close()

    def load(self) -> dict:
        """
        Load data from MongoDB collection and prepare it for the dataset.

        Returns:
            Dictionary containing "image" and "text" fields.
        """
        images = []
        texts = []

        # Fields to ignore during dataset creation
        fields_to_ignore = ["_id", "image_urls", "image_paths", "thumb_paths", "sku"]

        for watch in self.collection.find({}):
            for img in watch["image_paths"]:
                images.append(path.join(self.image_dir, img))
                # Create text description for the watch
                texts.append(
                    ",".join(
                        [
                            f"{key}:{value}"
                            for key, value in watch.items()
                            if key not in fields_to_ignore
                        ]
                    )
                )
        return {"image": images, "text": texts}

    def save(self, path: str) -> None:
        """
        Save the dataset to disk.

        Parameters:
            path: Path to save the dataset.
        """
        self.ds.save_to_disk(path)


if __name__ == "__main__":
    d = WatchesDataset(
        mongo_uri="localhost",
        mongo_port=27017,
        mongo_db="watch_scraping",
        mongo_collection="watches",
        image_dir="images",
    )
    d.save("datasets/watches_dataset")
