from util import memoized
import json
import itertools
import requests
import os


def api_id(obj):
    return obj.id


def validate(resp):
    if not (resp.status_code / 100) == 2:
        raise ValueError("request (headers: {}, body:{} failed with {}: {}".format(
            resp.request.headers,
            resp.request.body,
            resp.status_code,
            resp.text))


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __str__(self):
        return str(self.__dict__)


class WunderList(object):
    def __init__(self, api_base, oauth_headers):
        self.api_base = api_base
        self.oauth_headers = oauth_headers
        self.cache = {}

    def tasks(self, list_id, reload=False):
        if 'tasks' not in self.cache:
            self.cache['tasks'] = {}
        if reload or list_id not in self.cache['tasks']:
            self.cache['tasks'][list_id] = [Struct(**t) for t in self.api_get('tasks', params={'list_id': list_id})]
        return self.cache['tasks'][list_id]

    def create_task(self, list_id, title):
        return self.api_post('tasks', data={'list_id': list_id, 'title': title})

    def update_task(self, task_id, revision, **kwargs):
        return self.api_patch(os.path.join('tasks', str(task_id)), data=dict(kwargs, revision=revision))

    def lists(self, reload=False):
        if reload or 'lists' not in self.cache:
            unsorted_lists = [Struct(**l) for l in self.api_get('lists')]
            position = self.list_positions()
            self.cache['lists'] = self._by_position(unsorted_lists, position)
        return self.cache['lists']

    def list(self, ident, reload=False):
        if 'lists' not in self.cache:
            self.cache['lists'] = []
        if reload or ident not in map(self.cache['lists'], api_id):
            # Struct(api_get(os.path.join('lists', ident)))
            # just reload everything for now
            self.cache['lists'] = self.lists(True)
            # still missing?
            if ident not in map(self.cache['lists'], api_id):
                raise ValueError("{} doesn't exist".format(ident))

        return next(item for item in self.cache['lists'] if item.id == ident)

    def list_positions(self):
        return [Struct(**pos) for pos in self.api_get('list_positions')][0]

    def folders(self, reload=False):
        if reload or 'folders' not in self.cache:
            self.cache['folders'] = [Struct(**f) for f in self.api_get('folders')]
        return self.cache['folders']

    def api_verb(self, verb, endpoint, params, data):
        resp = verb(
            os.path.join(self.api_base, endpoint),
            headers=dict(self.oauth_headers, **{'Content-Type': 'application/json'}),
            data=json.dumps(data),
            params=params)
        validate(resp)
        return resp.json()

    def api_get(self, endpoint, params={}, data={}):
        return self.api_verb(requests.get, endpoint, params, data)

    def api_put(self, endpoint, params={}, data={}):
        return self.api_verb(requests.put, endpoint, params, data)

    def api_post(self, endpoint, params={}, data={}):
        return self.api_verb(requests.post, endpoint, params, data)

    def api_patch(self, endpoint, params={}, data={}):
        return self.api_verb(requests.patch, endpoint, params, data)

    def _by_position(self, to_sort, positions):
        """ Sorts lists or tasks by posisiton list """
        by_id = {item.id: item for item in to_sort}
        result = list(itertools.repeat(None, len(to_sort) + len(by_id)))
        for i, item_id in enumerate(positions.values):
            result[i] = by_id.pop(item_id, None)

        # spec says to sort by id if not in positions
        result[len(positions.values):] = sorted(by_id.values(), key=api_id)

        # filter out Nones (position references we don't have)
        return filter(None, result)


@memoized
def get_client():
    from config import API_BASE
    from auth import oauth_headers
    return WunderList(API_BASE, oauth_headers())

if __name__ == '__main__':
    from auth import oauth_headers
    c = WunderList('http://localhost:8888', oauth_headers())
    c.api_post('tasks', data={'list_id': 165068116, 'title': "madeup"})
