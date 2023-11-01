select
    b.tconst,
    e.parenttconst,
    b.primarytitle,
    b.originaltitle,
    e.seasonnumber,
    e.episodenumber
from {{ source('raw_imdb', 'title_basics') }} b
inner join {{ source('raw_imdb', 'title_episode') }} e on e.tconst = b.tconst
where b.titletype = 'tvEpisode'
and b.isadult is false
