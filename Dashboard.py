from dash import dcc, html, Dash
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output
from collections import Counter #Needed for finding top products in certain categories
import base64


import pandas as pd

from Crud import TransactionData
connection_string = 'mongodb://localhost:27017/db.transactions'
DB = 'db'
COL = 'transactions'

image_filename = 'transaction.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#Define stylistic choices
background_color_blue = '#67b1e6'
background_color_gray='#36393d'

app = Dash(__name__)
db = TransactionData()
df = pd.DataFrame.from_records(db.read({}))

#Assign the key-value pairs globally in order to avoid positional argument errors
payment_options = dict(zip(df['Payment_Method'].unique(), df['Payment_Method'].unique()))
payment_options['All'] = 'All'
city_options = dict(zip(df['City'].unique(), df['City'].unique()))
city_options['All'] = 'All'
df.drop(columns=['_id'],inplace=True)


#HTML aspects contained here
app.layout = html.Div([
    html.Div([
        html.Header([
            html.Center([
                html.B(html.H1('Data Transaction Dashboard'), style={'backgroundColor': background_color_blue, 'fontFamily' : 'Trebuchet MS', 'font-size':'20px'}),
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width='250', height='250',style={'vertical-align': 'middle'})
                ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            html.Hr(),
            #Display filtering options (Dropdown bars)
            html.Div(className='row',
                    style={'display': 'flex'},
                    children=[
                        html.Div(
                            dcc.Dropdown(
                                id='payment-filter',
                                options=sorted(payment_options),
                                placeholder= 'Filter By Payment Type'
                            ),
                            style={'width': '20%'}
                        ),
                        html.Div(
                            dcc.Dropdown(
                                id='city_filter',
                                options = sorted(city_options),
                                placeholder = 'Filter By City'
                            ),
                            style={'width': '20%'}
                        )
                    ])
        ]),
        html.Hr(),
        dash_table.DataTable(
            id='datatable-id',
            columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
            data=df.to_dict('records'),
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="single",
            row_deletable=False,
            selected_columns=[],
            selected_rows=[0],
            page_action="native",
            page_current=0,
            page_size=20,
            fill_width=False,
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
            style_data={
                'backgroundColor': 'rgb(65, 65, 65)',
                'color': 'white'
            },
        ),
        html.Br(),
        html.Hr(),
        #Ensures both graphs are displayed side-by-side
        html.Div(className='row',
                 style={'display':'flex'},
                 children=[
                     html.Div(
                        id='graph-id',
                        className='col s12 m6',
                        style={'width': '40%'}
                    ),
                    html.Div(
                        id='pie-id',
                        className= 'col s12 m6',
                        style={'width': '40%'}
                    )])
                ], style={'backgroundColor': background_color_blue})
])

#Callback and function that updates dashboard upon filter selection
@app.callback([Output('datatable-id', 'data')],
              [Input('payment-filter', 'value'),
               Input('city_filter', 'value')])

def update_dashboard(payment_filter, city_filter):
    if payment_filter != 'All' and payment_filter != None:
        if city_filter != 'All' and city_filter != None:
            df = pd.DataFrame.from_records(db.read({"Payment_Method": payment_filter, "City": city_filter}))
        else:
            df = pd.DataFrame.from_records(db.read({"Payment_Method": payment_filter}))
    elif city_filter != 'All' and city_filter != None:
        df = pd.DataFrame.from_records(db.read({"City": city_filter}))
    else:
        df = pd.DataFrame.from_records(db.read({}))

    df.drop(columns=['_id'],inplace=True)
    return [df.to_dict('records')]
    
#Callback and function that updates bar chart upon filter selection
@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")])

def update_bar(viewData):
    if viewData is None:
        return
    
    df = pd.DataFrame.from_records(viewData)
    return [
        dcc.Graph(
            figure = px.histogram(df, x = 'City', y = 'Total_Cost', color = "Customer_Category",
                                   title = 'Total Spending Per Demographic', barmode='group')
                                   .update_layout(paper_bgcolor=background_color_blue)
        )
    ]

#Callback and function that updates pie chart upon filter selection
@app.callback(
    Output('pie-id', "children"),
    [Input('datatable-id', "derived_virtual_data")])

def update_pie(viewData):
    if viewData is None:
        return
    
    df = pd.DataFrame.from_records(viewData)
    transactionCounter = Counter(df['Product']).most_common(5) #Counts the top 5 most purchased products within filtering parameters and stores them in a dictionary
    top_products = [product[0] for product in transactionCounter] #product[0] accesses the product name(key)
    counts = [product[1] for product in transactionCounter] #product[1] accesses the count of occurrences of the product(value)
    return [
        dcc.Graph(
            figure= px.pie(df, values=counts,
                           names=top_products,
                           title= 'Top 5 Most Purchased Items'
            ).update_layout(paper_bgcolor=background_color_blue)
        )
    ]
    
if __name__ == '__main__':
    app.run(debug=True)