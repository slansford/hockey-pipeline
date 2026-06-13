with source as (
    select * from {{ source('hockey_raw', 'goalie') }}
),

renamed as (
    select
        goalieFullName                      as player_name,
        teamAbbrevs                         as team,
        gamesPlayed                         as games_played,
        wins,
        losses,
        otLosses                            as ot_losses,
        COALESCE(savePct, 0)                as save_pct,
        COALESCE(goalsAgainstAverage, 0)    as gaa,
        shutouts,
        shotsAgainst                        as shots_against,
        saves
    from source
)

select * from renamed