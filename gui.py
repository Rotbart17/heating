#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Any

import plotly.graph_objects as go
# import pandas as pd
from nicegui import ui, app
import time
from datetime import datetime
import settings
from dataview import maindata
from main import BACKEND_READY, STOP_MESSAGE, startbackend
import logging
import sys
from multiprocessing import Queue
import multiprocessing
from queue import Empty

@dataclass
class GuiState:
    backendproc: multiprocessing.Process
    queue_to_backend: Any
    queue_to_frontend: Any
    datav: maindata
    stopped: bool = False


def wait_for_backend(queue_to_frontend: Any, backendproc: multiprocessing.Process, timeout: int = 30) -> None:
    # Warten, bis startbackend alle Backend-Komponenten gestartet hat.
    start_time = time.time()

    logging.info("Warte auf Backend-Start...")
    while True:
        if time.time() - start_time > timeout:
            logging.error("Timeout beim Warten auf Backend-Start.")
            sys.exit("Backend konnte nicht initialisiert werden.")

        try:
            message = queue_to_frontend.get(timeout=1)
        except Empty:
            if not backendproc.is_alive():
                logging.error("Backend-Prozess wurde vor dem Startsignal beendet.")
                sys.exit("Backend-Prozess wurde vor dem Startsignal beendet.")
            continue

        if message == BACKEND_READY:
            logging.info("Backend ist bereit. Initialisiere GUI-Daten.")
            return

        logging.debug(f"Ignoriere Backend-Startmeldung: {message}")


def create_state() -> GuiState:
    queue_to_backend = Queue()
    queue_to_frontend = Queue()
    backendproc = multiprocessing.Process(
        target=startbackend,
        name="Backend-Prozess",
        args=(queue_to_backend, queue_to_frontend),
    )
    backendproc.start()
    try:
        wait_for_backend(queue_to_frontend, backendproc)
    except BaseException:
        queue_to_backend.put(STOP_MESSAGE)
        backendproc.join(timeout=5)
        raise

    datav = maindata()
    datav.queue_to_backend = queue_to_backend
    datav.queue_to_frontend = queue_to_frontend

    return GuiState(
        backendproc=backendproc,
        queue_to_backend=queue_to_backend,
        queue_to_frontend=queue_to_frontend,
        datav=datav,
    )


def shutdown_state(state: GuiState) -> None:
    if state.stopped:
        return
    state.stopped = True

    state.datav.stop_polling()
    state.queue_to_backend.put(STOP_MESSAGE)
    state.backendproc.join(timeout=5)
    if state.backendproc.is_alive():
        logging.warning("Backend-Prozess konnte nicht innerhalb des Timeouts beendet werden. Erzwinge Stop.")
        state.backendproc.terminate()
        state.backendproc.join(timeout=5)
    if state.backendproc.is_alive():
        logging.error("Backend-Prozess läuft trotz terminate() weiter.")


def build_gui(state: GuiState) -> None:
    global id, handle_id, heiztype, tage, von, bis
    global s1, s2, s3, s4

    datav = state.datav
    # Fügt eigenes CSS hinzu, um die Pfeile der numerischen Eingabe ui.input zu vergrößern
    # funktioniert nicht bei Firefox
    ui.add_head_html('''
    <style>
    /* Vergrößert die Auf/Ab-Pfeile in numerischen Eingabefeldern für WebKit-Browser (Chrome, Safari, etc.) */
    .q-field__native::-webkit-inner-spin-button,
    .q-field__native::-webkit-outer-spin-button {
        /* Die Breite und Höhe können nach Bedarf angepasst werden */
        width: 1.2em;
        height: 2.2em;
        opacity: 1; /* Stellt sicher, dass die Pfeile sichtbar sind */
    }
    </style>
    ''')

    # globale Variablen und Funktionen für die 3 Reiter "Einstellungen
    # Spalten für die Tabelle der Heizungssteuerung: Typ (z.B. Brauchwasser), Tage, Zeit von, zeit bis

    # Zeilennummer in der Tabelle setzen
    if len(datav.Zeitsteuerungszeilen)> 0:
        id = len (datav.Zeitsteuerungszeilen)
    else:
        id=0
    # Welche Zeile in der Tabelle wird bearbeitet
    handle_id = 0
    # welcher Heiztyp
    heiztype = 0
    # wann wird der Heiztyp verwendet
    tage = 0
    # Zeitperiode für den Heiztyp
    von = '12:00'
    bis = '12:01'



    # Definitionen der verschiedenen Tagesmöglichkeiten die man für die Einstellungen hat
    tagedict = {
        1: 'Mo',
        2: 'Die',
        3: 'Mi',
        4: 'Do',
        5: 'Fr',
        6: 'Sa',
        7: 'So',
        8: 'Mo-Fr',
        9: 'Sa-So',
        10: 'Mo-So',
    }
    tage_r_dict = {label: value for value, label in tagedict.items()}


    # Definition der verschiedenen Heizungsmodi
    typdict = {
        1: 'Brauchw',
        2: 'Heizen',
        3: 'Nachtabsenk.',
    }
    typ_r_dict = {label: value for value, label in typdict.items()}


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



    # Backend stoppen
    def de_init_data() -> None:
        shutdown_state(state)
        app.shutdown()

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
                ui.label().bind_text_from(datav, 'vAussen', lambda v: f'Aussen-Temp = {v}').classes('text-sm col-start-1')
                ui.label().bind_text_from(datav, 'vWinter', lambda v: 'Winterbetrieb' if v else 'Sommerbetrieb').classes('text-sm col-start-2 ')
                ui.label().bind_text_from(datav, 'vInnen', lambda v: f'Innen-Temp = {v}').classes('text-sm col-start-3')
                ui.button('Hand-Dusche', color='#1e5569', on_click=lambda: set_hand_dusche()).classes('col-start-4 w-32 h-12')

            # Zeile 2
            with ui.grid(columns=4, rows=1).classes('w-full'):
                figtemp = go.Figure()
                figtemp.add_trace(go.Scatter(x=datav.vAussenDaten_x, y=datav.vAussenDaten_y, name='Aussen-T'))
                figtemp.add_trace(go.Scatter(x=datav.vInnenDaten_x, y=datav.vInnenDaten_y, name='Innen-T'))
                figtemp.add_trace(go.Scatter(x=datav.vKesselIstDaten_x, y=datav.vKesselIstDaten_y, name='Kessel-T'))
                figtemp.add_trace(go.Scatter(x=datav.vBrauchwasserDaten_x, y=datav.vBrauchwasserDaten_y, name='Brauchw-T'))
                figtemp.update_layout(margin=dict(l=35, r=20, t=9, b=18), plot_bgcolor='#E5ECF6',
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
                ui.label().bind_text_from(datav, 'vKesselSoll', lambda v: f'Kessel-Soll-Temp = {v}').classes('text-sm col-start-1  flex items-center')
                ui.label().bind_text_from(datav, 'vKessel', lambda v: f'Kessel-Temp = {v}').classes('text-sm flex items-center')
                ui.label().bind_text_from(datav, 'vBrauchwasser', lambda v: f'Brauchw-Temp = {v}').classes('text-sm col-start-3 flex items-center')
                ui.label('Brauchw-Pumpe').classes('text-sm col-start-4 flex items-center')
                ui.spinner('facebook', size='sm').bind_visibility_from(datav, 'vPumpe_Brauchwasser_an').classes('mt-3')
            # Zeile 4
                ui.label('Brenner läuft').classes('text-sm col-start-1 h-9')
                ui.spinner(type='ball', color='red', size='sm').bind_visibility_from(datav, 'vBrenner_an').classes('h-9')
                ui.label('Brennerstörung').classes('text-sm col-start-2 h-9')
                ui.spinner(size='sm', color='red').bind_visibility_from(datav, 'vBrenner_Stoerung').classes('h-9')
                ui.label('H-Pumpe oben').classes('text-sm col-start-3 h-9')
                ui.spinner('facebook', size='sm').bind_visibility_from(datav, 'vPumpe_oben_an').classes('h-9')
                ui.label('H-Pumpe unten').classes('text-sm col-start-4  h-9')
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
                # ui.label('Steuerdaten:').classes('text-sm').classes('mt-4')
                ui.button('Neu', on_click=tabledialogadd.open).classes('ml-4')
                ui.button('Ändern', on_click=updateeditdialog).classes('ml-8')
                ui.button('Löschen', on_click=remove).classes('ml-8')

            # Das malt dann die Tabelle unter die Knöpfe
            update_table()



        #---------------------------------------------------------------------------------------------------------
        # Dritter Reiter -----------------------------------------------
        with ui.tab_panel(kesselsteuerung):
            kessel_x = datav.vKesselDaten_x.copy()
            saved_kessel_y = datav.vKesselDaten_y.copy()
            preview_kessel_y = saved_kessel_y.copy()
            selected_range: dict[str, float] = {
                'min': float(settings.AussenMinTemp),
                'max': float(settings.AussenMaxTemp),
            }
            history: list[list[float]] = []
            adjustment_step = settings.AussenTempStep

            figkessel = {
                'data':
                [
                    {
                        'type': 'scatter',
                        'name': 'Gespeichert',
                        'x': kessel_x,
                        'y': saved_kessel_y,
                        'mode': 'lines',
                        'line': {'color': '#8a8f98', 'dash': 'dot', 'width': 2},
                    },
                    {
                        'type': 'scatter',
                        'name': 'Vorschau',
                        'x': kessel_x,
                        'y': preview_kessel_y,
                        'mode': 'lines+markers',
                        'line': {'color': '#4f8cff', 'width': 3},
                        'marker': {'color': '#4f8cff', 'size': 6},
                    },
                    {
                        'type': 'scatter',
                        'name': 'Auswahl',
                        'x': kessel_x,
                        'y': preview_kessel_y,
                        'mode': 'markers',
                        'marker': {'color': '#f59e0b', 'size': 10},
                    },
                ],
                'layout':
                {
                    'margin': {'l': 35, 'r': 20, 't': 20, 'b': 35},
                    'plot_bgcolor': '#E5ECF6',
                    'xaxis': {'title': 'Aussentemp','gridcolor': 'white'},
                    'yaxis': {'title': 'Kesseltemp','gridcolor': 'white'},
                    'legend': {'orientation': 'h', 'y': 1.12},
                },
                'config': {'displayModeBar': False, 'responsive': True},
            }
            plotkessel= ui.plotly(figkessel).classes('w-full h-64')

            range_label = ui.label().classes('text-base ml-4')
            status_label = ui.label().classes('text-sm ml-4')

            def has_unsaved_changes() -> bool:
                return any(abs(a - b) > 0.001 for a, b in zip(saved_kessel_y, preview_kessel_y))

            def selected_points() -> tuple[list[float], list[float]]:
                start = min(selected_range['min'], selected_range['max'])
                stop = max(selected_range['min'], selected_range['max'])
                points = [
                    (x, y)
                    for x, y in zip(kessel_x, preview_kessel_y)
                    if start <= x <= stop
                ]
                if not points:
                    return [], []
                x_values, y_values = zip(*points)
                return list(x_values), list(y_values)

            def update_plot() -> None:
                selected_x, selected_y = selected_points()
                figkessel['data'][0]['y'] = saved_kessel_y.copy()
                figkessel['data'][1]['y'] = preview_kessel_y.copy()
                figkessel['data'][2]['x'] = selected_x
                figkessel['data'][2]['y'] = selected_y
                range_label.set_text(f"Bereich: {selected_range['min']:.1f} °C bis {selected_range['max']:.1f} °C")
                status_label.set_text('Vorschau geändert' if has_unsaved_changes() else 'Keine ungespeicherten Änderungen')
                plotkessel.update()

            def set_range(e):
                selected_range['min'] = float(e.value['min'])
                selected_range['max'] = float(e.value['max'])
                update_plot()

            def remember_preview() -> None:
                history.append(preview_kessel_y.copy())
                if len(history) > 20:
                    history.pop(0)

            def smoothstep(value: float) -> float:
                value = max(0.0, min(1.0, value))
                return value * value * (3.0 - 2.0 * value)

            def range_weight(x: float) -> float:
                start = min(selected_range['min'], selected_range['max'])
                stop = max(selected_range['min'], selected_range['max'])
                if x < start or x > stop:
                    return 0.0

                span = stop - start
                if span <= adjustment_step:
                    return 1.0 if abs(x - start) <= adjustment_step / 2 else 0.0

                edge_width = min(4.0, span / 4.0)
                left_weight = 1.0
                right_weight = 1.0
                if start > settings.AussenMinTemp and edge_width > 0:
                    left_weight = smoothstep((x - start) / edge_width)
                if stop < settings.AussenMaxTemp and edge_width > 0:
                    right_weight = smoothstep((stop - x) / edge_width)
                return min(left_weight, right_weight)

            def apply_to_preview(delta_func) -> None:
                nonlocal preview_kessel_y
                remember_preview()
                changed = False
                new_values = preview_kessel_y.copy()
                for idx, x in enumerate(kessel_x):
                    delta = delta_func(x)
                    if abs(delta) > 0.001:
                        new_values[idx] = round(new_values[idx] + delta, 1)
                        changed = True
                if changed:
                    preview_kessel_y = new_values
                    update_plot()
                else:
                    history.pop()
                    ui.notify('Im ausgewählten Bereich liegt kein Kurvenpunkt.')

            def adjust_level(amount: float) -> None:
                apply_to_preview(lambda x: amount * range_weight(x))

            def adjust_slope(direction: float) -> None:
                start = min(selected_range['min'], selected_range['max'])
                stop = max(selected_range['min'], selected_range['max'])
                center = (start + stop) / 2.0
                half_span = max((stop - start) / 2.0, adjustment_step)

                def delta(x: float) -> float:
                    cold_side_factor = (center - x) / half_span
                    return direction * adjustment_step * cold_side_factor * range_weight(x)

                apply_to_preview(delta)

            def undo_preview() -> None:
                nonlocal preview_kessel_y
                if not history:
                    ui.notify('Keine Änderung zum Rückgängig machen.')
                    return
                preview_kessel_y = history.pop()
                update_plot()

            def discard_preview() -> None:
                nonlocal preview_kessel_y
                preview_kessel_y = saved_kessel_y.copy()
                history.clear()
                update_plot()

            def save_preview() -> None:
                nonlocal saved_kessel_y
                saved_kessel_y = preview_kessel_y.copy()
                datav.vKesselDaten_y = saved_kessel_y.copy()
                history.clear()
                update_plot()
                ui.notify('Kesselkurve gespeichert.')

            with ui.column().classes('w-full gap-4'):
                ui.range(
                    min=settings.AussenMinTemp,
                    max=settings.AussenMaxTemp,
                    step=settings.AussenTempStep,
                    value={'min': settings.AussenMinTemp, 'max': settings.AussenMaxTemp},
                    on_change=set_range,
                ).props('label label-always snap').classes('w-11/12 ml-4 mt-2')

                with ui.grid(columns=2).classes('w-full px-4 gap-4'):
                    ui.button('Niveau -', on_click=lambda: adjust_level(-adjustment_step)).classes('h-16 text-lg')
                    ui.button('Niveau +', on_click=lambda: adjust_level(adjustment_step)).classes('h-16 text-lg')
                    ui.button('Flacher', on_click=lambda: adjust_slope(-1.0)).classes('h-16 text-lg')
                    ui.button('Steiler', on_click=lambda: adjust_slope(1.0)).classes('h-16 text-lg')

                with ui.grid(columns=3).classes('w-full px-4 gap-4'):
                    ui.button('Rückgängig', on_click=undo_preview).classes('h-14 text-base')
                    ui.button('Verwerfen', on_click=discard_preview).classes('h-14 text-base')
                    ui.button('Speichern', color='#1e5569', on_click=save_preview).classes('h-14 text-base')

            update_plot()




        #---------------------------------------------------------------------------------------------------------
        # Vierter  Reiter ------------------


        with ui.tab_panel(einstellungen):
            with ui.grid(rows=4,columns=4):

                # hier brauchen wir nun Sommer Winterumschaltung Temp
                def setwinter(value):
                    datav.vWintertemp=value
                    ui.notify('Winter ab: '+str(datav.vWintertemp)+' Grad C°')


                ui.number(label='Winter ab:', suffix='Grad',min=10.0, max=25.0,  precision=2, value=datav.vWintertemp, \
                    on_change=lambda e: setwinter(e.value)).classes('flex-1 w-32')

                # Knopf zum Ausschalten
                ui.button('Programm Stop', color='#1e5569', on_click=lambda: de_init_data()).classes('col-start-4 w-25 h-25')
                # offene Themen:
                # Schalter Brauchwasser vollstandig ausschalten!
                # ggf die Gleichung füe die Kesselkurve eingeben

# -------------------------------------------------------------------------------------------------
# Start der GUI


def main() -> None:
    state = create_state()
    app.on_shutdown(lambda: shutdown_state(state))
    build_gui(state)
    ui.run(favicon='🚀', port=8000, title='Buderus Ecomatic', dark=True, reload=False, show=False)


if __name__ == '__main__':
    main()
