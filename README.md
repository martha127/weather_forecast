# Analiza danych meteorologicznych

Projekt ma polegać na pobraniu danych meteorologicznych, analizie oraz prezentacji wyników.

W projekcie rozwijany będzie pakiet o nazwie `meteopy`, który będzie pozwalał na analityczne interkacje z danymi publicznymi z Instytutu Meteorologii i Gospodarki Wodnej.

## Setup

Create a virtual environment for the project:

`make env`

Run pre-commit hooks:

`make pc`

## Opis projektu:
Projekt zawiera nastepujące funkcjonalności:

- funkcja fetcher: służy do przeszukiwania katalogów w oparciu o ich strukturę.
Funkcja bierze pod uwagę róznorodne ułożenie lat w katalogach na stronie, z której pobieramy dane, dlatego m.in.: stosuje różne metody dla danych przed 2001 i po 2001 roku.
Uzytkownik może wyszukać zarówno pojedynczy rok (np. 2017), listę lat (np. 2017,2018,2019), a także pojedynczy przedział (np. 1990-1999), dowolne lata i przedziały, a także wiele przedziałów.
Funkcja zwraca linki, które pasują do podanych przez uzytkowinka lat i przekauje je dalej.
- funkcje pobierające dane: na pobranie danych okreslonych przez linki zebrane wyżej składa się kilka funkcji: download_file, download_and_extract_zip oraz extract_zip. Odpowiadają one za pobranie i rozpakowanie danych (z plików zip do plików csv).
- funkcja handler: opdowiada za preprocessing danych, wczytuje je i dzieli na stacje, a także nadaje im nazwy zgodne z rokiem i miesiącem pobrania danych. Dla dwóch pakietów dane na stronie maja dopisek t, w plikach z tym dopiskiem znajdują się inne dane niż w plikach bez, dlatego "_t" jest uwzgęldniane przez kolejne funkcje podczas dalszych analiz, a takze umieszczone w nazwie plików.
Ponadto funkcja dodaje nagłówki do danych na podstawie pliku tekstowego zawartego na stronie. po dodaniu nagłówków funkcja usuwa brakujące dane, oraz dane które nie wnosza nic do analizy (te, w którcyh np. w całej kolumnie występuje tylko jedna wartość).
- wizualizacja danych: funkcja plot_time_series tworzy szeregi czasowe na podstawie podanych przez uzytkownika wytycznych. Użytkownik mooze okreslic parametr, który ma znaleźć się na wykresie, przedział czasowy dla pobieranych danych, stacje, typ danych (klimat, synop lub opad) oraz to czy dane mają pochodzic z pliku z postfixem "_t".
W celu przekazania odpowiednich danych do funkcji wizualizującej dane utworzone zostały dodatkowe metody: find_file, get_ready, get_months_in_range. Metody te służą stworzeniu DataFrame'u, który bedzie zawierał dane określone przez uzytkownika. Wykresy sa zapisywane w folderze plot, dzielonym ze względu na typ danych.
- analizy statystyczne- wykonywane przez dwie funkcje: calculate_basic_stats oraz calculate_correlation. Pierwsza z nich zwraca podstawowe statystyki dla dancyh określonych przez uzytkownika (funkcja przyjmuje takie argumenty jak funkcja wyżej oraz korzysta z jej metody do uporządkowywania danych: get_ready). Dane są zapisywane w formie tabel w folderze stats/basic_stats.
Druga funkcja słuzy do obliczania korelacji, bazuje jednka na danych które zostały juz przekazane do funkcji obliczającej statystyke. Uzytkownik może jednak wprowadzic dwa parametry, między którymi ma zostać obliczony współczynnik korelacji. Warto zauważyć, że nie wszystkie dane w kolumnach są numeryczne, jeśli dane nie sa numeryczne funkcja konwertuje je  (na wartości 0 lub 1) co pozwala obliczyc korelację. Pliki jak poprzednio sa zapisywane do folderu: stats/correlation.
- prognozowanie: funkcja linear_regresion_forecast słuzy do przeprowadzania prognoz na przyszłość na podstawie danych historycznych. Funkcja przyjumuje od użytkownika następujące parametry: listę stacji, typ danych, prametr, który ma zostać prognozowany, początkowy dzień prognozy oraz uzycie plików "_t". Uzytkownik nie podaje drugiego parametru potzebnego do przeprowadzenia regresji liniowej, ponieważ jest to z gory narzucony parametr daty. Wiąże się to z faktem, że prognoza jest automatycznie generowana na siedem dni w przód, dlatego data musi byc pierwszym parametrem. W klasie IMGWSimpleForecaster znajduje sie też funkcja pomocnicza: chceck_existing_years. Do wykonania regresji uzywamy danych historycznych z 3 lat przed wybrana data początkowo, dlatego została dodana funkcja, która sprawdza czy potrzebne dane zostały już pobrane i w przypadku wystąpienia braków, pobiera brakujące dane. Ta funcjonalnosc pozwala tez na uruchamianie prognozy niezaleznie od innych funkcji.

## Przykładowe uruchomienie
- uruchomienie ręczne: funkcje można uruchamiać po kolei bezpośrednio z plików, testowe wywołania każdej z funkcji znajduja sie pod kodem dla każdego pliku, sugerowana kolejnosc wywoływania to:
- fetcher->download_file->handler->plot_time_series->calculate_basic_stats->calculate_correlation->linear_regresion_forecast 
- Warto wspomnieć, że funkcja, która może byc uruchamiana bez wcześiejszego pobrania danych jest linear_regresion_forecast.

### Przykładowe wywołania w cli:
- uruchomienie przez command line: do projektu zostały dodane trzy komendy:full_analysis - wykonuje pełną analizę, basic_summary- zwraca tylko podstawowe dany statystyczne oraz
download - słuzy wyłącznie do pobierania danych, przykłodwe wywołania tych komend:

- mycli download --data-type synop --years 2001-2005 
- mycli basic_summary --parameter "Średnia dobowa prędkość wiatru [m/s]" --stations BIAŁYSTOK --data-type synop --start-date 02.02.2017 --end-date 12.04.2017 --use-t-files
- mycli full_analysis --parameter "Średnia temperatura dobowa [°C]" --parameter1 "Dzień" --parameter2 "Minimalna temperatura dobowa [°C]" --stations BIAŁYSTOK --data-type synop --start-date 02.02.2004 --end-date 12.04.2004
