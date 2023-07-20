
#!/usr/bin/env python3

import os
import random
from   nicegui import ui
import time


columns = [
    {'name': 'id',       'label' :'ID' ,      'field' : 'id', 'required': True, 'align': 'left'},
    {'name': 'typ',      'label': 'Typ',      'field': 'typ', 'required': True},
    {'name': 'tage',     'label': 'Tage',     'field': 'tage', 'required': True},
    {'name': 'zeitvon',  'label': 'Zeit von', 'field': 'von', 'required': True},
    {'name': 'zeitbis',  'label': 'Zeit bis', 'field': 'bis', 'required': True},
]

rows = []
id : int=0
typ :int=0
tage:int=0
von:str='12:00'
bis:str='12:00'


tagesdefinition ={1:'Mo',2:'Die',3:'Mi',4:'Do',5:'Fr',6:'Sa',7:'So',8:'Mo-Fr',9:'Sa-So'}
typen = {1: 'Brauchw', 2: 'Heizen', 3: 'Nachtabsenk.'}


def handle_click():
    ui.notify(table.selected)

    # table.remove_rows(table.selected)

def remove():
    ui.notify(table.selected)
    if table.selected!=None:
        table.remove_rows(table.selected[0])

   


# def dialog für das hinzufügen von Werten
with ui.dialog() as tabledialog, ui.card().classes('top-8 left-8'):
    with ui.row():
        
        #Prüft ob es eine Gültige Zeit ist
        def isTimeFormat(input):
            try:
                time.strptime(input, '%H:%M')
                return True
            except ValueError:
                return False
            
        def settyp(value):
            global typ
            typ=value
            ui.notify(typen[typ])

        def settage(value):
            global tage
            tage=value
            ui.notify(tagesdefinition[tage])

        def setvon(value):
            erg=isTimeFormat(value)
            if erg == True:
                global von
                von=value
                ui.notify(von)
            return(erg)

        def setbis(value):
            erg=isTimeFormat(value)
            if erg == True:
                global bis
                bis=value
                ui.notify(bis)     
            return(erg)
        
        def close():
            global id, typ,tage,von,bis
            table.add_rows({'id': id, 'typ':typen[typ], 'tage':tagesdefinition[tage], 'von':von, 'bis': bis})
            id +=1
            tabledialog.close()
            
        ui.select(options=typen,label='Typ',with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
        ui.select(options=tagesdefinition,label='Tage', on_change=lambda e: settage(e.value)).classes('w-40')
        ui.input(label='Zeit', value='12:00',placeholder='Zeit von', validation={'Zeitformat!!': lambda value: setvon(value)==True}).classes('w-30')
        ui.input(label='Zeit', value='12:00',placeholder='Zeit bis', validation={'Zeitformat!!': lambda value: setbis(value)==True}).classes('w-30')
        
        
    ui.button('OK', on_click=close)
    
  


with ui.row():
    ui.button('remove', on_click=remove)
    ui.button('add', on_click=tabledialog.open)

table=ui.table(title='Steuerdaten',selection='single',columns=columns, rows=rows, row_key='id',on_select=handle_click).classes('w-70')



ui.run()