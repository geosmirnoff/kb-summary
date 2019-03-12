kanboardapipath = ''
kanboardtoken = ''

import logging
import requests
from kanboard import Kanboard
from datetime import datetime

class KanSupport:

    def __init__(self):
        self.kb = Kanboard(kanboardapipath, "jsonrpc", kanboardtoken)
        self.project_id = self.kb.getProjectByIdentifier(identifier="GLOBALSUPPORT")['id']
        self.statusToColumn = {}
        self.get_status_to_columns()
        self.swimlane = self.kb.getActiveSwimlanes(project_id=self.project_id)[0]['id']
        self.logger = logging.getLogger("gsup.KanSupport")
        #self.colors = self.kb.
        self.default_color = self.kb.getDefaultTaskColor()
        #self.categories = self.kb.getAllCategories(project_id=self.project_id)


def row(tsk, tbl, cats, cols):
    color = 'color'
    if color in tsk:
        item = tsk[color]
        background = 'background'
        if background in item:
            rgb = item[background]
    tbl += '<tr style=\'background-color: ' + rgb + '\'>\n'
    for key in tsk:
        if key == 'id':
            tbl += '<td>' + str(tsk[key]) + '</td>\n'
            tags = kb.getTaskTags(task_id=tsk[key])
            for item in tags:
                tag = tags[item]
            tbl += '<td>' + str(tag) + '</td>\n'
        if key == 'title':
            tbl += '<td>' + str(tsk[key]) + '</td>\n'
        if key == 'column_id':
            for col in cols:
                if ('id' and 'title') in col:
                    if col['id'] == tsk[key]:
                        tbl += '<td>' + col['title'] + '</td>\n'
        if key == 'category_id':
            for cat in cats:
                if ('id' and 'name') in cat:
                    if cat['id'] == tsk[key]:
                        tbl += '<td class=\'td_cat\'>' + cat['name'] + '</td>\n'
        if key == 'url':
            url = str(tsk[key])
            tbl += '<td><a href=\'' + url + '\' target=\'_blank\'>' + url + '</a></td>\n'
    tbl += '</tr>\n'
    return tbl


def count(tsk, col, c, id_col):
    if tsk[col] == id_col:
        c.append(tsk['id'])
    return c


def message(c, out, m=''):
    link = 'http://kanboard.nordsy.spb.ru/project/16/task/'
    if len(c) > 0:
        m += '<p>' + out + ': ' + str(len(c)) + ' ['
        for item in c:
            m += ' <a href="' + link + str(item) + '" target="_blank">' + str(item) + '</a> '
        m += ']</p>'
    return m


if __name__ == '__main__':
    r = requests.get('http://172.16.2.106/jsonrpc.php')
    print(r)

    stamp = int(datetime.today().timestamp())
    #today = str(datetime.utcfromtimestamp(stamp).strftime('%Y-%m-%d'))
    today = '2019-02-08'

    kb = Kanboard(kanboardapipath, "jsonrpc", kanboardtoken)

    id = kb.getProjectByIdentifier(identifier="GLOBALSUPPORT")['id']

    categories = kb.getAllCategories(project_id=id)
    columns = kb.getColumns(project_id=id)
    tasks = kb.getAllTasks(project_id=id, status_id=1)

    html = '<!DOCTYPE html>\n<html>\n<head>'
    html += '<meta charset="windows-1251">\n'
    html += '<title>Сводка KanBoard</title>\n'
    html += '<link rel="stylesheet" href="style.css" />\n'
    html += '</head>\n<body>\n'
    table = '<table border="1" cellspacing="0">\n'
    table += '<thead>\n<tr>\n<th>#</th>\n<th>Тег</th>\n<th>Тема</th>\n<th class=\'th_col\'>Колонка</th>\n<th>Категория</th>\n<th>Ссылка</th>\n</tr>\n</thead>\n<tbody>\n'

    count_create = 0  # сегодня создано
    count_change = 0  # сегодня изменено
    c_new = []  # Новых
    c_watch = []  # На рассмотрении исполнителя
    c_wait = []  # Ожидает информации от заказчика
    c_reject = []  # Отклонено
    c_done = []  # Выполнено
    c_accept = []  # Принято

    for task in tasks:
        date = 'date_creation'
        description = 'description'
        column = 'column_id'

        if (date and description and column) in task:
            created_stamp = int(task[date])
            created = str(datetime.utcfromtimestamp(created_stamp).strftime('%Y-%m-%d'))
            changed = task[description]

            if created == today:
                count_create += 1
                table = row(task, table, categories, columns)

                c_new = count(task, column, c_new, 76)
                c_watch = count(task, column, c_watch, 77)
                c_wait = count(task, column, c_wait, 88)
                c_reject = count(task, column, c_reject, 78)
                c_done = count(task, column, c_done, 80)
                c_accept = count(task, column, c_accept, 89)

            if today in changed and created != today:
                count_change += 1
                table = row(task, table, categories, columns)

                c_new = count(task, column, c_new, 76)
                c_watch = count(task, column, c_watch, 77)
                c_wait = count(task, column, c_wait, 88)
                c_reject = count(task, column, c_reject, 78)
                c_done = count(task, column, c_done, 80)
                c_accept = count(task, column, c_accept, 89)

    table += '</tbody>\n</table>\n'

    if count_create > 0:
        msg = '<p>Обращений на ' + today + ' создано: ' + str(count_create) + '</p>\n'
        msg += '<p>Обращений на ' + today + ' изменено: ' + str(count_change) + '</p>\n'

        msg += message(c_new, 'Новых')
        msg += message(c_watch, 'На рассмотрении Исполнителя')
        msg += message(c_wait, 'Ожидает информации от Заказчика')
        msg += message(c_reject, 'Отклонено')
        msg += message(c_done, 'Выполнено')
        msg += message(c_accept, 'Принято Заказчиком')

        html += msg
        html += table
    else:
        msg = '<p>Обращений на сегодня нет</p>\n</body>\n</html>'
        html += msg
    html += '</body>\n</html>'

    with open('index.html', 'w') as outfile:
        outfile.write(html)
    outfile.close()
