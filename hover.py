
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

app = dash.Dash(__name__)

def plot_function(func, x_min, x_max):
    x_vals = np.linspace(x_min, x_max, 100)
    y_vals = func(x_vals)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines'))
    return fig

def plot_derivative(func, h, x_min, x_max):
    x_vals = np.linspace(x_min, x_max, 100)
    y_vals = (func(x_vals + h) - func(x_vals)) / h
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines'))
    return fig

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
        y0=min(fig.data[0].y),
        y1=max(fig.data[0].y),
        line=dict(color='red', width=2)
    )
    fig.update_layout(shapes=[vertical_line])

    # Add hover template
    hovertext = [f"x: {x_coord:.2f}" for _ in range(len(fig.data[0].x))]
    fig.data[0].update(hoverinfo='x+y', hovertext=hovertext)

app.layout = html.Div([
    dcc.Graph(id='function-plot'),
    dcc.Graph(id='derivative-plot'),
])

# ... (previous code)

@app.callback(
    [Output('function-plot', 'figure'),
     Output('derivative-plot', 'figure')],
    [Input('function-plot', 'hoverData'),
     Input('derivative-plot', 'hoverData')]
)
def update_layout(hover_data_function, hover_data_derivative):
    fig_function = plot_function(np.sin, -5, 5)
    fig_derivative = plot_derivative(np.sin, 0.01, -5, 5)

    x_coord_function = None
    x_coord_derivative = None
    
    if hover_data_function:
        x_coord_function = hover_data_function['points'][0]['x']
        update_shapes_and_hovertext(fig_function, x_coord_function)
        update_shapes_and_hovertext(fig_derivative, x_coord_function)

    if hover_data_derivative:
        x_coord_derivative = hover_data_derivative['points'][0]['x']
        update_shapes_and_hovertext(fig_derivative, x_coord_derivative)
        update_shapes_and_hovertext(fig_function, x_coord_derivative)

    return fig_function, fig_derivative


if __name__ == '__main__':
    app.run_server(debug=True)

