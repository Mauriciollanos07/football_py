import requests
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash import dash_table
from functions import get_mathces_list_wc, get_mathces_list_cl, get_wc_stage_component, get_cl_stage_component
from dash import Input, Output, callback

# API and token
API_URL_MATCHES_WC = 'https://api.football-data.org/v4/competitions/WC/matches'
API_URL_MATCHES_CL = 'https://api.football-data.org/v4/competitions/CL/matches'
API_TOKEN = '02c8648f03b64960af5df010463cc253'
headers = {'X-Auth-Token': API_TOKEN}

# Fetch 2022 World Cup match data
wc_resp = requests.get(API_URL_MATCHES_WC, headers=headers)
wc_data = wc_resp.json()
wc_matches = wc_data.get('matches', [])

cl_resp = requests.get(API_URL_MATCHES_CL, headers=headers)
cl_data = cl_resp.json()
cl_matches = cl_data.get('matches', [])

# Prepare the WC data
wc_match_list = get_mathces_list_wc(wc_matches)
wc_df = pd.DataFrame(wc_match_list)

# Prepare the CL data
cl_match_list = get_mathces_list_cl(cl_matches)
cl_df = pd.DataFrame(cl_match_list)

# Define stage order and labels
stage_order = {
    "WC": ["GROUP_STAGE", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "THIRD_PLACE", "FINAL"],
    "CL": ["LEAGUE_STAGE", "PLAYOFFS", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"]
    }
stage_labels = {
    "WC": {
        "GROUP_STAGE": "Group Stage",
        "LAST_16": "Round of 16",
        "QUARTER_FINALS": "Quarterfinals",
        "SEMI_FINALS": "Semifinals",
        "THIRD_PLACE": "Third Place",
        "FINAL": "Final"
    },
    "CL": {
        "LEAGUE_STAGE": "League Stage",
        "PLAYOFFS": "Playoffs",
        "LAST_16": "Round of 16",
        "QUARTER_FINALS": "Quarterfinals",
        "SEMI_FINALS": "Semifinals",
        "FINAL": "Final"
    }
}

# create tabs that will contain each round
tabs = []
#wc_tabs = get_wc_tab(wc_df, stage_order["WC"], stage_labels["WC"])
#wc_tabs = {f"wc-tab-{stage}": get_wc_stage_component(wc_df, stage, stage_labels["WC"][stage]) for stage in stage_order["WC"]}
#cl_tabs = get_cl_tab(cl_df, stage_order["CL"], stage_labels["CL"])
#cl_tabs = {f"cl-tab-{stage}": get_cl_stage_component(cl_df, stage, stage_labels["CL"][stage]) for stage in stage_order["CL"]}

""" tabs.append( dcc.Tab( id="FIFA-WORLD-CUP-MAIN-TAB", label="FIFA WORLD CUP QATAR 2022", children=[
            html.Div(
        html.Img(src="/assets/resources/Qatar-main.jpg"), id="wc-image"
    ),
    html.Div( dcc.Tabs(wc_tabs),
    className="tabs-container", id="wc-tabs-container", style={"width": "100%"})
]))

tabs.append( dcc.Tab( id="CHAMPIONS-LEAGUE-MAIN-TAB", label="2024/2025 CHAMPIONS LEAGUE", children=[
            html.Div(
        html.Img(src="/assets/resources/Champions-League.avif"),id="cl-image"
    ),
    html.Div( dcc.Tabs(cl_tabs), id="cl-tabs-container")
])) """

# Initialize app
app = dash.Dash(__name__)
app.title = "World Cup 2022 Dashboard"


# App layout
app.layout = html.Div(children=[
    dcc.Store(id="tabs-store", data={"tabs": tabs}),
    dcc.Tabs(id="tabs-main-container", className="tabs", children=[
        dcc.Tab( id="FIFA-WORLD-CUP-MAIN-TAB", label="FIFA WORLD CUP QATAR 2022", value="FIFA WORLD CUP QATAR 2022", children=[
            html.Div(children=[
                html.Div(
                    html.Img(src="/assets/resources/Qatar-main.jpg"), id="wc-image"
                ),
                html.Div(dcc.Tabs(id="wc-general-tabs", value=f"wc-tab-GROUP_STAGE", children=[dcc.Tab(id=f"wc-tab-{t}", label=f"WC {t}", value=f"wc-tab-{t}") for t in stage_order["WC"]]),
        className="tabs-container", id="wc-tabs-container", style={"width": "100%"})])
        ]),
        dcc.Tab( id="CHAMPIONS-LEAGUE-MAIN-TAB", label="2024/2025 CHAMPIONS LEAGUE", value="2024/2025 CHAMPIONS LEAGUE", children=[
            html.Div(children=[
                html.Div(
                    html.Img(src="/assets/resources/Champions-League.avif"),id="cl-image"
                ),
                html.Div(dcc.Tabs(id="cl-general-tabs", value=f"cl-tab-LEAGUE_STAGE", children=[dcc.Tab(id=f"cl-tab-{t}", label=f"CL {t}", value=f"cl-tab-{t}") for t in stage_order["CL"]]), id="cl-tabs-container")])
            ])
        ]),
        html.Div(id="tabs-content"),
], className="main-container")

@callback(
    Output('tabs-content', 'children'),
    Input('tabs-main-container', 'value'),
    Input('wc-general-tabs', 'value'),
    Input('cl-general-tabs', 'value'),
)

def update_tab(tournament_tab, wc_tab, cl_tab):
    tab = tournament_tab
    print(f"tournament_tab is {tournament_tab}")
    print(f"wc_tab is {wc_tab}")
    print(f"cl_tab is {cl_tab}")
    print(f"wc_tab is {wc_tab}")
    print(f"cl_tab is {cl_tab}")
    print(f"split wc.tab is {stage_labels['WC'][wc_tab.split('-')[-1]]}")
    if not tab:
        raise 
    else:
        if tab == "FIFA WORLD CUP QATAR 2022":
            if wc_tab is None:
                return html.Div("No data available")
            else:
                return get_wc_stage_component(wc_df, wc_tab.split("-")[-1], stage_labels["WC"][wc_tab.split("-")[-1]])
        elif tab == "2024/2025 CHAMPIONS LEAGUE":
            if cl_tab is None:
                return html.Div("No data available")
            else:
                return get_cl_stage_component(cl_df, cl_tab.split("-")[-1], stage_labels["CL"][cl_tab.split("-")[-1]])
        else:
            return html.Div("No data available")
 

# children=[dcc.Tab(id=f"wc-tab-{t}", label=f"WC-{t}") for t in stage_order["WC"]]
# Run
if __name__ == '__main__':
    app.run_server(debug=True)

"""        dcc.Tab( id="FIFA-WORLD-CUP-MAIN-TAB", label="FIFA WORLD CUP QATAR 2022", children=[
            html.Div(children=[
                html.Div(
                    html.Img(src="/assets/resources/Qatar-main.jpg"), id="wc-image"
                ),
                html.Div(dcc.Tabs(children=[dcc.Tab(id=f"wc-tab-{t}", label=f"WC-{t}") for t in stage_order["WC"]]),
        className="tabs-container", id="wc-tabs-container", style={"width": "100%"})])
        ]),
        dcc.Tab( id="CHAMPIONS-LEAGUE-MAIN-TAB", label="2024/2025 CHAMPIONS LEAGUE", children=[
            html.Div(children=[
                html.Div(
                    html.Img(src="/assets/resources/Champions-League.avif"),id="cl-image"
                ),
                html.Div(dcc.Tabs(children=[dcc.Tab(id=f"CL-tab-{t}", label=f"CL {t}") for t in stage_order["CL"]]), id="cl-tabs-container")])
            ])
        ])"""
