from dash import Dash, dcc, html, Input, Output, callback_context
import plotly.graph_objects as go
import pandas as pd
import scipy.stats as stats
import numpy as np

# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=False)

# Load your data
data = pd.read_csv("results-viz.csv")
def update_shapes_and_hovertext(fig, x_coord):
    # Remove the vertical line if x_coord is None
    if x_coord is None:
        fig.update_layout(shapes=[])
        return

    # Add a vertical line at the hovered x-coordinate
    vertical_line = dict(
        type='line',
        x0=x_coord,
        x1=x_coord,
        y0=0,
        y1=max(fig.data[0].y),
        line=dict(color='red', width=2)
    )
    fig.update_layout(shapes=[vertical_line])

    # Add hover template
    hovertext = [f"x: {x_coord:.2f}" for _ in range(len(fig.data[0].x))]
    fig.data[0].update(hoverinfo='x+y', hovertext=hovertext)
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
    dcc.Graph(id='combined-kde-plot')  # The graph for KDE plots
])

# Define the server-side callback for updating the graph based on the selected metric
@app.callback(
    Output('combined-kde-plot', 'figure'),
    [Input('metric-dropdown', 'value'),
     Input('combined-kde-plot', 'hoverData')]  # Assuming hoverData is the property and 'graph-id' is the ID of the graph component
)
def update_kde_plots(metric_value,hover_data):
    if metric_value:
        true_data = data[(data['metric'] == metric_value) & (data['is_match'] == True)]['score']
        false_data = data[(data['metric'] == metric_value) & (data['is_match'] == False)]['score']

        fig = go.Figure()

        # Plot for is_match True in red
        kde_true = stats.gaussian_kde(true_data)
        x_vals_true = np.linspace(min(true_data), max(true_data), 1000)
        y_vals_true = kde_true(x_vals_true)
        fig.add_trace(go.Scatter(x=x_vals_true, y=y_vals_true, mode='lines', fill='tozeroy', name='is_match True', line=dict(color='red')))

        # Plot for is_match False in blue
        kde_false = stats.gaussian_kde(false_data)
        x_vals_false = np.linspace(min(false_data), max(false_data), 1000)
        y_vals_false = kde_false(x_vals_false)
        fig.add_trace(go.Scatter(x=x_vals_false, y=y_vals_false, mode='lines', fill='tozeroy', name='is_match False', line=dict(color='blue')))

        fig.update_layout(title=f'KDE Plot for {metric_value}', xaxis_title='Score', yaxis_title='Density')
        if hover_data:
         x_coord_derivative = hover_data['points'][0]['x']
         if x_coord_derivative is not None:
        # Evaluate the y-coordinate for the KDE plots at x_coord_derivative
          y_val_true = kde_true(x_coord_derivative)[0]  # Evaluate KDE for true_data
          y_val_false = kde_false(x_coord_derivative)[0]  # Evaluate KDE for false_data

        # Determine the maximum y-value to extend the vertical line
          max_y_val = max(y_val_true, y_val_false)

        # Define the vertical line with updated y1 to match the KDE plot's y-coordinate
          vertical_line = dict(
            type='line',
            x0=x_coord_derivative,
            x1=x_coord_derivative,
            y0=0,
            y1=max_y_val,  # Updated to extend to the correct y-value
            line=dict(color='red', width=2)
        )
          fig.update_layout(shapes=[vertical_line])

        # Add hover template
          
          
         return fig
        else:
         return fig

# Define the clientside callback for adding a dynamic hover line

if __name__ == '__main__':
    app.run_server(debug=True)
