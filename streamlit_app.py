import streamlit as st
from streamlit_functions import make_segments, run_analysis
from parser import parse_txt, extract_paragraphs, extract_character_names, extract_character_replicas, replace_ids_with_names


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


            paragraphs = extract_paragraphs(uploaded_file)
            st.divider()
            segments = make_segments(paragraphs, mode)

            # --- Общая эмоциональная динамика ---
            st.divider()
            st.subheader("📈 Эмоциональная динамика")

            if st.button("Построить эмоциональную арку"):
                run_analysis(segments, model_type, "Общая эмоциональная динамика")
          


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
                st.warning("Недостаточно данных по персонажам")
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
            st.divider()

            segments = make_segments(paragraphs, mode)

            # --- 3. Общая эмоциональная динамика ---
            st.divider()

            st.subheader("📈 Эмоциональная динамика")

            if st.button("Построить эмоциональную арку"):
                run_analysis(segments, model_type, f"Эмоциональная арка. {selected_character}")


elif data_mode == "TXT (один файл)":

    uploaded_file = st.file_uploader("Загрузите TXT файл", type=["txt"])
    if uploaded_file:
        st.success("Файл успешно загружен!")

        model_type = st.radio(
                "Выберите метод анализа тональности:",
                ["Лексиконный (RuSentiLex)", "Нейросетевой (RuBERT)"]
            )
        
        paragraphs = parse_txt(uploaded_file)
        st.divider()
        segments = make_segments(paragraphs, mode='txt')

        # --- 3. Общая эмоциональная динамика ---
        st.divider()
        st.subheader("📈 Эмоциональная динамика")

        if st.button("Построить эмоциональную арку"):
            run_analysis(segments, model_type, "Общая эмоциональная динамика")