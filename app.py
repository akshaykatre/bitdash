'''
Author: Akshay Katre <akshaykatre@gmail.com> 

This module displays the dashboard. It sources the data 
from local sqlite databases that have been created by 
the createtable.py module. 

To do:
    * Beautify 
    * Make available on local network 
    * There should be a single call back
    * Include the timestamp in call back 


'''

import dash 
from dash import dcc, html 
from dash.dependencies import Output, Input
from profit_loss import PNL
from bitstamp_trial import trading_client
from datetime import datetime

#dcc._css_dist[0]['relative_package_path'].append('tlayout.css')


app = dash.Dash(__name__)#, external_stylesheets='tlayout.css')
currenttime = datetime.now().strftime("%D %H:%M:%S")
colors = {
    'background': 'black',
    'text': 'cyan'
}

app.layout = html.Div(children=[
    html.H1(
        children='Hello Dash'
    ),

    html.Div(id='left-column', children='Last updated: '+currenttime),
    html.Div(
            dcc.Dropdown(id='curr-selection', 
                            options=[
                                {'label': 'Ethereum', 'value': 'eth' },
                                {'label': 'Bitcoin', 'value': 'btc' },
                                {'label': 'Synthetic', 'value': 'snx' },
                                {'label': 'Ripple', 'value': 'xrp'},    
                                {'label': 'Algorand', 'value': 'algo' }
                                
                                    ],
                            value='eth' 
                            ), 
    ),
    html.Div(className='boxset1', 
        children=[
            html.Div(className='box box1',
                children=[
                    html.Div(className='crypt-title', children='Crypto holding'),
                    html.Div(className='crypt-values', id='current-crypto-holding')
                ]
            ),
            html.Div(className='box box2',
                children=[
                    html.Div(className='crypt-title', children='Currently holding'),
                    html.Div(className='crypt-values', id='current-eur-holding')
                ]
            )
    ]),
    html.Div(className='boxset2',
    children=[
        html.Div(className='box box3',
            children=[
                html.Div(className='crypt-title', children='Current Investment'),
                html.Div(className='crypt-values', id='active-eur-investment')
            ]),
        html.Div(className='box box4',
            children=[
                html.Div(className='crypt-title', children='Current Profit (FIFO)'),
                html.Div(className='crypt-values', id='current-eur-profit')
            ])
    ])
])

@app.callback(
     Output(component_id='current-crypto-holding', component_property='children'),
     Input(component_id='curr-selection', component_property='value')
)
def update_holding(input_value):
    y = PNL('crypto', 'crypinvest', input_value)
    curr_holding = sum([x[0] for x in y.bought]) - sum([x[0] for x in y.sold])
    return "{0} {1} ".format(round(curr_holding, 5), input_value).upper()

@app.callback(
     Output(component_id='current-eur-holding', component_property='children'),
     Input(component_id='curr-selection', component_property='value')
)
def update_holding(input_value):
    y = PNL('crypto', 'crypinvest', input_value)
    curr_holding = (sum([x[0] for x in y.bought]) - sum([x[0] for x in y.sold])) * float(trading_client.ticker(input_value, 'eur')['ask'])
    return "{0} EUR ".format(round(curr_holding, 5))

@app.callback(
     Output(component_id='current-eur-profit', component_property='children'),
     Output(component_id='active-eur-investment', component_property='children'),
     Input(component_id='curr-selection', component_property='value')
)
def update_holding(input_value):
    y = PNL('crypto', 'crypinvest', input_value)
    curr_profit, curr_investment = y.profit_loss(y.bought, y.sold) 
    return "{0} EUR ".format(round(curr_profit, 5)), "{0} EUR ".format(round(curr_investment, 5)) 


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')