import threading
import webbrowser
from datetime import datetime, timedelta

from flask import Flask, render_template, request
from flask_caching import Cache
from pymongo import MongoClient

from api import get_data_from_url

app = Flask(__name__)
APP_PORT = 8000

# Configure caching
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)
CACHE_TTL = 300

API_KEY = 'd4c211a2fcbd4268b66b430969f34fbc'

COMPETITIONS = {
    'Premier League': 'PL',
    'Bundesliga': 'BL1',
    'La Liga': 'PD',
    'Serie A': 'SA',
    'Ligue 1': 'FL1'
}

SEASONS = [2021, 2022, 2023]

# Configure DB
client = MongoClient('localhost', 27017)
db = client.soccer_data


@cache.memoize(CACHE_TTL)
def fetch_data(competition_id, season, endpoint, params=None):
    base_url = f'https://api.football-data.org/v4/competitions/{competition_id}/{endpoint}'
    headers = {'X-Auth-Token': API_KEY}
    params = params if params else {'season': season}
    response = get_data_from_url(base_url, headers=headers, params=params)
    save_response_to_db(competition_id, season, endpoint, response)

    return response


def save_response_to_db(competition_id, season, endpoint, response):
    collection_name = {
        'standings': 'standings',
        'matches': 'matches',
        'club_flags': 'club_flags'
    }.get(endpoint.split('/')[0], 'unknown')

    status = 'SCHEDULED' if 'status=SCHEDULED' in endpoint else \
        'FINISHED' if 'status=FINISHED' in endpoint else \
            'UNKNOWN'

    document = {
        'competition_id': competition_id,
        'season': season,
        'status': status,
        'data': response,
        'timestamp': datetime.utcnow()
    }

    db[collection_name].insert_one(document)


def get_competition_standings(competition_id, season):
    return fetch_data(competition_id, season, 'standings')


def get_competition_matches(competition_id, season, status='SCHEDULED'):
    endpoint = f'matches?status={status}'
    try:
        response = fetch_data(competition_id, season, endpoint)
    except Exception:
        # check DB if remote not available
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        document = db.matches.find_one({
            'competition_id': competition_id,
            'season': season,
            'status': status,
            'timestamp': {'$gte': one_day_ago}
        })
        if document:
            return document['data']
        else:
            raise Exception("Failed to fetch data from remote and no recent data in local storage.")

    return response


@cache.memoize(CACHE_TTL)
def fetch_club_flags_from_network(competition_id):
    url = f'https://cdn.logosports.net/club/fb/list?region={competition_id}'
    response = get_data_from_url(url, {}, {})
    save_response_to_db(competition_id, None, 'club_flags', response)

    return response


def get_club_flags(competition_id, season):
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    document = db.club_flags.find_one({
        'competition_id': competition_id,
        'timestamp': {'$gte': one_day_ago}
    })
    if document:
        return document['data']
    else:
        return fetch_club_flags_from_network(competition_id)


def set_logos(data, key, logo_list):
    if not logo_list:  # Check if logo_list is empty
        for item in data[key]:
            if 'table' in item:
                for entry in item['table']:
                    entry['team']['logo'] = ""
            else:  # For matches
                item['homeTeam']['logo'] = ""
                item['awayTeam']['logo'] = ""
        return

    for item in data[key]:
        if 'table' in item:
            for entry in item['table']:
                entry['team']['logo'] = get_logo_by_team_name(entry['team']['name'], logo_list)
        else:  # For matches
            item['homeTeam']['logo'] = get_logo_by_team_name(item['homeTeam']['name'], logo_list)
            item['awayTeam']['logo'] = get_logo_by_team_name(item['awayTeam']['name'], logo_list)


def get_logo_by_team_name(name, logo_list):
    for logo in logo_list:
        if logo['name'] == name:
            return logo['logo']
    return ""


@app.route('/')
def home():
    competition_id = request.args.get('competition_id', 'PL')
    season = int(request.args.get('season', '2023'))

    logo_list = get_club_flags(competition_id, season)
    standings = get_competition_standings(competition_id, season)
    matches = get_competition_matches(competition_id, season)
    completed_matches = get_competition_matches(competition_id, season, 'FINISHED')

    set_logos(standings, 'standings', logo_list)
    set_logos(matches, 'matches', logo_list)
    set_logos(completed_matches, 'matches', logo_list)

    return render_template(
        'index.html',
        competitions=COMPETITIONS,
        selected_competition=competition_id,
        seasons=SEASONS,
        selected_season=season,
        standings=standings,
        matches=matches,
        completed_matches=completed_matches
    )


def open_browser():
    webbrowser.open('http://localhost:8000/')


if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(port=APP_PORT)
