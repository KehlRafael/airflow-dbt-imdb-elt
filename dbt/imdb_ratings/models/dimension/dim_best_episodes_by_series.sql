with best_rated as (
    select distinct
        e.parenttconst,
        max(e.averagerating) as max_rating
    from {{ ref('fact_episode_rating') }} e
    group by e.parenttconst
)
select 
    s.tconst as series_code,
    e.tconst as episode_code,
    s.originaltitle as seriesoriginaltitle,
    s.primarytitle as seriestitle,
    e.originaltitle as episodeoriginaltitle,
    e.primarytitle as episodetitle,
    e.seasonnumber,
    e.episodenumber,
    fer.averagerating,
    fer.numvotes
from {{ ref('stg_series') }} s
inner join best_rated br on br.parenttconst = s.tconst
inner join {{ ref('fact_episode_rating') }} fer on fer.parenttconst = s.tconst and fer.averagerating = br.max_rating
inner join {{ ref('stg_series_episode') }} e on e.tconst = fer.tconst
