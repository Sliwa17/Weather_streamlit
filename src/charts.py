from __future__ import annotations

import pandas as pd
import plotly.express as px


CITY_LABELS = {
    "temperature_2m_mean": "Srednia temperatura [C]",
    "temperature_2m_max": "Maksymalna temperatura [C]",
    "temperature_2m_min": "Minimalna temperatura [C]",
    "precipitation_sum": "Suma opadow [mm]",
    "wind_speed_10m_max": "Maksymalna predkosc wiatru [km/h]",
    "wind_gusts_10m_max": "Maksymalne porywy wiatru [km/h]",
    "shortwave_radiation_sum": "Promieniowanie sloneczne [MJ/m2]",
    "temp_range": "Dobowa amplituda temperatury [C]",
}


def line_temperature(df: pd.DataFrame, metric: str):
    daily = df.groupby(["date", "city"], as_index=False)[metric].mean()
    return px.line(
        daily,
        x="date",
        y=metric,
        color="city",
        markers=True,
        title=f"Trend w czasie: {CITY_LABELS.get(metric, metric)}",
        labels={"date": "Data", "city": "Miasto", metric: CITY_LABELS.get(metric, metric)},
    )


def bar_city_ranking(df: pd.DataFrame, metric: str):
    ranking = df.groupby("city", as_index=False)[metric].mean().sort_values(metric, ascending=False)
    return px.bar(
        ranking,
        x="city",
        y=metric,
        title=f"Ranking miast wedlug sredniej wartosci: {CITY_LABELS.get(metric, metric)}",
        labels={"city": "Miasto", metric: CITY_LABELS.get(metric, metric)},
    )


def scatter_temp_precip(df: pd.DataFrame):
    return px.scatter(
        df,
        x="temperature_2m_mean",
        y="precipitation_sum",
        color="city",
        size="wind_speed_10m_max",
        hover_data=["date", "temp_range"],
        title="Zaleznosc: temperatura, opady i wiatr",
        labels={
            "temperature_2m_mean": "Srednia temperatura [C]",
            "precipitation_sum": "Suma opadow [mm]",
            "wind_speed_10m_max": "Maks. wiatr [km/h]",
            "city": "Miasto",
        },
    )


def histogram_temperature(df: pd.DataFrame):
    return px.histogram(
        df,
        x="temperature_2m_mean",
        color="city",
        nbins=35,
        marginal="box",
        title="Rozklad srednich temperatur dziennych",
        labels={"temperature_2m_mean": "Srednia temperatura [C]", "city": "Miasto"},
    )


def map_weather(df: pd.DataFrame, metric: str):
    city_map = df.groupby(["city", "latitude", "longitude"], as_index=False)[metric].mean()
    fig = px.scatter_map(
        city_map,
        lat="latitude",
        lon="longitude",
        size=metric,
        color=metric,
        hover_name="city",
        zoom=5,
        title=f"Mapa miast: {CITY_LABELS.get(metric, metric)}",
        labels={metric: CITY_LABELS.get(metric, metric)},
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig


def heatmap_weekday_month(df: pd.DataFrame, metric: str):
    heat = df.groupby(["month_name", "day_of_week_num", "day_of_week"], as_index=False)[metric].mean()
    pivot = heat.pivot(index="day_of_week", columns="month_name", values=metric)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([day for day in order if day in pivot.index])
    return px.imshow(
        pivot,
        aspect="auto",
        title=f"Heatmapa: {CITY_LABELS.get(metric, metric)} wedlug miesiaca i dnia tygodnia",
        labels={"x": "Miesiac", "y": "Dzien tygodnia", "color": CITY_LABELS.get(metric, metric)},
    )


def boxplot_city(df: pd.DataFrame, metric: str):
    return px.box(
        df,
        x="city",
        y=metric,
        points="outliers",
        title=f"Porownanie rozkladow miedzy miastami: {CITY_LABELS.get(metric, metric)}",
        labels={"city": "Miasto", metric: CITY_LABELS.get(metric, metric)},
    )
