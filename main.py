# -*- coding: utf-8 -*-
"""
Created on Sun October 28 22:10:07 2020

@author: Jacob Kjaerager
"""

from pathlib import Path
import dash
from callbacks import init_callback
from layout import layout

if __name__ == '__main__':

    app = dash.Dash(
           __name__,
           assets_folder="{}/styling".format(Path(__file__).parent)
          )

    app = layout(app)
    init_callback(app)
    app.run_server(host="0.0.0.0", debug=True, port=8050)


