from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import scipy.stats as stats
import numpy as np
from dash import dash_table

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




# Define your Dash app layout
app.layout = html.Div([
    dcc.Dropdown(
        id='metric-dropdown',
        options=metric_options,
        value=None,  # Optionally set a default value
        placeholder="Select a metric"
    ),html.Div(id='ratio-display'),
    dcc.Graph(id='combined-kde-plot'),  # The graph for KDE plots
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
            # all three widths are needed
            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
            'whiteSpace': 'normal'
        }
    )
])


# Callback to update the graph based on the selected metric and click data
@app.callback(
    [Output('combined-kde-plot', 'figure'),
     Output('ratio-display', 'children'),
     Output('closest-points-table', 'data')],  # Add this line
    [Input('metric-dropdown', 'value'),
     Input('combined-kde-plot', 'clickData')]
)

def update_kde_plots_and_display_ratio(metric_value, clickData):
    fig = go.Figure()
    table_data = []
    ratio_message = "Click on a point in the graph."

    if metric_value:
        # KDE plot preparation
        filtered_data = data[data['metric'] == metric_value].copy()
        true_data = data[(data['metric'] == metric_value) & (data['is_match'] == True)]['score']
        false_data = data[(data['metric'] == metric_value) & (data['is_match'] == False)]['score']
        kde_true = stats.gaussian_kde(true_data)
        kde_false = stats.gaussian_kde(false_data)
        x_vals = np.linspace(min(min(true_data), min(false_data)), max(max(true_data), max(false_data)), 1000)
        y_vals_true = kde_true(x_vals)
        y_vals_false = kde_false(x_vals)

        fig.add_trace(go.Scatter(x=x_vals, y=y_vals_true, mode='lines', fill='tozeroy', name='True', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals_false, mode='lines', fill='tozeroy', name='False', line=dict(color='blue')))
        fig.update_layout(title=f'KDE Plot for {metric_value}', xaxis_title='Score', yaxis_title='Density')

        if clickData and 'points' in clickData and len(clickData['points']) > 0:
            clicked_point_x = clickData['points'][0]['x']
            clicked_point_y_true = kde_true([clicked_point_x])[0]
            clicked_point_y_false = kde_false([clicked_point_x])[0]
            max_y_value = max(clicked_point_y_true, clicked_point_y_false)
            # Mark the clicked x-coordinate with a vertical line
            

            # Calculate and display ratio of densities at the clicked x-coordinate
            
            fig.add_shape(type="line", x0=clicked_point_x, y0=0, x1=clicked_point_x, y1=max_y_value,
                          line=dict(color="Red", width=2),
                          xref="x", yref="y")
            if clicked_point_y_false != 0:
                ratio = clicked_point_y_true / clicked_point_y_false
                ratio_text = f"At x={clicked_point_x:.2f}: ratio of densities is {ratio:.2f}\n\n "
            else:
                ratio_text = "Ratio cannot be calculated (division by zero).\n\n"
            
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
