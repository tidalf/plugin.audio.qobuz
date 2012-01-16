CREATE TABLE "genres" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "name" TEXT NOT NULL,
    "qobuz_id" INTEGER
);
CREATE TABLE "labels" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "name" TEXT NOT NULL
);
CREATE TABLE images (
    "id" INTEGER NOT NULL,
    "url" TEXT NOT NULL,
    "type" TEXT NOT NULL
);
CREATE TABLE "track_urls" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "format_id" INTEGER,
    "streaming_url" TEXT
);
CREATE TABLE albums (id INTEGER PRIMARY KEY, album_id TEXT, title TEXT, release_date INTEGER);
CREATE TABLE tracks (created_on NUMERIC, played_count NUMERIC, last_played_on NUMERIC, updated_on NUMERIC, track_id TEXT, id INTEGER PRIMARY KEY, track_number INTEGER, title TEXT, media_number INTEGER, duration INTEGER, streaming_type TEXT, album_id TEXT);
