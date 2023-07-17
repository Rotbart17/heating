
#!/usr/bin/env python3

import os
import random
from nicegui import ui


id=3
columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
    {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
]
rows = [
    {'id': 1, 'name': 'Alice', 'age': 18},
    {'id': 2, 'name': 'Bob', 'age': 21},
    {'id': 3 ,'name': 'Carol'},
]
# ui.table(columns=columns, rows=rows, row_key='name')

def handle_click():
    ui.notify(table.selected)

    # table.remove_rows(table.selected)

def remove():
    ui.notify(table.selected)
    table.remove_rows(table.selected[0])


def add():
    item = os.urandom(10 // 2).hex()
    global id
    id +=1
    table.add_rows({'id': id, 'name': item, 'age': random.randint(0, 100)})


ui.button('remove', on_click=remove)
ui.button('add', on_click=add)

table=ui.table(title='NASE',selection='single',columns=columns, rows=rows, row_key='id',on_select=handle_click)


ui.run()