select
    e.tconst,
    e.parenttconst,
    r.averagerating,
	r.numvotes
from {{ ref('stg_series_episode') }} e
inner join {{ source('raw_imdb', 'title_ratings') }} r on e.tconst = r.tconst
