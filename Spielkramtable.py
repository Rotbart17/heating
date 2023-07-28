
#!/usr/bin/env python3

import os
from   nicegui import ui
import time



# globale Variablen für dieses Modul
# Spalten für die Tabelle der Heizungssteuerung: Typ (z.B. Brauchwasser), Tage, Zeit von, zeit bis
columns = [
    {'name': 'id',       'label' :'ID' ,      'field' : 'id', 'required': True, 'align': 'left'},
    {'name': 'typ',      'label': 'Typ',      'field': 'typ', 'required': True},
    {'name': 'tage',     'label': 'Tage',     'field': 'tage', 'required': True},
    {'name': 'zeitvon',  'label': 'Zeit von', 'field': 'von', 'required': True},
    {'name': 'zeitbis',  'label': 'Zeit bis', 'field': 'bis', 'required': True},
]

# ts={}
rows = []  # leeres Feld für die Zeilen der Tabelle
id : int=0
typ :int=0
tage:int=0
von:str='12:00'
bis:str='12:01'


# Definitionen der verschiedenen Tagesmöglichkeiten die man für die Einstellungen hat
tagesdefinition ={1:'Mo',2:'Die',3:'Mi',4:'Do',5:'Fr',6:'Sa',7:'So',8:'Mo-Fr',9:'Sa-So'}
# Definition der verschiedenen Heizungsmodi
typen = {1: 'Brauchw', 2: 'Heizen', 3: 'Nachtabsenk.'}



# Wird aufgerufen wenn man bei einer Zabellenzeile die Checkbox markiert
# dann werden mal ale Werte der tabelle in die globale Variable befördert.
def handle_click():
    ui.notify(table.selected)
    
    if table.selected != []:
        global id, typ,tage,von,bis
        typ=table.selected[0]['typ']
        tage=table.selected[0]['tage']
        von=table.selected[0]['von']
        bis=table.selected[0]['bis']
        print(typ,tage,von, bis)

   
# löscht eine markierte Tabellenzeile
def remove():
    ui.notify(table.selected)
    if table.selected!=None:
        table.remove_rows(table.selected[0])

# Prüft ob es eine gültige Zeit ist
def isTimeFormat(input):
    try:
        time.strptime(input, '%H:%M')
        return True
    except ValueError:
        return False

# setzt den Typ    
def settyp(value):
    global typ
    typ=value
    ui.notify(typen[typ])

# Setzt die Tage
def settage(value):
    global tage
    tage=value
    ui.notify(tagesdefinition[tage])

# Setzt den Beginn einer Aufgabe
def setvon(value):
    erg=isTimeFormat(value)
    if erg == True:
        global von
        von=value
        ui.notify(von)
    return(erg)

# setzt  das Ende einer Aufgabe
def setbis(value):
    erg=isTimeFormat(value)
    if erg == True:
        global bis
        bis=value
        ui.notify(bis)
        vontemp=time.strptime(von, '%H:%M')
        bistemp=time.strptime(bis, '%H:%M')
        # der Beginn des Zeitintervalls sollte schon vor dem Ende liegen.
        if vontemp >= bistemp :
            erg=False     
    return(erg)

# Definition des Dialog für das Hinzufügen von Werten
with ui.dialog() as tabledialogadd, ui.card().classes('top-8 left-8'):
    with ui.row():
        # schliesst den Dialog
        def close_add():
            global id, typ, tage, von, bis
            table.add_rows({'id': id, 'typ':typen[typ], 'tage':tagesdefinition[tage], 'von':von, 'bis': bis})
            id +=1
            tabledialogadd.close()
        print(typ,tage)
        ui.select(options=typen, label='Typ', with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
        ui.select(options=tagesdefinition, label='Tage', on_change=lambda e: settage(e.value)).classes('w-40')
        ui.input(label='Zeit von', value='12:00',placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
        ui.input(label='Zeit bis', value='12:05',placeholder='Zeit', validation={'Ungültig!! (Format oder Intervall)': lambda value: setbis(value)==True}).classes('w-30')
    ui.button('OK', on_click=close_add)

# Daten für den Anzeigedialog updaten
def updateeditdialog():
    s1.update()
    s2.update()
    s3.update()
    s4.update()
    tabledialogedit.open()



# macht eine Tabellenzeile Editierbar
with ui.dialog() as tabledialogedit, ui.card().classes('top-8 left-8'):
    with ui.row():
        # schliesst den Dialog
        def close_edit():
            print(typ,tage,von,bis)
            tabledialogedit.close()
        
        s1=ui.select(options=typen,label='Typ', value=typ, with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
        s2=ui.select(options=tagesdefinition,label='Tage',value=tage ,on_change=lambda e: settage(e.value)).classes('w-40')
        s3=ui.input(label='Zeit von', value=von, placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
        s4=ui.input(label='Zeit bis', value=bis, placeholder='Zeit', validation={'Ungültig!! (Format oder Intervall)': lambda value: setbis(value)==True}).classes('w-30')
                   
    ui.button('OK', on_click=close_edit)  

# hier beginnt die Anzeige der Seite ------
# Zuerst 3 Knöpfe in einer Zeile und dann die Tabelle
with ui.row():
    ui.button('Neu', on_click=tabledialogadd.open)
    ui.button('Ändern', on_click=updateeditdialog)
    ui.button('Löschen', on_click=remove)

table=ui.table(title='Steuerdaten',selection='single',columns=columns, rows=rows, row_key='id',on_select=handle_click).classes('w-70')


ui.run()