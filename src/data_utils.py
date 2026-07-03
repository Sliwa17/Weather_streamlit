from __future__ import annotations

from datetime import date
from typing import Iterable

import numpy as np
import pandas as pd
import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Lista miast trzymana lokalnie, zeby aplikacja nie wymagala zadnych plikow ani kluczy API.
# Dane pogodowe sa za kazdym razem pobierane z prawdziwego API Open-Meteo.
POLISH_CITIES = pd.DataFrame(
    [
        {"city": "Warszawa", "latitude": 52.2297, "longitude": 21.0122, "region": "mazowieckie"},
        {"city": "Krakow", "latitude": 50.0647, "longitude": 19.9450, "region": "malopolskie"},
        {"city": "Lodz", "latitude": 51.7592, "longitude": 19.4560, "region": "lodzkie"},
        {"city": "Wroclaw", "latitude": 51.1079, "longitude": 17.0385, "region": "dolnoslaskie"},
        {"city": "Poznan", "latitude": 52.4064, "longitude": 16.9252, "region": "wielkopolskie"},
        {"city": "Gdansk", "latitude": 54.3520, "longitude": 18.6466, "region": "pomorskie"},
        {"city": "Szczecin", "latitude": 53.4285, "longitude": 14.5528, "region": "zachodniopomorskie"},
        {"city": "Bydgoszcz", "latitude": 53.1235, "longitude": 18.0084, "region": "kujawsko-pomorskie"},
        {"city": "Lublin", "latitude": 51.2465, "longitude": 22.5684, "region": "lubelskie"},
        {"city": "Bialystok", "latitude": 53.1325, "longitude": 23.1688, "region": "podlaskie"},
        {"city": "Katowice", "latitude": 50.2649, "longitude": 19.0238, "region": "slaskie"},
        {"city": "Rzeszow", "latitude": 50.0412, "longitude": 21.9991, "region": "podkarpackie"},
        {"city": "Olsztyn", "latitude": 53.7784, "longitude": 20.4801, "region": "warminsko-mazurskie"},
        {"city": "Kielce", "latitude": 50.8661, "longitude": 20.6286, "region": "swietokrzyskie"},
        {"city": "Opole", "latitude": 50.6751, "longitude": 17.9213, "region": "opolskie"},
        {"city": "Zielona Gora", "latitude": 51.9355, "longitude": 15.5062, "region": "lubuskie"},
    ]
)

DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "shortwave_radiation_sum",
]


def fetch_city_weather(city_row: pd.Series, start_date: date, end_date: date) -> pd.DataFrame:
    """Pobiera dzienne dane historyczne Open-Meteo dla jednego miasta."""
    params = {
        "latitude": city_row["latitude"],
        "longitude": city_row["longitude"],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Europe/Warsaw",
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if "daily" not in payload or "time" not in payload["daily"]:
        return pd.DataFrame()

    df = pd.DataFrame(payload["daily"])
    df["city"] = city_row["city"]
    df["region"] = city_row["region"]
    df["latitude"] = city_row["latitude"]
    df["longitude"] = city_row["longitude"]
    return df


def fetch_weather_for_cities(cities: Iterable[str], start_date: date, end_date: date) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    selected = POLISH_CITIES[POLISH_CITIES["city"].isin(list(cities))]
    for _, row in selected.iterrows():
        frames.append(fetch_city_weather(row, start_date, end_date))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """Czyszczenie i przygotowanie danych: typy, braki, kolumny pochodne, jednostki."""
    if df.empty:
        return df

    clean = df.copy()
    clean.columns = [col.strip().lower() for col in clean.columns]

    clean["date"] = pd.to_datetime(clean["time"], errors="coerce")
    clean = clean.drop(columns=["time"], errors="ignore")
    clean = clean.dropna(subset=["date", "city"])
    clean = clean.drop_duplicates(subset=["city", "date"])

    numeric_cols = [
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "shortwave_radiation_sum",
        "latitude",
        "longitude",
    ]
    for col in numeric_cols:
        if col in clean.columns:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")

    # Sensowne uzupelnienia: brak opadu/sniegu traktujemy jako 0, temperatur nie wymyslamy.
    for col in ["precipitation_sum", "rain_sum", "snowfall_sum"]:
        if col in clean.columns:
            clean[col] = clean[col].fillna(0)

    clean["year"] = clean["date"].dt.year
    clean["month"] = clean["date"].dt.month
    clean["month_name"] = clean["date"].dt.strftime("%Y-%m")
    clean["day_of_week"] = clean["date"].dt.day_name()
    clean["day_of_week_num"] = clean["date"].dt.dayofweek
    clean["temp_range"] = clean["temperature_2m_max"] - clean["temperature_2m_min"]
    clean["is_rainy_day"] = clean["precipitation_sum"] > 0
    clean["precipitation_bucket"] = pd.cut(
        clean["precipitation_sum"],
        bins=[-0.01, 0, 2, 10, np.inf],
        labels=["brak", "lekki", "umiarkowany", "duzy"],
    )

    return clean.sort_values(["city", "date"]).reset_index(drop=True)


def filter_weather_data(
    df: pd.DataFrame,
    min_temp: float,
    max_wind: float,
    only_rainy_days: bool,
) -> pd.DataFrame:
    filtered = df.copy()
    filtered = filtered[filtered["temperature_2m_mean"] >= min_temp]
    filtered = filtered[filtered["wind_speed_10m_max"] <= max_wind]
    if only_rainy_days:
        filtered = filtered[filtered["is_rainy_day"]]
    return filtered
