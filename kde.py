from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import scipy.stats as stats
import numpy as np
from dash import dash_table
from dash.exceptions import PreventUpdate
# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=False)

# Load your data
data = pd.read_csv("results-viz.csv")

# Define options for the dropdown based on your metrics
metric_options = [
    {'label': 'nearest_points', 'value': 'nearest_points'},
    {'label': 'clique_size', 'value': 'clique_size'},
    {'label': 'time', 'value': 'time'},
    {'label': 'ImagePOC', 'value': 'ImagePOC'},
    {'label': 'clique_fraction', 'value': 'clique_fraction'},
    {'label': 'median_distance', 'value': 'median_distance'},
    {'label': 'overlap_percentage', 'value': 'overlap_percentage'},
    {'label': 'ImageNCC', 'value': 'ImageNCC'},
    {'label': 'MCNCC', 'value': 'MCNCC'},
    {'label': 'MCPOC', 'value': 'MCPOC'}
]
extractor_options = [
    {'label': 'AKAZE', 'value': 'AKAZE'},
    {'label': 'CENSURE', 'value': 'CENSURE'},
    {'label': 'FAST', 'value': 'FAST'},
    {'label': 'KAZE', 'value': 'KAZE'},
    {'label': 'Shi-Tomasi', 'value': 'Shi-Tomasi'},
    {'label': 'SIFT', 'value': 'SIFT'},
    {'label': 'SIFT+AKAZE', 'value': 'SIFT+AKAZE'},
    {'label': 'SIFT+CENSURE', 'value': 'SIFT+CENSURE'},
    {'label': 'SIFT+FAST', 'value': 'SIFT+FAST'},
    {'label': 'SIFT+Fast+AKAZE', 'value': 'SIFT+Fast+AKAZE'},
    {'label': 'SIFT+Fast+KAZE', 'value': 'SIFT+Fast+KAZE'},
    {'label': 'SIFT+KAZE', 'value': 'SIFT+KAZE'},
    {'label': 'SIFT+KAZE+AKAZE', 'value': 'SIFT+KAZE+AKAZE'}
]

combined_options = [
    {'label': 'Metric: ' + option['label'], 'value': 'metric-' + option['value']}
    for option in metric_options
] + [
    {'label': 'Extractor: ' + option['label'], 'value': 'extractor-' + option['value']}
    for option in extractor_options
]



# Define your Dash app layout
# Define your Dash app layout
app.layout = html.Div([
    dcc.Dropdown(
        id='combined-metric-extractor-dropdown',
        options=combined_options,
        multi=True,
        placeholder="Select one metric and one extractor",    
    ),
    dcc.Graph(id='combined-kde-plot'),  # The graph for KDE plots
    html.Div(id='ratio-display'),  # The ratio message
    dash_table.DataTable(
        id='closest-points-table',
        columns=[  # Initial columns
            {'name': 'ID', 'id': 'cmpid'},
            {'name': 'Config', 'id': 'config'},
            {'name': 'Match', 'id': 'is_match'},
            {'name': 'Metric', 'id': 'metric'},
            {'name': 'Score', 'id': 'score'},
            {'name': 'Blur', 'id': 'blur'},
            {'name': 'Extractor', 'id': 'extractor'}
        ],
        data=[],  
        style_table={'overflowX': 'auto'},
        style_cell={
            'height': 'auto',
            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
            'whiteSpace': 'normal'
        }
    )
])



# Callback to update the graph based on the selected metric and click data
@app.callback(
    [Output('combined-kde-plot', 'figure'),
     Output('ratio-display', 'children'),
     Output('closest-points-table', 'data')],
    [Input('combined-metric-extractor-dropdown', 'value'),
     Input('combined-kde-plot', 'clickData')]
)

def update_kde_plots_and_display_ratio(selected_options, clickData):
   
    fig = go.Figure()
    table_data = []
    ratio_message = "Select exactly one metric and one extractor."

    if not selected_options or len(selected_options) > 2:
        # Prevent the update if the selection rule is violated
        ratio_message = "Please select exactly one metric and one extractor."
        fig.update_layout(title="Invalid selection", xaxis_title='Score', yaxis_title='Density')
        return fig, ratio_message, table_data

    selected_metric = None
    selected_extractor = None
    for option in selected_options:
        if option.startswith('metric-') and not selected_metric:
            selected_metric = option.replace('metric-', '')
        elif option.startswith('extractor-') and not selected_extractor:
            selected_extractor = option.replace('extractor-', '')

    # Ensure one metric and one extractor are selected
    if not selected_metric and selected_extractor:
        ratio_message = "Please select both a metric and an extractor."
        fig.update_layout(title="Incomplete selection", xaxis_title='Score', yaxis_title='Density')
        return fig, ratio_message, table_data

    if selected_metric and selected_extractor:
        # KDE plot preparation
        filtered_data = data[(data['metric'] == selected_metric) & (data['extractor'] == selected_extractor)].copy()
       
        true_data = filtered_data[filtered_data['is_match'] == True]['score']
        false_data = filtered_data[filtered_data['is_match'] == False]['score']

        kde_true = stats.gaussian_kde(true_data)
        kde_false = stats.gaussian_kde(false_data)
        x_vals = np.linspace(min(min(true_data), min(false_data)), max(max(true_data), max(false_data)), 1000)
        y_vals_true = kde_true(x_vals)
        y_vals_false = kde_false(x_vals)

        fig.add_trace(go.Scatter(x=x_vals, y=y_vals_true, mode='lines', fill='tozeroy', name='True', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals_false, mode='lines', fill='tozeroy', name='False', line=dict(color='red')))
        fig.update_layout(title=f'KDE Plot for {selected_metric,selected_extractor}', xaxis_title='Score', yaxis_title='Density')

        if clickData and 'points' in clickData and len(clickData['points']) > 0:
            clicked_point_x = clickData['points'][0]['x']
            clicked_point_y_true = kde_true([clicked_point_x])[0]
            clicked_point_y_false = kde_false([clicked_point_x])[0]
            max_y_value = max(clicked_point_y_true, clicked_point_y_false)
            # Mark the clicked x-coordinate with a vertical line
            

            # Calculate and display ratio of densities at the clicked x-coordinate
            
            
            if clicked_point_y_false != 0:
                ratio = clicked_point_y_true / clicked_point_y_false
                ratio_text = (f"At Score={clicked_point_x:.2f}: the ratio of densities is {ratio:.2f}.\n\n")
                
            else:
                ratio_text = "Ratio cannot be calculated (division by zero).\n\n"
               
            
            if ratio>1:
              fig.add_shape(type="line", x0=clicked_point_x, y0=0, x1=clicked_point_x, y1=max_y_value,
                          line=dict(color="Blue", width=2),
                          xref="x", yref="y")
            else:
               fig.add_shape(type="line", x0=clicked_point_x, y0=0, x1=clicked_point_x, y1=max_y_value,
                          line=dict(color="Red", width=2),
                          xref="x", yref="y")
            # Identify and display the top 5 closest points
            filtered_data['x_distance'] = abs(filtered_data['score'] - clicked_point_x)
            closest_points = filtered_data.sort_values(by='x_distance').head(5)
            
            table_data = closest_points.to_dict('records')
        # Combine ratio text and closest points details
            ratio_message = ratio_text 
            
    else:
        # Optionally, you can adjust the figure or other outputs to indicate that no data is available
        fig.update_layout(title="No metric selected", xaxis_title='Score', yaxis_title='Density')


    return fig, ratio_message,table_data


if __name__ == '__main__':
    app.run_server(debug=True)
