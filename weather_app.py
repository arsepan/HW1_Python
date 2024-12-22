import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

def get_current_temperature(city, api_key):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return data['main']['temp']
        else:
            st.error(f"Ошибка: {data.get('message', 'Invalid API key')}")
            return None
    except Exception as e:
        st.error(f'Произошла ошибка: {e}')
        return None

def is_temperature_anomalous(city_data, temp):
    temp_mean = city_data['temperature'].mean()
    temp_std = city_data['temperature'].std()
    lower_bound = temp_mean - 2 * temp_std
    upper_bound = temp_mean + 2 * temp_std
    
    if temp < lower_bound or temp > upper_bound:
        return True, lower_bound, upper_bound
    return False, lower_bound, upper_bound


def main():
    st.title('Приложение: Анализ Погоды')

    api_key = st.text_input('Введите ваш OpenWeatherMap API Key:')
    if not api_key:
        st.warning('Введите API-ключ для получения текущей погоды')

    st.subheader('Загрузите данные о температуре')
    uploaded_file = st.file_uploader('Загрузите файл CSV с историческими данными (city, timestamp, temperature)', type='csv')

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write('Пример данных:')
        st.write(data.head(3))

        city_selection = st.selectbox('Выберите город:', options=data['city'].unique())
        city_data = data[data['city'] == city_selection]
        
        st.write(f'Данные для города: {city_selection}')
        st.dataframe(city_data)
        st.subheader('Описательная статистика по историческим данным')
        st.write(city_data.describe())

        st.subheader('Временной ряд температур')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(pd.to_datetime(city_data['timestamp']), city_data['temperature'], label='Температура')
        ax.set_title(f'Временной ряд температур для {city_selection}')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Температура')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.subheader('Сезонные профили')
        city_data['month'] = pd.to_datetime(city_data['timestamp']).dt.month
        seasonal_profile = city_data.groupby('month')['temperature'].agg(['mean', 'std']).reset_index()
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.bar(seasonal_profile['month'], seasonal_profile['mean'], yerr=seasonal_profile['std'], label='Средняя температура', alpha=0.7, capsize=5)
        ax.set_title(f'Сезонные профили температуры для {city_selection}')
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Температура')
        st.pyplot(fig)

        if api_key:
            curr_temp = get_current_temperature(city_selection, api_key)
            if curr_temp is not None:
                st.write(f'Текущая температура в городе {city_selection}: {curr_temp}')

                anomalous, lower_bound, upper_bound = is_temperature_anomalous(city_data, curr_temp)
                if anomalous:
                    st.error(f'Температура {curr_temp} градусов по Цельсию является аномальной. Нормальный диапазон: {lower_bound:.2f} : {upper_bound:.2f}')
                else:
                    st.success(f'Температура {curr_temp} градусов по Цельсию является нормальной. Нормальный диапазон: {lower_bound:.2f} : {upper_bound:.2f}')

if __name__ == '__main__':
    main()