#!/usr/bin/env python3

import plotly.graph_objects as go
# import pandas as pd
from nicegui import ui, app
import time
from datetime import datetime
import settings
from dataview import datav as datav
import logging


# Muster für logging
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.critical('critical')


# globale Variablen und Funktionen für die 3 Reiter "Einstellungen
# Spalten für die Tabelle der Heizungssteuerung: Typ (z.B. Brauchwasser), Tage, Zeit von, zeit bis

rows = []  # leeres Feld für die Zeilen der Tabelle

@ui.refreshable
def update_table() ->None:
    global table, columns, rows
    columns = [
        {'name': 'id',       'label': 'ID' ,      'field': 'id'  , 'required': True, 'sortable': True,'align': 'left'},
        {'name': 'typ',      'label': 'Typ',      'field': 'typ' , 'required': True},
        {'name': 'tage',     'label': 'Tage',     'field': 'tage', 'required': True},
        {'name': 'zeitvon',  'label': 'Zeit von', 'field': 'von' , 'required': True},
        {'name': 'zeitbis',  'label': 'Zeit bis', 'field': 'bis' , 'required': True},
    ]
    rows
    #title='Steuerdaten'
    table=ui.table(selection='single',columns=columns, rows=rows, row_key='id',on_select=handle_click).classes('w-11/12 mr-4').props('hide-no-data')

# Zeilennummer in der Tabelle
id : int=0
# Welche Zeile in der Tabelle wird bearbeitet
handle_id: int=0 
# welcher Heiztyp
typ :int=0
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


# Kesseldatenanpassungsvariablen
# Grad von, Grad bis, Gradanpassung
gradv : float= 0
gradb : float= 0
gradanpass : float= 0

# Initialisieren von Daten für die GUI. ggf. noch nicht der Weisheit letzter Schluss
def init_gui_data():
   
   logging.basicConfig(
       filename='gui.log',
       filemode='w',
       format='%(asctime)s %(levelname)s: %(message)s',
       level=logging.INFO
       )


# ich weiß noch nicht ob man das hier braucht. Aber die Hülle ist schon mal da.
def de_init_gui_data():
    del datav

    
# Irgendwie durchlaüft nicegui das Programm mehrfach daher geht das hier nicht.
            
app.on_startup(lambda: init_gui_data())
app.on_shutdown(lambda: de_init_gui_data())




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


# Alle Sensordaten für die Grafik auf im ersten Reiter updaten
# Messwertreihen zuweisen
def updatesensordata():
    figtemp['data'][0]['x']=datav.vAussenDaten_x
    figtemp['data'][0]['y']=datav.vAussenDaten_y
    figtemp['data'][1]['x']=datav.vInnenDaten_x
    figtemp['data'][1]['y']=datav.vInnenDaten_y
    figtemp['data'][2]['x']=datav.vKesselIstDaten_x
    figtemp['data'][2]['y']=datav.vKesselIstDaten_y
    figtemp['data'][3]['x']=datav.vBrauchwasserDaten_x
    figtemp['data'][3]['y']=datav.vBrauchwasserDaten_y
    ui.update(plottemp)


# ------------------
# Grafiken anzeigen
def malen() -> None:

    global figtemp
    figtemp = {
        'data': 
        [
            {
                'type': 'scatter',
                'name': 'Aussen-T',
                'x': datav.vAussenDaten_x,
                'y': datav.vAussenDaten_y,
            },
            {
                'type': 'scatter',
                'name': 'Innen-T',
                'x': datav.vInnenDaten_x,
                'y': datav.vInnenDaten_y,
            },
            {
                'type': 'scatter',
                'name': 'Kessel-T',
                'x': datav.vKesselIstDaten_x,
                'y': datav.vKesselIstDaten_y,
            },
            {
                'type': 'scatter',
                'name': 'Brauchw-T',
                'x': datav.vBrauchwasserDaten_x,
                'y': datav.vBrauchwasserDaten_y,
            },          
        ],
        'layout': 
        {
            'margin': {'l': 35, 'r': 20, 't': 20, 'b': 40},
            'plot_bgcolor': '#E5ECF6',
            'xaxis': {'title': 'Datum Uhrzeit','gridcolor': 'white'},
            'yaxis': {'title': 'Temperatur','gridcolor': 'white'},
        },
    }
    global plottemp
    plottemp= ui.plotly(figtemp).classes('w-full h-40 col-start-1 col-span-4') 
    ui.update(plottemp)


# Hand Dusche toggeln
def set_hand_dusche():
    if datav.vHand_Dusche==False:
        datav.vHand_Dusche=True
        ui.notify('Brauchwasser eingeschaltet!')
    else:
        datav.vHand_Dusche=False
        ui.notify('Brauchwasser ausgeschaltet!')
       
# Alle 2 Minuten das Upate der Daten für die Grafik aufrufen
ui.timer(120.0, lambda: updatesensordata()) 

#---------------------------------------------------------------------------------------------------------
# hier werden 4 TABs definiert (Information  / Heizbetrieb / Kesselsteuerung / Einstellungen)
with ui.tab_panels(tabs, value=information).classes('w-full'):
   

    #---------------------------------------------------------------------------------------------------------   
    # Erster Reiter ------------------
    with ui.tab_panel(information):
        with ui.grid(columns=4, rows=1).classes('w-full'):
        # Zeile 1      
            ui.label(f'Aussen-Temp = {datav.vAussen}').classes('text-base col-start-1')
            if datav.vWinter==True:
                t='Winterbetrieb'
            else:
                t='Sommerbetrieb'
            ui.label(f'{t}').classes('text-base col-start-2 ')
            ui.label(f'Innen-Temp = {datav.vInnen}').classes('text-base col-start-3')   
            ui.button('Hand-Dusche', color='#1e5569', on_click=lambda: set_hand_dusche()).classes('col-start-4 w-25 h-25')

        # Zeile 2
        with ui.grid(columns=4, rows=1).classes('w-full'):    
            malen()

        # Zeile 3
        with ui.grid(columns=4, rows=2).classes('w-full'):      
            ui.label(f'Kessel-Soll-Temp = {datav.vKesselSoll}').classes('text-base col-start-1  flex items-center')  
            ui.label(f'Kessel-Temp = {datav.vKessel}').classes('text-base flex items-center')
            ui.label(f'Brauchw-Temp = {datav.vBrauchwasser}').classes('text-base col-start-3 flex items-center') 
            ui.label('Brauchw-Pumpe').classes('text-base col-start-4 flex items-center')
            ui.spinner('Facebook',size='sm').bind_visibility_from(target_object=datav,target_name='vPumpe_Brauchwasser_an',value='True').classes('mt-3')

        # Zeile 4
            ui.label(f'Brenner läuft').classes('text-base col-start-1 h-9')
            ui.spinner(type='ball', color='red' ,size='sm').bind_visibility_from(target_object=datav,target_name='vBrenner_an', value='False').classes('h-9')
            ui.label('Brennerstörung').classes('text-base col-start-2 h-9')
            ui.spinner(size='sm',color='red').bind_visibility_from(target_object=datav,target_name='vBrenner_Stoerung', value='False').classes('h-9')
            ui.label('H-Pumpe oben').classes('text-base col-start-3 h-9')
            ui.spinner('Facebook',size='sm').bind_visibility_from(target_object=datav,target_name='vPumpe_oben_an', value='False').classes('h-9')
            ui.label('H-Pumpe unten').classes('text-base col-start-4  h-9')
            ui.spinner('Facebook',size='sm').bind_visibility_from(target_object=datav,target_name='vPumpe_unten_an', value='False').classes('h-9')

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
                global id, typ,tage,von,bis,handle_id
                # print("Handle Click:",table.selected)
                handle_id =table.selected[0]['id']
                typval=table.selected[0]['typ']
                typ=typ_r_dict[typval]
                tageval=table.selected[0]['tage']
                tage=tage_r_dict[tageval]
                von=table.selected[0]['von']
                bis=table.selected[0]['bis']
                # print("global gesetzt handle_id:",handle_id,"typ:",typ,"tage:",tage,von, bis)
            
                                
        # löscht eine markierte Tabellenzeile
        def remove():
            # ui.notify(table.selected)
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
            # ui.notify(typ)

        # Setzt die Tage
        def settage(value):
            global tage
            tage=value
            # ui.notify(tage)

        # Setzt den Beginn einer Aufgabe
        def setvon(value):
            erg=isTimeFormat(value)
            if erg == True:
                global von
                von=value
                # ui.notify(von)
            return(erg)

        # setzt  das Ende einer Aufgabe
        def setbis(value):
            erg=isTimeFormat(value)
            if erg == True:
                global bis
                bis=value
                # ui.notify(bis)   
            return(erg)
        

        # Definition des Dialog für das Hinzufügen von Werten
        with ui.dialog() as tabledialogadd, ui.card().classes('top-8 left-8'):
            with ui.grid(columns=2, rows=3):
                # schliesst den Dialog
                def close_add():
                    global id, typ, tage, von, bis
                    id +=1
                    # print('Anzulegen:',id,typ,tage,von,bis)
                    if typ != 0 and tage !=0:
                        table.add_rows({'id': id, 'typ':typdict[typ], 'tage':tagedict[tage], 'von':von, 'bis': bis})
                        # print('Neu Angelegt:',id,typ,tage,von,bis)
                        datav.vZeitsteuerung=tuple((id, typdict[typ], tagedict[tage],von,bis))
                        tabledialogadd.close()
                
                ui.select(options=typdict, label='Typ',   with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
                ui.select(options=tagedict, label='Tage', with_input=True, on_change=lambda e: settage(e.value)).classes('w-40')
                ui.input(label='Zeit von', value='12:00',placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
                ui.input(label='Zeit bis', value='12:01',placeholder='Zeit', validation={'Ungültig!! (Format)': lambda value: setbis(value)==True}).classes('w-30')
                ui.button('OK', on_click=close_add).classes('w-20')

        # Daten für den Anzeigedialog updaten
        def updateeditdialog():
            # print("vor dem Edit Dialog:",handle_id,typ,tage,von,bis)
            if handle_id !=0:
                s1.value=typ
                s2.value=tage
                s3.value=von
                s4.value=bis
                tabledialogedit.open()


        # macht eine Tabellenzeile editierbar
        with ui.dialog() as tabledialogedit, ui.card().classes('top-8 left-8'):
            with ui.grid(columns=2, rows=3):
                # schliesst den Dialog
                def close_edit():
                    # print("Nach Edit",handle_id, typ,tage,von,bis)
                
                    if table.selected != []:
                        if typ != 0 and tage !=0:
                            # aktuelle zeile entfernen
                            remove()
                            #neue Zeile Hinzufügen
                            table.add_rows({'id': handle_id, 'typ':typdict[typ], 'tage':tagedict[tage], 'von':von, 'bis': bis})
                            # hier muss die Zeile in die DB
                            # table.sorted
                            # print('Edit Neu Angelegt:',handle_id,typ,tage,von,bis)
                            datav.vZeitsteuerung=(handle_id, typdict[typ], tagedict[tage],von,bis)
                            update_table.refresh()
                    # handle_id=0
                    tabledialogedit.close()
                
                s1=ui.select(options=typdict, label='Typ',   with_input=True, on_change=lambda e: settyp(e.value)).classes('w-30')
                s2=ui.select(options=tagedict,label='Tage',  with_input=True, on_change=lambda e: settage(e.value)).classes('w-40')
                s3=ui.input(label='Zeit von',  value='12:00',placeholder='Zeit', validation={'Ungültig!!': lambda value: setvon(value)==True}).classes('w-30')
                s4=ui.input(label='Zeit bis',  value='12:01',placeholder='Zeit', validation={'Ungültig!! (Format)': lambda value: setbis(value)==True}).classes('w-30')
                ui.button('OK', on_click=close_edit).classes('w-20')
        

        # hier beginnt die Anzeige der  linken Seite des Reiters -----------
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
        # ui.label('Kesselsteuerung')           
        figkessel = {
            'data': 
            [
                {
                    'type': 'scatter',
                    'name': 'Kessel',
                    'x': datav.vKesselDaten_x,
                    'y': datav.vKesselDaten_y,
                },          
            ],
            'layout': 
            {
                'margin': {'l': 35, 'r': 20, 't': 20, 'b': 35},
                'plot_bgcolor': '#E5ECF6',
                'xaxis': {'title': 'Aussentemp','gridcolor': 'white'},
                'yaxis': {'title': 'Kesseltemp','gridcolor': 'white'},
            },
        }
        plotkessel= ui.plotly(figkessel).classes('w-full h-64')  
        # jetzt braucht es noch Knöpfe und Funktionen um die Kurve zu verändern
        # "von Grad", "bis Grad", "Yeränderung" -> 3Knöpfe
        # alle in einer Zeile
        def gradvon(value):
            global gradv
            gradv=value
            # ui.notify(gradv) 
            
        # Die eingegebene Temperatur liegt im Bereich von -30 und 30 Grad
        # Die "Bis Temperatur" muss größer sein als die "von Temperatur"
        def gradbis(value):
            global gradb
            gradb=value
            # ui.notify(gradb) 
            
        def gradanpassen(value):
            global gradanpass
            gradanpass=value
            # ui.notify(gradanpass) 
            
        # passt die Kesselkennlinie in einem Bereich (start-stop) um einen Wert ungleich Null an 
        def anpassen():
            with plotkessel:
                if gradanpass!=0:
                    startidx = 0
                    stopidx=0
                    foundstart= False
                    foundstop=False
                    i=0
                    for _ in datav.vKesselDaten_x:
                        if (datav.vKesselDaten_x[i]>= gradv) and foundstart==False:
                            # Anfang des zu veränderden Intervalls
                            startidx=i
                            foundstart=True
                        if (datav.vKesselDaten_x[i]> gradb) and foundstop==False:
                            # gerade übder das ENde des Intervalls hinaus
                            stopidx=i-1
                            foundstop=True
                            break
                        i+=1

                    # So jetzt sollten Anfang und Ende festliegen
                    # damit kann man dann alle betroffenen Y-Werte um den betrag Gradanpass anpassen
                    # ui.notify(f"startidx:{startidx}, stopidx:{stopidx}, gradanpass:{gradanpass}")
                    if startidx<=stopidx and startidx>=0 and stopidx>=0:
                        # Liste vorher kopieren, denn der Speichervorgang löst ein vollständiges Schreiben der Liste in der DB aus.
                        # hoffentlich passiert das nicht wenn man die .copy Funktion verwendet
                        templist=datav.vKesselDaten_y.copy()
                        i=startidx
                        while i<=stopidx:
                            templist[i]+=gradanpass
                            i+=1
                        datav.vKesselDaten_y=templist.copy()
                        plotkessel.figure['data'][0]['y']=templist.copy()
                        ui.update(plotkessel)
                        
                    else:
                        ui.notify(f"Kesselkurvenanpassung misslungen Startindex:{startidx} Stopindex{stopidx}")
            ui.update(plotkessel)
        

        # hier hätten wir noch 3 Eingaben und einen Knopf um die Kesselkurve zu verändern.                    
        with ui.grid(columns=4, rows=1).classes('w-full'):
            ui.number(label='Grad von',   value='0', step=settings.AussenTempStep, min=settings.AussenMinTemp,max=settings.AussenMaxTemp,
                      placeholder='Grad von', suffix='Grad', on_change= lambda e: gradvon(e.value)).classes('w-22 mr-4')
            ui.number(label='Grad bis',   value='0', step=settings.AussenTempStep,  min=settings.AussenMinTemp,max=settings.AussenMaxTemp,
                      placeholder='Grad bis', suffix='Grad', on_change= lambda e: gradbis(e.value)).classes('w-22 mr-4')
            ui.number(label='Anpassen um',value='0', step=(settings.AussenTempStep/10), min=settings.AussenMinTemp,max=settings.AussenMaxTemp,
                      placeholder='Differenz', suffix='Grad', on_change= lambda e: gradanpassen(e.value)).classes('w-22 mr-4')
            ui.button('OK', on_click=anpassen).classes('w-20 mt-4') 


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
            # offene Themen:
            # Schalter Brauchwasser vollstandig ausschalten!
            # ggf die Gleichung füe die Kesselkurve eingeben




# ui.run(title='Buderus Ecomatic',window_size=(800,480), resizable=False, confirm_close=True )
ui.run(native=False, favicon='🚀',port=8000, title='Buderus Ecomatic',window_size=(800,480), dark=True )
# ui.run()
