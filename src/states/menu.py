import time

# Menu presence events can arrive in quick bursts; reuse one party lookup
# briefly instead of issuing two remote requests per event.
PARTY_API_CACHE_SECONDS = 5


class Menu:
    def __init__(self, Requests, log, presences):
        self.Requests = Requests
        self.log = log
        self.presences = presences
        self._party_api_cache = None

    def get_party_json(self, GamePlayersPuuid, presencesDICT):
        game_players = {str(puuid).lower() for puuid in GamePlayersPuuid}
        party_json = {}
        for presence in presencesDICT:
            presence_puuid = str(presence.get("puuid", "")).lower()
            if presence_puuid in game_players:
                decodedPresence = self.presences.decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    
                    # Temp fix: Riot is swapping between nested and flat API structures.
                    party_size = 0
                    party_id = ""
                    if "partyPresenceData" in decodedPresence: # Check for nested structure
                        party_size = decodedPresence["partyPresenceData"]["partySize"]
                        party_id = decodedPresence["partyPresenceData"]["partyId"]
                    elif "partySize" in decodedPresence: # Check for flattened structure
                        party_size = decodedPresence["partySize"]
                        party_id = decodedPresence["partyId"]
                    else:
                        # No known structure found, log and fail
                        self.log("ERROR: Unknown presence API structure in 'get_party_json'.")
                        party_id = decodedPresence["partyPresenceData"]["partyId"]

                    if party_size > 1:
                        try:
                            party_json[party_id].append(presence["puuid"])
                        except KeyError:
                            party_json.update({party_id: [presence["puuid"]]})

        #remove non-in-game parties from with one player in game
        parties_to_delete = []
        for party in party_json:
            if len(party_json[party]) == 1:
                parties_to_delete.append(party)
        for party in parties_to_delete:
            del party_json[party]

        self.log(f"retrieved party json: {party_json}")
        return party_json

    def get_party_members(self, self_puuid, presencesDICT):
        # The party service lists every member, including players who are not
        # on this account's friends list. Presence only exposes friends, so it
        # is kept as a fallback for when the party service is unavailable.
        members = self._get_party_members_from_api(self_puuid)
        if members:
            return members
        return self._get_party_members_from_presence(self_puuid, presencesDICT)

    def _get_party_members_from_api(self, self_puuid):
        now = time.monotonic()
        cached = self._party_api_cache
        if cached and cached[0] == self_puuid and now - cached[1] < PARTY_API_CACHE_SECONDS:
            return cached[2]

        members = []
        try:
            player = self.Requests.fetch(
                "glz", f"/parties/v1/players/{self_puuid}", "get", rate_limit_seconds=1
            )
            party_id = player.get("CurrentPartyID") if isinstance(player, dict) else None
            if party_id:
                party = self.Requests.fetch(
                    "glz", f"/parties/v1/parties/{party_id}", "get", rate_limit_seconds=1
                )
                party_members = party.get("Members", []) if isinstance(party, dict) else []
                for member in party_members:
                    subject = member.get("Subject")
                    if not subject:
                        continue
                    identity = member.get("PlayerIdentity") or {}
                    members.append({
                        "Subject": subject,
                        "PlayerIdentity": {"AccountLevel": identity.get("AccountLevel", 0)},
                    })
        except Exception as exc:
            self.log(f"party API lookup failed: {exc}")
            members = []

        # A valid party always contains the current player; anything else is
        # treated as a failed lookup so the presence fallback is used.
        if not any(str(m["Subject"]).lower() == str(self_puuid).lower() for m in members):
            members = []
        if members:
            self.log(f"retrieved party members from party API: {members}")
        self._party_api_cache = (self_puuid, now, members)
        return members

    def _get_party_members_from_presence(self, self_puuid, presencesDICT):
        res = []
        party_id = ""
        self_puuid = str(self_puuid).lower()
        
        for presence in presencesDICT:
            if str(presence.get("puuid", "")).lower() == self_puuid:
                decodedPresence = self.presences.decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    
                    # Temp fix: Riot is swapping between nested and flat API structures.
                    account_level = 0
                    if "partyPresenceData" in decodedPresence: # Check for nested structure
                        party_id = decodedPresence["partyPresenceData"]["partyId"]
                        account_level = decodedPresence["playerPresenceData"]["accountLevel"]
                    elif "partyId" in decodedPresence: # Check for flattened structure
                        party_id = decodedPresence["partyId"]
                        account_level = decodedPresence["accountLevel"]
                    else:
                        # No known structure found, log and fail
                        self.log("ERROR: Unknown presence API structure in 'get_party_members' (self).")
                        party_id = decodedPresence["partyPresenceData"]["partyId"]
                        
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel": account_level}})
        
        # Find other party members
        for presence in presencesDICT:
            if str(presence.get("puuid", "")).lower() == self_puuid:
                continue # Skip self
                
            decodedPresence = self.presences.decode_presence(presence["private"])
            if decodedPresence["isValid"]:
                
                # Temp fix: Riot is swapping between nested and flat API structures.
                current_party_id = ""
                account_level = 0
                if "partyPresenceData" in decodedPresence: # Check for nested structure
                    current_party_id = decodedPresence["partyPresenceData"]["partyId"]
                    account_level = decodedPresence["playerPresenceData"]["accountLevel"]
                elif "partyId" in decodedPresence: # Check for flattened structure
                    current_party_id = decodedPresence["partyId"]
                    account_level = decodedPresence["accountLevel"]
                else:
                    # No known structure found, log and fail
                    self.log("ERROR: Unknown presence API structure in 'get_party_members'.")
                    current_party_id = decodedPresence["partyPresenceData"]["partyId"]

                if current_party_id and current_party_id == party_id:
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel": account_level}})
                    
        self.log(f"retrieved party members: {res}")
        return res