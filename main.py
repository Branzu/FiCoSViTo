import streamlit as st
from business_logic import ElaboratoreDati
from input import GestoreInputManuale, GeneratoreDatiStorici
from crea_mappa_zone_pesca import GestoreMappa
from datetime import date
from data_viz import (
    GestoreVisualizzazioneDati,
    GestoreFiltroDati,
    GestoreSimulazione,
    GestoreDati,
    GestoreLayoutPagina,
    GestoreSidebar,
)

def main():
    # Inizializzo tutti gli oggetti necessari per l'applicazione
    generatore_storico = GeneratoreDatiStorici()
    gestore_input_manuale = GestoreInputManuale()
    elaboratore_dati = ElaboratoreDati()
    gestore_mappa = GestoreMappa("eez_boundaries_v12.gpkg")

    # Creo le istanze delle varie classi per gestire le diverse funzionalità
    gestore_layout_pagina = GestoreLayoutPagina()
    gestore_dati = GestoreDati(generatore_storico, gestore_input_manuale, elaboratore_dati)
    gestore_sidebar = GestoreSidebar(generatore_storico, gestore_input_manuale, gestore_dati)
    gestore_filtro_dati = GestoreFiltroDati()
    gestore_simulazione = GestoreSimulazione(elaboratore_dati)
    gestore_visualizzazione_dati = GestoreVisualizzazioneDati(elaboratore_dati, gestore_mappa)

    # Configuro la pagina e la sidebar
    gestore_layout_pagina.visualizza_header()
    gestore_sidebar.visualizza_sidebar()

    # Carico i dati storici e manuali e aggiorno st.session_state
    record_storici = gestore_dati.carica_dati()
    record_storici = gestore_dati.aggiorna_dati_storici(record_storici)
    record_manuali = gestore_input_manuale.carica_record_manuali()
    st.session_state["manual_records"] = record_manuali

    # Seleziono l'intervallo temporale di riferimento tramite il gestore dei filtri
    data_inizio, data_fine = gestore_filtro_dati.seleziona_intervallo_date()

    # Ora chiamo unisci_dati solo se non è già stato fatto nella sidebar
    if "record_finali" not in st.session_state:
        # Unisco i dati storici e manuali
        record_finali = gestore_dati.unisci_dati(record_storici, st.session_state["manual_records"])
        st.session_state["record_finali"] = record_finali
    else:
        record_finali = st.session_state["record_finali"]

    # Filtro i record in base all'intervallo di date selezionato
    record_finali = gestore_filtro_dati.filtra_record_per_data(record_finali, data_inizio, data_fine)

    # Preparo i dati prima della simulazione (calcolo qualità, utile, prezzo finale, costo)
    record_preparati = elaboratore_dati.prepara_dati_storici(record_finali)

    # Mostro il numero di campioni selezionati nel periodo
    st.info(f"Campioni inclusi nel periodo selezionato: {len(record_finali)}")

    # Creo la griglia per i grafici e i dataframe
    row1, row2 = gestore_layout_pagina.crea_griglia()

    # Creo i due slider per la simulazione con step al 25%
    with st.container():
        left, right = st.columns([2, 1])
        with left:
            # Slider per il riciclo degli scarti
            scarto = st.slider("Riciclo Scarti (%) - se aumento il riciclo, diminiusco lo scarto ma alzo i costi di produzione", 0, 100, 0, step=25, key="scarto_sim")
            # Slider per la lavorazione intensiva
            lavorazione = st.slider("Lavorazione Intensiva (%) - se la lavorazione è più intensiva, aumento l'utile netto ma riduco la qualità", 0, 100, 0, step=25, key="lavorazione_sim")

            # Applico la simulazione ai record preparati
            record_simulati = elaboratore_dati.applica_simulazione_ai_record(
                record_preparati,
                riciclo_scarti_pct=scarto,
                lavorazione_intensiva_pct=lavorazione
            )

            # Visualizzo le metriche nel footer
            record_simulati = gestore_simulazione.visualizza_metriche_footer(record_preparati, record_simulati, scarto, lavorazione)

        with right:
            # Visualizzo gli indicatori di circolarità e Green Action Score
            gestore_simulazione.visualizza_indicatori_circolarita(scarto, lavorazione)

    # Visualizzo i grafici e le tabelle nelle celle della griglia
    with st.container():
        with row1[0]:
            gestore_layout_pagina.visualizza_contenitore_cella()
            gestore_visualizzazione_dati.visualizza_mappa(record_finali)
            gestore_layout_pagina.chiudi_contenitore_cella()

        with row1[1]:
            gestore_layout_pagina.visualizza_contenitore_cella()
            gestore_visualizzazione_dati.visualizza_grafico_torta(record_simulati)
            gestore_layout_pagina.chiudi_contenitore_cella()

        with row1[2]:
            gestore_layout_pagina.visualizza_contenitore_cella()
            gestore_visualizzazione_dati.visualizza_grafico_barre(record_simulati)
            gestore_layout_pagina.chiudi_contenitore_cella()

        with row2[0]:
            gestore_layout_pagina.visualizza_contenitore_cella()
            gestore_visualizzazione_dati.visualizza_grafico_costi(record_simulati)
            gestore_layout_pagina.chiudi_contenitore_cella()

        with row2[1]:
            gestore_layout_pagina.visualizza_contenitore_cella()
            gestore_visualizzazione_dati.visualizza_indicatore_qualita(record_simulati)
            gestore_layout_pagina.chiudi_contenitore_cella()

        with row2[2]:
            gestore_layout_pagina.visualizza_contenitore_cella()
            gestore_visualizzazione_dati.visualizza_grafico_temporale(record_simulati, data_inizio, data_fine)
            gestore_layout_pagina.chiudi_contenitore_cella()
    st.markdown('</div>', unsafe_allow_html=True)

    # Visualizzo il footer
    gestore_layout_pagina.visualizza_footer()


if __name__ == "__main__":
    main()
