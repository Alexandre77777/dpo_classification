# Импорт необходимых библиотек
import streamlit as st
import requests
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas

# Заголовок приложения
st.title("Классификация изображений")

# Опция для выбора режима ввода изображения
mode = st.radio("Выберите способ ввода изображения:", ("Нарисовать изображение", "Загрузить изображение"))

if mode == "Загрузить изображение":
    # Загрузка изображения
    uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Создание колонок для размещения изображения и прогноза рядом
        col1, col2 = st.columns(2)

        with col1:
            # Отображение загруженного изображения
            image = Image.open(uploaded_file)
            st.image(image, caption="Загруженное изображение", use_column_width=True)

        # Подготовка изображения для отправки
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Отправка запроса на сервер FastAPI
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict/",
                files={"file": ("image.png", img_byte_arr, "image/png")}
            )
            response.raise_for_status()

            # Получение и отображение результата
            prediction = response.json()["prediction"]

            with col2:
                # Вывод предсказания с увеличенным размером шрифта
                st.markdown(
                    f"<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>"
                    f"<h1 style='font-size: 48px;'>{prediction}</h1>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка при отправке запроса: {e}")
        except ValueError as e:
            st.error(f"Ошибка при обработке ответа: {e}")

elif mode == "Нарисовать изображение":
    # Настройки для canvas
    stroke_width = st.slider("Толщина линии:", 1, 25, 9)

    # Размещаем выбор цвета линии и фона в одной строке
    col_color1, col_color2 = st.columns(2)
    with col_color1:
        stroke_color = st.color_picker("Цвет линии:", "#FFFFFF")
    with col_color2:
        bg_color = st.color_picker("Цвет фона:", "#000000")

    realtime_update = st.checkbox("Обновлять в реальном времени", True)

    # Создание колонок для размещения изображения и прогноза рядом
    col1, col2 = st.columns(2)

    with col1:
        # Создание canvas для рисования
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            update_streamlit=realtime_update,
            height=280,
            width=280,
            drawing_mode="freedraw",
            key="canvas",
        )

    if canvas_result.image_data is not None:
        # Преобразование данных холста в изображение
        image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')

        # Подготовка изображения для отправки
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Отправка запроса на сервер FastAPI
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict/",
                files={"file": ("image.png", img_byte_arr, "image/png")}
            )
            response.raise_for_status()

            # Получение и отображение результата
            prediction = response.json()["prediction"]

            with col2:
                # Вывод предсказания с увеличенным размером шрифта
                st.markdown(
                    f"<div style='display: flex; align-items: center; justify-content: center; height: 280px;'>"
                    f"<h1 style='font-size: 48px;'>{prediction}</h1>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка при отправке запроса: {e}")
        except ValueError as e:
            st.error(f"Ошибка при обработке ответа: {e}")