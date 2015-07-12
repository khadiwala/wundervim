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
        'tasks': lambda s, id, **_: {0: map(mock_api_object, list1_tasks)}[id],
        'subtasks': constant([])
    })
    assert wv.task_view(client, lists[0])[3:] == map(wv.format_task, list1_tasks)


def test_task_creation():
    new_todo = "new todo!"
    updated = []

    def create_task(self, list_id, new_title):
        assert list_id == 0
        assert new_title == new_todo
        updated.append(None)
        return mock_api_object(new_title)

    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(lists)]),
        'tasks': lambda s, id, **_: {0: map(mock_api_object, list1_tasks)}[id],
        'create_task': create_task,
        'subtasks': constant([])
    })

    wv.update_tasks(client, wv.task_header(lists[0]) + map(wv.format_task, list1_tasks + [new_todo]))

    # check that create_task was called
    assert updated


def test_subtask_creation():
    new_subtask = "new todo!"
    updated = []

    def create_subtask(self, task_id, new_title):
        assert task_id == 1
        assert new_title == new_subtask
        updated.append(True)
        return mock_api_object(new_title)

    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(lists)]),
        'tasks': lambda s, id, **_: {0: [mock_api_object(t, id=i) for i, t in enumerate(list1_tasks)]}[id],
        'create_subtask': create_subtask,
        'subtasks': constant([])
    })
    formatted_tasks = map(wv.format_task, list1_tasks)
    formatted_tasks.insert(2, wv.format_subtask(new_subtask))  # add subtask to task t2
    wv.update_tasks(client, wv.task_header(lists[0]) + formatted_tasks)

    # check that create_task was called
    assert updated


def test_task_completion():
    updated = []

    def update_task(self, task_id, old_revision, **kwargs):
        assert 'completed' in kwargs
        assert kwargs['completed']
        assert old_revision == 2
        assert task_id == 2
        updated.append(True)

    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3,t4,t5'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(lists)]),
        'tasks': lambda s, id, **_: {0: [mock_api_object(t, i, {'revision': 2}) for i, t in enumerate(list1_tasks)]}[id],
        'update_task': update_task,
        'subtasks': constant([])
    })
    wv.update_tasks(client, wv.task_header(lists[0]) + map(wv.format_task, (list1_tasks[0:2] + list1_tasks[3:])))
    assert updated


def test_subtask_completion():
    updated = []

    def update_subtask(self, subtask_id, old_revision, **kwargs):
        assert 'completed' in kwargs
        assert kwargs['completed']
        assert old_revision == 2
        assert subtask_id == 2
        updated.append(True)

    lists = "list1,list2".split(',')
    list1_tasks = 't1,t2,t3,t4,t5'.split(',')
    t2_subtasks = 'st1,st2,st3'.split(',')
    client = mock_client({
        'lists': constant([mock_api_object(t, id=i) for i, t in enumerate(lists)]),
        'tasks': lambda s, id, **_: {0: [mock_api_object(t, i) for i, t in enumerate(list1_tasks)]}[id],
        'subtasks': lambda s, id, **_: [mock_api_object(t, i, {'revision': 2}) for i, t in enumerate(t2_subtasks)] if id == 1 else [],
        'update_subtask': update_subtask
    })
    formatted_tasks = map(wv.format_task, list1_tasks)
    with_subtasks = formatted_tasks[0:2] + map(wv.format_subtask, t2_subtasks)[:-1] + formatted_tasks[2:]

    wv.update_tasks(client, wv.task_header(lists[0]) + with_subtasks)
    assert updated
