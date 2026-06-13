with goalies as (
    select * from {{ ref('stg_goalies') }}
),

final as (
    select
        player_name,
        team,
        games_played,
        wins,
        losses,
        ot_losses,
        save_pct,
        gaa,
        shutouts,
        shots_against,
        saves,

        -- calculated metrics
        wins + losses + ot_losses                               as total_decisions,
        round(wins / nullif(games_played, 0), 3)               as win_pct,
        round(saves / nullif(shots_against, 0), 4)             as calculated_save_pct
    from goalies
)

select * from final