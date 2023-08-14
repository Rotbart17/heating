#!/usr/bin/env python3

from nicegui import ui

rows = []  # leeres Feld für die Zeilen der Tabelle
id=0
handle_id=0

def handle_click():
    global handle_id
    handle_id =table.selected[0]['id']
    ui.notify(table.selected)
    
                    


@ui.refreshable
def update_table() ->None:
    global table, columns, rows
    columns = [
        {'name': 'id',       'label' :'ID' ,      'field': 'id',  'required': True, 'sortable': True,'align': 'left'},
        {'name': 'typ',      'label': 'Typ',      'field': 'typ', 'required': True},
    ]
    table=ui.table(selection='single',columns=columns, rows=rows, row_key='id',on_select=handle_click).props('hide-no-data')

def add_row():
    global id
    table.add_rows({'id': id, 'typ':'Content'})
    id+=1

def replace_row():
    global handle_id
    table.add_rows({'id': handle_id, 'typ':'Content'})


def remove_row():
    if table.selected!=None:
        table.remove_rows(table.selected[0])

update_table()
ui.button('Add', on_click=add_row)
ui.button('Remove', on_click=remove_row)
ui.button('Replace', on_click=replace_row)

ui.run()


