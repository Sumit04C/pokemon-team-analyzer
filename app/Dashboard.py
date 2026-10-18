import plotly.express as px
import streamlit as st
from db import query

st.set_page_config(page_title="PokéDash", layout="wide")
st.title("PokéDash")

total = query("SELECT COUNT(*) AS n FROM playthroughs").iloc[0, 0]

gens = query("""
    SELECT g.name, COUNT(*) AS plays
    FROM playthroughs p
    JOIN games ga ON ga.id = p.game_id
    JOIN generations g ON g.id = ga.generation_id
    GROUP BY g.name ORDER BY plays DESC
""")

types = query("""
    SELECT t.name, COUNT(*) AS uses
    FROM team_members tm
    JOIN pokemon_types pt ON pt.pokemon_id = tm.pokemon_id
    JOIN types t ON t.id = pt.type_id
    GROUP BY t.name ORDER BY uses DESC
""")

top_mons = query("""
    SELECT po.name, COUNT(*) AS uses
    FROM team_members tm
    JOIN pokemon po ON po.id = tm.pokemon_id
    GROUP BY po.name ORDER BY uses DESC LIMIT 10
""")

c1, c2, c3 = st.columns(3)
c1.metric("Playthroughs", total)
c2.metric("Most played gen", gens.iloc[0]["name"] if not gens.empty else "—")
c3.metric("Most used Pokémon", top_mons.iloc[0]["name"] if not top_mons.empty else "—")

left, right = st.columns(2)
left.plotly_chart(px.bar(gens, x="name", y="plays", title="Playthroughs by generation"),
                  use_container_width=True)
right.plotly_chart(px.bar(types, x="name", y="uses", title="Most common types"),
                   use_container_width=True)
st.plotly_chart(px.bar(top_mons, x="uses", y="name", orientation="h",
                       title="Top 10 Pokémon"), use_container_width=True)
