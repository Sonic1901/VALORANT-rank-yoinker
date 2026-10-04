
class Rank:
    def __init__(self, Requests, log, content, ranks_before):
        self.Requests = Requests
        self.log = log
        self.ranks_before = ranks_before
        self.content = content
        self.requestMap = {}

    def get_request(self, puuid):
        if puuid in self.requestMap:
            return self.requestMap[puuid]

        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        self.requestMap[puuid] = response
        return response

    def invalidate_cached_responses(self):
        self.requestMap = {}

    #in future rewrite this code
    def get_rank(self, puuid, seasonID):
        response = self.get_request(puuid)
        final = {
            "rank": None,
            "rr": None,
            "leaderboard": None,
            "peakrank": None,
            "wr": None,
            "numberofgames": 0,
            "peakrankact": None,
            "peakrankep": None,
            "statusgood": None,
            "statuscode": None,
            }
        r = {}
        try:
            if response is not None and response.ok:
                # self.log("retrieved rank successfully")
                r = response.json()
                season_data = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]
                rankTIER = season_data["CompetitiveTier"]
                if int(rankTIER) >= 21:
                    # rank = [rankTIER,
                            # r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            # r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["LeaderboardRank"]]

                    final["rank"] = rankTIER
                    final["rr"] = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"]
                    final["leaderboard"] = season_data.get("LeaderboardRank") or 0
                elif int(rankTIER) not in (0, 1, 2):
                    final["rank"] = rankTIER
                    final["rr"] = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"]
                    final["leaderboard"] = 0

                    # rank = [rankTIER,
                            # r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            # 0]
                else:
                    final["rank"] = 0
                    final["rr"] = 0
                    final["leaderboard"] = 0

            else:
                self.log("failed getting rank")
                if response is not None:
                    self.log(response.text)
                final["rank"] = 0
                final["rr"] = 0
                final["leaderboard"] = 0
        except TypeError:
            final["rank"] = 0
            final["rr"] = 0
            final["leaderboard"] = 0
        except KeyError:
            final["rank"] = 0
            final["rr"] = 0
            final["leaderboard"] = 0
        max_rank = final["rank"]
        max_rank_season = seasonID
        seasons = r.get("QueueSkills", {}).get("competitive", {}).get(
            "SeasonalInfoBySeasonID"
        )
        if seasons is not None:
            for season in seasons:
                wins_by_tier = seasons[season].get("WinsByTier")
                if wins_by_tier is not None:
                    for winByTier in wins_by_tier:
                        if season in self.ranks_before:
                            if int(winByTier) > 20:
                                winByTier = int(winByTier) + 3
                        if int(winByTier) > max_rank:
                            max_rank = int(winByTier)
                            max_rank_season = season
            # rank.append(max_rank)
            final["peakrank"] = max_rank
        else:
            # rank.append(max_rank)
            final["peakrank"] = max_rank
        try:
            wins = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfWinsWithPlacements"]
            total_games = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfGames"]
            final["numberofgames"] = total_games
            try:
                wr = int(wins / total_games * 100)
            except ZeroDivisionError: #no loses
                wr = 100
        except (KeyError, TypeError): #haven't played this season, #no data?
            # print("test")
            wr = "N/A"


        # rank.append(wr)
        final["wr"] = wr
        final["statusgood"] = response is not None and response.ok
        final["statuscode"] = response.status_code if response is not None else None
        

        #peak rank act and ep
        peak_rank_act_ep = (
            self.content.get_act_episode_from_act_id(max_rank_season)
            if max_rank_season
            else {"act": None, "episode": None}
        )
        final["peakrankact"] = peak_rank_act_ep["act"]
        final["peakrankep"] = peak_rank_act_ep["episode"]
        return final
