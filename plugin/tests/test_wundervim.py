import random
from api import Struct
import wundervim as wv


def mock_client(fun_dic):
    mc = type("MockClient", (object,), fun_dic)
    return mc()


def constant(res):
    def con(*args, **kwargs):
        return res
    return con


def mock_api_object(title, id=None, additional={}):
    return Struct(**dict(additional, id=(random.randint(0, 1000) if id is None else id), title=title))


def test_list_view():
    assert wv.wunder_view(mock_client({
        'folders': constant([]),
        'lists': constant(map(mock_api_object, "These are test lists".split()))
        })) == "These are test lists".split()


def test_with_folders():
    assert wv.wunder_view(mock_client({
        'folders': constant([mock_api_object("my_folder", additional={'list_ids': [1, 2]})]),
        'lists': constant(mock_api_object(l, id=i) for i, l in enumerate("These are test lists".split()))
        })) == ["These", "my_folder", "  are", "  test", "lists"]


def test_task_view():
    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(["list1", "list2"])]),
        'tasks': lambda s, id, **_: {0: map(mock_api_object, list1_tasks)}[id]
    })
    assert wv.task_view(client, lists[0])[3:] == list1_tasks


def test_task_creation():
    new_todo = "new todo!"
    updated = []

    def create_task(self, list_id, new_title):
        assert list_id == 0
        assert new_title == new_todo
        updated.append(None)

    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(lists)]),
        'tasks': lambda s, id, **_: {0: map(mock_api_object, list1_tasks)}[id],
        'create_task': create_task
    })

    wv.update_tasks(client, [lists[0], '='*len(lists[0]), ''] + list1_tasks + [new_todo])

    # check that create_task was called
    assert updated


def test_task_completion():
    updated = []

    def update_task(self, task_id, old_revision, **kwargs):
        assert 'completed' in kwargs
        assert kwargs['completed']
        assert old_revision == 2
        assert task_id == 2
        updated.append(None)

    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3,t4,t5'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(lists)]),
        'tasks': lambda s, id, **_: {0: [mock_api_object(t, i, {'revision': 2}) for i, t in enumerate(list1_tasks)]}[id],
        'update_task': update_task
    })
    wv.update_tasks(client, [lists[0], '', ''] + (list1_tasks[0:2] + list1_tasks[3:]))
    assert updated
