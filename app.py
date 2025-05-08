import requests
import pandas as pd
import dash
from dash import dcc, html
from functions import get_mathces_list_wc, get_mathces_list_cl, get_wc_stage_component, get_cl_stage_component
from dash import Input, Output, callback
from dash import ctx
import time

# API and token
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


# Initialize app
app = dash.Dash(__name__)
server = app.server
app.title = "World Cup 2022 Dashboard"


# App layout
app.layout = html.Div(children=[
    dcc.Tabs(id="tabs-main-container", className="tabs", children=[
        dcc.Tab( id="FIFA-WORLD-CUP-MAIN-TAB", label="FIFA WORLD CUP QATAR 2022", value="FIFA WORLD CUP QATAR 2022", children=[
            html.Div(children=[
                html.Div(
                    html.Img(src="/assets/resources/Qatar-main.jpg"), id="wc-image"
                ),
                html.Div(dcc.Tabs(id="wc-general-tabs", value=f"wc-tab-GROUP_STAGE", children=[dcc.Tab(id=f"wc-tab-{t}", label=f"WC {t}", value=f"wc-tab-{t}", style={"color": "#f5f0ec", "backgroundColor": "#2a010f", "border": "none", "fontWeight": "bolder"}, selected_style={"backgroundColor": "#f5f0ec", "color": "#2a010f", "fontWeight": "bolder"}) for t in stage_order["WC"]]),
                className="tabs-container-wc", id="wc-tabs-container", style={"width": "100%"})])
        ]),
        dcc.Tab( id="CHAMPIONS-LEAGUE-MAIN-TAB", label="2024/2025 CHAMPIONS LEAGUE", value="2024/2025 CHAMPIONS LEAGUE", children=[
            html.Div(children=[
                html.Div(
                    html.Img(src="/assets/resources/Champions-League.avif"),id="cl-image"
                ),
                html.Div(dcc.Tabs(id="cl-general-tabs", value=f"cl-tab-LEAGUE_STAGE", children=[dcc.Tab(id=f"cl-tab-{t}", label=f"CL {t}", value=f"cl-tab-{t}", style={"color": "#f5f0ec", "backgroundColor": "#01164b", "border": "none", "fontWeight": "bolder"}, selected_style={"backgroundColor": "#f5f0ec", "color": "#01164b", "fontWeight": "bolder"}) for t in stage_order["CL"]]), 
                className="tabs-container-cl", id="cl-tabs-container")])
            ])
        ]),
        dcc.Loading(id="loading", children=[html.Div(id="tabs-content")]),
        html.Div(id="callback-div")
], className="main-container")

@callback(
    Output('loading', 'children'),
    Input('tabs-main-container', 'value'),
    Input('wc-general-tabs', 'value'),
    Input('cl-general-tabs', 'value'),
)

def update_tab(tournament_tab, wc_tab, cl_tab):
    tab = tournament_tab
    time.sleep(1)
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
 
# Run
if __name__ == '__main__':
    app.run_server(debug=True)

