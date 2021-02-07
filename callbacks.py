# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 20:25:43 2020

@author: jacob
"""
import datetime as dt
from dash.dependencies import Input, Output
import pandas as pd
import os
from DataLoader import get_stock_data
from pathlib import Path
import plotly.graph_objs as go

class DataObject:

    def __init__(self):
        self.stock_data = get_stock_data()

def get_filtered_data(df, dd_value, start_date, end_date, hour_selector):
    if hour_selector:
        df = df[pd.to_datetime(df["tx_timestamp"]).dt.hour.isin(hour_selector)]

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    if dd_value != "all_data":
        df = df[df["gateway_name"] == dd_value]

    df = df[(df["tx_timestamp"] > start_date) & (df["tx_timestamp"] < end_date)]
    return df

def init_callback(app):

    do = DataObject()

    @app.callback(
        [
            Output(component_id ='latest_update', component_property='children'),
            Output(component_id ='latest_update', component_property='style'),
        ],
        [
            Input(component_id='data_updater', component_property='n_intervals')
        ]
    )
    def update_all_data(n):
        time_now = dt.datetime.now().strftime("%H:%M:%S  %d/%m/%Y")
        do.stock_data = get_stock_data()
        style = {"align":"center"}
        return ["Data last updated at: {}".format(time_now), style]

    @app.callback(
        [
            Output(component_id='dropdown_below_timestamp', component_property='options'),
            Output(component_id='dropdown_below_timestamp', component_property='value'),
        ],
        [
            Input(component_id='dummy_id_for_default', component_property='style')
        ]
    )
    def update_dropdown(dummy):
        df = do.full_uplink_data
        options = [{'label': i, 'value': i} for i in sorted(list(df["gateway_name"].unique()))]
        options.insert(0, {"label": "all data", "value": "all_data"})
        value =  next(iter(options))["value"]

        return options, value

    @app.callback(
        [
            Output(component_id ='datepicker', component_property='start_date'),
            Output(component_id ='datepicker', component_property='end_date'),
            Output(component_id ='datepicker', component_property='min_date_allowed'),
            Output(component_id ='datepicker', component_property='max_date_allowed'),
        ],
        [
            Input(component_id='dropdown_below_timestamp', component_property='value'),
        ]
    )
    def update_datepicker(dd_value):
        df = do.full_uplink_data
        df = df[df["tx_latitude"] != 0]
        if dd_value != "all_data":
            df = df[df["gateway_name"] == dd_value]

        start_date = df["rx_timestamp"].min()
        end_date = df["rx_timestamp"].max()

        return start_date, end_date, start_date, end_date


    @app.callback(
        [
            Output(component_id ='datatable', component_property='columns'),
            Output(component_id ='datatable', component_property='data'),
        ],
        [
            Input(component_id ='dropdown_below_timestamp', component_property='value'),
            Input(component_id ='datepicker', component_property='start_date'),
            Input(component_id ='datepicker', component_property='end_date'),
            Input(component_id ='hour_selector', component_property='value'),
        ]
    )
    def update_table_data(dd_value, start_date, end_date, hour_selector):
        df = do.full_uplink_data
        df = df[df["tx_latitude"] != 0]

        df = get_filtered_data(df, dd_value, start_date, end_date, hour_selector)

        columns=[{"name": i, "id": i} for i in df.columns]
        data=df.to_dict('records')

        return columns, data

    @app.callback(
        [
            Output(component_id ='full_round_bar_chart', component_property='figure'),
        ],
        [
            Input(component_id ='dropdown_below_timestamp', component_property='value'),
            Input(component_id ='datepicker', component_property='start_date'),
            Input(component_id ='datepicker', component_property='end_date'),
            Input(component_id ='hour_selector', component_property='value'),
            Input(component_id ='map_legend_picker', component_property='value'),
        ]
    )
    def update_map(dd_value, start_date, end_date, hour_selector, legend_picker):
        df = do.full_uplink_data
        df = df[df["tx_latitude"] != 0]

        df = get_filtered_data(df, dd_value, start_date, end_date, hour_selector)

        mapbox_access_token = "pk.eyJ1IjoiamFjb2I3NCIsImEiOiJjazhzcW9peXgwMjF2M21wOGdxenozMWRpIn0.cvEeafk5_3_FS-zkcOE6Jw"
        data=[
            go.Scattermapbox(
                mode="markers",
                lat = df["tx_latitude"],
                lon = df["tx_longitude"],
                hovertext = df[legend_picker],
                marker=go.scattermapbox.Marker(
                    size=11,
                    color=df[legend_picker],
                    colorbar=dict(
                        title=legend_picker,
                    ),
                    colorscale="Jet",
                )
            ),
        ]
        fig = go.Figure(
                   data=data,
               )
        fig.update_layout(
            title="Map for endpoint with GPS enabled",
            autosize=True,
            hovermode='closest',
            showlegend = False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict( #Center of map
                    lat = 56.155737,
                    lon = 10.189122,
                ),
                pitch=0,
                zoom=16,
            ),
            legend_title="{} for endpoints".format(legend_picker),
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        return [fig]

    @app.callback(
        [
            Output(component_id ='gps_success_circular_graph', component_property='figure'),
        ],
        [
            Input(component_id ='dropdown_below_timestamp', component_property='value'),
            Input(component_id ='datepicker', component_property='start_date'),
            Input(component_id ='datepicker', component_property='end_date'),
            Input(component_id ='hour_selector', component_property='value'),
        ]
    )
    def update_gps_piechart(dd_value, start_date, end_date, hour_selector):
        df_unfiltered = do.full_uplink_data


        df_user_inputted = get_filtered_data(df_unfiltered, dd_value, start_date, end_date, hour_selector)

        df_with_gps = df_user_inputted[df_user_inputted["tx_latitude"] != 0]
        df_no_gps = df_user_inputted[df_user_inputted["tx_latitude"] == 0]
        data=[
            go.Pie(
                labels=["GPS found", "No GPS found"],
                values=[df_with_gps.shape[0], df_no_gps.shape[0]],
                marker=dict(
                    colors=["green", "red"],
                ),
            )
        ]
        fig = go.Figure(
                   data=data,
               )
        fig.update_layout(
            title="GPS successes",
        )
        return [fig]



