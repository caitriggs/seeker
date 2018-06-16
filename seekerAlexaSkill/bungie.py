import requests

class BungieData(object):

    def __init__(self, api_key, gamertag="BalancedSeeker6", session=None):
        '''
        session: an object from login.py defining a user session by 
        logging into Bungie.net (oAuth verified)
        '''
        self.session = session
        self.api_key = api_key
        self.gamertag = gamertag
        self.destiny_id = self.get_DestinyUserId()
       
        
    def get_playerByTagName(self):
        site_call = "https://bungie.net/Platform/Destiny2/SearchDestinyPlayer/2/" + self.gamertag
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']
    
    def get_DestinyUserId(self):
        info = self.get_playerByTagName()
        return int(info[0]['membershipId'])

    def get_BungieUserId(self):
        '''
        Use old Destiny endpoint for PSN user to get the BUNGIE membershipId for a user
        '''
        site_call = "https://bungie.net/Platform/User/GetMembershipsById/" + str(self.destiny_id) + "/2/" 
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return int(request.json()['Response']['bungieNetUser']['membershipId'])
    
    def get_DestinyUserProfile(self, components=[100]):
        '''
        Use new Destiny 2 endpoint for PSN player using the Destiny membershipId 
        '''
        components = "?components=" + ','.join([str(c) for c in components])
        site_call = "https://bungie.net/Platform/Destiny2/2/Profile/" + str(self.destiny_id) + "/" + components
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']
    
    def get_postGameStats(self, game_id):
        site_call = "https://bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/" + str(game_id)
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']
    
    def get_Manifest(self):
        site_call = "https://bungie.net/Platform/Destiny2/Manifest/"
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']
    
    def get_PlayerStats(self):
        site_call = "https://bungie.net/Platform/Destiny2/2/Account/" + str(self.destiny_id) + "/Stats/"
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']
    
    def get_StatDefinitions(self):
        site_call = "https://bungie.net/Platform/Destiny2/Stats/Definition/"
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_ActivityHistory(self, character_id, count=None):
        site_call = "https://bungie.net/Platform/Destiny2/2/Account/" + str(self.destiny_id)+\
            "/Character/" + str(character_id) + "/Stats/Activities/" 
        if count:
            site_call = site_call + "?count=" + str(count)
        request = requests.get(site_call, 
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']
