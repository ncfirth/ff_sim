import json
import numpy as np


def get_league_status(session):
    url = 'https://fantasy.premierleague.com/drf/leagues-h2h-standings/44274'
    res = session.get(url)
    res = json.loads(res.text)
    return res


def get_fixtures(session):
    has_next = True
    page_n = 1
    fixtures_dict = {}
    while has_next is True:
        url = ('https://fantasy.premierleague.com/drf/'
               'leagues-h2h-matches/league/44274?page=')
        url += str(page_n)
        res = session.get(url)
        res = json.loads(res.text)
        has_next = res['has_next']
        page_n += 1
        for match in res['results']:
            gw_over = match['entry_1_win'] + match['entry_1_draw']
            gw_over += match['entry_1_loss']
            if gw_over != 0:
                continue
            gw = match['event']
            if gw not in fixtures_dict:
                fixtures_dict[gw] = []
            home_team = match['entry_1_player_name']
            away_team = match['entry_2_player_name']
            fixtures_dict[gw].append([home_team, away_team])
    return fixtures_dict


def sim_league(league_start, fixtures):
    league = league_start.copy()
    for gw_n, matches in fixtures.items():
        for match in matches:
            res = np.random.choice([0, 1, 2], p=[0.495, 0.495, 0.01])
            if res == 0:
                league[match[0]] += 3
            elif res == 1:
                league[match[1]] += 3
            else:
                league[match[0]] += 1
                league[match[1]] += 1
    return league


def mcmc_season(league_start, fixtures, n_iter):
    league_rankings = dict((x, np.empty(n_iter)) for x in league_start.keys())
    for i in range(n_iter):
        league_end = sim_league(league_start, fixtures)
        league_end_zip = zip(league_end.keys(), league_end.values())
        league_end_zip = sorted(league_end_zip, key=lambda x: x[1],
                                reverse=True)
        for j in range(len(league_end_zip)):
            league_rankings[league_end_zip[j][0]][i] = j + 1
    return league_rankings
