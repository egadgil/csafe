from dash import Dash, dcc, html, Input, Output
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
    dcc.Markdown(id='ratio-display', style={'fontSize': 20, 'marginTop': 20})  # Display the details here using Markdown
])

# Callback to update the graph based on the selected metric and click data
@app.callback(
    [Output('combined-kde-plot', 'figure'),
     Output('ratio-display', 'children')],
    [Input('metric-dropdown', 'value'),
     Input('combined-kde-plot', 'clickData')]
)
def update_kde_plots_and_display_ratio(metric_value, clickData):
    fig = go.Figure()
    ratio_message = "Click on a point in the graph."

    if metric_value:
        # KDE plot preparation
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
            data['x_distance'] = abs(data['score'] - clicked_point_x)
            closest_points = data.sort_values(by='x_distance').head(5)
            closest_points_message = "### Top 5 closest points:\n" + "\n".join([
                        f"- **ID**: {row['cmpid']}, **Config**: {row['config']}, **Match**: {row['is_match']}, **Metric**: {row['metric']}, **Score**: {row['score']:.4f}, **Blur**: {row['blur']}, **Extractor**: {row['extractor']}" 
            for _, row in closest_points.iterrows()
        ])
        
        # Combine ratio text and closest points details
            ratio_message = ratio_text + closest_points_message

    return fig, ratio_message


if __name__ == '__main__':
    app.run_server(debug=True)
