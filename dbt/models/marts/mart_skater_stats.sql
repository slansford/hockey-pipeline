with skaters as (
    select * from {{ ref('stg_skaters') }}
),

final as (
    select
        player_id,
        player_name,
        team,
        position,
        games_played,
        goals,
        assists,
        points,
        plus_minus,
        penalty_minutes,
        power_play_goals,
        power_play_points,
        short_handed_goals,
        shots,
        shooting_pct,
        toi_per_game,

        -- calculated metrics
        round(goals / nullif(games_played, 0), 3)       as goals_per_game,
        round(assists / nullif(games_played, 0), 3)     as assists_per_game,
        round(points / nullif(games_played, 0), 3)      as points_per_game,
        round(shots / nullif(games_played, 0), 3)       as shots_per_game
    from skaters
)

select * from final