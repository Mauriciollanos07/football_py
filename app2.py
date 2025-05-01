import requests
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash import dash_table

# API and token
API_URL_MATCHES = 'https://api.football-data.org/v4/competitions/WC/matches'
API_TOKEN = '02c8648f03b64960af5df010463cc253'
headers = {'X-Auth-Token': API_TOKEN}

# Fetch 2022 World Cup match data
resp = requests.get(API_URL_MATCHES, headers=headers)
data = resp.json()
matches = data.get('matches', [])

# Prepare the data
match_list = []
for match in matches:
    date = match['utcDate'][:10]
    stage = match.get('stage')
    group = match.get('group')
    home_team = match['homeTeam']['name']
    away_team = match['awayTeam']['name']
    home_score = match['score']['fullTime']['home']
    away_score = match['score']['fullTime']['away']
    winner_flag = match['score'].get('winner')
    winner = ''
    if stage != 'GROUP_STAGE':
        if winner_flag == 'HOME_TEAM':
            winner = home_team
        elif winner_flag == 'AWAY_TEAM':
            winner = away_team
    match_list.append({
        "Date": date,
        "Stage": stage,
        "Group": group,
        "Home Team": home_team,
        "Away Team": away_team,
        "Home Score": home_score,
        "Away Score": away_score,
        "Winner": winner
    })

df = pd.DataFrame(match_list)

# Define stage order and labels
stage_order = ["GROUP_STAGE", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "THIRD_PLACE", "FINAL"]
stage_labels = {
    "GROUP_STAGE": "Group Stage",
    "LAST_16": "Round of 16",
    "QUARTER_FINALS": "Quarterfinals",
    "SEMI_FINALS": "Semifinals",
    "THIRD_PLACE": "Third Place",
    "FINAL": "Final"
}

# Initialize app
app = dash.Dash(__name__)
app.title = "World Cup 2022 Dashboard"

tabs = []
for stage_code in stage_order:
    stage_df = df[df["Stage"] == stage_code]
    if stage_df.empty:
        continue

    # Sort and select columns
    if stage_code == "GROUP_STAGE":
        stage_df = stage_df.sort_values(["Group", "Date"])
        display_cols = ["Date", "Group", "Home Team", "Away Team", "Home Score", "Away Score"]
    else:
        stage_df = stage_df.sort_values("Date")
        display_cols = ["Date", "Home Team", "Away Team", "Home Score", "Away Score", "Winner"]

    # Table
    table = dash_table.DataTable(
        data=stage_df[display_cols].to_dict('records'),
        columns=[{"name": col, "id": col} for col in display_cols],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f2f2f2'},
        page_size=4
    )

    # Chart
    stage_df["Total Goals"] = stage_df["Home Score"] + stage_df["Away Score"]
    if stage_code == "GROUP_STAGE":
        goals_summary = stage_df.groupby("Group", as_index=False)["Total Goals"].sum()
        fig = px.bar(goals_summary, x="Group", y="Total Goals", title="Total Goals by Group")
    else:
        stage_df["Match"] = stage_df["Home Team"] + " vs " + stage_df["Away Team"]
        fig = px.bar(stage_df, x="Match", y="Total Goals",
                     title=f"Goals per Match - {stage_labels[stage_code]}")
        fig.update_xaxes(title="Match")

    # Tab
    tabs.append(
        dcc.Tab(label=stage_labels[stage_code], children=[
            html.Br(),
            table,
            html.Br(),
            dcc.Graph(figure=fig)
        ])
    )

# App layout
app.layout = html.Div([
    html.H1("FIFA World Cup 2022 Dashboard"),
    dcc.Tabs(tabs)
])

# Run
if __name__ == '__main__':
    app.run_server(debug=True)