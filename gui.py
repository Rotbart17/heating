#!/usr/bin/env python3

import plotly.graph_objects as go 
# import pandas as pd
from nicegui import ui, run,app
import time
from datetime import datetime
import settings
from dataview import maindata
from main import startbackend, stopbackend
import logging
import sys
from multiprocessing import Manager, Queue
import multiprocessing


# Muster für logging
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.critical('critical')

# nur die datav Klasse initialisieren wenn der Subprozess
# von nicegui gestratetwird damit die Prozesse nicht 2 Mal gestartet sind.

if __name__ in ['__mp_main__', '__main__']:
    global backendproc , queue_to_backend, queue_from_backend
    queue_to_backend = Queue()
    queue_from_backend = Queue()
    backendproc = multiprocessing.Process(target=startbackend, name="Backend-Prozess", args=(queue_to_backend, queue_from_backend)) 
    backendproc.start()
    # global datav
    time.sleep(40)
    datav=maindata()
   

# globale Variablen und Funktionen für die 3 Reiter "Einstellungen
# Spalten für die Tabelle der Heizungssteuerung: Typ (z.B. Brauchwasser), Tage, Zeit von, zeit bis

# rows = []  # leeres Feld für die Zeilen der Tabelle

@ui.refreshable
def update_table() ->None:
    global table, columns, rows
    columns = [
        {'name': 'id',        'label': 'ID' ,       'field': 'line_id'   , 'required': True, 'sortable': True,'align': 'left'},
        {'name': 'typ',       'label': 'Typ',       'field': 'type'      , 'required': True},
        {'name': 'tage',      'label': 'Tage',      'field': 'tage'      , 'required': True},
        {'name': 'zeitvon',   'label': 'Zeit von',  'field': 'von'       , 'required': True},
        {'name': 'zeitbis',   'label': 'Zeit bis',  'field': 'bis'       , 'required': True},
        {'name': 'active',    'label': 'Aktiv'   ,  'field': 'active'    , 'required': True},
        {'name': 'changetime','label': 'Changetime','field': 'changetime', 'required': True, 'classes': 'hidden','headerClasses': 'hidden'}  
    ]
    
    #title='Steuerdaten'
    rows= [{'line_id': item[0], 'type':item[1], 'tage':item[2], 'von':item[3], 'bis': item[4], 'active':item[5], 'changetime':item[6]} for item in datav.vZeitsteuerung]
    table=ui.table(selection='single',columns=columns, rows=rows, row_key='line_id',on_select=handle_click).classes('w-11/12 mr-4').props('hide-no-data')

# Zeilennummer in der Tabelle
if len(datav.Zeitsteuerungszeilen)> 0:
    id = len (datav.Zeitsteuerungszeilen)
else:
    id=0
# Welche Zeile in der Tabelle wird bearbeitet
handle_id: int=0 
# welcher Heiztyp
heiztype :int=0
# wann wird der Heiztyp verwendet
tage:int=0
# Zeitperiode für den Heiztyp
von:str='12:00'
bis:str='12:01'



# Definitionen der verschiedenen Tagesmöglichkeiten die man für die Einstellungen hat
tagedict={   1:'Mo', 2:'Die', 3:'Mi', 4:'Do', 5:'Fr', 6:'Sa',  7:'So', 8:'Mo-Fr', 9:'Sa-So', 10:'Mo-So'}
tage_r_dict={'Mo':1, 'Die':2, 'Mi':3, 'Do':4, 'Fr':5 , 'Sa':6, 'So':7, 'Mo-Fr':8, 'Sa-So':9,'Mo-So':10}


# Definition der verschiedenen Heizungsmodi
typdict = {1:'Brauchw', 2:'Heizen', 3:'Nachtabsenk.'}
typ_r_dict = {'Brauchw':1, 'Heizen':2, 'Nachtabsenk.':3}


# Initialisieren von Daten für die GUI. ggf. noch nicht der Weisheit letzter Schluss
def init_data():
    pass
   # global backendproc
   # backendproc = multiprocessing.Process(target=startbackend, name="Backend-Prozess", args=(queue_to_backend, queue_from_backend)) 
   # backendproc.start()



# ich weiß noch nicht ob man das hier braucht. Aber die Hülle ist schon mal da.
def de_init_data():
    stopbackend(True)
    datav.threadstop=True
    backendproc.join()
    # del datav

    
# Irgendwie durchläuft nicegui das Programm mehrfach.
            
app.on_startup(lambda: init_data())
app.on_shutdown(lambda: de_init_data())


#---------------------------------------------------------------------------------------------------------
# Kopfzeile ----------------------------------
with ui.header().classes(replace='row items-center') as header:
    
    with ui.tabs() as tabs:     
        information=ui.tab('Information')
        heizbetrieb=ui.tab('Heizbetrieb')
        kesselsteuerung=ui.tab('Kesselsteuerung')
        einstellungen=ui.tab('Einstellungen')
    label = ui.label().classes('ml-44')
    ui.timer(60.0, lambda: label.set_text(f'{datetime.now():%H:%M}'))  

#---------------------------------------------------------------------------------------------------------
# Fusszeile ----------------------------------
with ui.footer(value=True).classes('height-hint=30') as footer:
    ui.label('Buderus Ecomatic Digital V1.0.0')


# Hand Dusche toggeln
def set_hand_dusche():
    if datav.vHand_Dusche==False:
        datav.vHand_Dusche=True
        ui.notify('Brauchwasser eingeschaltet!')
    else:
        datav.vHand_Dusche=False
        ui.notify('Brauchwasser ausgeschaltet!')

#---------------------------------------------------------------------------------------------------------
# hier werden 4 TABs definiert (Information  / Heizbetrieb / Kesselsteuerung / Einstellungen)
with ui.tab_panels(tabs, value=information).classes('w-full'):
   

    #---------------------------------------------------------------------------------------------------------   
    # Erster Reiter ------------------
    with ui.tab_panel(information):
        with ui.grid(columns=4, rows=1).classes('w-full'):
            # Zeile 1
            ui.label().bind_text_from(datav, 'vAussen', lambda v: f'Aussen-Temp = {v}').classes('text-base col-start-1')
            ui.label().bind_text_from(datav, 'vWinter', lambda v: 'Winterbetrieb' if v else 'Sommerbetrieb').classes('text-base col-start-2 ')
            ui.label().bind_text_from(datav, 'vInnen', lambda v: f'Innen-Temp = {v}').classes('text-base col-start-3')
            ui.button('Hand-Dusche', color='#1e5569', on_click=lambda: set_hand_dusche()).classes('col-start-4 w-25 h-25')

        # Zeile 2
        with ui.grid(columns=4, rows=1).classes('w-full'):    
            figtemp = go.Figure()
            figtemp.add_trace(go.Scatter(x=datav.vAussenDaten_x, y=datav.vAussenDaten_y, name='Aussen-T'))
            figtemp.add_trace(go.Scatter(x=datav.vInnenDaten_x, y=datav.vInnenDaten_y, name='Innen-T'))
            figtemp.add_trace(go.Scatter(x=datav.vKesselIstDaten_x, y=datav.vKesselIstDaten_y, name='Kessel-T'))
            figtemp.add_trace(go.Scatter(x=datav.vBrauchwasserDaten_x, y=datav.vBrauchwasserDaten_y, name='Brauchw-T'))
            figtemp.update_layout(margin=dict(l=35, r=20, t=20, b=40), plot_bgcolor='#E5ECF6',
                                      xaxis=dict(title='Datum Uhrzeit', gridcolor='white'),
                                      yaxis=dict(title='Temperatur', gridcolor='white'))
            # Wir übergeben das Figure-Objekt an das UI-Element, behalten aber eine Referenz darauf.
            plottemp = ui.plotly(figtemp).classes('w-full h-40 col-start-1 col-span-4')

            def updatesensordata():
                # Wir operieren direkt auf unserem 'figtemp'-Objekt.
                # Der Linter weiß, dass 'figtemp' ein go.Figure ist und kennt dessen Methoden.
                with figtemp.batch_update():
                    figtemp.update_traces(x=datav.vAussenDaten_x, y=datav.vAussenDaten_y, selector={'name': 'Aussen-T'})
                    figtemp.update_traces(x=datav.vInnenDaten_x, y=datav.vInnenDaten_y, selector={'name': 'Innen-T'})
                    figtemp.update_traces(x=datav.vKesselIstDaten_x, y=datav.vKesselIstDaten_y, selector={'name': 'Kessel-T'})
                    figtemp.update_traces(x=datav.vBrauchwasserDaten_x, y=datav.vBrauchwasserDaten_y, selector={'name': 'Brauchw-T'})
                
                # Nachdem wir das Datenmodell (figtemp) geändert haben,
                # teilen wir dem UI-Element mit, dass es sich neu zeichnen soll.
                plottemp.update()

            # Die Sensordaten in datav werden alle 60s aktualisiert. Wir passen den Timer an.
            ui.timer(60.0, updatesensordata)

        # Zeile 3
        with ui.grid(columns=4, rows=2).classes('w-full'):
            ui.label().bind_text_from(datav, 'vKesselSoll', lambda v: f'Kessel-Soll-Temp = {v}').classes('text-base col-start-1  flex items-center')
            ui.label().bind_text_from(datav, 'vKessel', lambda v: f'Kessel-Temp = {v}').classes('text-base flex items-center')
            ui.label().bind_text_from(datav, 'vBrauchwasser', lambda v: f'Brauchw-Temp = {v}').classes('text-base col-start-3 flex items-center')
            ui.label('Brauchw-Pumpe').classes('text-base col-start-4 flex items-center')
            ui.spinner('facebook', size='sm').bind_visibility_from(datav, 'vPumpe_Brauchwasser_an').classes('mt-3')
        # Zeile 4
            ui.label('Brenner läuft').classes('text-base col-start-1 h-9')
            ui.spinner(type='ball', color='red', size='sm').bind_visibility_from(datav, 'vBrenner_an').classes('h-9')
            ui.label('Brennerstörung').classes('text-base col-start-2 h-9')
            ui.spinner(size='sm', color='red').bind_visibility_from(datav, 'vBrenner_Stoerung').classes('h-9')
            ui.label('H-Pumpe oben').classes('text-base col-start-3 h-9')
            ui.spinner('facebook', size='sm').bind_visibility_from(datav, 'vPumpe_oben_an').classes('h-9')
            ui.label('H-Pumpe unten').classes('text-base col-start-4  h-9')
            ui.spinner('facebook', size='sm').bind_visibility_from(datav, 'vPumpe_unten_an').classes('h-9')

    #---------------------------------------------------------------------------------------------------------      
    # Zweiter Reiter ------------------
    with ui.tab_panel(heizbetrieb):
        '''
        - Zeit(en) für Brauchwasser festlegen / Anzeigen für Wochentag und Zeit
        - Zeit(en) für Heizbetrieb festlegen  / anzeigen für Wochentag und Zeit
        - Zeit(en) für Nachtabsenkung festlegen / anzeigen für Wochentag und Zeit
            Einstellen mit:
                Dropdown: Mo-Fr, Mo, Die, Mi, Do, Fr, Sa, So, Sa+So, 
                Feld: Uhrzeit von
                Feld: Uhrzeit bis
                Eigenschaft: Heizen Start, Heizen Stop, Nachtabsenkung Start, Nachtabsenkung Stop, Warmwasser Start, Warmwasser Stop

            - max. Kesseltemperatur einstellen = Vorlauf Temperatur
            - Sommer / Winterumschaltung per Temperatur und Anzeige Jahreszeit, ggf. noch eine Berücksichtigung der Jahreszeit für Sommer.-Winterumschaltung?
        '''
        # Wird aufgerufen wenn man bei einer Tabellenzeile die Checkbox markiert
        # dann werden mal alle Werte der Tabelle in die globalen Variablen befördert.
        def handle_click():
            # ui.notify(table.selected)
            if table.selected != []:
                global id, heiztype,tage,von,bis,handle_id
                # print("Handle Click:",table.selected)
                handle_id =table.selected[0]['line_id']
                typval=table.selected[0]['type']
                heiztype=typ_r_dict[typval]
                tageval=table.selected[0]['tage']
                tage=tage_r_dict[tageval]
                von=table.selected[0]['von']
                bis=table.selected[0]['bis']
                print("global gesetzt handle_id:",handle_id,"typ:",typval,"tage:",tage,von, bis)
            
                                
        # löscht eine markierte Tabellenzeile
        def remove():
            # ui.notify(table.selected)
            if table.selected!=[]:
                table.remove_row(table.selected[0])
                rows.sort(key=lambda x: x['line_id'])
                datav.vZeitsteuerung=rows
            

        # Prüft ob es eine gültige Zeit ist
        def isTimeFormat(input):
            try:
                time.strptime(input, '%H:%M')
                return True
            except ValueError:
                return False

        # setzt den Typ    
        def settyp(value):
            global heiztype
            heiztype=value
            # ui.notify(typ)

        # Setzt die Tage
        def settage(value):
            global tage
            tage=value
            # ui.notify(tage)    

        # Setzt den Beginn einer Aufgabe
        def setvon(value):
            global von
            von=value
            # ui.notify(von)
            return(True)

        # setzt  das Ende einer Aufgabe
        def setbis(value):
            global bis
            bis=value
            # ui.notify(bis)   
            return(True)
        

        # Definition des Dialog für das Hinzufügen von Werten
        with ui.dialog() as tabledialogadd, ui.card().classes('top-8 left-8'):
            with ui.grid(columns=3, rows=3):
                # schliesst den Dialog
                def close_add():
                    global id, heiztype, tage, von, bis,rows
                    id +=1
                    # print('Anzulegen:',line_id,heiztype,tage,von,bis)
                    if heiztype != 0 and tage !=0:
                        table.add_row({'line_id': id, 'type':typdict[heiztype], 'tage':tagedict[tage], 'von':von, 'bis': bis})
                        # print('Neu Angelegt:',line_id,heiztype,tage,von,bis)
                        rows.sort(key=lambda x: x['line_id'])
                        datav.vZeitsteuerung=rows
                        tabledialogadd.close()
                
                s1=ui.select(options=typdict, label='Typ',   with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
                s2=ui.select(options=tagedict, label='Tage', with_input=True, on_change=lambda e: settage(e.value)).classes('w-40')
                ui.label(' ')
                s3=ui.input(label='Zeit von', value='12:00',placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
                # Eingabe von zeitvon
                with ui.dialog().props('no-parent-event') as menuvon:
                    ui.time().bind_value_to(s3)
                ui.icon('watch_later').on('click', menuvon.open).classes('cursor-pointer').classes('text-4xl')
                ui.label(' ')
                
                # Eingabe von zeitbis
                s4=ui.input(label='Zeit bis', value='12:01',placeholder='Zeit', validation={'Ungültig!! (Format)': lambda value: setbis(value)==True}).classes('w-30')
                with ui.dialog().props('no-parent-event') as menubis:
                    ui.time().bind_value_to(s4)
                ui.icon('watch_later').on('click', menubis.open).classes('cursor-pointer').classes('text-4xl')
                
                ui.button('OK', on_click=close_add).classes('w-20')

        # Daten für den Anzeigedialog updaten
        def updateeditdialog():
            # print("vor dem Edit Dialog:",handle_id,heiztype,tage,von,bis)
            global s3
            if handle_id !=0:
                s1.value=heiztype
                s2.value=tage
                s3.value=von
                s4.value=bis
                tabledialogedit.open()
        
        
        # macht eine Tabellenzeile editierbar
        with ui.dialog() as tabledialogedit, ui.card().classes('top-8 left-8'):
            with ui.grid(columns=3, rows=3):

                # schliesst den Dialog
                def close_edit():
                    # print("Nach Edit",handle_id, heiztype,tage,von,bis)               
                    if table.selected != []:
                        if heiztype != 0 and tage !=0:
                            # aktuelle zeile entfernen
                            table.remove_row(table.selected[0])
                            # neue Zeile Hinzufügen
                            table.add_row({'line_id': handle_id, 'type':typdict[heiztype], 'tage':tagedict[tage], 'von':von, 'bis': bis})
                            table.update()
                            # print('Edit Neu Angelegt:',handle_id,heiztype,tage,von,bis)
                            rows.sort(key=lambda x: x['line_id'])
                            datav.vZeitsteuerung=rows                   
                    # handle_id=0
                    tabledialogedit.close()             
                
                s1=ui.select(options=typdict, label='Typ',   with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
                s2=ui.select(options=tagedict,label='Tage',  with_input=True, on_change=lambda e: settage(e.value)).classes('w-40')
                ui.label(' ')
                s3=ui.input(label='Zeit von',  value='12:00',placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
                # Eingabe von zeitvon
                with ui.dialog().props('no-parent-event') as menuvon:
                    ui.time().bind_value_to(s3)
                ui.icon('watch_later').on('click', menuvon.open).classes('cursor-pointer').classes('text-4xl')
                ui.label(' ')
                
                # Eingabe von zeitbis
                s4=ui.input(label='Zeit bis',  value='12:01',placeholder='Zeit', validation={'Ungültig!! (Format)': lambda value: setbis(value)==True}).classes('w-30')              
                with ui.dialog().props('no-parent-event') as menubis:
                    ui.time().bind_value_to(s4)
                ui.icon('watch_later').on('click', menubis.open).classes('cursor-pointer').classes('text-4xl')
                
                ui.button('OK', on_click=close_edit).classes('w-20')
        

        # hier beginnt die Anzeige der linken Seite des Reiters -----------
        # Zuerst 3 Knöpfe in einer Zeile und dann die Tabelle
        with ui.row(wrap=False):
            # ui.label('Steuerdaten:').classes('text-base').classes('mt-4')
            ui.button('Neu', on_click=tabledialogadd.open).classes('ml-4')
            ui.button('Ändern', on_click=updateeditdialog).classes('ml-8')
            ui.button('Löschen', on_click=remove).classes('ml-8')

        # Das malt dann die Tabelle unter die Knöpfe    
        update_table()

        
            
    #---------------------------------------------------------------------------------------------------------            
    # Dritter Reiter -----------------------------------------------            
    with ui.tab_panel(kesselsteuerung):
        # Die Kessel-Grafik wird modern und robust mit plotly.graph_objects erstellt.
        figkessel = go.Figure(go.Scatter(
            x=datav.vKesselDaten_x,
            y=datav.vKesselDaten_y,
            name='Kessel',
        ))
        figkessel.update_layout(
            margin={'l': 35, 'r': 20, 't': 20, 'b': 35},
            plot_bgcolor='#E5ECF6',
            xaxis={'title': 'Aussentemp', 'gridcolor': 'white'},
            yaxis={'title': 'Kesseltemp', 'gridcolor': 'white'},
        )
        # Wir machen die Grafik editierbar und fügen einen Event-Handler für 'relayout' hinzu.
        plotkessel = ui.plotly(figkessel, config={'editable': True}).classes('w-full h-64')  # type: ignore

        def handle_curve_drag(e):
            """Wird aufgerufen, wenn der Benutzer einen Punkt auf der Kennlinie verschiebt."""
            event_data = e.args
            # Plotly sendet bei einer Punkt-Verschiebung ein Event mit diesem spezifischen Schlüssel.
            # Wir prüfen, ob dieser Schlüssel vorhanden ist, um nur auf diese Aktion zu reagieren.
            if event_data and 'update_sources[0]' in event_data:
                update_info = event_data['update_sources[0]']
                if 'point_index' in update_info and 'y' in update_info:
                    point_index = update_info['point_index'][0]
                    new_y_value = round(update_info['y'][0], 1)  # Runden auf eine Nachkommastelle

                    # Eine Kopie der y-Werte erstellen, um sie sicher zu ändern.
                    templist = datav.vKesselDaten_y.copy()

                    # Nur speichern, wenn sich der Wert tatsächlich geändert hat.
                    if templist[point_index] != new_y_value:
                        templist[point_index] = new_y_value

                        # Die neuen Daten im Datenmodell speichern (dies löst die Speicherung in der DB aus).
                        datav.vKesselDaten_y = templist

                        # Den Benutzer über die erfolgreiche Speicherung informieren.
                        x_val = datav.vKesselDaten_x[point_index]
                        ui.notify(f"Punkt bei {x_val}°C auf {new_y_value}°C gesetzt und gespeichert.")

        # Den Event-Handler an das Plot-Element binden.
        plotkessel.on('relayout', handle_curve_drag)

        # Die numerischen Eingabefelder sind nicht mehr notwendig, da die Interaktion direkt über die Grafik erfolgt.
        # with ui.grid(columns=4, rows=1).classes('w-full'):
        #     ... (alter Code für die Eingabefelder)


    #---------------------------------------------------------------------------------------------------------   
    # Vierter  Reiter ------------------

    
    with ui.tab_panel(einstellungen):
        with ui.grid(rows=4,columns=4):    
            
            # hier brauchen wir nun Sommer Winterumschaltung Temp
            def setwinter(value):
                datav.vWintertemp=value
                ui.notify('Winter ab: '+str(datav.vWintertemp))


            ui.number(label='Winter ab:', suffix='Grad',min=10.0, max=25.0,  precision=2, value=datav.vWintertemp, \
                on_change=lambda e: setwinter(e.value)).classes('flex-1 w-32')
            
            # Knopf zum Ausschalten
            ui.button('Programm Stop', color='#1e5569', on_click=lambda: de_init_data()).classes('col-start-4 w-25 h-25')
            # offene Themen:
            # Schalter Brauchwasser vollstandig ausschalten!
            # ggf die Gleichung füe die Kesselkurve eingeben

# -------------------------------------------------------------------------------------------------
# Start der GUI



# ui.run(favicon='🚀',port=8000, title='Buderus Ecomatic',window_size=(800,480))
ui.run(favicon='🚀',port=8000,title='Buderus Ecomatic', dark= True, reload= False)
