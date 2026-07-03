# Analiza pogody w polskich miastach - Streamlit

Autor: Albert Śliwiński

Link do aplikacji: https://weatherapp-9v6r4qroqc8rv5ajamqjmw.streamlit.app/

## Opis projektu

Aplikacja analizuje historyczne dane pogodowe dla wybranych polskich miast. Dashboard pozwala porownywac temperature, opady, wiatr i sezonowosc pogody w czasie. Dane sa pobierane bezposrednio z Open-Meteo Archive API, dlatego projekt nie wymaga pobierania plikow CSV, zakladania konta ani uzywania klucza API.

Glowne pytanie analityczne:

> Jak roznia sie warunki pogodowe w polskich miastach i jakie wzorce sezonowe widac w danych historycznych?

## Zrodlo danych

Dane pochodza z Open-Meteo Historical Weather API:

- https://open-meteo.com/en/docs/historical-weather-api
- https://open-meteo.com/

API udostepnia historyczne dane pogodowe dla dowolnych wspolrzednych geograficznych. W aplikacji wykorzystano wspolrzedne najwiekszych polskich miast, a nastepnie pobierane sa dzienne dane pogodowe.

## Zakres danych

Aplikacja pobiera m.in. nastepujace zmienne:

- srednia temperatura dzienna,
- minimalna i maksymalna temperatura,
- suma opadow,
- suma deszczu,
- suma sniegu,
- maksymalna predkosc wiatru,
- maksymalne porywy wiatru,
- promieniowanie sloneczne.

## Czyszczenie i przygotowanie danych

W projekcie wykonano kilka krokow przygotowania danych:

- standaryzacja nazw kolumn,
- konwersja dat na typ `datetime`,
- konwersja kolumn liczbowych,
- usuwanie duplikatow dla kombinacji miasto-data,
- obsluga brakow w danych opadowych,
- utworzenie kolumn pochodnych: rok, miesiac, dzien tygodnia, amplituda temperatury, flaga dnia z opadem, kategoria opadow.

## Funkcje dashboardu

Aplikacja zawiera:

- sidebar z filtrami,
- KPI w kolumnach,
- zakladki tematyczne,
- interaktywne wykresy Plotly,
- tabele danych,
- przycisk pobrania przefiltrowanych danych.

## Filtry

Uzytkownik moze filtrowac dane przez:

- wybor miast,
- zakres dat,
- wybor glownej metryki,
- minimalna srednia temperature,
- maksymalna predkosc wiatru,
- tylko dni z opadem.

## Wizualizacje

Projekt zawiera wiecej niz 5 typow wykresow:

1. wykres liniowy,
2. wykres slupkowy,
3. boxplot,
4. scatter plot,
5. histogram,
6. mapa punktowa,
7. heatmapa.

## Uruchomienie lokalne

Sklonuj repozytorium:

```bash
git clone https://github.com/TWOJ_LOGIN/weather-streamlit-dashboard.git
cd weather-streamlit-dashboard
```

Utworz srodowisko wirtualne:

```bash
python -m venv .venv
```

Aktywuj srodowisko.

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Zainstaluj biblioteki:

```bash
pip install -r requirements.txt
```

Uruchom aplikacje:

```bash
streamlit run app.py
```

## Deployment

Aplikacja jest przygotowana do wdrozenia na Streamlit Community Cloud.

Kroki:

1. Wrzuc kod na publiczne repozytorium GitHub.
2. Wejdz na https://share.streamlit.io.
3. Wybierz `New app`.
4. Wybierz repozytorium i branch `main`.
5. Jako plik glowny ustaw `app.py`.
6. Kliknij `Deploy`.

## Struktura projektu

```text
weather_streamlit_project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── src/
    ├── charts.py
    └── data_utils.py
```
