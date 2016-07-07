# modified from https://github.com/seemethere/nba_py

from nba_py_mod import _api_scrape, _get_json

class PlayByPlay:
    _endpoint = 'playbyplay'

    def __init__(self,
                 game_id,
                 start_period=1,
                 end_period=4):
        self.json = _get_json(endpoint=self._endpoint,
                              params={'GameID': game_id,
                                      'StartPeriod': start_period,
                                      'EndPeriod': end_period})

    def info(self):
        return _api_scrape(self.json, 0)

    def available_video(self):
        return _api_scrape(self.json, 1)
