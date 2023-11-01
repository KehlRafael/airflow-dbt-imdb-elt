select
    tconst,
    primarytitle,
    originaltitle,
    startyear,
    endyear
from {{ source('raw_imdb', 'title_basics') }}
where titletype = 'tvSeries'
and isadult is false
