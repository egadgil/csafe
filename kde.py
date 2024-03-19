from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import scipy.stats as stats
import plotly.graph_objects as go

app = Dash(__name__, suppress_callback_exceptions=True)

def update_shapes_and_hovertext(fig, hover_data):
    if hover_data:
        x_coord = hover_data['points'][0]['x']
        # Define the vertical line
        vertical_line = dict(
            type='line',
            x0=x_coord,
            x1=x_coord,
           y0=min(fig.data[0].y),
        y1=max(fig.data[0].y),
            line=dict(color='red', width=2)
        )
        fig.update_layout(shapes=[vertical_line])
     
# Assuming data is loaded similarly to your original code
data = pd.read_csv("results-viz.csv")
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

app.layout = html.Div([
    dcc.Dropdown(
        id='metric-dropdown',
        options=metric_options,
        placeholder="Select a metric"
    ),
    html.Div(id='dd-output-container'),
    dcc.Graph(id='combined-kde-plot')  # Single Graph for combined KDE plots
])


@app.callback(
    Output('combined-kde-plot', 'figure'),
    [Input('metric-dropdown', 'value'),
     Input('combined-kde-plot', 'hoverData')]
)
def update_kde_plots(metric_value, hover_data):
    if not metric_value:
        empty_figure = go.Figure()
        empty_figure.update_layout(title='Please select a metric')
        return empty_figure

    true_data = data[(data['metric'] == metric_value) & (data['is_match'] == True)]['score']
    false_data = data[(data['metric'] == metric_value) & (data['is_match'] == False)]['score']

    fig = go.Figure()

    # KDE for is_match True
    kde_true = stats.gaussian_kde(true_data)
    x_vals_true = true_data.sort_values()
    y_vals_true = kde_true(x_vals_true)
    fig.add_trace(go.Scatter(x=x_vals_true, y=y_vals_true, mode='lines', fill='tozeroy', name='is_match True', line=dict(color='red')))

    # KDE for is_match False
    kde_false = stats.gaussian_kde(false_data)
    x_vals_false = false_data.sort_values()
    y_vals_false = kde_false(x_vals_false)
    fig.add_trace(go.Scatter(x=x_vals_false, y=y_vals_false, mode='lines', fill='tozeroy', name='is_match False', line=dict(color='blue')))

    fig.update_layout(title=f'KDE Plot for {metric_value}', xaxis_title='Score', yaxis_title='Density')

    # Check if hoverData is provided and valid
    if hover_data and 'points' in hover_data and len(hover_data['points']) > 0:
        hover_x = hover_data['points'][0]['x']
        # Add vertical line at hover_x position
        fig.add_shape(type="line", x0=hover_x, y0=0, x1=hover_x, y1=1,
                      line=dict(color="Red", width=2), xref="x", yref="paper")

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)