from config import CLIENT_SECRET, CLIENT_ID, USER_CONFIG, AUTH_BASE, PORT
import json
import urllib
import requests
import random
import string
import webbrowser


def oauth_headers():
    return {
        'X-Access-Token': get_token(),
        'X-Client-ID': CLIENT_ID
    }

def load_token():
    d = {}

    # random state
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    url = '/'.join([AUTH_BASE, "oauth", "authorize"])
    url = url + "?" + urllib.urlencode({
        'client_id': CLIENT_ID,
        'state': state,
        'redirect_uri': 'http://localhost:{}'.format(PORT),
    })

    from flask import Flask, request
    from multiprocessing import Process, Event
    key_wait = Event()
    app = Flask(__name__.split('.')[0])

    @app.route('/')
    def code():
        try:
            code = request.args.get('code')
            url = '/'.join([AUTH_BASE, "oauth", "access_token"])
            resp = requests.post(url, {
                'code': code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            })
            d['access_token'] = resp.json()['access_token']
            with open(USER_CONFIG, "w") as f:
                json.dump(d, f)
            return "Success! token granted"
        except Exception as e:
            print e
            return 500, e
        finally:
            key_wait.set()

    @app.route('/kill', methods=['POST'])
    def kill():
        try:
            request.environ.get('werkzeug.server.shutdown')()
        except Exception as e:
            print e

    def killer():
        key_wait.wait()
        requests.post('http://localhost:{}/kill'.format(PORT))

    Process(target=killer).start()
    webbrowser.open(url)
    app.run(port=PORT)
    return d


def get_token():
    """ Generate a user token or acquire from cached config """
    try:
        d = json.load(open(USER_CONFIG))
    except:
        d = {}
    if "access_token" not in d:
        load_token()
    return json.load(open(USER_CONFIG))['access_token']


if __name__ == '__main__':
    load_token()
