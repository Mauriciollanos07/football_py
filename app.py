import requests
import pandas as pd
import dash
from dash import dcc, html
from functions import get_mathces_list_wc, get_mathces_list_cl, get_wc_stage_component, get_cl_stage_component
from dash import Input, Output, callback
from dash import ctx
import time
import os
#from config import API_TOKEN, API_URL_MATCHES_WC, API_URL_MATCHES_CL (for development)
from functions import WC_MAIN_BG_COLOR, CL_MAIN_BG_COLOR, WC_MAIN_COLOR, CL_MAIN_COLOR

API_TOKEN = os.environ.get('API_TOKEN') # Get API token from environment variable
API_URL_MATCHES_WC = os.environ.get('API_URL_MATCHES_WC') # Get WC API URL from environment variable
API_URL_MATCHES_CL = os.environ.get('API_URL_MATCHES_CL') # Get CL API URL from environment variable

# API and token
headers = {'X-Auth-Token': API_TOKEN}

# Fetch 2026 World Cup match data
try:
    wc_resp = requests.get(API_URL_MATCHES_WC, headers=headers)
    wc_resp.raise_for_status()
    wc_data = wc_resp.json()
    wc_matches = wc_data.get('matches', [])
except (requests.RequestException, ValueError, KeyError):
    wc_matches = []

try:
    cl_resp = requests.get(API_URL_MATCHES_CL, headers=headers)
    cl_resp.raise_for_status()
    cl_data = cl_resp.json()
    cl_matches = cl_data.get('matches', [])
except (requests.RequestException, ValueError, KeyError):
    cl_matches = []

# Prepare the WC data
wc_match_list = get_mathces_list_wc(wc_matches)
wc_df = pd.DataFrame(wc_match_list)

# Prepare the CL data
cl_match_list = get_mathces_list_cl(cl_matches)
cl_df = pd.DataFrame(cl_match_list)

# Define stage order and labels
WC_STAGES = wc_df['Stage'].unique().tolist()
CL_STAGES = cl_df['Stage'].unique().tolist()
stage_order = {
    "WC": WC_STAGES,
    "CL": CL_STAGES
    }
stage_labels = {
    "WC": {
        stage: stage.replace("_", " ").title() for stage in WC_STAGES
    },
    "CL": {
        stage: stage.replace("_", " ").title() for stage in CL_STAGES
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
        dcc.Tab( id="FIFA-WORLD-CUP-MAIN-TAB", label="FIFA WORLD CUP", value="FIFA WORLD CUP", children=[
            html.Div(style={"backgroundColor": WC_MAIN_BG_COLOR}, children=[
                html.Div(
                    html.Img(src="/assets/resources/2026-wc-banner.webp"), id="wc-image"
                ),
                html.Div(dcc.Tabs(id="wc-general-tabs", value=f"wc-tab-GROUP_STAGE", children=[dcc.Tab(id=f"wc-tab-{t}", label=f"WC {t}", value=f"wc-tab-{t}", style={"color": CL_MAIN_COLOR, "backgroundColor": WC_MAIN_BG_COLOR, "border": "none", "fontWeight": "bolder"}, selected_style={"backgroundColor": CL_MAIN_COLOR, "color": WC_MAIN_BG_COLOR, "fontWeight": "bolder"}) for t in stage_order["WC"]]),
                className="tabs-container-wc", id="wc-tabs-container", style={"width": "100%"})])
        ]),
        dcc.Tab( id="CHAMPIONS-LEAGUE-MAIN-TAB", label="2025/2026 CHAMPIONS LEAGUE", value="2025/2026 CHAMPIONS LEAGUE", children=[
            html.Div(style={"backgroundColor": CL_MAIN_BG_COLOR}, children=[
                html.Div(
                    html.Img(src="/assets/resources/Champions-League.avif"), id="cl-image"
                ),
                html.Div(dcc.Tabs(id="cl-general-tabs", value=f"cl-tab-LEAGUE_STAGE", children=[dcc.Tab(id=f"cl-tab-{t}", label=f"CL {t}", value=f"cl-tab-{t}", style={"color": CL_MAIN_COLOR, "backgroundColor": CL_MAIN_BG_COLOR, "border": "none", "fontWeight": "bolder"}, selected_style={"backgroundColor": CL_MAIN_COLOR, "color": CL_MAIN_BG_COLOR, "fontWeight": "bolder"}) for t in stage_order["CL"]]), 
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
        if tab == "FIFA WORLD CUP":
            if wc_tab is None:
                return html.Div("No data available")
            else:
                return get_wc_stage_component(wc_df, wc_tab.split("-")[-1], stage_labels["WC"][wc_tab.split("-")[-1]])
        elif tab == "2025/2026 CHAMPIONS LEAGUE":
            if cl_tab is None:
                return html.Div("No data available")
            else:
                return get_cl_stage_component(cl_df, cl_tab.split("-")[-1], stage_labels["CL"][cl_tab.split("-")[-1]])
        else:
            return html.H1("Select a tournament")
 
# Run
if __name__ == '__main__':
    app.run_server(debug=True)

