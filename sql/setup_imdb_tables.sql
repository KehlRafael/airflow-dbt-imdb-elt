create schema if not exists raw_imdb;

create table if not exists raw_imdb.title_basics (
    tconst varchar(50),
    titleType varchar(50),
    primaryTitle text,
    originalTitle text,
    isAdult boolean,
    startYear integer,
    endYear integer,
    runtimeMinutes integer,
    genres text
);

create table if not exists raw_imdb.title_episode (
    tconst varchar(50),
    parentTconst varchar(50),
    seasonNumber integer,
    episodeNumber integer
);

create table if not exists raw_imdb.title_ratings (
    tconst varchar(50),
    averageRating numeric,
    numVotes  integer
);
