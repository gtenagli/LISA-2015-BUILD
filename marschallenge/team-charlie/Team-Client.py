#!/usr/bin/python
# Mars Team Client Example written in Python
# Requires the following library to install: sudo pip install websocket-client
# if you encounter errors with a Six import:
# you can try: pip remove six; pip install six
# Windows users: you may need to install the Microsoft Visual C++ Compiler for Python 2.7
# Windows users. please use this link: http://aka.ms/vcpython27
import requests
import websocket
import json


# Global Variables
team_name = 'AggressiveSimon'                        # The Name of the Team
team_auth = '1234'                                  # The Team Authentication Tocken
server_url = 'http://localhost:8080/api'   # URL of the SERVER API
server_ws = 'ws://localhost:8080/ws'       # URL of the Sensors Websocket


# Server Method Calls ------------------------------------------------

def register_team(team_name):
    """
    Registers the Team in the Server
    :param team_name:The team name
    :return:The Team authentication Token
    """

    url = server_url + "/join/" + team_name
    print('Server API URL: ' + url)
    payload = ''

    # POST with form-encoded data
    response = requests.post(url, data=payload)

    team_auth = response.text
    # print ('Team Authentication Code:' + team_auth )

    if response.status_code == 200:
        print ('Team \'' + team_name + '\' joined the game!')
        print (team_name + ' authentication Code: ' + team_auth)
    else:
        print ('Team \'' + team_name + '\' joining game Failed!')
        print ("HTTP Code: " + str(response.status_code) + " | Response: " + response.text)

    return team_auth


# Shield Method Calls ------------------------------------------------
def team_shield_up(team_name, team_auth):
    """
    Sets the team shield up
    curl -i -H 'X-Auth-Token: 1335aa6af5d0289f' -X POST http://localhost:8080/api/shield/enable
    :param team_name:The team name
    :param team_auth:The team authentication token
    :return: nothing
    """
    url = server_url + '/shield/enable'
    auth_header = {'X-Auth-Token': team_auth}
    shield_up = requests.post(url, headers=auth_header)
    if shield_up.status_code == 200:
        print ('Server: Team: ' + team_name + ' Shield is UP!')
    else:
        print ('Server: Team: ' + team_name + ' Shield UP! request Failed!')
        print ("HTTP Code: " + str(shield_up.status_code) + " | Response: " + shield_up.text)


def team_shield_down(team_name, team_auth):
    """
    Sets the team shield Down
    curl -i -H 'X-Auth-Token: 1335aa6af5d0289f' -X POST http://localhost:8080/api/shield/disable
    :param team_name:The team name
    :param team_auth:The team authentication token
    :return: nothing
    """
    url = server_url + '/shield/disable'
    auth_header = {'X-Auth-Token': team_auth}
    shield_down = requests.post(url, headers=auth_header)
    if shield_down.status_code == 200:
        print ('Server: Team: ' + team_name + ' Shield is DOWN!')
    else:
        print ('Server: Team: ' + team_name + ' Shield DOWN! request Failed!')
        print ("HTTP Code: " + str(shield_down.status_code) + " | Response: " + shield_down.text)


# Client Logic ------------------------------------------------

def data_recording(parsed_json):
    """
    Saves the Mars sensor data in data repository
    :param parsed_json:Readings from Mars Sensors
    :return:Nothing
    """
    print("\nData Recording: Saving Data row for persistence. Time: " + str(parsed_json['startedAt']))


def team_strategy(parsed_json):
    """
  Contains the Team's strategy.
  :param parsed_json: Readings from the Mars Sensors
  :return:Nothing
  """
    # The Strategy for this client is to have the shield up constantly until it is depleted.
    # Then wait until is charged again to a 10% and enable it again

    # Get the Team List
    teams_list = parsed_json['teams']

#######our magic########
    goldenratio = 0.45
#        normalisedtemp = readings['temperature'] + 200
    normalisedtemp = int(parsed_json['readings']['temperature']) + 200
#        ratio = normalisedtemp / float(readings['radiation'])
    ratio = normalisedtemp / float(parsed_json['readings']['radiation'])

    temp = int(parsed_json['readings']['temperature'])
    rad = int (parsed_json['readings']['radiation'])

#if positive turn shield on, if negative turn shield off
    decision = 2
    if rad < 400: #very low radiation not worth burning energy
        decision += -1
    elif rad < 400: #low radiation not worth burning energy
        decision += 0
    elif rad > 700: #high radiation gotta protect life
        decision += 0
    else:
        decision += 0
    if parsed_json['readings']['solarFlare'] is True: #solar flare is really bad
        decision += 0
    if temp > -30: # we will quickly regenerate energy
        decision += -1
    elif temp > -10: # we will less quickly regenerate energy
        decision += 0
    elif temp < -40: # we won't quickly regenerate energy
        decision += 0
    else:
        decision += 0

#    for team in teams_list: #a sanity check based on the other teams
#        if team['name'] != team_name:
#            if team['shield'] is True:
#                decision +=1
#            if team['shield'] is False:
#                decision += -1
#        else:
#        if team['name'] == team_name:
#            if team['energy'] < 10: #running out of energy better save it
#                decision += -2
#            if team['energy'] > 85: #we've got energy to burn
#                decision += 4
#            if team['life'] < 5: # we gonna die!
#                decision += 10
#            if team['life'] > 75: # we have life to burn
#                decision += -2



            ######################
    # Find this team
    for team in teams_list:
        if team['name'] == team_name:
#            print ("decision: " + decision + "\n")
            if decision > 0:
                team_shield_up(team_name, team_auth)
            else:
                team_shield_down(team_name, team_auth)

# Register the Team
team_auth = register_team(team_name)

# Create the WebSocket for Listening
ws = websocket.create_connection(server_ws)

while True:

    json_string = ws.recv()  # Receives the the json information

    # Received '{"running":false,"startedAt":"2015-08-04T00:44:40.854306651Z","readings":{"solarFlare":false,"temperature":-3.
    # 960996217958863,"radiation":872},"teams":[{"name":"TheBorgs","energy":100,"life":0,"shield":false},{"name":"QuickFandang
    # o","energy":100,"life":0,"shield":false},{"name":"InTheBigMessos","energy":32,"life":53,"shield":false},{"name":"MamaMia
    # ","energy":100,"life":100,"shield":false}]}'

    parsed_json = json.loads(json_string)
    # Check if the game has started
    print("Game Status: " + str(parsed_json['running']))
    if not parsed_json['running']:
        print('Waiting for the Game Start')
    else:
        data_recording(parsed_json)
        team_strategy(parsed_json)
        print ("Solar Flare: " + str(parsed_json['readings']['solarFlare']) + " Radiation: " + str(parsed_json['readings']['radiation']) + ", Temperature: " + str(parsed_json['readings']['temperature']) + "\n")
    
    oldtemp = int(parsed_json['readings']['temperature'])
    oldrad = int (parsed_json['readings']['radiation'])


ws.close()

print "Good bye!"
