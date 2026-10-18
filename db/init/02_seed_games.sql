-- Total playthroughs
SELECT COUNT(*) FROM playthroughs;

-- Most-played generation
SELECT g.name, COUNT(*) AS plays
FROM playthroughs p
JOIN games ga ON ga.id = p.game_id
JOIN generations g ON g.id = ga.generation_id
GROUP BY g.name ORDER BY plays DESC;

-- Most common types across all teams
SELECT t.name, COUNT(*) AS uses
FROM team_members tm
JOIN pokemon_types pt ON pt.pokemon_id = tm.pokemon_id
JOIN types t ON t.id = pt.type_id
GROUP BY t.name ORDER BY uses DESC;

-- Most-used Pokémon
SELECT po.name, COUNT(*) AS uses
FROM team_members tm
JOIN pokemon po ON po.id = tm.pokemon_id
GROUP BY po.name ORDER BY uses DESC LIMIT 10;