from random import choice
import os
import json
import re
# import bungie as bun
from . import bungie as bun


# --- Helpers 

def create_response(message):
    lambda_json = json.loads('''{
      "version": "1.0",
      "response": {
        "outputSpeech": {
          "type": "PlainText",
          "text": ""
        },
        "shouldEndSession": false
      }
    }''')
    lambda_json['response']['outputSpeech']['text'] = message
    return lambda_json
    
def try_exists(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """
    try:
        return func()
    except KeyError:
        return None


# ---- Bungie Class & Intent Functions for API requests

def create_bungie_object():
    """
    Create BungieData instance using my API Key
    """
    return bun.BungieData(os.environ['BUNGIE_API_KEY'])

def get_player_stats(bungie):
    """
    Get my own stats
    """
    my_destiny_id = bungie.get_DestinyUserId("BalancedSeeker6")
    my_stats = bungie.get_PlayerStats(my_destiny_id)
    return my_stats
    
def format_player_stat(my_stats, play_type):
    play_type_phoneme = '.'.join(list(play_type[-3:]))
    play_stats = my_stats['mergedAllCharacters']['results'][play_type]['allTime']
    rand_stat_key = choice(list(play_stats.keys()))
    rand_stat_key_message = ' '.join(re.findall('[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', rand_stat_key))
    random_stat = play_stats[rand_stat_key]['basic']['displayValue']
    message = "In {}, your {} is currently {}".format(play_type_phoneme, rand_stat_key_message, random_stat)
    return create_response(message)

# ---- Intents

def get_random_stat(intent_request, bungie):
    """
    Returns a random stat for a random play type (PvP or PvE)
    """
    # session_attributes = intent_request['session'] if intent_request['session'] is not None else {}
    
    # grab player stats
    my_stats = get_player_stats(bungie)
    play_type = choice(['allPvP', 'allPvE'])
    return format_player_stat(my_stats, play_type)
    
def get_random_PVE_stat(intent_request, bungie):
    """
    Returns a random stat for PvE
    """
    my_stats = get_player_stats(bungie)
    return format_player_stat(my_stats, 'allPvE')
    
def get_random_PVP_stat(intent_request, bungie):
    """
    Returns a random stat for PvE
    """
    my_stats = get_player_stats(bungie)
    return format_player_stat(my_stats, 'allPvP')


# ---- Kick off Intent functionality

def dispatch(event):
    """
    Called when the user specifies an intent for this bot
    """
    intent_request = event['request']['intent']
    intent_name = event['request']['intent']['name']
    
    #  logger.debug('dispatch userId={}, intentName={}'.format(event['userId'], intent_name))
    
    bungie = create_bungie_object()
    
    # Dispatch to Alexa's intent handlers
    if intent_name == 'GetRandomPlayerStat':
        return get_random_stat(intent_request, bungie)
    elif intent_name == 'GetRandomPvEPlayerStat':
        return get_random_PVE_stat(intent_request, bungie)
    elif intent_name == 'GetRandomPvPPlayerStat':
        return get_random_PVP_stat(intent_request, bungie)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    return dispatch(event)
