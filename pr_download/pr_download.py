import requests
import uuid

class PodcastDownloader:

    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db

    # 
    # INTERNET / FILESYSTEM
    #

    def download_file(self, url):
        filename = self.cfg.download_path + '/' + str(uuid.uuid1()) # TODO - get extension
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=(1 * 1024 * 1024)):
                    if chunk:
                        f.write(chunk)
        return filename

    def remove_file(self, filename):
        pass

    #
    # DATABASE
    #

    def reserve_next_file(self):
        pass

    def mark_file_as_downloaded(self, url, filename):
        pass

    def register_error(self, url, exception):
        pass

    def files_to_remove(self):
        pass

    def mark_file_as_removed(self, filename):
        pass
