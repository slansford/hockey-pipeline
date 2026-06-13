with source as (
    select * from {{ source('hockey_raw', 'skater') }}
),

renamed as (
    select
        playerId                        as player_id,
        skaterFullName                  as player_name,
        teamAbbrevs                     as team,
        positionCode                    as position,
        gamesPlayed                     as games_played,
        goals,
        assists,
        points,
        plusMinus                       as plus_minus,
        penaltyMinutes                  as penalty_minutes,
        ppGoals                         as power_play_goals,
        ppPoints                        as power_play_points,
        shGoals                         as short_handed_goals,
        shots,
        COALESCE(shootingPct, 0)        as shooting_pct,
        COALESCE(timeOnIcePerGame, 0)   as toi_per_game
    from source
)

select * from renamed