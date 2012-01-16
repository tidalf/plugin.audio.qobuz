--     Copyright 2011 Joachim Basmaison, Cyril Leclerc
--
--     This file is part of xbmc-qobuz.
--
--     xbmc-qobuz is free software: you can redistribute it and/or modify
--     it under the terms of the GNU General Public License as published by
--     the Free Software Foundation, either version 3 of the License, or
--     (at your option) any later version.
--
--     xbmc-qobuz is distributed in the hope that it will be useful,
--     but WITHOUT ANY WARRANTY; without even the implied warranty of
--     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
--     GNU General Public License for more details.
--
--     You should have received a copy of the GNU General Public License
--     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.

--
-- GENRES
--
CREATE TABLE "genres" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "name" TEXT NOT NULL,
    "qobuz_id" INTEGER
);

--
-- LABELS
--
CREATE TABLE "labels" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "name" TEXT NOT NULL
);

--
-- IMAGES
--
CREATE TABLE images (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "url" TEXT NOT NULL,
    "type" TEXT NOT NULL
);

--
-- TRACK URLS
--
CREATE TABLE "track_urls" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "format_id" INTEGER,
    "streaming_url" TEXT
);

--
-- ALBUMS
--
CREATE TABLE albums (
    "id" INTEGER PRIMARY KEY NOT NULL, 
    "album_id" TEXT NOT NULL, 
    "title TEXT", 
    "release_date" INTEGER
);

--
-- TRACKS
--
CREATE TABLE tracks (
    "id" INTEGER PRIMARY KEY NO NULL, 
    "album_id" TEXT NOT NULL
    "created_on" NUMERIC, 
    "played_count" NUMERIC, 
    "last_played_on" NUMERIC, 
    "updated_on" NUMERIC, 
    "track_id" TEXT, 
    "track_number" INTEGER, 
    "title" TEXT, 
    "media_number" INTEGER, 
    "duration" INTEGER, 
    "streaming_type" TEXT, 
);
