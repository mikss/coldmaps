# modified from https://github.com/seemethere/nba_py

from requests import get

HAS_PANDAS = True
try:
    from pandas import DataFrame
except ImportError:
    HAS_PANDAS = False

# Constants
BASE_URL = 'http://stats.nba.com/stats/{endpoint}/'


def _api_scrape(json_inp, ndx):
    """
    Internal method to streamline the getting of data from the json

    Args:
        json_inp (json): json input from our caller
        ndx (int): index where the data is located in the api

    Returns:
        If pandas is present:
            DataFrame (pandas.DataFrame): data set from ndx within the
            API's json
        else:
            A dictionary of both headers and values from the page
    """
    try:
        headers = json_inp['resultSets'][ndx]['headers']
        values = json_inp['resultSets'][ndx]['rowSet']
    except KeyError:
        # This is so ugly but this is what you get when your data comes out
        # in not a standard format
        try:
            headers = json_inp['resultSet'][ndx]['headers']
            values = json_inp['resultSet'][ndx]['rowSet']
        except KeyError:
            # Added for results that only include one set (ex. LeagueLeaders)
            headers = json_inp['resultSet']['headers']
            values = json_inp['resultSet']['rowSet']
    if HAS_PANDAS:
        return DataFrame(values, columns=headers)
    else:
        # Taken from www.github.com/bradleyfay/py-goldsberry
        return [dict(zip(headers, value)) for value in values]


def _get_json(endpoint, params):
    """
    Internal method to streamline our requests / json getting

    Args:
        endpoint (str): endpoint to be called from the API
        params (dict): parameters to be passed to the API

    Raises:
        HTTPError: if requests hits a status code != 200

    Returns:
        json (json): json object for selected API call
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'}
    _get = get(BASE_URL.format(endpoint=endpoint), params=params, headers=headers)
    print (_get.url)
    _get.raise_for_status()
    return _get.json()
