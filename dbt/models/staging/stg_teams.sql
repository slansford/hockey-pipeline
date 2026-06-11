with source as (
    select * from {{ source('hockey_raw', 'teams') }}
),

renamed as (
    select
        teamFullName            as team_name,
        gamesPlayed             as games_played,
        wins,
        losses,
        otLosses                as ot_losses,
        points,
        pointPct                as point_pct,
        goalsFor                as goals_for,
        goalsAgainst            as goals_against,
        powerPlayPct            as power_play_pct,
        penaltyKillPct          as penalty_kill_pct
    from source
)

select * from renamed