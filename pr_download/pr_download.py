class PodcastDownloader:

    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db

    # 
    # INTERNET / FILESYSTEM
    #

    def download_file(self, url):
        pass

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
