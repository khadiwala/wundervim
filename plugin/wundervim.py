from collections import OrderedDict
from itertools import chain, repeat, groupby


def update_tasks(client, buff):
    list_title, new_tasks = buff[0].strip(), buff[3:]
    lis = next(l for l in client.lists() if l.title.strip() == list_title)
    old_tasks = client.tasks(lis.id)

    by_title = OrderedDict([(t.title, t) for t in old_tasks])
    assert len(by_title) == len(old_tasks), "Duplicate todo titles are currently unhandled"

    for t in new_tasks:
        if t not in by_title:
            client.create_task(lis.id, t)

    # positions = repeat(None, len(new_tasks))
    # for i,t in enumerate(new_tasks):
    #     if t.title in by_title:
    #         positions[i] =


def task_view(client, list_title):
    """
    <List title>
    ==========

    <task 1>
    <task 2>
    ...
    """
    list_title = list_title.strip()
    header = [list_title, '='*len(list_title), '']
    lists = client.lists()
    for l in lists:
        if l.title.strip() == list_title:
            return header + [t.title for t in client.tasks(l.id, reload=True)]
    return ["Specified list ({}) not found - possibly deleted?".format(list_title)]


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
            prefix += "  "
        for lis in v:
            res.append(prefix + lis.title)
    return res
