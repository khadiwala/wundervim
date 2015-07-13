from collections import OrderedDict, defaultdict
from itertools import chain, repeat, groupby

INDENT = ' ' * 2
TASK_SYMBOL = '*'
SUBTASK_SYMBOL = '-'


def format_task(s):
    return TASK_SYMBOL + ' ' + s


def format_subtask(s):
    return INDENT + SUBTASK_SYMBOL + ' ' + s


def deformat_task(s):
    return s.replace(TASK_SYMBOL, '', 1).strip()


def deformat_subtask(s):
    return s.replace(SUBTASK_SYMBOL, '', 1).strip()


def task_header(list_title):
    """
    <List title>

    <help>
    ==========
    """
    header = [
        list_title,
        '',
        'Delete a line to complete a task, add a line to create one',
        '{} For regular tasks'.format(TASK_SYMBOL),
        '{}{} For subtasks'.format(INDENT, SUBTASK_SYMBOL)
    ]
    return header + ['=' * max(map(len, header))]


def wunder_view(client):
    """
    <Folder 1>
      <List 1>
      <List 2>
    <List 3>
    """
    folders = client.folders()
    folders_by_id = {f.id: f for f in folders}
    lists_by_folder = dict(chain(*[zip(f.list_ids, repeat(f.id)) for f in folders]))
    by_fid = groupby(client.lists(reload=True), lambda k: lists_by_folder.get(k.id, None))

    res = []
    for k, v in by_fid:
        prefix = ""
        if k is not None:
            res.append(folders_by_id[k].title)
            prefix += INDENT
        for lis in v:
            res.append(prefix + lis.title)
    return res


def task_view(client, list_title):
    """
    <task header>
    * <task 1>
    * <task 2>
      - <subtask 2-1>
    ...
    """
    list_title = list_title.strip()
    lists = client.lists()
    for l in lists:
        if l.title.strip() == list_title:
            return task_header(list_title) + list(chain.from_iterable(
                [format_task(t.title)] + [format_subtask(st.title) for st in client.subtasks(t.id)] for t in client.tasks(l.id, reload=True)))
    return ["Specified list ({}) not found - possibly deleted?".format(list_title)]


def update_tasks(client, buff):
    list_title, lines = buff[0].strip(), buff[len(task_header("")):]
    assert lines[0].strip().startswith(TASK_SYMBOL), "New todo list must start with a task (*)"

    # TODO make fewer passes

    # seperate tasks / subtasks
    curr_task = deformat_task(lines[0])
    new_tasks = [curr_task]
    new_subtasks = defaultdict(list)
    for line in lines[1:]:
        if line.strip().startswith(TASK_SYMBOL):
            curr_task = deformat_task(line)
            new_tasks.append(curr_task)
        elif line.strip().startswith(SUBTASK_SYMBOL):
            new_subtasks[curr_task].append(deformat_subtask(line))

    lis = next(l for l in client.lists() if l.title.strip() == list_title)
    old_tasks = client.tasks(lis.id)

    by_title = OrderedDict([(t.title, t) for t in old_tasks])
    assert len(by_title) == len(old_tasks), "Duplicate todo titles are currently unhandled"

    def id_from_title(title):
        """ Creates the task with title if it doesnt already exist """
        return by_title[title].id if title in by_title else client.create_task(lis.id, title).id

    # maps from task id -> subtasks for task for old tasks
    old_st_by_id = {t.id: client.subtasks(t.id) for t in old_tasks}

    # maps from task id -> subtask title for task for new tasks
    new_st_by_id = {id_from_title(t): new_subtasks[t] for t in new_tasks}

    # create new subtasks
    for nid, nsts in new_st_by_id.items():
        osts = map(lambda s: s.title, old_st_by_id.get(nid, []))
        isnew = lambda k: k not in osts
        for a in filter(isnew, nsts):
            client.create_subtask(nid, a)

    # complete any tasks that have finished
    for t in by_title.values():
        if t.title not in new_tasks:
            client.update_task(t.id, t.revision, completed=True)

    # complete any subtasks that have finished
    for oid, osts in old_st_by_id.items():
        isgone = lambda k: k.title not in new_st_by_id.get(oid, [])
        for a in filter(isgone, osts):
            client.update_subtask(a.id, a.revision, completed=True)
