#!/usr/bin/env python3

import plotly.graph_objects as go
from nicegui import ui

# Grfiken anzeigen
def malen() -> None:
    fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    ui.plotly(fig).classes('w-full h-40')  

# Kopfzeile
with ui.header().classes(replace='row items-center') as header:
    # ui.button(on_click=lambda: left_drawer.toggle()).props('flat color=white icon=menu')
    with ui.tabs() as tabs:
        information=ui.tab('Information')
        einstellungen=ui.tab('Einstellungen')
    
#Fusszeile
with ui.footer(value=False) as footer:
    ui.label('Footer')

'Menü links'
# with ui.left_drawer().classes('bg-blue-100') as left_drawer:
#     ui.label('Side menu')

with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
    ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

temp=100
with ui.tab_panels(tabs, value=information).classes('w-full'):
    with ui.tab_panel(information):
        with ui.grid(columns=2, rows=4):
            with ui.row():
                ui.label(f'Aussen-Temp = {temp}').classes('text-2xl').classes('object-center')
                malen()
            with ui.row():    
                ui.label(f'Innen-Temp = {temp}').classes('text-2xl')
                malen()
            with ui.row():                         
                ui.label(f'Kessel-Temp = {temp}').classes('text-2xl')
                ui.label(f'Brenner läuft').classes('ml-4').classes('text-2xl')
                ui.spinner(size='lg')
                malen()
                ui.label('Brennerstörung').classes('ml-4').classes('text-2xl')
                ui.spinner(size='lg',color='red')
            with ui.row(): 
                ui.label(f'Brauchwasser = {temp}').classes('text-2xl')
                ui.label('Brauchwasser-P').classes('ml-4').classes('text-2xl')
                ui.spinner(size='lg')
                malen()
                ui.button('Hand-Dusche',on_click=lambda: ui.notify(f'Hand Duche an!')).classes('ml-4')
            with ui.row():
                ui.label('H-Pumpe oben').classes('ml-4').classes('text-2xl')
                ui.spinner(size='lg')
                ui.label('H-Pumpe unten').classes('ml-4').classes('text-2xl')
                ui.spinner(size='lg')
    with ui.tab_panel(einstellungen):
        ui.label('Content of B')

            


ui.run()