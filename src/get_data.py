import requests
import os
import json
import numpy as np

class BungieData(object):

    def __init__(self, api_key, membershipType):
        '''
        api_key (str): The api key given to you by Bungie when you registered your app with them
        membershipType (int): The console/network the player's account is on (i.e. 1=Xbox, 2=PSN)
        '''
        self.api_key = api_key
        self.membershipType = membershipType
        self.membership_id = 0 #gets set once get_DestinyUserId is called
        self.gamertag = "" #gets set once get_DestinyUserId is called

    def get_PlayerByTagName(self, gamertag):
        '''gamertag (str): The gamertag a player uses on Destiny 2'''
        self.gamertag = str(gamertag)
        site_call = "https://bungie.net/Platform/Destiny2/SearchDestinyPlayer/" \
            + str(self.membershipType) + "/" + gamertag
        request = requests.get(site_call,
                               headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_DestinyUserId(self, gamertag):
        '''gamertag (str): The gamertag a player uses on Destiny 2'''
        info = self.get_PlayerByTagName(gamertag)
        self.membership_id = int(info[0]['membershipId'])
        return self.membership_id

    def get_BungieUserId(self):
        '''
        membership_id (int): the Destiny membership_id of a player (the id returned by get_DestinyUserId)
        Uses old Destiny endpoint for a PSN user to get the BUNGIE membershipId
        '''
        site_call = "https://bungie.net/Platform/User/GetMembershipsById/" \
            + str(self.membership_id) + "/" + str(self.membershipType)
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return int(request.json()['Response']['bungieNetUser']['membershipId'])

    def get_DestinyUserProfile(self, components=[100]):
        '''
        membership_id (int): the Destiny membership_id of a player (returned by get_DestinyUserId)
        components (list of ints): the type of info you want returned according the Bungie API docs.
          Defaults to 100: basic profile info ([100, 200] would also return more detailed info by Destiny character
        Uses new Destiny 2 endpoint for PSN player using the Destiny membershipId
        '''
        components = "?components=" + ','.join([str(c) for c in components])
        site_call = "https://bungie.net/Platform/Destiny2/" + str(self.membershipType) + "/Profile/" \
            + str(self.membership_id) + "/" + components
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_activitiesByCharacter(self, character_id):
        '''This is an endpoint that does NOT offer instanceIds which enable you to call PGCR by instanceID'''
        site_call = "https://bungie.net/Platform/Destiny2/" + str(self.membershipType) + "/Profile/" \
            + str(self.membership_id) + "/Character/" + str(character_id) + "/?components=CharacterActivities"
        request = requests.get(site_call,
                               headers={"X-API-Key":self.api_key})
        return request.json()['Response']['activities']

    def get_ActivitiesStatsByCharacter(self, character_id):
        site_call = "https://bungie.net/Platform/Destiny2/" + str(self.membershipType) + "/Account/" + \
            str(self.membership_id) + "/Character/" + str(character_id) + "/Stats/Activities/?"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']['activities']

    def get_InstanceIdsByCharacter(self, character_id):
        activities = self.get_ActivitiesStatsByCharacter(character_id)
        instance_ids = []
        for activity in activities:
            instance_ids.append(activity['activityDetails']['instanceId'])
        return instance_ids

    def get_CharacterIds(self):
        user_data = self.get_DestinyUserProfile(components=[100])
        return user_data['profile']['data']['characterIds']

    def get_PlayerByCharacterId(self, character_id):
        pass

    def get_PGCR(self, instance_id):
        '''
        instance_id (int): the game instanceId which can be found by calling
            the endpoint in get_ActivitiesStatsByCharacter()
        returns the Post Game Carnage Report (lovingly known as a PGCR in the Bungie API community)
        '''
        site_call = "https://bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/" + str(instance_id)
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        try:
            return request.json()['Response']
        except KeyError:
            return request.json()

    def get_Manifest(self):
        site_call = "https://bungie.net/Platform/Destiny2/Manifest/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_PlayerStats(self):
        site_call = "https://bungie.net/Platform/Destiny2/" + str(self.membershipType) + \
            "/Account/" + str(self.membership_id) + "/Stats/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_StatDefinitions(self):
        site_call = "https://bungie.net/Platform/Destiny2/Stats/Definition/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']


if __name__ == '__main__':
    bungie = BungieData(api_key=os.environ["BUNGIE_API_KEY"], membershipType=2) # Never put your keys in code... export 'em!

    # Get my Destiny MembershipId by PSN gamertag; sets my destinyId for bungie instance
    bungie.get_DestinyUserId("BalancedSeeker6")
    print("Player: {}\n".format(bungie.gamertag))

    # Get a random game's post carnage stats for a Character
    character_id = np.random.choice(bungie.get_CharacterIds(), size=1)[0]
    instance_id = np.random.choice(bungie.get_InstanceIdsByCharacter(character_id), size=1)[0]
    game_stats = bungie.get_PGCR(instance_id)
    print("Stats (PGCReport) of a random Destiny 2 game of mine: \n{}".format(json.dumps(game_stats, indent=2)))
