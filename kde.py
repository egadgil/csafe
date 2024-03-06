from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__, suppress_callback_exceptions=True)

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
    dcc.Graph(id='kde-plot-true'),  # KDE plot for is_match True
    dcc.Graph(id='kde-plot-false')  # KDE plot for is_match False
])

@app.callback(
    [Output('kde-plot-true', 'figure'),
     Output('kde-plot-false', 'figure')],
    [Input('metric-dropdown', 'value')]
)
def update_kde_plots(metric_value):
    if metric_value:
        true_data = data[(data['metric'] == metric_value) & (data['is_match'] == True)]['score']
        false_data = data[(data['metric'] == metric_value) & (data['is_match'] == False)]['score']

        kde_true = px.density_contour(true_data, x='score', title=f'KDE Plot for {metric_value} (is_match True)')
        kde_false = px.density_contour(false_data, x='score', title=f'KDE Plot for {metric_value} (is_match False)')

        kde_true.update_traces(contours_coloring='fill', contours_showlabels=False)
        kde_false.update_traces(contours_coloring='fill', contours_showlabels=False)

        return kde_true, kde_false
    else:
        empty_figure = px.scatter(title='Please select a metric')
        return empty_figure, empty_figure

if __name__ == '__main__':
    app.run_server(debug=True)
