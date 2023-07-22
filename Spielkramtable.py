
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
id  :int=0
typ :str='Brauchw'
tage:str='Mo'
von :str='12:00'
bis :str='12:01'
kesseltemp :int=10


# Definitionen der verschiedenen Tagesmöglichkeiten die man für die Einstellungen hat
tagefeld=['Mo','Die','Mi','Do','Fr','Sa','So','Mo-Fr','Sa-So']
# Definition der verschiedenen Heizungsmodi
typfeld = ['Brauchw', 'Heizen', 'Nachtabsenk.']



# Wird aufgerufen wenn man bei einer tabellenzeit die Checkbox markiert
def handle_click():
    # ui.notify(table.selected)
    # print(table.selected)
    if table.selected != []:
        global id, typ,tage,von,bis
        id =table.selected[0]['id']
        typ=table.selected[0]['typ']
        tage=table.selected[0]['tage']
        von=table.selected[0]['von']
        bis=table.selected[0]['bis']
        print(typ,tage,von, bis)


   
# löscht eine Tabellenzeile
def remove():
    # ui.notify(table.selected)
    if table.selected!=None:
        table.remove_rows(table.selected[0])


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
    # ui.notify(typ)

def settage(value):
    global tage
    tage=value
    # ui.notify(tage)

def setvon(value):
    erg=isTimeFormat(value)
    if erg == True:
        global von
        von=value
        # ui.notify(von)
        
    return(erg)

def setbis(value):
    erg=isTimeFormat(value)
    if erg == True:
        global bis
        bis=value
        # ui.notify(bis)
        vontemp=time.strptime(von, '%H:%M')
        bistemp=time.strptime(bis, '%H:%M')
        # der Beginn des Zeitintervalls sollte schon vor dem Ende liegen.
        if vontemp >= bistemp :
            erg=False     
    return(erg)





# def dialog für das hinzufügen von Werten
with ui.dialog() as tabledialogadd, ui.card().classes('top-8 left-8'):
    with ui.row():
        # schliesst den Dialog
        def close_add():
            global id, typ, tage, von, bis
            table.add_rows({'id': id, 'typ':typ, 'tage':tage, 'von':von, 'bis': bis})
            print('Neu Angelegt:',id,typ,tage,von,bis)
            id +=1
            tabledialogadd.close()
           

        print(typ,tage)
        ui.select(options=typfeld, label='Typ', with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
        ui.select(options=tagefeld, label='Tage', on_change=lambda e: settage(e.value)).classes('w-40')
        ui.input(label='Zeit von', value='12:00',placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
        ui.input(label='Zeit bis', value='12:05',placeholder='Zeit', validation={'Ungültig!! (Format oder Intervall)': lambda value: setbis(value)==True}).classes('w-30')
       
    ui.button('OK', on_click=close_add)


def updateeditdialog():

    with ui.dialog() as tabledialogedit, ui.card().classes('top-8 left-8'):
        with ui.row():
            # schliesst den Dialog
            def close_edit():
                print('zu speichern:',id, typ,tage,von,bis)
                rows[id]['typ']=typ
                rows[id]['tage']=tage
                rows[id]['von']=von
                rows[id]['bis']=bis
                tabledialogedit.close()
                table.update()
            
            ui.select(options=typfeld,label='Typ', value=typ, with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
            ui.select(options=tagefeld,label='Tage',value=tage ,on_change=lambda e: settage(e.value)).classes('w-40')
            ui.input(label='Zeit von', value=von, placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
            ui.input(label='Zeit bis', value=bis, placeholder='Zeit', validation={'Ungültig!! (Format oder Intervall)': lambda value: setbis(value)==True}).classes('w-30')
                   
        ui.button('OK', on_click=close_edit)  
    tabledialogedit.open()

def settemp(value):
    global kesseltemp
    kesseltemp=value
    ui.notify('Kesseltemp',kesseltemp)

# hier beginnt die Anzeige der Seite ------
# Zuerst 3 Knöpfe und dann die Tabelle
with ui.splitter(value=60).classes('w-full') as splitter:
    with splitter.before:
        ui.label('Zeitsteuerung').classes('font-bold').classes('text-xl').classes('my-3')
        with ui.row():
            ui.button('Neu', on_click=tabledialogadd.open).classes('mb-4 ml-8')
            ui.button('Ändern', on_click=updateeditdialog).classes('mb-4').classes('justify-normal')
            ui.button('Löschen', on_click=remove).classes('mr-2').classes('mb-4')
        table=ui.table(selection='single',columns=columns, 
                       rows=rows, row_key='id',on_select=handle_click).classes('mr-2')
    with splitter.after:
        
    # Nachtabsenkung Stop, Warmwasser Start, Warmwasser Stop
    # - max. Kesseltemperatur einstellen = Vorlauf Temperatur
    # - Sommer / Winterumschaltung per Temperatur und Anzeige Jahreszeit, 
    # ggf. noch eine Berücksichtigung der Jahreszeit für Sommer.-Winterumschaltung?
        ui.label('Steuerdaten').classes('font-bold').classes('text-xl').classes('my-3')
        an1=ui.toggle(['Sommer', 'Winter'], value='Sommer').classes('ml-2').classes('mb-4')
        an1.disable()
        an2=ui.toggle(['Tag', 'Nacht'], value='Tag').classes('ml-2').classes('mb-5')
        an2.disable()
        an3=ui.toggle(['Heizung', 'Warmwasser'], value='Heizung').classes('ml-2').classes('mb-5')
        an3.disable()
        ui.label('Kesseltemperatur [Grad C°]').classes('text-lg').classes('my-3 ml-2')
        ui.knob(value=10, min=0,max=90,step=1, show_value=True, track_color='grey-2',on_value_change=lambda e: settemp(e.value)) \
                .classes('ml-8').classes('mb-5 font-bold text-8xl')

ui.run()