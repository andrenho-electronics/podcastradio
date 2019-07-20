CREATE TABLE IF NOT EXISTS podcasts (
  url           TEXT PRIMARY KEY,
  title         TEXT,
  image_path    TEXT,
  keep_episodes INTEGER   DEFAULT 5,
  last_status   INTEGER,
  error         TEXT
);

CREATE TABLE IF NOT EXISTS episodes (
  podcast_url   TEXT,
  episode_url   TEXT,
  title         TEXT,
  date          INTEGER,
  length        TEXT,
  filename      TEXT      DEFAULT NULL,
  nbytes        INTEGER   DEFAULT NULL,
  downloaded    BOOLEAN   DEFAULT 0,
  keep          BOOLEAN   DEFAULT 0,
  last_status   INTEGER   DEFAULT NULL,
  error         TEXT      DEFAULT NULL,
  PRIMARY KEY(podcast_url, episode_url),
  FOREIGN KEY(podcast_url) REFERENCES podcasts(url)
);

CREATE TABLE IF NOT EXISTS downloads (
  url             TEXT     PRIMARY KEY,
  episode_rowid   INTEGER  UNIQUE,
  podcast_title   TEXT,
  episode_title   TEXT,
  thread          INTEGER  DEFAULT NULL,
  episode_size    INTEGER  DEFAULT NULL,
  bytes_downd     INTEGER  DEFAULT 0,
  filename        TEXT     DEFAULT NULL,
  FOREIGN KEY(url) REFERENCES episodes(episode_url)
);

CREATE TABLE IF NOT EXISTS to_remove (
  url             TEXT    PRIMARY KEY,
  FOREIGN KEY(url) REFERENCES episodes(episode_url)
);

CREATE TABLE IF NOT EXISTS player (
  filename        TEXT    PRIMARY_KEY,
  time            TEXT    DEFAULT "0:00",
  playing         BOOLEAN DEFAULT false
);
