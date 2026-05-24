import plotly.graph_objects as go
from scipy.signal import savgol_filter
import streamlit as st


def smooth_signal(sentiments):
    filter_user = st.checkbox('Добавить сглаживание', value=True)

    st.info(
        "Сглаживание уменьшает локальные колебания тональности "
        "и позволяет выделить общую эмоциональную динамику произведения. "
        "Для обработки используется фильтр Савицкого — Голея, " \
        "принцип которого заключается в усреднении значения в окне арки данных. "
        "Чем сильнее сглаживание, тем менее заметны кратковременные "
        "эмоциональные всплески, но тем лучше видна общая тенденция."
        
    )

    if filter_user:
        max_window = max(
            5,
            len(sentiments) // 3
        )

        if max_window % 2 == 0:
            max_window -= 1

        
        smoothing_percent = st.slider(
            "Степень сглаживания (%)",
            min_value=1,
            max_value=35,
            value=10,
            step=1,
            help=(
                "Размер окна сглаживания "
                "относительно длины эмоциональной арки."
            )
        )

        window_length = int(len(sentiments) * smoothing_percent / 100)
        filtered_sentiments = savgol_filter(sentiments, window_length, polyorder=0)
        window_percent = round(
            window_length / len(sentiments) * 100
        )

        st.caption(
            f"Текущее окно сглаживания: "
            f"{window_percent}% от длины арки"
)
        return filtered_sentiments
    
    else:
        return sentiments


def plot_curve_interactive(smoothed, sentiments, title):
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