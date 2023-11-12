import pymongo
from datasets import Dataset, Image
from os import path


class WatchesDataset:
    def __init__(self, mongo_uri, mongo_port, mongo_db, mongo_collection, image_dir) -> None:
        self.client = pymongo.MongoClient(mongo_uri, mongo_port)
        self.db = self.client[mongo_db]
        self.collection = self.db[mongo_collection]
        self.image_dir = image_dir
        self.ds = Dataset.from_dict(self.load()).cast_column("image", Image())
        self.client.close()

    def load(self):
        images = []
        texts = []

        fields_to_ignore = ["_id", "image_urls", "image_paths", "thumb_paths", "sku"]
        for watch in self.collection.find({}):
            for img in watch["image_paths"]:
                images.append(path.join(self.image_dir, img))
                texts.append(
                    ",".join([f"{key}:{value}" for key, value in watch.items() if key not in fields_to_ignore])
                )
        return {"image": images, "text": texts}

    def save(self, path):
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
