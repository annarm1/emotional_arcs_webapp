import streamlit as st
from parser import parse_txt, extract_paragraphs, extract_character_names, extract_character_replicas, replace_ids_with_names
from utils import smooth_signal, plot_curve_interactive
from segmentation import segmentation_settings_ui, segments_by_paragraphs, apply_overlap, prepare_segments_for_download
from sentiment_model import run_analysis
from lexicon import lexicon_settings_ui

def reset_analysis_state(current_key):

    if (
        "analysis_key" not in st.session_state
        or st.session_state["analysis_key"] != current_key
    ):
        st.session_state.pop("sentiments", None)
        st.session_state.pop("segments", None)

        st.session_state["analysis_key"] = current_key


with st.spinner("Загрузка модели..."):
    from sentiment_model import load_model
    load_model()


st.title("📊 Анализ эмоциональной динамики текста")

data_mode = st.radio(
    "Выберите тип входных данных",
    ["TXT (один файл)", "TEI (XML) — с возможностью анализа речи персонажей"]
)

if data_mode == "TEI (XML) — с возможностью анализа речи персонажей":

    mode = st.radio(
        "Выберите тип анализа",
        ["Общая сюжетная арка", "Арка персонажа"]
    )

    # --------------СЮЖЕТНАЯ АРКА-----------------
    if mode == "Общая сюжетная арка":
        uploaded_file = st.file_uploader(
                "Загрузите документ с TEI-разметкой",
                type=["xml"]
            )

        if uploaded_file:
            st.success("Файл успешно загружен!")

            model_type = st.radio(
                "Выберите метод анализа тональности:",
                ["Лексиконный (RuSentiLex)", "Нейросетевой (RuBERT)"]
            )
            
            if model_type == 'Лексиконный (RuSentiLex)':
                lexicon = lexicon_settings_ui()

            paragraphs = extract_paragraphs(uploaded_file)

            min_words, max_words, use_overlap, overlap_sentences = (
                segmentation_settings_ui(paragraphs, mode)
            )

            current_analysis_key = (
                uploaded_file.name,
                min_words,
                max_words,
                use_overlap,
                overlap_sentences,
                model_type
            )

            reset_analysis_state(current_analysis_key)

            segments = segments_by_paragraphs(
                paragraphs,
                min_words,
                max_words
            )

            if use_overlap:
                segments = apply_overlap(
                    segments,
                    overlap_sentences
                )

            st.session_state["segments"] = segments
                
            if st.button('Сегментировать текст'):
                with st.spinner('Сегментируем и анализируем текст...'):
                    sentiments = run_analysis(segments, model_type, lexicon)
                    st.session_state["sentiments"] = sentiments
            if "sentiments" in st.session_state:
                prepare_segments_for_download(
                    st.session_state["segments"],
                    st.session_state["sentiments"]
                )

                st.divider()

                st.subheader("Построение графика")

                smoothed_sentiments = smooth_signal(
                    st.session_state["sentiments"]
                )

                fig = plot_curve_interactive(
                    smoothed_sentiments,
                    st.session_state["sentiments"],
                    'Общая эмоциональная динамика'
                )

                st.plotly_chart(fig, use_container_width=True)
                

        # --------------АРКИ ПЕРСОНАЖЕЙ------------
    elif mode == "Арка персонажа":
        uploaded_file = st.file_uploader(
                "Загрузите документ с TEI-разметкой",
                type=["xml"]
            )
        
        if uploaded_file:
            st.success("Файл успешно загружен!")

            model_type = st.radio(
                "Выберите метод анализа тональности:",
                ["Лексиконный (RuSentiLex)", "Нейросетевой (RuBERT)"]
            )
            
            character_map = extract_character_names(uploaded_file)
            uploaded_file.seek(0)
            replicas = extract_character_replicas(uploaded_file)
            replicas = replace_ids_with_names(replicas, character_map)
            
            if not replicas:
                st.warning("Недостаточно данных по персонажам или в файле применяются отличные от <speaker> теги для обозначения прямой речи")
                st.stop()
            
            # сортировка по количеству реплик
            characters = sorted(replicas.keys(), key=lambda x: len(replicas[x]), reverse=True)

            selected = st.selectbox(
                "Выберите персонажа",
                characters
            )

            selected_character = selected.split(" (")[0]
            char_replicas = replicas[selected_character]

            st.write(
            f"Количество реплик: {len(char_replicas)}"
            )


            paragraphs = char_replicas

            min_words, max_words, use_overlap, overlap_sentences = (
                segmentation_settings_ui(paragraphs, mode)
            )


            current_analysis_key = (
                uploaded_file.name,
                min_words,
                max_words,
                use_overlap,
                overlap_sentences,
                model_type
            )

            reset_analysis_state(current_analysis_key)

            segments = segments_by_paragraphs(
                paragraphs,
                min_words,
                max_words
            )

            if use_overlap:
                segments = apply_overlap(
                    segments,
                    overlap_sentences
                )

            st.session_state["segments"] = segments
                
            if st.button('Сегментировать текст'):
                with st.spinner('Сегментируем и анализируем текст...'):
                    sentiments = run_analysis(segments, model_type)
                    st.session_state["sentiments"] = sentiments
            if "sentiments" in st.session_state:
                prepare_segments_for_download(
                    st.session_state["segments"],
                    st.session_state["sentiments"]
                )

                st.divider()

                st.subheader("График эмоциональной динамики")

                smoothed_sentiments = smooth_signal(
                    st.session_state["sentiments"]
                )

                fig = plot_curve_interactive(
                    smoothed_sentiments,
                    st.session_state["sentiments"],
                    f'Эмоциональная динамика {selected_character}'
                )

                st.plotly_chart(fig, use_container_width=True)


elif data_mode == "TXT (один файл)":

    uploaded_file = st.file_uploader("Загрузите TXT файл", type=["txt"])
    if uploaded_file:
        st.success("Файл успешно загружен!")

        model_type = st.radio(
                "Выберите метод анализа тональности:",
                ["Лексиконный (RuSentiLex)", "Нейросетевой (RuBERT)"]
            )
        
        paragraphs = parse_txt(uploaded_file)

        mode = 'txt'
        min_words, max_words, use_overlap, overlap_sentences = (
            segmentation_settings_ui(paragraphs, mode)
        )
        
        
        current_analysis_key = (
            uploaded_file.name,
            min_words,
            max_words,
            use_overlap,
            overlap_sentences,
            model_type
        )

        reset_analysis_state(current_analysis_key)
        
        segments = segments_by_paragraphs(
            paragraphs,
            min_words,
            max_words
        )

        if use_overlap:
            segments = apply_overlap(
                segments,
                overlap_sentences
            )

        st.session_state["segments"] = segments
                
        if st.button('Сегментировать текст'):
            with st.spinner('Сегментируем и анализируем текст...'):
                sentiments = run_analysis(segments, model_type)
                st.session_state["sentiments"] = sentiments
        if "sentiments" in st.session_state:
            prepare_segments_for_download(
                st.session_state["segments"],
                st.session_state["sentiments"]
            )

            st.divider()

            st.subheader("Построение графика")

            smoothed_sentiments = smooth_signal(
                st.session_state["sentiments"]
            )

            fig = plot_curve_interactive(
                smoothed_sentiments,
                st.session_state["sentiments"],
                'Общая эмоциональная динамика'
            )

            st.plotly_chart(fig, use_container_width=True)