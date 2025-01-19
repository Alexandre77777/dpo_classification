# Импорт необходимых библиотек
import streamlit as st  # Для создания веб-приложения
import requests  # Для отправки HTTP-запросов
from PIL import Image  # Для работы с изображениями
import io  # Для работы с потоками ввода/вывода
from streamlit_drawable_canvas import st_canvas  # Для создания интерактивного холста

# Заголовок приложения
st.title("Классификация изображений")  # Отображение заголовка приложения

# Опция для выбора режима ввода изображения
mode = st.radio("Выберите способ ввода изображения:", ("Нарисовать изображение", "Загрузить изображение"))

# Функция для отправки изображения на сервер и получения предсказания
def get_prediction(image_data):
    """
    Отправляет изображение на сервер FastAPI и возвращает предсказание.
    """
    try:
        # Отправка POST-запроса с изображением
        response = requests.post(
            "https://dpo-classification.onrender.com/predict/",
            files={"file": ("image.png", image_data, "image/png")}
        )
        response.raise_for_status()  # Проверка на наличие ошибок HTTP
        return response.json()["prediction"]  # Возврат предсказания из ответа
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при отправке запроса: {e}")  # Обработка ошибок запроса
    except ValueError as e:
        st.error(f"Ошибка при обработке ответа: {e}")  # Обработка ошибок ответа
    return None

# Обработка режима "Загрузить изображение"
if mode == "Загрузить изображение":
    # Загрузка изображения через интерфейс
    uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Создание колонок для отображения изображения и предсказания
        col1, col2 = st.columns(2)

        with col1:
            # Отображение загруженного изображения
            image = Image.open(uploaded_file)
            st.image(image, caption="Загруженное изображение", use_container_width=True)  # Используем use_container_width вместо use_column_width

        # Преобразование изображения в байтовый поток
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Получение предсказания
        prediction = get_prediction(img_byte_arr)

        if prediction:
            with col2:
                # Отображение предсказания с увеличенным шрифтом
                st.markdown(
                    f"<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>"
                    f"<h1 style='font-size: 48px;'>{prediction}</h1>"
                    f"</div>",
                    unsafe_allow_html=True
                )

# Обработка режима "Нарисовать изображение"
elif mode == "Нарисовать изображение":
    # Настройки для холста
    stroke_width = st.slider("Толщина линии:", 1, 25, 9)  # Выбор толщины линии

    # Размещение выбора цвета линии и фона в одной строке
    col_color1, col_color2 = st.columns(2)
    with col_color1:
        stroke_color = st.color_picker("Цвет линии:", "#FFFFFF")  # Выбор цвета линии
    with col_color2:
        bg_color = st.color_picker("Цвет фона:", "#000000")  # Выбор цвета фона

    realtime_update = st.checkbox("Обновлять в реальном времени", True)  # Опция обновления в реальном времени

    # Создание колонок для отображения холста и предсказания
    col1, col2 = st.columns(2)

    with col1:
        # Создание интерактивного холста для рисования
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",  # Цвет заливки (прозрачный)
            stroke_width=stroke_width,  # Толщина линии
            stroke_color=stroke_color,  # Цвет линии
            background_color=bg_color,  # Цвет фона
            update_streamlit=realtime_update,  # Обновление в реальном времени
            height=280,  # Высота холста
            width=280,  # Ширина холста
            drawing_mode="freedraw",  # Режим рисования
            key="canvas",  # Уникальный ключ для холста
        )

    if canvas_result.image_data is not None:
        # Преобразование данных холста в изображение
        image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')

        # Преобразование изображения в байтовый поток
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Получение предсказания
        prediction = get_prediction(img_byte_arr)

        if prediction:
            with col2:
                # Отображение предсказания с увеличенным шрифтом
                st.markdown(
                    f"<div style='display: flex; align-items: center; justify-content: center; height: 280px;'>"
                    f"<h1 style='font-size: 48px;'>{prediction}</h1>"
                    f"</div>",
                    unsafe_allow_html=True
                )