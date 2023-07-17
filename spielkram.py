#!/usr/bin/env python3

import plotly.graph_objects as go
import pandas as pd
from nicegui import ui, app
import time

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

# Kopfzeile
with ui.header().classes(replace='row items-center') as header:
    # ui.button(on_click=lambda: left_drawer.toggle()).props('flat color=white icon=menu')
    with ui.tabs() as tabs:
        information=ui.tab('Information')
        einstellungen=ui.tab('Einstellungen')
    
#Fusszeile
with ui.footer(value=False) as footer:
    ui.label('Buderus Ecomatic')



temp=100
with ui.tab_panels(tabs, value=information):
    with ui.tab_panel(information):
        with ui.grid(columns=2, rows=2):
            with ui.row():
                ui.label(f'Aussen-Temp = {temp}').classes('text-base')
                malen()
            with ui.row():    
                ui.label(f'Innen-Temp = {temp}').classes('text-base')
                
                ui.button('Hand-Dusche', color='#1e5569', on_click=lambda: ui.notify(f'Hand Dusche an!')).classes('ml-10')
                malen()
            with ui.row():                         
                ui.label(f'Kessel-Temp = {temp}').classes('text-base')
                ui.label(f'Brenner läuft').classes('ml-4').classes('text-base')
                ui.spinner(size='sm')
                malen()
                ui.label('Brennerstörung').classes('text-base')
                ui.spinner(size='sm',color='red')
            with ui.row(): 
                ui.label(f'Brauchw = {temp}').classes('text-base')
                ui.label('Brauchw-P').classes('ml-16').classes('text-base')
                ui.spinner(size='sm')
                malen()
                ui.label('H-Pumpe oben').classes('text-base')
                ui.spinner(size='sm')
                ui.label('H-Pumpe unten').classes('text-base')
                ui.spinner(size='sm')
           
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
            
            def isTimeFormat(input):
                try:
                    time.strptime(input, '%H:%M')
                    return True
                except ValueError:
                    return False
            
            typ = ui.select({1: 'Brauchw', 2: 'Heizung', 3: 'Nacht'},label='  Typ  ')
            tage = ui.select({1:'Mo',2:'Die',3:'Mi',4:'Do',5:'Fr',6:'Sa',7:'So',8:'Mo-Fr',9:'Sa-So'},label='Tage')
            i=ui.input(label='Zeit', value='12:00',placeholder='Zeit von',
                validation={'Zeitformat!!': lambda value: isTimeFormat(value)==True})
            von=i.value
            ui.label(f'viel zeit {von}')


            #ui.time(value='12:00', on_change=lambda e: von.set_text(e.value))
            #von = ui.label()
            #ui.time(value='12:00', on_change=lambda f: bis.set_text(f.value))
            # bis = ui.label()


            


# ui.run(title='Buderus Ecomatic',window_size=(800,480), resizable=False, confirm_close=True )
ui.run(favicon='🚀',port=8080, title='Buderus Ecomatic',window_size=(800,480), native= True, fullscreen=True, reload=False,uvicorn_logging_level="warning", dark=True, show=False)
# ui.run()
