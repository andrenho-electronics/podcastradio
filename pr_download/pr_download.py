import os
import requests
import uuid

class PodcastDownloader:

    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db

    # 
    # INTERNET / FILESYSTEM
    #

    def download_file(self, url, incomplete_download_filename=None):
        filename = incomplete_download_filename or str(uuid.uuid1())
        filepath = self.cfg.download_path + '/' + filename
        headers = {}
        if os.path.isfile(filepath):
            headers['Range'] = 'bytes=%d-' % os.path.getsize(filepath)
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=(1 * 1024 * 1024)):
                    if chunk:
                        f.write(chunk)
        return filename

    def remove_file(self, filename):
        pass

    #
    # DATABASE
    #

    def incomplete_download_filename(self, url):
        pass

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
