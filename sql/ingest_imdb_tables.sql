truncate raw_imdb.title_basics;
copy raw_imdb.title_basics from '/sources/data/title.basics.tsv'
delimiter E'\t'
quote E'\b'
null '\N'
encoding 'UTF8'
csv header;

truncate raw_imdb.title_episode;
copy raw_imdb.title_episode from '/sources/data/title.episode.tsv'
delimiter E'\t'
quote E'\b'
null '\N'
encoding 'UTF8'
csv header;

truncate raw_imdb.title_ratings;
copy raw_imdb.title_ratings from '/sources/data/title.ratings.tsv'
delimiter E'\t'
quote E'\b'
null '\N'
encoding 'UTF8'
csv header;
