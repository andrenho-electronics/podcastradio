import logging
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
        logging.info('Downloading file from URL <' + url + '>')
        filename = incomplete_download_filename or str(uuid.uuid1())
        filepath = self.cfg.download_path + '/' + filename
        headers = {}
        if os.path.isfile(filepath):
            headers['Range'] = 'bytes=%d-' % os.path.getsize(filepath)
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            self.update_download_filename(url, filename)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=(1 * 1024 * 1024)):
                    if chunk:
                        f.write(chunk)
        logging.info('File from URL <' + url + '> downloaded as ' + filename)
        return filename

    def remove_file(self, filename):
        try:
            logging.info('File ' + filename + ' removed')
            os.remove(filename)
        except OSError:
            pass

    #
    # DATABASE
    #

    def update_download_filename(self, url, filename):
        self.db.execute('UPDATE downloads SET filename = ? WHERE url = ?', (filename, url))
        self.db.commit()

    def incomplete_download_filename(self, url):
        return self.db.execute('SELECT filename FROM downloads WHERE url = ?', (url,)).fetchone()[0]

    def reserve_next_file(self):
        self.db.execute('BEGIN EXCLUSIVE TRANSACTION')   # locks the database
        url = self.db.execute('SELECT url FROM downloads WHERE thread IS NULL LIMIT 1').fetchone()[0]
        if url:
            self.db.execute('UPDATE downloads SET thread = ? WHERE url = ?', (os.getpid(), url))
            logging.info('URL ' + url + ' reserved for download by process ' + str(os.getpid()))
        self.db.commit()
        return url

    def mark_file_as_downloaded(self, url, filename):
        self.db.execute('''
            UPDATE episodes 
               SET downloaded = 1
                 , last_status = ?
                 , filename = ? 
             WHERE episode_url = ?''', (200, filename, url))
        self.db.execute('DELETE FROM downloads WHERE url = ?', (url,))
        self.db.commit()

    def register_error(self, url, exception, last_status=None):
        logging.warning('Registered error ' + str(exception) + ' (status ' + str(last_status) + ') downloading from URL ' + url)
        self.db.execute('UPDATE episodes SET error = ?, last_status = ? WHERE episode_url = ?', 
                (str(exception), last_status, url))
        self.db.commit()

    def files_to_remove(self):
        return [f[0] for f in self.db.execute('SELECT url FROM to_remove')]

    def mark_file_as_removed(self, filename):
        self.db.execute('''DELETE
                             FROM to_remove
                            WHERE url IN (SELECT episode_url
                                            FROM episodes 
                                           WHERE filename = ?)''', (filename,))
        self.db.execute('''UPDATE episodes
                              SET downloaded = 0
                                , last_status = NULL
                                , filename = NULL
                            WHERE filename = ?''', (filename,))
        self.db.commit()
