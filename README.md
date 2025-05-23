# Fi.Co? S.Vi.To.! - Fishing Company Simulation and Visualization Tool

![App Screenshot](https://github.com/Branzu/FicCoSViTo/blob/main/screenshot.png)

**Fi.Co? S.Vi.To.!** è uno strumento innovativo di simulazione e visualizzazione per la gestione di una piccola azienda operante nel settore ittico e della pesca. Si tratta di una dashboard interattiva con metriche basate su input storici e manuali, generazione di sotrico accurato con elementi randomizzati di distribuzione, visualizzazione dei dati per periodo e slider per la simulazione della variazione dei valori rappresentati.

## Caratteristiche Principali

*   **Generazione di Dati Storici:** Simula dati storici di pesca su un arco di 5 anni, basandosi su valori di riferimento con variazioni casuali basate su specie, zona di pesca e condizioni meteo.
*   **Input Manuale:** Permette l'inserimento manuale di campioni di pesce per simulare andamenti differenti rispetto a quelli proposti dallo storico.
*   **Visualizzazione Dati:**
    *   **Mappa Interattiva:** mostra la distribuzione dei campioni nelle diverse zone di pesca.
    *   **Grafici a Torta e a Barre:** analizza la distribuzione di netto e scarto, e le quantità per tipo di pesce.
    *   **Grafico dei Costi:** visualizza i costi di produzione, l'utile lordo e il prezzo finale per tipo di pesce.
    *   **Indicatore di Qualità:** fornisce un indice di qualità del prodotto, sia per tipo di pesce che globale.
    *   **Grafico Temporale:** mostra l'andamento di quantità, prezzo e qualità nel tempo.
    *   **Tabelle Riassuntive:** presenta dati aggregati in tabelle.
*   **Simulazione:**
    *   **Riciclo Scarti:** Simula l'impatto del riciclo degli scarti sulla quantità di scarto e sui costi di produzione.
    *   **Lavorazione Intensiva:** Simula l'effetto della lavorazione intensiva sull'utile netto e sulla qualità del prodotto.
    *   **Indicatori di Circolarità:** Calcola la percentuale di circolarità e il Green Action Score.
*   **Filtri:** Permette di filtrare i dati per intervallo di date.
* **Aggiornamento automatico**: I dati storici vengono aggiornati automaticamente all'ultima data disponibile.

## Installazione e Avvio

1.  **Clona il repository:**
    ```bash
    git clone https://github.com/your-username/Fico_Svito.git
    ```
2.  **Naviga nella directory del progetto:**
    ```bash
    cd Fico_Svito_test
    ```
3.  **Crea un ambiente virtuale (consigliato):**
    ```bash
    python3 -m venv venv
    ```
4.  **Attiva l'ambiente virtuale:**
    *   **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
5.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```
    *   Nota: per creare il file requirements.txt, puoi usare il comando `pip freeze > requirements.txt`
6.  **Avvia l'applicazione:**
    ```bash
    streamlit run main.py
    ```

## Struttura del Progetto

*   `main.py`: File principale che avvia l'applicazione Streamlit.
*   `business_logic.py`: Contiene la logica di business per l'elaborazione dei dati.
*   `input.py`: Gestisce l'input manuale e la generazione di dati storici.
*   `data_viz.py`: Gestisce la visualizzazione dei dati (grafici, tabelle, mappe).
*   `crea_mappa_zone_pesca.py`: Gestisce la creazione e la visualizzazione della mappa delle zone di pesca.
*   `eez_boundaries_v12.gpkg`: File GeoPackage contenente i confini delle Zone Economiche Esclusive (EEZ).
*   `manual_data.json`: File JSON per la memorizzazione dei dati inseriti manualmente.
*   `historical_data.json`: File JSON per la memorizzazione dei dati storici generati.
*   `requirements.txt`: Elenco delle dipendenze del progetto.
*   `UML.txt e UML.png`: Diagrammi UML del progetto e delle classi e funzioni che lo compongono
* `README.md`: Questo file.

## Autore

*   Gianluca Buttigliero

## Licenza

Questo progetto è rilasciato sotto la licenza GPL-3.0.

