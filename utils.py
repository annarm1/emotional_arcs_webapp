import numpy as np
import plotly.graph_objects as go
from scipy.signal import savgol_filter


def smooth_signal(sentiments):
    filtered_sentiments = savgol_filter(sentiments, window_length=len(sentiments)//15, polyorder=0)
    return filtered_sentiments


def normalize_positions(n):
    return np.linspace(0, 1, n)


def plot_curve_interactive(smoothed, title=""):
    x = list(range(1, len(smoothed) + 1))  # номера сегментов

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=smoothed,
        mode='lines',
        name='Тональность',
        text=[f"Сегмент {i}" for i in x],
        hoverinfo="text+y"
    ))

    # линия нуля
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
    )

    fig.update_layout(
        title=title,
        xaxis_title="Номер сегмента",
        yaxis_title="Тональность",
        template="plotly_white"
    )

    return fig