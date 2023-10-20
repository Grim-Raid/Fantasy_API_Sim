from calendar import week
from sqlite3 import SQLITE_TRANSACTION
from tkinter import N
from turtle import position
import requests
def get_player_id(name):
    url = "https://stage.api.fantasy.nfl.com/v3/players"
    headers = {
        "Content-Type": "application/json",
        # Add any additional headers if required
    }

    params = {
        "appKey": "d3dw9q3jg3w9q3jg3w9q3jg3w9",
        "filter[searchQuery]": f"{name}",
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes
        data = response.json()
        # Search for the player using first name and last name
        return data['data'][0]['id'], data['data'][0]['attributes']['position']
        
        return None  # If player not found
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")

def get_player_projected_points(player_id, week):
    url = f"https://staging-api2.fantasy.nfl.com/v3/players/{player_id}/projectedstats"
    headers = {
        "Content-Type": "application/json",
        # Add any additional headers if required
    }
    params = {
        "week": week,
    }


    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes
        data = response.json()

        print(data['included'][0]['attributes']['points'])
        return data['included'][0]['attributes']['points']
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception: {err}")
def optimizeLineupPoints(players, week):
    # find highest projected QB
    QB_points = 0
    for player in players:
        if players[player]['position'] == 'QB':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] >= QB_points:
                QB_points = players[player]['points']
                QB = player
    players.pop(QB)
    # find highest projected Flex (RB, WR)
    Flex_points = 0
    for player in players:
        if players[player]['position'] == 'RB' or players[player]['position'] == 'WR':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] >= Flex_points:
                Flex_points = players[player]['points']
                Flex = player
    players.pop(Flex)
    # find highest projected TE
    TE_points = 0
    for player in players:
        if players[player]['position'] == 'TE':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] >= TE_points:
                TE_points = players[player]['points']
                TE = player
    players.pop(TE)
    # find highest projected K
    K_points = 0
    for player in players:
        if players[player]['position'] == 'K':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] >= K_points:
                K_points = players[player]['points']
                K = player
    players.pop(K)
    # find highest projected DEF
    DEF_points = 0
    for player in players:
        if players[player]['position'] == 'DEF':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] >= DEF_points:
                DEF_points = players[player]['points']
                DEF = player
    players.pop(DEF)
    # find highest projected 2 RB
    RB1_points = 0
    RB2_points = 0
    for player in players:
        if players[player]['position'] == 'RB':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] > RB1_points:
                RB1_points = players[player]['points']
                RB1 = player
            elif players[player]['points'] >= RB2_points:
                RB2_points = players[player]['points']
                RB2 = player
    players.pop(RB1)
    players.pop(RB2)
    # find highest projected 2 WR
    WR1_points = 0
    WR2_points = 0
    for player in players:
        if players[player]['position'] == 'WR':
            players[player]['points'] = get_player_projected_points(players[player]['id'], week)
            if players[player]['points'] == None:
                players[player]['points'] = 0
            if players[player]['points'] > WR1_points:
                WR1_points = players[player]['points']
                WR1 = player
            elif players[player]['points'] >= WR2_points:
                WR2_points = players[player]['points']
                WR2 = player
    players.pop(WR1)
    players.pop(WR2)
    return [QB, RB1, RB2, WR1, WR2, TE, Flex, K, DEF], QB_points + RB1_points + RB2_points + WR1_points + WR2_points + TE_points + Flex_points + K_points + DEF_points


# Example usage


player_names = ['Buffalo Bills', 'Jalen Hurts', 'Jaylen Waddle', "Dalton Schultz", 'Travis Etienne', 'Davante Adams', 'Michael Thomas', 'George Kittle', 'Alexander Mattison', 'Geno Smith', 'Tyler Allgeier', 'T.J. Hockenson', 'JuJu Smith-Schuster', 'Kadarius Toney', 'Jason Myers']
players = dict.fromkeys(player_names)
for name in player_names:
    temp = {'id': '', 'position': ''}
    player_id, position = get_player_id(name)
    temp['id'] = player_id
    temp['position'] = position
    players[name] = temp
    for x, y in players.items():
        print(x, y)
season_points = 0
for i in range(7,14):
    result, points = optimizeLineupPoints(players.copy(), i)
    season_points += points
    print(result, points, season_points)
print("Optimal Lineup: ", season_points)