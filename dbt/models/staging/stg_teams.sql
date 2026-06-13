with source as (
    select * from {{ source('hockey_raw', 'team') }}
),

renamed as (
    select
        teamFullName                    as team_name,
        gamesPlayed                     as games_played,
        wins,
        losses,
        otLosses                        as ot_losses,
        points,
        COALESCE(pointPct, 0)           as point_pct,
        goalsFor                        as goals_for,
        goalsAgainst                    as goals_against,
        COALESCE(powerPlayPct, 0)       as power_play_pct,
        COALESCE(penaltyKillPct, 0)     as penalty_kill_pct
    from source
)

select * from renamed