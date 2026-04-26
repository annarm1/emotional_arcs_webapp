import numpy as np
import plotly.graph_objects as go
from scipy.signal import savgol_filter


def smooth_signal(sentiments):
    filtered_sentiments = savgol_filter(sentiments, window_length=len(sentiments)//15, polyorder=0)
    return filtered_sentiments

def plot_curve_interactive(smoothed, sentiments, title=""):
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
        line_width=2
    )

    # линия средней тональности
    fig.add_hline(
        y=sum(sentiments)/len(sentiments),
        line_dash="dot",
        line_color="orange",
        line_width=2
    )

    fig.update_layout(
        title=title,
        xaxis_title="Номер сегмента",
        yaxis_title="Тональность",
        template="plotly_white"
    )

    return fig