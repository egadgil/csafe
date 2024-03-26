from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import scipy.stats as stats
import numpy as np

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

# Define your Dash app layout
app.layout = html.Div([
    dcc.Dropdown(
        id='metric-dropdown',
        options=metric_options,
        placeholder="Select a metric"
    ),
    dcc.Graph(id='combined-kde-plot'),  # The graph for KDE plots
    html.Div(id='ratio-display', style={'fontSize': 20, 'marginTop': 20})  # Display the ratio here
])

# Callback to update the graph based on the selected metric and hover data
@app.callback(
    [Output('combined-kde-plot', 'figure'),
     Output('ratio-display', 'children')],
    [Input('metric-dropdown', 'value'),
     Input('combined-kde-plot', 'hoverData')]
)
def update_kde_plots_and_display_ratio(metric_value, hoverData):
    fig = go.Figure()
    ratio_message = "Hover over a point to see the ratio."

    if metric_value:
        true_data = data[(data['metric'] == metric_value) & (data['is_match'] == True)]['score']
        false_data = data[(data['metric'] == metric_value) & (data['is_match'] == False)]['score']

        kde_true = stats.gaussian_kde(true_data)
        kde_false = stats.gaussian_kde(false_data)
        x_vals = np.linspace(min(min(true_data), min(false_data)), max(max(true_data), max(false_data)), 1000)
        y_vals_true = kde_true(x_vals)
        y_vals_false = kde_false(x_vals)

        fig.add_trace(go.Scatter(x=x_vals, y=y_vals_true, mode='lines', fill='tozeroy', name='is_match True', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals_false, mode='lines', fill='tozeroy', name='is_match False', line=dict(color='blue')))

        fig.update_layout(title=f'KDE Plot for {metric_value}', xaxis_title='Score', yaxis_title='Density')

        if hoverData and 'points' in hoverData and len(hoverData['points']) > 0:
            hovered_point_x = hoverData['points'][0]['x']
            hovered_point_y_true = kde_true([hovered_point_x])[0]
            hovered_point_y_false = kde_false([hovered_point_x])[0]
            max_y_value = max(hovered_point_y_true, hovered_point_y_false)
            
            # Add vertical line at hovered x-coordinate
            fig.add_shape(type="line", x0=hovered_point_x, y0=0, x1=hovered_point_x, y1=max_y_value,
                          line=dict(color="Red", width=2),
                          xref="x", yref="y")

            # Calculate and display ratio if y_false is not 0
            if hovered_point_y_false != 0:
                ratio = hovered_point_y_true / hovered_point_y_false
                ratio_message = f"Ratio of densities (True/False) at x={hovered_point_x:.2f}: {ratio:.2f}"
            else:
                ratio_message = "Hovered point y_false is 0, cannot calculate ratio."

    return fig,ratio_message
if __name__ == '__main__':
    app.run_server(debug=True)