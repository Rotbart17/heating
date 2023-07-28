#!/usr/bin/env python3

import plotly.graph_objects as go
import pandas as pd
from nicegui import ui, app
import time
from datetime import datetime
import settings


# Fenstergröße darf nicht verändert werden
# app.native.window_args['resizable'] = True
# app.native.window_args['width']='800'
# app.native.window_args['height']='480'
# app.native.window_args['resizable']=False
# app.native.window_args['title']='Buderus Ecomatic'
# app.native.start_args['debug'] = True


# Grfiken anzeigen
def malen() -> None:
    # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
    # fig = go.Figure([go.Scatter(x=df['Date'], y=df['AAPL.High'])])
    
    fig = go.Figure(go.Scatter(y = [10, 12, 20, 22, 20, 17, 16, 14], x=[8, 10, 12, 14, 16, 18, 20, 22]))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    ui.plotly(fig).classes('w-5/6 h-20')  

# Funktionen für... notwenig. Timer gesteuerter Abruf aus der DB!
# get Startwerte und dann updates für Aussentemperatur,Innentemperatur, 
#     Kesseltemperatur, Brauchwasser, Brennerstörung, Pumpen: oben, unten, Brauchwasser

# Kopfzeile
with ui.header().classes(replace='row items-center') as header:
    # ui.button(on_click=lambda: left_drawer.toggle()).props('flat color=white icon=menu')
    # hier muss noch die aktuelle Zeit hin


    with ui.tabs() as tabs:
        
        information=ui.tab('Information')
        einstellungen=ui.tab('Einstellungen')
    label = ui.label().classes('row col-7 justify-end')
    ui.timer(1.0, lambda: label.set_text(f'{datetime.now():%H:%M}'))  


# Fusszeile
with ui.footer(value=True) as footer:
    ui.label('Buderus Ecomatic')


# Hand Dusche toggeln
def set_hand_dusche():
    if (settings.Hand_Dusche)==False:
        settings.Hand_Dusche=True
        ui.notify('Brauchwasser eingeschaltet!')
        # Wert in DB setzen
    else:
        settings.Hand_Dusche=False
        ui.notify('Brauchwasser ausgeschaltet!')
        # Wert in DB setzen

# schaltet das "ist aktive" Element ein und aus
def set_brenner_spin():
    if settings.Brenner_an==True:
        brenner_spin.set_visibility(True)
    else: 
        brenner_spin.set_visibility(False)

# schaltet das "ist aktive" Element ein und aus
def set_brennerstoerung_spin():
    if settings.Brenner_Stoerung==True:
        brennerstoerung_spin.set_visibility(True)
    else: 
        brennerstoerung_spin.set_visibility(False)

# schaltet das "ist aktive" Element ein und aus
def set_brauchwasser_spin():
    if settings.Pumpe_Brauchwasser_an==True:
        brauchwasser_spin.set_visibility(True)
    else: 
        brauchwasser_spin.set_visibility(False)

# schaltet das "ist aktive" Element ein und aus
def set_pumpe_oben_spin():
    if settings.Pumpe_oben_an==True:
        pumpe_oben.set_visibility(True)
    else: 
        pumpe_oben.set_visibility(False)

# schaltet das "ist aktive" Element ein und aus
def set_pumpe_unten_spin():
    if settings.Pumpe_unten_an==True:
        pumpe_unten.set_visibility(True)
    else: 
        pumpe_unten.set_visibility(False)


# hier werden 2 TABs definiert (Information / Einstellungen)
with ui.tab_panels(tabs, value=information):
    with ui.tab_panel(information):
        with ui.grid(columns=2, rows=2):
            with ui.row():
                ui.label(f'Aussen-Temp = {settings.Aussen}').classes('text-base')
                malen()
            with ui.row():    
                ui.label(f'Innen-Temp = {settings.Innen}').classes('text-base')
                ui.button('Hand-Dusche', color='#1e5569', on_click=lambda: set_hand_dusche()).classes('w-30')
                malen()
            with ui.row():                         
                ui.label(f'Kessel-Temp = {settings.Kessel}').classes('text-base')
                ui.label(f'Brenner läuft').classes('ml-4').classes('text-base')
                brenner_spin=ui.spinner(type='ball', color='red' ,size='sm')
                malen()
                ui.label('Brennerstörung').classes('text-base')
                brennerstoerung_spin=ui.spinner(size='sm',color='red')
            with ui.row(): 
                ui.label(f'Brauchw = {settings.Brauchwasser}').classes('text-base')
                ui.label('Brauchw-P').classes('ml-16').classes('text-base')
                brauchwasser_spin=ui.spinner(size='sm')
                malen()
                ui.label('H-Pumpe oben').classes('text-base')
                pumpe_oben=ui.spinner(size='sm')
                ui.label('H-Pumpe unten').classes('text-base')
                pumpe_unten=ui.spinner(size='sm')
           
    with ui.tab_panel(einstellungen):
        ui.label('Content of B')
        '''
        - Zeit(en) für Brauchwasser festlegen / Anzeigen für Wochentag und Zeit
        - Zeit(en) für Heizbetrieb festlegen  / anzeigen für Wochentag und Zeit
            Einstellen mit:
                Dropdown: Mo-Fr, Mo, Die, Mi, Do, Fr, Sa, So, Sa+So, 
                Feld: Uhrzeit von
                Feld: Uhrzeit bis
                Eigenschaft: Heizen Start, Heizen Stop, Nachtabsenkung Start, Nachtabsenkung Stop, Warmwasser Start, Warmwasser Stop

            - max. Kesseltemperatur einstellen = Vorlauf Temperatur
            - Sommer / Winterumschaltung per Temperatur und Anzeige Jahreszeit, ggf. noch eine Berücksichtigung der Jahreszeit für Sommer.-Winterumschaltung?
        '''
        with ui.row():
            pass
            
           

set_brenner_spin()           
set_brennerstoerung_spin()
set_brauchwasser_spin()
set_pumpe_oben_spin()
set_pumpe_unten_spin()




# ui.run(title='Buderus Ecomatic',window_size=(800,480), resizable=False, confirm_close=True )
ui.run(favicon='🚀',port=8000, title='Buderus Ecomatic',window_size=(800,480), fullscreen=True,uvicorn_logging_level="warning", dark=True, show=False)
# ui.run()
