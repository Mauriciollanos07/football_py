import pandas as pd
import dash
from dash import dcc, html
from dash import dash_table

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
            "Winner": winner
        }
        list.append(match_dict)
    return list

def get_wc_tab(df, stages, stage_labels):
    df = pd.DataFrame(df)
    # Create a list to store the tabs
    tabs = []

    # Iterate through the stages and create a tab for each one
    for stage_code in stages:
        if stage_code not in stages:
            continue
        # Filter the DataFrame for the current stage
        stage_df = df[df["Stage"] == stage_code]
        if stage_df.empty:
            continue

        stage_component = []
        if stage_code == "GROUP_STAGE":
            page_number = 6
            # Stage_list will contain the list of groups and stage_teams will contain the teams for each group 
            stage_list = []
            stage_teams = []
            stage_df = stage_df.sort_values(["Group", "Date"])
            display_cols = ["Date", "Group", "Home Team", "Home Score", "Away Score", "Away Team"]
            # create stage groups to store all different groups 
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
                    html.Ul(
                        group_elements
                        )
                    ], className="unordered-list", id=f"{g}-wc-group")
                )
        else:
            page_number = 8
            stage_df = stage_df.sort_values("Date")
            display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]
            # store each matchup in a list to display after
            match_elements = []
            for index, row in stage_df.iterrows():
                match_elements.append(
                    html.Span(f"{row['Home Team']} vs. {row['Away Team']}", className="generic-text-2", id=f"{row['Home Team']}-vs-{row['Away Team']}-wc-match")
                    )
            stage_component.append(
                html.Div([
                html.H3("GAMES"),
                html.Div(
                    match_elements, className="spans-container"
                    )
                ], className="flex-spans", id=f"{stage_code}-wc-match")
            )
        # Create a tab for the current stage
        tab = dcc.Tab(
            id=f"{stage_code}_tab_wc",
            label=stage_labels[stage_code],
            children=[
             html.Div(
                stage_component, className="wrapper"
            ),
                dash_table.DataTable(
                    id=f"{stage_code}_table_wc",
                    columns=[{"name": col, "id": col} for col in display_cols],
                    data=stage_df[display_cols].to_dict("records"),
                    style_table={'overflowX': 'auto', 'padding': '1vh', 'max-width': '95vw'},
                    style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': '#2b010e','color': 'white'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#811037', 'color': 'white'},
                    page_size=page_number,
                )
            ],
        style={'backgroundColor': '#2b010e', 'color': 'white'}, selected_style={'backgroundColor': '#f5f0ec', 'color': '#2b010e'})
        tabs.append(tab)

    return tabs

def get_cl_tab(df, stages, stage_labels):
    df = pd.DataFrame(df)
    # Create a list to store the tabs
    tabs = []

    # Iterate through the stages and create a tab for each one
    for stage_code in stages:
        if stage_code not in stages:
            continue
        # Filter the DataFrame for the current stage
        stage_df = df[df["Stage"] == stage_code]
        if stage_df.empty:
            continue
        stage_df = stage_df.sort_values(["Stage", "Date"])
        display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]


        # Create a tab for the current stage
        tab = dcc.Tab(
            id=f"{stage_code}_tab_cl",
            label=stage_labels[stage_code],
            children=[
                dash_table.DataTable(
                    id=f"{stage_code}_table_cl",
                    columns=[{"name": col, "id": col} for col in display_cols],
                    data=stage_df[display_cols].to_dict("records"),
                    style_table={'overflowX': 'auto', 'padding': '1vh', 'max-width': '95vw'},
                    style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': '#01164b','color': 'white'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#08c9f3', 'color': 'white'},
                    page_size=18,
                )
            ],
        style={'backgroundColor': '#01164b', 'color': 'white'}, selected_style={'backgroundColor': '#08c9f3', 'color': '#0d679c'})
        tabs.append(tab)

    return tabs


def get_wc_stage_component(df, stage_code, stage_label):
    df = pd.DataFrame(df)
    # Filter the DataFrame for the current stage
    stage_df = df[df["Stage"] == stage_code]
    if stage_df.empty:
        return None

    stage_component = []
    if stage_code == "GROUP_STAGE":
        page_number = 6
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
        page_number = 8
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

    return dcc.Tab(
        id=f"{stage_code}_tab_wc",
        label=stage_label,
        children=[
            html.Div(stage_component, className="wrapper"),
            dash_table.DataTable(
                id=f"{stage_code}_table_wc",
                columns=[{"name": col, "id": col} for col in display_cols],
                data=stage_df[display_cols].to_dict("records"),
                style_table={'overflowX': 'auto', 'padding': '1vh', 'max-width': '95vw'},
                style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': '#2b010e', 'color': 'white'},
                style_header={'fontWeight': 'bold', 'backgroundColor': '#811037', 'color': 'white'}
            )
        ],
        style={'backgroundColor': '#2b010e', 'color': 'white'}, selected_style={'backgroundColor': '#f5f0ec', 'color': '#2b010e'}
    )


def get_cl_stage_component(df, stage_code, stage_label):
    df = pd.DataFrame(df)
    # Filter the DataFrame for the current stage
    stage_df = df[df["Stage"] == stage_code]
    if stage_df.empty:
        return None

    stage_df = stage_df.sort_values(["Stage", "Date"])
    display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]

    return dcc.Tab(
        id=f"{stage_code}_tab_cl",
        label=stage_label,
        children=[
            dash_table.DataTable(
                id=f"{stage_code}_table_cl",
                columns=[{"name": col, "id": col} for col in display_cols],
                data=stage_df[display_cols].to_dict("records"),
                style_table={'overflowX': 'auto', 'padding': '1vh', 'max-width': '95vw'},
                style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': '#01164b', 'color': 'white'},
                style_header={'fontWeight': 'bold', 'backgroundColor': '#08c9f3', 'color': 'white'}
            )
        ],
        style={'backgroundColor': '#01164b', 'color': 'white'}, selected_style={'backgroundColor': '#08c9f3', 'color': '#0d679c'}
    )