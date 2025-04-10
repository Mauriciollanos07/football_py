import requests
import pandas as pd

# Define the API endpoint and your API token
api_url = 'https://api.football-data.org/v4/competitions/WC/matches'
headers = {'X-Auth-Token': '9b3bba4a9ab24ab68b70aac4677adbbe'}  # Replace with your actual API token

# Send a GET request to the API
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    
    # Extracting relevant match information
    match_list = []
    for match in matches:
        match_list.append({
            "Date": match['utcDate'],
            "Home Team": match['homeTeam']['name'],
            "Away Team": match['awayTeam']['name'],
            "Home Score": match['score']['fullTime']['home'],
            "Away Score": match['score']['fullTime']['away'],
            "Status": match['status'],
            "Match Day": match['matchday']
        })
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(match_list)
    
    # Display the DataFrame
    print(df)

    df.to_csv('qatar_worldcup.csv', index=False)
    print("Data saved to 'qatar_worldcup.csv'.")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
