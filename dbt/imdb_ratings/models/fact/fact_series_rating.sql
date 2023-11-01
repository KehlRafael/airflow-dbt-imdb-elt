select
    s.tconst,
    r.averagerating,
	r.numvotes
from {{ ref('stg_series') }} s
inner join {{ source('raw_imdb', 'title_ratings') }} r on s.tconst = r.tconst
