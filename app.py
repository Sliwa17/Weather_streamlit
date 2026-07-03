from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.charts import (
    CITY_LABELS,
    bar_city_ranking,
    boxplot_city,
    heatmap_weekday_month,
    histogram_temperature,
    line_temperature,
    map_weather,
    scatter_temp_precip,
)
from src.data_utils import POLISH_CITIES, clean_weather_data, fetch_weather_for_cities, filter_weather_data

st.set_page_config(
    page_title="Analiza pogody w polskich miastach",
    page_icon="🌦️",
    layout="wide",
)

st.title("🌦️ Analiza pogody w polskich miastach")
st.markdown(
    """
    Interaktywny dashboard pobiera historyczne dane pogodowe z API Open-Meteo i pozwala porownac
    temperature, opady, wiatr oraz sezonowosc w wybranych polskich miastach.
    """
)

with st.sidebar:
    st.header("Filtry")

    city_options = POLISH_CITIES["city"].tolist()
    selected_cities = st.multiselect(
        "Miasta",
        options=city_options,
        default=["Warszawa", "Krakow", "Gdansk", "Wroclaw", "Poznan"],
    )

    max_available_date = date.today() - timedelta(days=5)
    default_start = max_available_date - timedelta(days=90)
    date_range = st.date_input(
        "Zakres dat",
        value=(default_start, max_available_date),
        min_value=date(2015, 1, 1),
        max_value=max_available_date,
    )

    metric = st.selectbox(
        "Glowna metryka do wykresow",
        options=list(CITY_LABELS.keys()),
        index=0,
        format_func=lambda value: CITY_LABELS.get(value, value),
    )

    min_temp = st.slider("Minimalna srednia temperatura [C]", -30.0, 40.0, -30.0, 1.0)
    max_wind = st.slider("Maksymalna predkosc wiatru [km/h]", 0.0, 120.0, 120.0, 5.0)
    only_rainy_days = st.checkbox("Pokaz tylko dni z opadem")

    st.caption("Dane sa pobierane na zywo z Open-Meteo Archive API. Aplikacja nie wymaga plikow CSV ani klucza API.")

if len(date_range) != 2:
    st.warning("Wybierz date poczatkowa i koncowa.")
    st.stop()

start_date, end_date = date_range

if not selected_cities:
    st.warning("Wybierz przynajmniej jedno miasto.")
    st.stop()

if start_date > end_date:
    st.error("Data poczatkowa nie moze byc pozniejsza niz data koncowa.")
    st.stop()

@st.cache_data(ttl=60 * 60)
def load_data(cities: tuple[str, ...], start: date, end: date) -> pd.DataFrame:
    raw = fetch_weather_for_cities(cities, start, end)
    return clean_weather_data(raw)

try:
    data = load_data(tuple(selected_cities), start_date, end_date)
except Exception as exc:
    st.error("Nie udalo sie pobrac danych z API. Sprobuj zmniejszyc zakres dat albo odswiez aplikacje za chwile.")
    st.exception(exc)
    st.stop()

if data.empty:
    st.warning("Brak danych dla wybranego zakresu.")
    st.stop()

filtered = filter_weather_data(data, min_temp=min_temp, max_wind=max_wind, only_rainy_days=only_rainy_days)

if filtered.empty:
    st.warning("Po zastosowaniu filtrow nie zostaly zadne rekordy. Zmien ustawienia w panelu bocznym.")
    st.stop()

st.subheader("Najwazniejsze wskazniki")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Liczba obserwacji", f"{len(filtered):,}".replace(",", " "))
col2.metric("Liczba miast", filtered["city"].nunique())
col3.metric("Srednia temp.", f"{filtered['temperature_2m_mean'].mean():.1f} C")
col4.metric("Suma opadow", f"{filtered['precipitation_sum'].sum():.1f} mm")
col5.metric("Najsilniejszy wiatr", f"{filtered['wind_speed_10m_max'].max():.1f} km/h")

st.markdown(
    f"**Zakres analizy:** {start_date} - {end_date}. "
    f"Po filtrach zostalo **{len(filtered)}** obserwacji dla **{filtered['city'].nunique()}** miast."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Trendy w czasie",
    "Porownanie miast",
    "Mapa i sezonowosc",
    "Dane i wnioski",
])

with tab1:
    st.plotly_chart(line_temperature(filtered, metric), use_container_width=True)
    st.caption("Wykres liniowy pokazuje, jak zmieniala sie wybrana metryka w czasie dla kazdego miasta.")

with tab2:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(bar_city_ranking(filtered, metric), use_container_width=True)
    with right:
        st.plotly_chart(boxplot_city(filtered, metric), use_container_width=True)

    st.plotly_chart(scatter_temp_precip(filtered), use_container_width=True)
    st.plotly_chart(histogram_temperature(filtered), use_container_width=True)

with tab3:
    st.plotly_chart(map_weather(filtered, metric), use_container_width=True)
    st.plotly_chart(heatmap_weekday_month(filtered, metric), use_container_width=True)

with tab4:
    st.markdown("### Krotkie wnioski automatyczne")
    warmest_city = filtered.groupby("city")["temperature_2m_mean"].mean().idxmax()
    rainiest_city = filtered.groupby("city")["precipitation_sum"].sum().idxmax()
    windiest_city = filtered.groupby("city")["wind_speed_10m_max"].mean().idxmax()

    st.write(f"- Najwyzsza srednia temperatura w wybranym zakresie wystapila w miescie: **{warmest_city}**.")
    st.write(f"- Najwieksza laczna suma opadow wystapila w miescie: **{rainiest_city}**.")
    st.write(f"- Najwyzsza srednia maksymalna predkosc wiatru wystapila w miescie: **{windiest_city}**.")

    st.markdown("### Przefiltrowane dane")
    st.dataframe(
        filtered.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Pobierz przefiltrowane dane CSV",
        data=csv,
        file_name="weather_filtered.csv",
        mime="text/csv",
    )
