with teams as (
    select * from {{ ref('stg_teams') }}
),

final as (
    select
        team_name,
        games_played,
        wins,
        losses,
        ot_losses,
        points,
        point_pct,
        goals_for,
        goals_against,
        power_play_pct,
        penalty_kill_pct,

        -- derived metrics
        goals_for - goals_against                               as goal_differential,
        round(goals_for / nullif(games_played, 0), 2)          as goals_for_per_game,
        round(goals_against / nullif(games_played, 0), 2)      as goals_against_per_game
    from teams
)

select * from final