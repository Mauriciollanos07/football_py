import pandas as pd
import dash
from dash import dcc, html
from dash import dash_table
import math

def get_mathces_list_wc (jason_file):
    list = []
    for match in jason_file:
        date = match['utcDate'][:10]
        stage = match.get('stage')
        group = match.get('group')
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        # if match is from group stage set penalties to false
        if stage == 'GROUP_STAGE' or match['score']['duration'] == 'REGULAR':
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']
            home_penalties_score = False
            away_penalties_score = False
        # If game had penalties, separate game time score (regular time and extra time) from penalties score
        else:
            home_score = match['score']['regularTime']['home'] + match['score']['extraTime']['home']
            away_score = match['score']['regularTime']['away'] + match['score']['extraTime']['away']
            home_penalties_score = match['score']['penalties']['home']
            away_penalties_score = match['score']['penalties']['away']
        winner_flag = match['score'].get('winner')
        winner = ''
        if stage != 'GROUP_STAGE':
            if winner_flag == 'HOME_TEAM':
                winner = home_team
            elif winner_flag == 'AWAY_TEAM':
                winner = away_team
        # Format score depending on penalties shootout
        if home_penalties_score != False:
            home_score = f"{home_score} ({home_penalties_score})"
            away_score = f"{away_score} ({away_penalties_score})"
        match_dict = {
            "Date": date,
            "Stage": stage,
            "Group": group,
            "Home Team": home_team,
            "Away Team": away_team,
            "Home Score": home_score,
            "Away Score": away_score,
            "Winner": winner
        }
        list.append(match_dict)
    return list

def get_mathces_list_cl (jason_file):
    list = []
    for match in jason_file:
        date = match['utcDate'][:10]
        stage = match.get('stage')
        match_day = match.get('matchday')
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        home_score = match['score']['fullTime']['home']
        away_score = match['score']['fullTime']['away']
        winner_flag = match['score'].get('winner')
        winner = ''
        if stage != 'LEAGUE_STAGE':
            if winner_flag == 'HOME_TEAM':
                winner = home_team
            elif winner_flag == 'AWAY_TEAM':
                winner = away_team
        match_dict = {
            "Date": date,
            "Stage": stage,
            "Home Team": home_team,
            "Away Team": away_team,
            "Home Score": home_score,
            "Away Score": away_score,
            "Winner": winner,
            "Match Day": match_day
        }
        list.append(match_dict)
    return list


def get_wc_stage_component(df, stage_code, stage_label):
    df = pd.DataFrame(df)
    # Filter the DataFrame for the current stage
    stage_df = df[df["Stage"] == stage_code]
    if stage_df.empty:
        return html.Div("No data available")

    stage_component = []
    if stage_code == "GROUP_STAGE":
        stage_list = []
        stage_teams = []
        stage_df = stage_df.sort_values(["Group", "Date"])
        display_cols = ["Date", "Group", "Home Team", "Home Score", "Away Score", "Away Team"]
        stage_groups = stage_df.drop_duplicates(subset="Group", keep="first").to_dict("records")
        for m in stage_groups:
            stage_list.append(m["Group"])
        for index, row in stage_df.iterrows():
            if {"team": row["Home Team"], "group": row["Group"]} not in stage_teams:
                stage_teams.append({"team": row["Home Team"], "group": row["Group"]})
            if {"team": row["Away Team"], "group": row["Group"]} not in stage_teams:
                stage_teams.append({"team": row["Away Team"], "group": row["Group"]})
        for g in stage_list:
            group_elements = []
            for t in stage_teams:
                if t["group"] == g:
                    group_elements.append(
                        html.Li(t["team"], className="generic-text", id=f"{t['team']}-wc-group")
                    )
            stage_component.append(
                html.Div([
                    html.H3(g),
                    html.Ul(group_elements)
                ], className="unordered-list", id=f"{g}-wc-group")
            )
    else:
        stage_df = stage_df.sort_values("Date")
        display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]
        match_elements = []
        for index, row in stage_df.iterrows():
            match_elements.append(
                html.Span(f"{row['Home Team']} vs. {row['Away Team']}", className="generic-text-2", id=f"{row['Home Team']}-vs-{row['Away Team']}-wc-match")
            )
        stage_component.append(
            html.Div([
                html.H3("GAMES"),
                html.Div(match_elements, className="spans-container")
            ], className="flex-spans", id=f"{stage_code}-wc-match")
        )

    return html.Div(
        id=f"{stage_code}_tab_wc",
        children=[
            html.Div(stage_component, className="wrapper"),
            html.Table([
                html.Caption(f"{stage_label} Results", className="wc-table-caption"),
                html.Thead(
                    html.Tr([html.Th(col) for col in display_cols], className="wc-table-header")
                ),
                html.Tbody(
                    [html.Tr([html.Td(row[col]) for col in display_cols], className="wc-tr") for index, row in stage_df.iterrows()],
                    className="wc-table-body")], className="wc-table"
            )
        ],
        style={'backgroundColor': '#2b010e', 'color': 'white', 'justifyContent': 'center', 'alignItems': 'center'}
    )


def get_cl_stage_component(df, stage_code, stage_label):
    df = pd.DataFrame(df)
    # Filter the DataFrame for the current stage
    stage_df = df[df["Stage"] == stage_code]
    if stage_df.empty:
        return html.Div("No data available")

    stage_df = stage_df.sort_values(["Stage", "Date"])
    display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]

    if stage_code == "LEAGUE_STAGE":
        league_stage_days = stage_df.drop_duplicates(subset="Match Day", keep="first").to_dict("records")
        match_day_list = [m['Match Day'] for m in league_stage_days]
        match_day_tables = []
        for m in match_day_list:
            new_df = stage_df[stage_df["Match Day"] == m]
            match_day_tables.append(
                html.Table([
                    html.Caption(f"{stage_label} Results", className="cl-table-caption"),
                    html.Thead(
                        html.Tr([html.Th(col) for col in display_cols], className="cl-table-header")
                    ),
                    html.Tbody(
                        [html.Tr([html.Td(row[col]) for col in display_cols], className="cl-tr") for index, row in new_df.iterrows()],
                        className="cl-table-body")], className="cl-table", style={'color': 'white', 'justifyContent': 'center', 'alignItems': 'center'}
                ))
        select_match_day = dcc.Tabs(children=[dcc.Tab(id=f"match-day-{m}",
                            label=f"Match Day {m}",
                            children=match_day_tables[i],
                            value=f'{m}',
                            style={'backgroundColor': '#01164b', 'color': 'white', 'justifyContent': 'center', 'alignItems': 'center'}) for i, m in enumerate(match_day_list)
                            ])
        return html.Div(
        id=f"{stage_code}_tab_cl",
        children=select_match_day)
    
    stage_teams = stage_df.drop_duplicates(subset="Home Team", keep="first").to_dict("records")
    stage_teams_list = [[m['Home Team'], m['Away Team']] for m in stage_teams]
    print(stage_teams_list)
    matchups_dict = {}
    for m in stage_teams_list:
        if m[0] == None or m[1] == None:
            continue
        sorted_key = sorted(m)
        if f"{sorted_key[0]} vs {sorted_key[1]}" in matchups_dict:
            matchups_dict[f"{sorted_key[0]} vs {sorted_key[1]}"].append(m)
        else:
            matchups_dict.update({f"{sorted_key[0]} vs {sorted_key[1]}": [m]})
    print(matchups_dict)
    stage_component = []
    for key, value in matchups_dict.items():
        print(f"{key} : {value}")
        div_elements = []
        for v in value:
            # Filter the DataFrame for the specific matchup
            matchup_df = stage_df[(stage_df["Home Team"] == v[0]) & (stage_df["Away Team"] == v[1])]
            if matchup_df.empty:
                continue
            for index, row in matchup_df.iterrows():
                if math.isnan(row["Home Score"])  and math.isnan(row["Away Score"]):
                    div_elements.append(
                        html.Div(
                        f"{row['Home Team']} vs. {row['Away Team']}",
                        className="generic-text-2",
                        id=f"{row['Home Team']}-vs-{row['Away Team']}-cl-match"
                        )
                    )
                else:
                    div_elements.append(
                        html.Div(
                        f"{row['Home Team']} {int(row['Home Score'])} - {int(row['Away Score'])} {row['Away Team']}",
                        className="generic-text-2",
                        id=f"{row['Home Team']}-vs-{row['Away Team']}-cl-match"
                        )
                    )
        stage_component.append(
            html.Div(
            children=[
                html.H2(key, className="matchup-header"),
                html.Div(div_elements, className="matchup-results")
            ],
            className="matchup-container",
            id=f"{key.replace(' ', '-')}-cl-matchup"
            )
        )

    return html.Div(
        id=f"{stage_code}_tab_cl",
        children=stage_component,
        className="wrapper",
        style={'backgroundColor': '#01164b', 'color': 'white', 'justifyContent': 'center', 'alignItems': 'center'})
