#!/usr/bin/env python3

import plotly.graph_objects as go
import pandas as pd
from nicegui import ui, app

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
    
    fig = go.Figure(go.Scatter(x= [10, 12, 20, 22, 20, 17, 16, 14], y=[8, 10, 12, 14, 16,18, 20, 22]))
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
                ui.label(f'Aussen-Temp = {temp}').classes('text-l')
                malen()
            with ui.row():    
                ui.label(f'Innen-Temp = {temp}').classes('text-l')
                
                ui.button('Hand-Dusche', color='#1e5569', on_click=lambda: ui.notify(f'Hand Dusche an!')).classes('ml-20')
                malen()
            with ui.row():                         
                ui.label(f'Kessel-Temp = {temp}').classes('text-l')
                ui.label(f'Brenner läuft').classes('ml-10').classes('text-l')
                ui.spinner(size='sm')
                malen()
                ui.label('Brennerstörung').classes('text-l')
                ui.spinner(size='sm',color='red')
            with ui.row(): 
                ui.label(f'Brauchw = {temp}').classes('text-l')
                ui.label('Brauchw-P').classes('ml-16').classes('text-l')
                ui.spinner(size='sm')
                malen()
                ui.label('H-Pumpe oben').classes('text-l')
                ui.spinner(size='sm')
                ui.label('H-Pumpe unten').classes('text-l')
                ui.spinner(size='sm')
           
    with ui.tab_panel(einstellungen):
        ui.label('Content of B')

            


# ui.run(title='Buderus Ecomatic',window_size=(800,480), resizable=False, confirm_close=True )
ui.run(favicon='🚀',port=8080, title='Buderus Ecomatic',window_size=(800,480), native= True, fullscreen=True, reload=False,uvicorn_logging_level="warning", dark=True, show=False)