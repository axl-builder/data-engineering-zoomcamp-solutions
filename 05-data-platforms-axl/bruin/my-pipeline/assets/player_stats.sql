/* @bruin

name: reports.player_stats
type: bq.sql
materialization:
  type: table
   
depends:
   - ingestion.players

@bruin */

SELECT 
    name, 
    count(*) AS player_count
FROM `de-bruin-488403.ingestion.players` -- Usamos backticks para BQ
GROUP BY 1