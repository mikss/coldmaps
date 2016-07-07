import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from nba_py_mod import player, shotchart, league, game

def get_all_misses():
    """
    Returns a df with every single missed shot in 2015-2016 NBA season.
    """
    players = player.PlayerList().info()['PERSON_ID']
    all_misses = pd.DataFrame()
    for pid in players:
        shots = shotchart.ShotChart(player_id = pid).shot_chart()
        misses = shots[shots['SHOT_MADE_FLAG'] == 0][['GAME_ID', 'GAME_EVENT_ID', 'LOC_X', 'LOC_Y','SHOT_DISTANCE']]
        all_misses = all_misses.append(misses)

    return all_misses

def get_all_games():
    """
    Returns a list of every game ID.
    """
    return league.GameLog().overall()['GAME_ID'].unique()

def pbp_calc_next(pbp):
    """
    Takes in a play-by-play pandas.DataFrame and returns a new df with "next-point" value calculated.
    """
    pbp = pbp[pbp['EVENTMSGTYPE'] <= 3]
    pbp = pbp[['GAME_ID', 'EVENTNUM', 'EVENTMSGTYPE', 'HOMEDESCRIPTION', 'VISITORDESCRIPTION']]

    pbp['NEXT'] = 0
    for i in range(len(pbp.index)):
        shot = pbp.iloc[i,:]

        # missed shot
        if shot['EVENTMSGTYPE'] == 2:
            if shot['HOMEDESCRIPTION'] and 'MISS' in shot['HOMEDESCRIPTION']:
                home_flag = True
            else:
                home_flag = False

            if i+1 >= len(pbp.index):
                break
            next_shot = pbp.iloc[i+1,:]

            # made shot
            if next_shot['EVENTMSGTYPE'] == 1:
                shoot_flag = bool(next_shot['HOMEDESCRIPTION'])
                if shoot_flag:
                    team = 'HOME'
                else:
                    team = 'VISITOR'
                sign = int(not (shoot_flag ^ home_flag)) * 2 - 1

                value = 2

                # check for three pointer
                if '3PT' in next_shot[team + 'DESCRIPTION']:
                    value += 1

                # check for foul on play
                if i+2 >= len(pbp.index):
                    break
                next_next_shot = pbp.iloc[i+2,:]
                if next_next_shot['EVENTMSGTYPE'] == 3:
                    team_flag = bool(next_next_shot['HOMEDESCRIPTION'])
                    if team_flag == shoot_flag:
                        if 'MISS' not in next_next_shot[team + 'DESCRIPTION']:
                            value += 1

                pbp.iloc[i,5] += sign * value

            # missed shot
            elif next_shot['EVENTMSGTYPE'] == 2:
                pbp.iloc[i,5] += 0

            # free throw
            elif next_shot['EVENTMSGTYPE'] == 3:
                ft_flag = bool(next_shot['HOMEDESCRIPTION'])
                if ft_flag:
                    team = 'HOME'
                else:
                    team = 'VISITOR'

                sign = int(not (ft_flag ^ home_flag)) * 2 - 1

                desc = next_shot[team + 'DESCRIPTION']
                if 'of' in desc:
                    count = int(desc.split(' of ')[1][0])
                    value = count - pbp.iloc[i+1:i+1+count,:][team + 'DESCRIPTION'].str.contains('MISS').sum()
                elif 'Technical' in desc and 'MISS' not in desc:
                    value = 1
                else:
                    value = 0

                pbp.iloc[i,5] += sign * value

    return pbp

def join_misses_locs(all_misses, games):
    """
    Matches misses and next-possession values to shot locations.
    """
    all_miss_locs_vals = pd.DataFrame()
    game_count = 0
    for g in games:
        pbp = game.PlayByPlay(g, start_period=1, end_period=4).info()
        pbp = pbp_calc_next(pbp)

        ms = all_misses[all_misses['GAME_ID'] == g][['GAME_EVENT_ID','LOC_X','LOC_Y','SHOT_DISTANCE']]
        ms.rename(columns = {'GAME_EVENT_ID':'EVENTNUM'}, inplace = True)

        miss_locs = pd.merge(pbp, ms, how = 'inner', on=['EVENTNUM'])
        miss_locs = miss_locs[miss_locs['EVENTMSGTYPE'] == 2]
        miss_locs = miss_locs[['LOC_X','LOC_Y','SHOT_DISTANCE','NEXT']]

        all_miss_locs_vals = all_miss_locs_vals.append(miss_locs)

        game_count += 1
        print(game_count)

    all_miss_locs_vals.index = list(range(len(all_miss_locs_vals.index)))
    return all_miss_locs_vals
