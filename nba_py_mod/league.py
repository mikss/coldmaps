from nba_py_mod import _api_scrape, _get_json
from nba_py_mod.constants import *

class GameLog:
    _endpoint = 'leaguegamelog'

    def __init__(self,
                 league_id=League.Default,
                 season=CURRENT_SEASON,
                 season_type=SeasonType.Default,
                 player_or_team=Player_or_Team.Default,
                 counter=Counter.Default,
                 sorter=Sorter.Default,
                 direction=Direction.Default,
                 ):

        self.json = _get_json(endpoint=self._endpoint,
                              params={'LeagueID': league_id,
                                      'Season': season,
                                      'SeasonType': season_type,
                                      'PlayerOrTeam': player_or_team,
                                      'Counter': counter,
                                      'Sorter': sorter,
                                      'Direction': direction
                                      })

    def overall(self):
        return _api_scrape(self.json, 0)
