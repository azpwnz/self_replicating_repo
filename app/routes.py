import base64
import json
import os
from urllib.parse import urlencode

import requests
from flask import redirect, render_template, request, url_for

from app import app

app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']

GITHUB_API_URL = 'https://api.github.com/'
# We may ask user to choose the name if needed
NEW_REPO_NAME = 'az_self_replicating_repo'
NEW_REPO_DESC = 'This app allows replicating its own code into user\'s Github repository.'

FILES = [
    'self_replicating.py',
    'requirements.txt',
    'Procfile',
    '.gitignore',
    'installation_doc.md',
    'tech_specification.md',
    'README.md',
    'app/templates/base.html',
    'app/templates/index.html',
    'app/templates/success.html',
    'app/templates/error.html',
    'app/static/img/git.png',
    'app/static/img/good_job.png',
    'app/__init__.py',
    'app/routes.py',
]


@app.route('/')
def index():
    """
    Home page
    """
    return render_template('index.html')


@app.route('/replicate/<string:token>')
def replicate(token):
    """
    Create the new repo on behalf of the authorized user and commit app's files there.
    """
    headers = {
        'Authorization': 'token {}'.format(token)
    }

    # Create new repo
    url = '{}user/repos'.format(GITHUB_API_URL)
    response = requests.post(url, headers=headers, json={'name': NEW_REPO_NAME, 'description': NEW_REPO_DESC})

    if response.status_code != 200 and 'errors' in response.json():
        return render_template('error.html', errors=response.json()['errors'])

    replica_url = response.json()['html_url']

    # Get user's username
    url = '{}user'.format(GITHUB_API_URL)
    username = requests.get(url, headers=headers).json()['login']

    # Commit all the files
    for file_name in FILES:
        with open(file_name, 'rb') as file:
            url = '{}repos/{}/{}/contents/{}'.format(GITHUB_API_URL, username, NEW_REPO_NAME, file_name)
            params = {
                'message': 'Add {}'.format(file_name),
                'content': base64.b64encode(file.read()).decode("utf-8"),

            }
            response = requests.put(url, headers=headers, data=json.dumps(params))
            if response.status_code != 200 and 'errors' in response.json():
                return render_template('error.html', errors=response.json()['errors'])

    return render_template('success.html', replica_url=replica_url, username=username)


@app.route('/login')
def login():
    """
    Redirect user to Github authorize page.
    After successful authorization Github will redirect user to authorize() route.
    """
    params = {'client_id': app.config['GITHUB_CLIENT_ID'], 'scope': 'public_repo'}
    url = 'https://github.com/login/oauth/authorize?{}'.format(urlencode(params))
    return redirect(url)


@app.route('/github-callback')
def authorize():
    """
    Exchange the code received from Github for access token.
    Then, redirect user to repo replication flow with access token.
    """
    params = dict(client_id=app.config['GITHUB_CLIENT_ID'],
                  client_secret=app.config['GITHUB_CLIENT_SECRET'],
                  code=request.args.get('code'))
    headers = {
        'Accept': 'application/json'
    }
    response = requests.post('https://github.com/login/oauth/access_token', data=params, headers=headers).json()
    access_token = response['access_token']

    return redirect(url_for('replicate', token=access_token))


if __name__ == '__main__':
    app.run()
