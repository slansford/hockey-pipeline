with source as (
    select * from {{ source('hockey_raw', 'goalies') }}
),

renamed as (
    select
        goalieFullName          as player_name,
        teamAbbrevs             as team,
        gamesPlayed             as games_played,
        wins,
        losses,
        otLosses                as ot_losses,
        savePct          as save_pct,
        goalsAgainstAverage     as gaa,
        shutouts,
        shotsAgainst            as shots_against,
        saves
    from source
)

select * from renamed