import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import paho.mqtt.client as mqtt
import plotly.graph_objs as go
import datetime
import dash_daq as daq 

# Global variables to store MQTT data and feed rate history
mqtt_data = {
    'Power On Time(in Mins)': 0,
    'Machine Mode': '',
    'Cycle Time': 0,
    'Spindle RPM Actual': 0,
    'Spindle Load': 0,
    'Feed Rate Override': 0,
    'Program name': '',
    'actblock': '',
    'Part Program': '',
    'Actual feed rate': 0,
    'Actual feed rate x': 0,  # New topic for X axis
    'Actual feed rate y': 0,  # New topic for Y axis
    'Actual feed rate z': 0,  # New topic for Z axis
    'Quality': 90,
    'Operating Time (in min)': 0,
    'No of parts': 0
}


feed_rate_history = []  # Store feed rate over time
time_history = []  # Store corresponding time values
mqtt_data['Operating Time (in min)'] = 0
mqtt_data['No of parts'] = 0 

feed_rate_history_x = []  # History for feed rate x
feed_rate_history_y = []  # History for feed rate y
feed_rate_history_z = []  # History for feed rate z

# Global variable to store OEE history
oee_history = []
oee_time_history = []



# MQTT broker details
BROKER = "localhost"
PORT = 1883

TOPICS = [
    ("Power On Time(in Mins)", 0),
    ("Machine Mode", 0),
    ("Cycle Time", 0),
    ("Spindle RPM Actual", 0),
    ("Spindle Load", 0),
    ("Feed Rate Override", 0),
    ("Program name", 0),
    ("actblock", 0),
    ("Part Program", 0),
    ("Actual feed rate", 0),
    ("Actual feed rate x", 0),  # Subscribe to new topic
    ("Actual feed rate y", 0),  # Subscribe to new topic
    ("Actual feed rate z", 0),  # Subscribe to new topic
    ("Operating Time (in min)", 0),
    ("No of parts", 0),
    ("Quality", 0)
]


# MQTT callback for when a message is received
def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode("utf-8")
    if topic in mqtt_data:
        mqtt_data[topic] = float(value) if value.replace('.', '', 1).isdigit() else value

# Set up MQTT client and connect
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)

# Subscribe to all topics
for topic, qos in TOPICS:
    client.subscribe(topic)

# Start MQTT loop in a separate thread
client.loop_start()

# Dash app initialization
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True  # Suppress callback exceptions

# Layout of the dashboard
app.layout = html.Div([

    dcc.Location(id='url', refresh=False),

    # Top section with Machine Name and Operator
    html.Div([
        html.H1("ASKAR FINE MILL 500", style={'text-align': 'center', 'display': 'inline-block', 'width': '75%', 'font-size': '55px', 'color': 'white'}),
        html.H2("Operator: Prakash", style={'text-align': 'right', 'display': 'inline-block', 'width': '25%','font-size': '30px'})
        ], style={'display': 'flex', 'justify-content': 'space-between', 'padding': '10px', 'background-color': '#67cb29'}),


    # Page Content will be rendered here
    html.Div(id='page-content'),

    # Interval component for real-time updates (every 2 seconds)
    dcc.Interval(
        id='interval-component',
        interval=0.5*1000,  # 2 seconds
        n_intervals=0  # Start at zero
    ),
])

# Reusable layout function with Back button
def create_page_layout(title, content):
    return html.Div([
        html.H2(title),
        content,  # Dynamic content passed for each page (Graph, Parameters, etc.)
        
        # Back button for all pages
        html.Div([
            dcc.Link('Back', href='/')
        ], style={'text-align': 'center', 'margin-top': '20px'})
    ])

# Layout for home page
home_page_layout = html.Div([
    html.Div([
        html.Div([
            html.H3("Machine Status", style={'font-size': '45px', 'backgroundColor': '#67cb29'}),
            html.P(id='power-status'),
            html.P(id='machine-mode')
        ], style={'border': '1px solid black', 'padding': '10px', 'width': '24%', 'float': 'right', 'text-align': 'center'}),

        html.Div([
            html.H3("Machining Parameters", style={'font-size': '45px', 'backgroundColor': '#67cb29'}),
            html.P(id='cycle-time'),
            html.P(id='spindle-rpm'),
            html.P(id='spindle-load'),
            html.P(id='feed-override')
        ], style={'border': '1px solid black', 'padding': '10px', 'width': '24%', 'float': 'right', 'text-align': 'center'}),

        html.Div([
            html.H3("Program Details", style={'font-size': '45px','backgroundColor': '#67cb29'}),
            html.P(id='program-name'),
            html.P(id='current-block')
        ], style={'border': '1px solid black', 'padding': '10px', 'width': '24%', 'float': 'right', 'text-align': 'center'}),

        html.Div([
            html.H3("CNC Program", style={'font-size': '45px','backgroundColor': '#67cb29'}),
            html.P(id='part-program')
        ], style={'border': '1px solid black', 'padding': '10px', 'width': '24%', 'float': 'right'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'padding': '10px','text-align': 'center'}),

    html.Br(),

    # Links to the other pages
    html.Div([
            dcc.Link('PERFORMANCE PARAMETERS', href='/performance', style={
            'margin': '20px', 
            'padding': '10px 20px', 
            'background-color': '#007bff',  # Blue for PERFORMANCE PARAMETERS
            'color': 'white', 
            'border-radius': '5px', 
            'text-decoration': 'none',  # Remove underline
            'display': 'inline-block'
        }),
            dcc.Link('FEED', href='/feed', style={
            'margin': '20px', 
            'padding': '10px 20px', 
            'background-color': '#28a745',  # Green for FEED
            'color': 'white', 
            'border-radius': '5px', 
            'text-decoration': 'none',  # Remove underline
            'display': 'inline-block'
        }),
            dcc.Link('OEE', href='/oee', style={
            'margin': '20px', 
            'padding': '10px 20px', 
            'background-color': '#dc3545',  # Red for OEE
            'color': 'white', 
            'border-radius': '5px', 
            'text-decoration': 'none',  # Remove underline
            'display': 'inline-block'
        })
        ], style={'text-align': 'center'}),


       ])


 

feed_page_layout = create_page_layout(
    "",
    html.Div([
        # Title section
        html.Div(
            "FEED",
            style={
                'textAlign': 'center',
                'fontSize': '36px',  # Increased font size for the title
                'color': '#f11130',  # Change text color as needed
                'backgroundColor': '#11eef1',  # Background color for the title
                'padding': '10px',  # Padding around the title
                'borderRadius': '5px'  # Optional: rounded corners
            }
        ),
        # Combined graph for all feed rates
        dcc.Graph(id='feed-rate-graph', config={'displayModeBar': False})  # Graph for combined feed rates
    ])
)




# Layout for OEE page with graph
oee_page_layout = create_page_layout(
    "",
        html.Div([
        # Title section
        html.Div(
            "OEE (%)",
            style={
                'textAlign': 'center',
                'fontSize': '36px',  # Increased font size for the title
                'color': '#f11130',  # Change text color as needed
                'backgroundColor': '#11eef1',  # Background color for the title
                'padding': '10px',  # Padding around the title
                'borderRadius': '5px'  # Optional: rounded corners
            }
        ),
    dcc.Graph(id='oee-graph')  # Placeholder for the OEE graph
        ])
)



performance_page_layout = create_page_layout(
    "",
    html.Div([

        # Title Section
        html.Div(
            "Performance Parameters",
            style={
                'textAlign': 'center',
                'fontSize': '36px',  # Increased font size for the title
                'color': '#f11130',  # Change text color as needed
                'backgroundColor': '#11eef1',  # Background color for the title
                'padding': '10px',  # Padding around the title
                'borderRadius': '5px'  # Optional: rounded corners
            }
        ),

                
        # Main container for styling
        html.Div([
            # Left half: Parameters
            html.Div([
                html.P(id='availability'), 
                html.P(id='productivity'),
                html.P(id='quality'),
                html.P(id='oee'),
                html.P(id='machine_downtime'),  # Machine Downtime
            ], style={
                'width': '50%', 
                'display': 'inline-block', 
                'vertical-align': 'top', 
                'padding': '20px'
            }),

            # Right half: Gauge
            html.Div([
                html.Div(
                    daq.Gauge(
                        id='oee_gauge',
                        value=0,  # Initial value
                        min=0,
                        max=100,
                        showCurrentValue=True,
                        style={
                            'margin': 'auto', 
                            'color': '#11eef1'  # Color for the gauge
                        }
                    ),
                    style={'text-align': 'center'}
                ),
                html.Div(
                    'Overall Equipment Efficiency (OEE)',  # The label
                    style={
                        'font-size': '24px',  # Adjust the font size here
                        'color': '#333',      # Text color
                        'backgroundColor': '#4dd60d',  # Background color for the label
                        'padding': '5px',     # Padding for the label
                        'border-radius': '5px',  # Optional: rounded corners
                        'text-align': 'center'  # Centering the label text
                    }
                )
            ], style={
                'width': '50%', 
                'display': 'inline-block', 
                'padding': '30px',
            }),
        ], style={
            'display': 'flex', 
            'justify-content': 'space-between', 
            'align-items': 'center', 
            'backgroundColor': '#f0f0f0',  # Background color for the whole section
            'padding': '20px',  # Padding for the entire container
            'border-radius': '10px'  # Optional: rounded corners
        }),

    ])
)



# Callback to handle page navigation
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/feed':
        return feed_page_layout
    elif pathname == '/performance':
        return performance_page_layout
    elif pathname == '/oee':
        return oee_page_layout
    else:
        return home_page_layout  # Default to the home page layout

   


# Callback to update the dashboard elements on the home page
@app.callback(
    [Output('power-status', 'children'),
     Output('machine-mode', 'children'),
     Output('cycle-time', 'children'),
     Output('spindle-rpm', 'children'),
     Output('spindle-load', 'children'),
     Output('feed-override', 'children'),
     Output('program-name', 'children'),
     Output('current-block', 'children'),
     Output('part-program', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    return [
        html.Div([
            html.Span("Power: ", style={'color': 'red', 'font-size': '30px'}),
            html.Span('On' if float(mqtt_data['Power On Time(in Mins)']) > 0 else 'Off', style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Machine Mode: ", style={'color': 'blue', 'font-size': '30px'}),
            html.Span('JOG' if mqtt_data['Machine Mode'] == 0 else 'MDI' if mqtt_data['Machine Mode'] == 1 else 'AUTO' if mqtt_data['Machine Mode'] == 2 else 'UNKNOWN', style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Cycle Time: ", style={'color': 'green', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['Cycle Time']} min", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Spindle RPM: ", style={'color': 'orange', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['Spindle RPM Actual']}", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Spindle Load: ", style={'color': 'purple', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['Spindle Load']}%", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Feed Override: ", style={'color': 'brown', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['Feed Rate Override']}%", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Program Name: ", style={'color': 'teal', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['Program name']}", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Current Block: ", style={'color': 'navy', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['actblock']}", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'}),
        
        html.Div([
            html.Span("Part Program: ", style={'color': 'maroon', 'font-size': '30px'}),
            html.Span(f"{mqtt_data['Part Program']}", style={'font-size': '30px'})
        ], style={'white-space': 'nowrap'})
    ]


@app.callback(
    Output('feed-rate-graph', 'figure'),  # Update output to the single graph
    [Input('interval-component', 'n_intervals')]
)
def update_feed_graphs(n):
    # Append current time to history
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    time_history.append(current_time)
    
    # Append MQTT data to history for X, Y, and Z
    feed_rate_history_x.append(mqtt_data.get('Actual feed rate x', 0))
    feed_rate_history_y.append(mqtt_data.get('Actual feed rate y', 0))
    feed_rate_history_z.append(mqtt_data.get('Actual feed rate z', 0))

    # Limit history to the last 50 points
    if len(time_history) > 50:
        time_history.pop(0)
        feed_rate_history_x.pop(0)
        feed_rate_history_y.pop(0)
        feed_rate_history_z.pop(0)

    # Create a single figure for all feed rates
    figure = go.Figure()

    # Add traces for each feed rate with increased line size
    figure.add_trace(go.Scatter(
        x=time_history,
        y=feed_rate_history_x,
        mode='lines',
        name='Feed Rate X',
        line=dict(width=3)  # Increase line width
    ))
    figure.add_trace(go.Scatter(
        x=time_history,
        y=feed_rate_history_y,
        mode='lines',
        name='Feed Rate Y',
        line=dict(width=3)  # Increase line width
    ))
    figure.add_trace(go.Scatter(
        x=time_history,
        y=feed_rate_history_z,
        mode='lines',
        name='Feed Rate Z',
        line=dict(width=3)  # Increase line width
    ))

    # Update layout with titles, legend position, and remove grid
    figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Feed Rate",
        legend=dict(
            orientation="v",  # Vertical orientation for legend
            x=1.05,  # Position legend to the right
            y=1
        ),
        xaxis=dict(showgrid=False),  # Remove grid lines from x-axis
        yaxis=dict(showgrid=False),   # Remove grid lines from y-axis
        width=1350,  # Set width of the graph (in pixels)
        height=550  # Set height of the graph (in pixels)
    )

    return figure  # Return the combined figure




@app.callback(
    [Output('availability', 'children'),
     Output('productivity', 'children'),
     Output('quality', 'children'),
     Output('oee', 'children'),
     Output('machine_downtime', 'children'),
     Output('oee_gauge', 'value')],
    [Input('interval-component', 'n_intervals')]
)




def update_metrics(n):
    # Calculate OEE
    operating_time = mqtt_data['Operating Time (in min)']
    power_on_time = mqtt_data['Power On Time(in Mins)']
    availability = (operating_time * 100 / (power_on_time * 60)) if power_on_time > 0 else 0
    quality = 90.0
    number_of_parts = mqtt_data['No of parts']
    productivity = (number_of_parts * 100 / 25) if number_of_parts > 0 else 0
    oee = (availability * quality * productivity) / 100
    
    # Machine Downtime
    cycletime = mqtt_data['Cycle Time'] if mqtt_data['Cycle Time'] > 0 else 1
    machine_downtime = ((operating_time - cycletime) * 100) / operating_time if operating_time > 0 else 0

    # Append the calculated OEE and current time to history
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    oee_history.append(oee)
    oee_time_history.append(current_time)

    # Limit history to the last 50 points
    if len(oee_history) > 50:
        oee_history.pop(0)
        oee_time_history.pop(0)

    # Create individual formatted strings for each metric
    availability_str = html.Div([
        html.Span("Availability: ", style={'font-size': '28px', 'color': '#19d546'}),
        html.Span(f'{availability:.2f}%', style={'font-size': '24px', 'color': 'black'})
    ])
    
    productivity_str = html.Div([
        html.Span("Productivity: ", style={'font-size': '28px', 'color': '#30d519'}),
        html.Span(f'{productivity:.2f}%', style={'font-size': '24px', 'color': 'black'})
    ])
    
    quality_str = html.Div([
        html.Span("Quality: ", style={'font-size': '28px', 'color': '#19d588'}),
        html.Span(f'{quality:.2f}%', style={'font-size': '24px', 'color': 'black'})
    ])
    
    oee_str = html.Div([
        html.Span("OEE: ", style={'font-size': '28px', 'color': '#1297de'}),
        html.Span(f'{oee:.2f}%', style={'font-size': '24px', 'color': 'black'})
    ])
    
    machine_downtime_str = html.Div([
        html.Span("Machine Downtime: ", style={'font-size': '28px', 'color': '#f50d09'}),
        html.Span(f'{machine_downtime:.2f}%', style={'font-size': '24px', 'color': 'black'})
    ])

    return (
        availability_str,
        productivity_str,
        quality_str,
        oee_str,
        machine_downtime_str,
        oee  # Update gauge value
    )





# Callback to update the OEE graph
@app.callback(
    Output('oee-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)

def update_oee_graph(n):
    # Create the OEE graph
    figure = go.Figure(
        data=[
            go.Scatter(x=oee_time_history, y=oee_history, mode='lines', name='OEE')
        ],
        layout=go.Layout(
            xaxis_title="Time",
            yaxis_title="OEE (%)",
            height=600
        )
    )
    
    
    return figure


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
