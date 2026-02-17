import pandas as pd
import dash
from dash import dcc, html
import math

WC_MAIN_BG_COLOR = 'black'
WC_MAIN_COLOR = 'whitesmoke'

CL_MAIN_BG_COLOR = '#01164b'
CL_MAIN_COLOR = '#f5f0ec'

def get_mathces_list_wc (jason_file):
    """ This function takes the JSON response from the API and returns a list of dictionaries with the relevant match information for the World Cup. 
    It handles both group stage matches and knockout stage matches, including those that went to penalties. 
        args:
            jason_file (list): A list of dictionaries containing match data from the API response.
        returns:
            list: A list of dictionaries with the following keys: "Date", "Stage", "Group", "Home Team", "Away Team", "Home Score", "Away Score", "Winner". The "Group" key will be None for knockout stage matches. 
            The "Winner" key will be an empty string for group stage matches and will contain the name of the winning team for knockout stage matches. 
            The "Home Score" and "Away Score" keys will contain the regular time score for group stage matches and the combined regular time and extra time score for knockout stage matches. 
            If a match went to penalties, the "Home Score" and "Away Score" keys will also include the penalties score in parentheses. If there is an error processing the data, the function will return an empty list.
    """
    try:
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
    except Exception:
        return []

def get_mathces_list_cl (jason_file):
    """ This function takes the JSON response from the API and returns a list of dictionaries with the relevant match information for the Champions League. 
    It handles both league stage matches and knockout stage matches. 
        args:
            jason_file (list): A list of dictionaries containing match data from the API response.
        returns:
            list: A list of dictionaries with the following keys: "Date", "Stage", "Home Team", "Away Team", "Home Score", "Away Score", "Winner", "Match Day". 
            The "Winner" key will contain the name of the winning team for knockout stage matches and will be an empty string for league stage matches. 
            The "Home Score" and "Away Score" keys will contain the regular time score for league stage matches and the combined regular time and extra time score for knockout stage matches. 
            If there is an error processing the data, the function will return an empty list."""
    try:
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
    except Exception:
        return []


def get_wc_stage_component(df, stage_code, stage_label):
    """ This function takes a DataFrame containing World Cup match data, a stage code, and a stage label, and returns a Dash HTML component that displays the matches for that stage. 
    The function filters the DataFrame for the specified stage and creates a component that displays the matches in a table format. 
    For the group stage, it also groups the teams by their respective groups and displays them in separate sections. 
    If there is an error processing the data, the function returns a simple HTML div with an error message. 
        args:
            df (DataFrame): A DataFrame containing World Cup match data with columns "Date", "Stage", "Group", "Home Team", "Away Team", "Home Score", "Away Score", and "Winner".
            stage_code (str): The code for the stage to filter the matches.
            stage_label (str): The label for the stage to display in the component.
        returns:
            A Dash HTML component that displays the matches for the specified stage in a table format. For the group stage, it also groups the teams by their respective groups and displays them in separate sections. 
            If there is an error processing the data, it returns a simple HTML div with an error message.
            """
    try:
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
            #Extract unique groups and teams for the group stage
            stage_groups = stage_df["Group"].unique().tolist()
            for m in stage_groups:
                stage_list.append(m)

            # Filter df for groups and extract unique teams for each group, then append to stage_teams list as dictionaries with team name and group name. This will be used to display teams by group in the component.
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
            stage_df['Home Team'] = stage_df['Home Team'].fillna('TBD')
            stage_df['Away Team'] = stage_df['Away Team'].fillna('TBD')
            display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]
            match_elements = []
            for index, row in stage_df.iterrows():
                match_elements.append(
                    html.Span(f"{row['Home Team']} vs. {row['Away Team']}", className="generic-text-2", id=f"{row['Home Team']}-vs-{row['Away Team']}-wc-match-{index}")
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
            style={'backgroundColor': 'whitesmoke', 'color': WC_MAIN_BG_COLOR, 'justifyContent': 'center', 'alignItems': 'center'}
        )
    except Exception:
        return html.Div("Error loading World Cup data")


def get_cl_stage_component(df, stage_code, stage_label):
    """ This function takes a DataFrame containing Champions League match data, a stage code, and a stage label, and returns a Dash HTML component that displays the matches for that stage. 
    The function filters the DataFrame for the specified stage and creates a component that displays the matches in a table format. 
    For the league stage, it also groups the matches by their respective match days and displays them in separate sections. 
    If there is an error processing the data, the function returns a simple HTML div with an error message. 
        args:
            df (DataFrame): A DataFrame containing Champions League match data with columns "Date", "Stage", "Home Team", "Away Team", "Home Score", "Away Score", "Winner", and "Match Day".
            stage_code (str): The code for the stage to filter the matches.
            stage_label (str): The label for the stage to display in the component.
        returns:
            A Dash HTML component that displays the matches for the specified stage in a table format. For the league stage, it also groups the matches by their respective match days and displays them in separate sections. 
            If there is an error processing the data, it returns a simple HTML div with an error message.
    """
    try:
        df = pd.DataFrame(df)
        # Filter the DataFrame for the current stage
        stage_df = df[df["Stage"] == stage_code]
        if stage_df.empty:
            return html.Div("No data available")

        stage_df = stage_df.sort_values(["Stage", "Date"])
        display_cols = ["Date", "Home Team", "Home Score", "Away Score", "Away Team"]

        if stage_code == "LEAGUE_STAGE":
            match_day_list = stage_df["Match Day"].unique().tolist()
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
                                style={'backgroundColor': f'{CL_MAIN_BG_COLOR}', 'color': 'white', 'justifyContent': 'center', 'alignItems': 'center'}) for i, m in enumerate(match_day_list)
                                ])
            return html.Div(
                id=f"{stage_code}_tab_cl",
                children=select_match_day
            )
        
        stage_teams = stage_df.drop_duplicates(subset="Home Team", keep="first").to_dict("records")
        stage_teams_list = [[m['Home Team'], m['Away Team']] for m in stage_teams]
        matchups_dict = {}
        for m in stage_teams_list:
            if m[0] == None or m[1] == None:
                continue
            sorted_key = sorted(m)
            if f"{sorted_key[0]} vs {sorted_key[1]}" in matchups_dict:
                matchups_dict[f"{sorted_key[0]} vs {sorted_key[1]}"].append(m)
            else:
                matchups_dict.update({f"{sorted_key[0]} vs {sorted_key[1]}": [m]})
        #print(matchups_dict)
        stage_component = []
        for key, value in matchups_dict.items():
            #print(f"{key} : {value}")
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
            style={'backgroundColor': f'{CL_MAIN_BG_COLOR}', 'color': 'white', 'justifyContent': 'center', 'alignItems': 'center'})
    except Exception:
        return html.Div("Error loading Champions League data")
    