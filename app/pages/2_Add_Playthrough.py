import streamlit as st
from sqlalchemy import text
from db import get_engine, query

st.title("Add a playthrough")

games = query("SELECT id, name FROM games ORDER BY id")
mons = query("SELECT id, name FROM pokemon ORDER BY id")
mon_names = dict(zip(mons["name"], mons["id"]))

with st.form("playthrough"):
    player = st.text_input("Player name")
    game = st.selectbox("Game", games["name"])
    team = [st.selectbox(f"Slot {i}", mon_names.keys(), key=f"slot{i}")
            for i in range(1, 7)]
    submitted = st.form_submit_button("Save")

if submitted:
    game_id = int(games.loc[games["name"] == game, "id"].iloc[0])
    with get_engine().begin() as conn:   # one transaction: all or nothing
        pid = conn.execute(
            text("INSERT INTO playthroughs (player_name, game_id) "
                 "VALUES (:p, :g) RETURNING id"),
            {"p": player, "g": game_id},
        ).scalar_one()
        for slot, name in enumerate(team, start=1):
            conn.execute(
                text("INSERT INTO team_members (playthrough_id, slot, pokemon_id) "
                     "VALUES (:pid, :s, :m)"),
                {"pid": pid, "s": slot, "m": int(mon_names[name])},
            )
    st.cache_data.clear()
    st.success("Saved!")
