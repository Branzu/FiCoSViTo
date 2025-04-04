# Fi.Co? S.Vi.To.! A Fishing Company Simulation and Visualization Tool - Ver. 1.0"- data_viz.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import random
import json
from datetime import date, datetime
from crea_mappa_zone_pesca import GestoreMappa
from streamlit_folium import folium_static

class GestoreVisualizzazioneDati:

    def __init__(self, elaboratore_dati, gestore_mappa):

        self.elaboratore_dati = elaboratore_dati
        self.gestore_mappa = gestore_mappa
        self.schema_colori = ["blue", "red"]
        self.configura_matplotlib()

    def configura_matplotlib(self):
        """
        Configura le impostazioni di default di Matplotlib per i grafici: imposta il colore di sfondo, il colore delle etichette, la dimensione e il peso dei titoli,
        il colore dei tick, la dimensione delle etichette dei tick, il colore del testo e la dimensione del testo della legenda.
        """
        mpl.rcParams.update({
            "axes.facecolor": "none",
            "axes.labelcolor": "white",
            "axes.titlesize": 20,
            "axes.titleweight": "bold",
            "xtick.color": "white",
            "ytick.color": "white",
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "text.color": "white",
            "legend.fontsize": 14,
        })

    def visualizza_mappa(self, record_finali):
        """ Visualiza la mappa delle zone di pesca con il numero di campioni per zona. """
        st.subheader("Mappa delle Zone di Pesca")
        # Calcola il numero massimo di campioni per zona
        max_count = max(self.gestore_mappa.conta_campioni_zone(record_finali).values(), default=0)
        # Crea la legenda della mappa
        legend_html = f"""
            <div class="map-legend-container" style="
                width: 100%;
                background-color: rgba(14, 17,23, 1);
                padding: 5px;
                border-radius: 5px;
                color: white;
                font-family: sans-serif;
                text-align: center;
                margin-bottom: 5px;
            ">
                <div style="display: inline-block; width: 97%; height: 10px; background: linear-gradient(to right, {self.schema_colori[0]}, {self.schema_colori[-1]});"></div>
                <div>
                    <span style="float: left;">Min.</span>
                    <span style="float: right;">Max.</span>
                </div>
                <div style="font-weight: bold; margin-top: 5px;">Numero di Campioni per Zona</div>
            </div>
        """
        # Carica le EEZ italiane
        eez_italiane = self.gestore_mappa.carica_eez_ita()
        # Crea la mappa personalizzata
        map_obj = self.gestore_mappa.crea_mappa_custom(
            self.gestore_mappa.suddividi_eez_ita(eez_italiane),
            self.gestore_mappa.conta_campioni_zone(record_finali),
            self.schema_colori
        )
        # Visualizza la mappa con Streamlit Folium
        folium_static(map_obj, width=None, height=380)
        # Visualizza la legenda
        st.markdown(legend_html, unsafe_allow_html=True)

    def visualizza_grafico_torta(self, record_preparati):
        """ Visualizza il grafico a torta della distribuzione di netto e scarto. """
        st.subheader("Distribuzione Quantità")
        # Calcola il netto e lo scarto
        summary = self.elaboratore_dati.calcola_netto_scarto(record_preparati)
        # Prendi i totali dalla riga "Totale" del DataFrame
        totale_netto = float(self.crea_totale_da_sommario(summary, "netto"))
        totale_scarto = float(self.crea_totale_da_sommario(summary, "scarto"))
        # Verifica se ci sono dati per il grafico
        if totale_netto + totale_scarto == 0:
            st.warning("Nessun dato disponibile per il grafico a torta.")
        else:
            # Crea il grafico a torta
            fig_pie, ax_pie = plt.subplots()
            fig_pie.patch.set_facecolor("none")
            ax_pie.set_facecolor("none")
            ax_pie.pie(
                [totale_scarto, totale_netto],
                labels=["Scarto", "Peso Netto"],
                autopct=lambda p: f"{p:.1f}%",
                textprops={"fontsize": 10, "color": "white", "weight": "bold"}
            )
            fig_pie.tight_layout()
            # Visualizza il grafico con Streamlit
            st.pyplot(fig_pie, use_container_width=True)
            # Visualizza i totali di scarto e netto
            st.markdown(f"<p style='text-align:center; font-size:24px'>Scarto: <b>{totale_scarto:.2f} kg</b> – Netto: <b>{totale_netto:.2f} kg</b></p>", unsafe_allow_html=True)

    def crea_totale_da_sommario(self, summary, key):
        """ Estrae il valore totale da un dizionario di riepilogo. """
        return summary.get("Totale", {}).get(key, 0)

    def visualizza_grafico_barre(self, record_preparati):
        """ Visualizza il grafico a barre delle quantità per tipo di pesce. """
        st.subheader("Quantità per Tipo di Pesce")
        # Calcola il netto e lo scarto per tipo di pesce
        summary = self.elaboratore_dati.calcola_netto_scarto(record_preparati)
        if summary:
            # Crea un DataFrame dal dizionario di riepilogo
            df_quantita = pd.DataFrame.from_dict(summary, orient="index")
            # Ordina il DataFrame per la colonna "totale" se presente
            if "totale" in df_quantita.columns:
                df_quantita = df_quantita.sort_values("totale", ascending=False)
            # Crea il grafico a barre
            fig_bar, ax_bar = plt.subplots()
            # Crea il grafico a barre con netto e scarto impilati
            df_quantita[["netto", "scarto"]].plot(
                kind="bar",
                stacked=True,
                ax=ax_bar,
                color=["#1f77b4", "#ff7f0e"],
                edgecolor="white",
                linewidth=0.5
            )
            ax_bar.set_ylabel("Kg")
            fig_bar.patch.set_facecolor("none")
            ax_bar.set_facecolor("none")
            ax_bar.tick_params(colors='white')
            # Imposta la dimensione e il peso del font per le etichette dell'asse x
            for label in ax_bar.get_xticklabels():
                label.set_fontsize(11)
                label.set_fontweight("bold")
            # Imposta la dimensione e il peso del font per le etichette dell'asse y
            for label in ax_bar.get_yticklabels():
                label.set_fontsize(11)
                label.set_fontweight("bold")
            fig_bar.tight_layout()
            # Visualizza il grafico con Streamlit
            st.pyplot(fig_bar, use_container_width=True)
            # Visualizza la tabella riassuntiva
            self.visualizza_tabella_riassuntiva(df_quantita)

    def visualizza_tabella_riassuntiva(self, df_quantita):
        """ Visualizza la tabella riassuntiva delle quantità. """
        if not df_quantita.empty:
            # Crea una copia del DataFrame e aggiunge la colonna "totale"
            df_tabella = df_quantita[["netto", "scarto"]].copy()
            df_tabella["totale"] = df_tabella["netto"] + df_tabella["scarto"]
            df_tabella.reset_index(inplace=True)
            # Rinomina le colonne
            df_tabella.rename(columns={"index": "Tipo di Pesce", "netto": "Netto (kg)", "scarto": "Scarto (kg)", "totale": "Totale (kg)"}, inplace=True)
            # Riordina le colonne
            cols = df_tabella.columns.tolist()
            cols = [cols[0], cols[3], cols[1], cols[2]]
            df_tabella = df_tabella[cols]
            # Aggiunge la riga "Totale" se non presente
            if "Totale" not in df_tabella["Tipo di Pesce"].values:
                somma_row = pd.DataFrame([{
                    "Tipo di Pesce": "Totale",
                    "Totale (kg)": df_tabella['Totale (kg)'].astype(float).sum(),
                    "Netto (kg)": df_tabella['Netto (kg)'].astype(float).sum(),
                    "Scarto (kg)": df_tabella['Scarto (kg)'].astype(float).sum()
                }])
                df_tabella = pd.concat([df_tabella, somma_row], ignore_index=True)
            # Visualizza la tabella con Streamlit
            st.dataframe(df_tabella, use_container_width=True, hide_index=True)
        else:
            st.warning("Nessun dato disponibile per la tabella delle quantità.")

    def visualizza_grafico_costi(self, record_simulati):
        """ Visualizza il grafico dei costi di produzione, utile e prezzo finale. """
        st.subheader("Costi di Produzione, Utile e Prezzo Finale (€/kg)")
        # Calcola i costi medi per tipo di pesce
        costi = self.elaboratore_dati.calcola_sommario_costi(record_simulati)
        if costi:
            # Crea un DataFrame dal dizionario dei costi
            df_costi = pd.DataFrame.from_dict(costi, orient="index").reset_index()
            # Rinomina le colonne
            df_costi.rename(columns={
                "index": "Tipo di Pesce",
                "costo_produzione": "Produzione (€/kg)",
                "utile_lordo": "Utile Lordo (€/kg)",
                "prezzo_finale": "Prezzo Finale (€/kg)"
            }, inplace=True)
            # Rimuovi la colonna "count" se presente
            if "count" in df_costi.columns:
                df_costi.drop(columns=["count"], inplace=True)
            # Crea il grafico a barre
            fig_costi, ax_costi = plt.subplots()
            # Crea il grafico a barre con i costi di produzione e l'utile lordo
            df_costi.set_index("Tipo di Pesce")[["Produzione (€/kg)", "Utile Lordo (€/kg)"]].plot(
                kind="bar",
                ax=ax_costi,
                edgecolor="white",
                linewidth=0.5
            )
            ax_costi.set_ylabel("€/kg")
            fig_costi.patch.set_facecolor("none")
            ax_costi.set_facecolor("none")
            ax_costi.tick_params(colors='white')
            # Imposta la dimensione e il peso del font per le etichette dell'asse x
            for label in ax_costi.get_xticklabels():
                label.set_fontsize(11)
                label.set_fontweight("bold")
            # Imposta la dimensione e il peso del font per le etichette dell'asse y
            for label in ax_costi.get_yticklabels():
                label.set_fontsize(11)
                label.set_fontweight("bold")
            fig_costi.tight_layout()
            # Visualizza il grafico con Streamlit
            st.pyplot(fig_costi, use_container_width=True)
            # Visualizza la tabella dei costi
            self.visualizza_tabella_costi(df_costi)

    def visualizza_tabella_costi(self, df_costi):
        """ Visualizza la tabella dei costi. """
        # Assicura che i dati siano di tipo float
        df_costi["Produzione (€/kg)"] = df_costi["Produzione (€/kg)"].astype(float)
        df_costi["Utile Lordo (€/kg)"] = df_costi["Utile Lordo (€/kg)"].astype(float)
        df_costi["Prezzo Finale (€/kg)"] = df_costi["Prezzo Finale (€/kg)"].astype(float)
        # Aggiunge la riga "Media" se non e' presente
        if "Media" not in df_costi["Tipo di Pesce"].values:
            media_row = pd.DataFrame([{
                "Tipo di Pesce": "Media",
                "Produzione (€/kg)": df_costi["Produzione (€/kg)"].mean(),
                "Utile Lordo (€/kg)": df_costi["Utile Lordo (€/kg)"].mean(),
                "Prezzo Finale (€/kg)": df_costi["Prezzo Finale (€/kg)"].mean()
            }])
            df_costi = pd.concat([df_costi, media_row], ignore_index=True)
        # Visualizza la tabella con Streamlit
        st.dataframe(df_costi, use_container_width=True, hide_index=True)

    def visualizza_indicatore_qualita(self, record_simulati):
        """ Visualizza l'indicatore di qualità del prodotto. """
        st.subheader("Indicatore di Qualità del Prodotto")
        # Calcola gli indici di qualità
        indici_qualita = self.elaboratore_dati.calcola_indice_qualita(record_simulati)
        def get_emoticon(score):
            """ Restituisce l'emoticon e il colore corrispondenti al punteggio. """
            if score >= 4.5:
                return "😃", "green"
            elif score >= 3.5:
                return "😊", "yellow"
            elif score >= 2.5:
                return "😐", "yellow"
            elif score >= 1.5:
                return "😟", "orange"
            else:
                return "😡", "red"
        # Visualizza gli indicatori per ogni tipo di pesce
        for tipo, score in indici_qualita.items():
            if tipo != "globale":
                emoticon, color = get_emoticon(score)
                st.markdown(f"<div style='text-align: center; font-size: 26px; color:{color};'>{tipo}: {emoticon} {score}</div>", unsafe_allow_html=True)
        # Visualizza l'indicatore globale
        global_score = indici_qualita.get("globale", 0)
        emoticon, color = get_emoticon(global_score)
        st.markdown(f"<div style='text-align: center; font-size: 36px; color:{color};'>Globale: {emoticon} {global_score}</div>", unsafe_allow_html=True)
        # Visualizza la legenda
        st.markdown("""
        <div style="
            width: 100%;
            background-color: rgba(14, 17, 23, 1);
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-family: sans-serif;
            text-align: center;
            margin-top: 20px;
        ">
            <h4 style="margin: 0; font-weight: bold;">Legenda</h4>
            <p style="margin: 5px 0; font-size: 16px;">😃 Verde: Ottima qualità</p>
            <p style="margin: 5px 0; font-size: 16px;">😊 Gialla: Buona qualità</p>
            <p style="margin: 5px 0; font-size: 16px;">😐 Gialla: Qualità media</p>
            <p style="margin: 5px 0; font-size: 16px;">😟 Arancione: Qualità bassa</p>
            <p style="margin: 5px 0; font-size: 16px;">😡 Rossa: Qualità pessima</p>
        </div>
        """, unsafe_allow_html=True)
        
    def visualizza_grafico_temporale(self, record_simulati, data_inizio, data_fine):
        """ Visualizza il grafico temporale dell'andamento di quantità, prezzo e qualità. """
        st.subheader("Andamento Temporale")
        # Crea un intervallo di date
        date_range = pd.date_range(start=data_inizio, end=data_fine).date
        dati_giornalieri = []
        # Inizializza un dizionario nella sessione per i valori casuali giornalieri
        if "daily_random" not in st.session_state:
            st.session_state["daily_random"] = {}

        # Gestisce il caso in cui sia selezionato un solo giorno
        if data_inizio == data_fine:
            st.markdown("<h2 style='text-align:center; font-weight:bold;'>Selezionare un intervallo più lungo per visualizzare gli andamenti temporali!</h2>", unsafe_allow_html=True)
            key = str(data_inizio)
            # Genera un valore casuale se non esiste già
            if key not in st.session_state["daily_random"]:
                st.session_state["daily_random"][key] = random.uniform(0, 1)
            # Filtra i record per il giorno selezionato
            record_giornalieri = [r for r in record_simulati if GestoreFiltroDati.parse_date(r) == data_inizio]
            # Calcola le metriche giornaliere
            metriche_giornaliere = self.elaboratore_dati.calcola_metriche_giornaliere(record_giornalieri)
            # Aggiunge i dati al dizionario
            dati_giornalieri.append({
                "Data": data_inizio,
                "Quantità": metriche_giornaliere['quantita'],
                "Prezzo Medio": metriche_giornaliere['prezzo_medio'],
                "Qualità Media": metriche_giornaliere['qualita_media'],
                "Circolarità": st.session_state["daily_random"][key]
            })
        # Gestisce il caso in cui sia selezionato un intervallo di date
        else:
            for single_date in date_range:
                key = str(single_date)
                # Genera un valore casuale se non esiste già
                if key not in st.session_state["daily_random"]:
                    st.session_state["daily_random"][key] = random.uniform(0, 1)
                # Filtra i record per il giorno corrente
                record_giornalieri = [r for r in record_simulati if GestoreFiltroDati.parse_date(r) == single_date]
                # Calcola le metriche giornaliere
                metriche_giornaliere = self.elaboratore_dati.calcola_metriche_giornaliere(record_giornalieri)
                # Aggiunge i dati al dizionario
                dati_giornalieri.append({
                    "Data": single_date,
                    "Quantità": metriche_giornaliere["quantita"],
                    "Prezzo Medio": metriche_giornaliere["prezzo_medio"],
                    "Qualità Media": metriche_giornaliere["qualita_media"],
                    "Circolarità": st.session_state["daily_random"][key]
                })
        # Visualizza il grafico solo se è selezionato un intervallo di date
        if data_inizio != data_fine:
            # Estrae i dati dalle liste
            quantities = [item["Quantità"] for item in dati_giornalieri]
            prices = [item["Prezzo Medio"] for item in dati_giornalieri]
            qualities = [item["Qualità Media"] for item in dati_giornalieri]
            circularities = [item["Circolarità"] for item in dati_giornalieri]
            # Normalizza i dati
            def normalize(data):
                """ Normalizza i dati in un intervallo tra 0 e 1 """
                min_val = min(data)
                max_val = max(data)
                return [(x - min_val) / (max_val - min_val) if max_val > min_val else 0 for x in data]
            quantities_norm = normalize(quantities)
            prices_norm = normalize(prices)
            qualities_norm = normalize(qualities)
            # Crea il grafico
            fig, ax = plt.subplots()
            # Traccia le linee per quantità, prezzo e qualità
            ax.plot(date_range, quantities_norm, label="Quantità", color="blue")
            ax.plot(date_range, prices_norm, label="Prezzo", color="green")
            ax.plot(date_range, qualities_norm, label="Qualità", color="orange")
            ax.set_xlabel("Data")
            ax.set_ylabel("Valore Normalizzato")
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2)
            fig.autofmt_xdate()
            # Formatta le date sull'asse x
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mpl.dates.AutoDateLocator())
            fig.patch.set_facecolor("none")
            ax.set_facecolor("none")
            ax.tick_params(colors='white')
            # Imposta la dimensione e il peso del font per le etichette dell'asse x
            for label in ax.get_xticklabels():
                label.set_fontsize(11)
                label.set_fontweight("bold")
            # Imposta la dimensione e il peso del font per le etichette dell'asse y
            for label in ax.get_yticklabels():
                label.set_fontsize(11)
                label.set_fontweight("bold")
            # Visualizza il grafico con Streamlit
            st.pyplot(fig, use_container_width=True)
        # Visualizza la tabella dei dati giornalieri
        if dati_giornalieri:
            df_daily = pd.DataFrame(dati_giornalieri)
            # Rimuove la colonna "Circolarità" se presente
            df_daily.drop(columns=["Circolarità"], inplace=True, errors="ignore")
            df_daily.reset_index(drop=True, inplace=True)
            # Formatta le colonne numeriche
            columns_to_format = ["Quantità", "Prezzo Medio", "Qualità Media"]
            df_daily[columns_to_format] = df_daily[columns_to_format].apply(lambda col: col.map(lambda x: f"{x:.2f}"))
            # Visualizza la tabella con Streamlit
            st.dataframe(df_daily, use_container_width=True, height=200)
        else:
            st.warning("Nessun dato disponibile per la tabella dei dati giornalieri.")

class GestoreFiltroDati:
    """ Classe per la gestione del filtro dei dati per data. """
    def __init__(self):
        pass

    def seleziona_intervallo_date(self):
        """ Visualizza i controlli per la selezione dell'intervallo di date. """
        # Visualizza i radio button per la selezione della modalità di data
        modalita_data = st.radio("Selezione Data", ["Giorno", "Periodo"], horizontal=True)
        # Se la modalità è "Giorno", visualizza il date input per la selezione del giorno
        if modalita_data == "Giorno":
            data_scelta = st.date_input("Scegli un giorno", value=date.today())
            data_inizio, data_fine = data_scelta, data_scelta
        # Se la modalità è "Periodo", visualizza i date input per la selezione dell'intervallo
        else:
            data_inizio = st.date_input("Data inizio", value=date.today().replace(day=1), key="start")
            data_fine = st.date_input("Data fine", value=date.today(), key="end")
        # Se la data di inizio è successiva alla data di fine, scambia le date e mostra un warning
        if data_inizio > data_fine:
            st.warning("La data di inizio non può essere successiva a quella di fine")
            data_inizio, data_fine = data_fine, data_inizio
        return data_inizio, data_fine

    @staticmethod
    def parse_date(record):
        """ Converte la data del record da stringa a oggetto date. """
        try:
            date_value = datetime.fromisoformat(record["data"]).date()
            return date_value
        except Exception as e:
            print(f"Error parsing date for record {record}: {e}")
            return None

    def filtra_record_per_data(self, records, data_inizio, data_fine):
        """ Filtra i record in base all'intervallo di date selezionato. """
        return [r for r in records if data_inizio <= self.parse_date(r) <= data_fine]

class GestoreSimulazione:
    """ Classe per la gestione della simulazione e della visualizzazione delle metriche. """
    def __init__(self, elaboratore_dati):
        self.elaboratore_dati = elaboratore_dati

    def visualizza_slider(self):
        """ Visualizza gli slider per la simulazione (riciclo scarti e lavorazione intensiva). """
        with st.container():
            left, right = st.columns([2, 1])
            with left:
                # Slider per il riciclo degli scarti
                scarto = st.slider("Riciclo Scarti (%) - se aumento il riciclo, diminiusco lo scarto ma alzo i costi di produzione", 0, 100, 0, step=25, key="scarto_sim")
                # Slider per la lavorazione intensiva
                lavorazione = st.slider("Lavorazione Intensiva (%) - se la lavorazione è più intensiva, aumento l'utile netto ma riduco la qualità", 0, 100, 0, step=25, key="lavorazione_sim")
            return scarto, lavorazione

    def calcola_delta(self, originale, simulato):
        """ Calcola la differenza percentuale tra due valori. """
        def arrotonda_delta(val):
            """ Arrotonda il valore del delta a due decimali, se necessario. """
            return 0 if abs(val) < 0.01 else round(val, 2)
        # Gestisce il caso in cui entrambi i valori siano zero
        if originale == 0 and simulato == 0:
            return "0%"
        # Gestisce il caso in cui il valore originale sia zero
        if originale == 0:
            return "-" if simulato == 0 else "∞"
        # Calcola la differenza percentuale e la formatta come stringa
        return f"{arrotonda_delta(((simulato - originale) / originale) * 100)}%"

    def media_valori(self, records):
        """ Calcola la media dei valori di costo, utile e qualità. """
        # Gestisce il caso in cui la lista dei record sia vuota
        if not records:
            return {"costo": 0, "utile": 0, "qualita": 0}
        # Calcola la media per ogni campo
        def media(campo):
            return sum(float(r.get(campo, 0)) for r in records) / len(records)
        return {
            "costo": media("costo"),
            "utile": media("utile"),
            "qualita": media("qualita")
        }

    def visualizza_metriche_footer(self, record_preparati, record_simulati, scarto, lavorazione):
        """ Visualizza le metriche nel footer (scarto, costo produzione, utile lordo, qualità). """
        # Calcola il riepilogo di netto e scarto per i record preparati
        summary_base = self.elaboratore_dati.calcola_netto_scarto(record_preparati)
        # Calcola il riepilogo dei costi per i record preparati
        costi_base = self.elaboratore_dati.calcola_sommario_costi(record_preparati)
        # Calcola l'indice di qualità per i record preparati
        indici_qualita_base = self.elaboratore_dati.calcola_indice_qualita(record_preparati)
        # Calcola le differenze percentuali tra i dati originali e simulati
        delta_footer = self.elaboratore_dati.calcola_delta_footer(
            {
                "scarto": summary_base.get("Totale", {}).get("scarto", 0),
                "costo": costi_base.get("Media", {}).get("costo_produzione", 0),
                "utile": costi_base.get("Media", {}).get("utile_lordo", 0),
                "qualita": indici_qualita_base.get("globale", 0)
            },
            {
                "scarto": sum(float(r.get("scarto", 0)) for r in record_simulati),
                "costo": self.elaboratore_dati.calcola_sommario_costi(record_simulati).get("Media", {}).get("costo_produzione", 0),
                "utile": self.elaboratore_dati.calcola_sommario_costi(record_simulati).get("Media", {}).get("utile_lordo", 0),
                "qualita": self.elaboratore_dati.calcola_indice_qualita(record_simulati).get("globale", 0)
            }
        )
        # Visualizza le metriche nel footer
        st.markdown("---")
        st.markdown("### Differenze rispetto ai dati storici")
        col1, col2, col3, col4 = st.columns(4)
        # Visualizza la metrica dello scarto
        col1.metric("Scarto", f"{sum(float(r.get('scarto', 0)) for r in record_simulati):.2f}", delta_footer["scarto_pct"])
        # Visualizza la metrica del costo di produzione
        col2.metric("Costo Produzione", f"{self.elaboratore_dati.calcola_sommario_costi(record_simulati).get('Media', {}).get('costo_produzione', 0):.2f}", delta_footer["costo_produzione"])
        # Visualizza la metrica dell'utile lordo
        col3.metric("Utile Lordo", f"{self.elaboratore_dati.calcola_sommario_costi(record_simulati).get('Media', {}).get('utile_lordo', 0):.2f}", delta_footer["utile_lordo"])
        # Visualizza la metrica della qualità
        col4.metric("Qualità", f"{self.elaboratore_dati.calcola_indice_qualita(record_simulati).get('globale', 0):.2f}", delta_footer["qualita"])
        return record_simulati

    def visualizza_indicatori_circolarita(self, scarto, lavorazione):
        """ Visualizza gli indicatori di circolarità e Green Action Score. """
        with st.container():
            left, right = st.columns([2, 1])
            with right:
                # Calcola la percentuale di circolarità
                circularity_percentage = int(scarto) - int(lavorazione // 2)
                # Assicura che la percentuale sia compresa tra 0 e 100
                circularity_percentage = max(0, min(100, circularity_percentage))
                # Calcola il Green Action Score
                green_action_score = int(scarto // 10) - int(lavorazione // 10)
                # Assicura che il Green Action Score sia compreso tra 0 e 10
                green_action_score = max(0, min(10, green_action_score))
                # Funzione per ottenere il colore in base alla percentuale di circolarità
                def get_circularity_color(percentage):
                    if percentage >= 80:
                        return "green"
                    elif percentage >= 50:
                        return "yellow"
                    else:
                        return "red"
                # Determina il colore della circolarità
                circularity_color = get_circularity_color(circularity_percentage)
                # Funzione per ottenere il simbolo e il colore in base al valore
                def get_indicator(value, thresholds, symbols, colors):
                    if value < thresholds[0]:
                        return symbols[0], colors[0]
                    elif value < thresholds[1]:
                        return symbols[1], colors[1]
                    else:
                        return symbols[2], colors[2]
                # Definisce i simboli e i colori per gli indicatori
                symbols = ["🟠", "🟡", "🟢"]
                symbols_green = ["🏜️", "🏘️", "🌱"]
                colors = ["orange", "gold", "green"]
                # Determina il simbolo e il colore per la circolarità
                circ_symbol, circ_color = get_indicator(circularity_percentage, [50, 80], symbols, colors)
                # Determina il simbolo e il colore per il Green Action Score
                green_symbol, green_color = get_indicator(green_action_score, [4, 8], symbols_green, colors)
                # Visualizza gli indicatori con Streamlit
                st.markdown(f"""
                    <div style="text-align: center; font-size: 50px; color: {circ_color};">{circ_symbol}</div>
                    <div style="text-align: center; font-size: 20px; color: {circ_color};">Circolarità Simulata: {circularity_percentage}%</div>
                    <div style="text-align: center; font-size: 50px; color: {green_color};">{green_symbol}</div>
                    <div style="text-align: center; font-size: 20px; color: {green_color};">Green Action Score: {green_action_score}/10</div>
                """, unsafe_allow_html=True)


class GestoreDati:
    """ Classe per la gestione dei dati storici e manuali. """
    def __init__(self, generatore_storico, gestore_input_manuale, elaboratore_dati):
        self.generatore_storico = generatore_storico
        self.gestore_input_manuale = gestore_input_manuale
        self.elaboratore_dati = elaboratore_dati

    def carica_dati(self):
        """ Carica i dati storici dal file JSON. """
        record_storici = []
        if os.path.exists("historical_data.json"):
            with open("historical_data.json", "r") as f:
                record_storici = json.load(f)
        return record_storici

    def aggiorna_dati_storici(self, record_storici):
        """ Aggiorna i dati storici se necessario; se i dati storici non sono aggiornati ad oggi, li rigenera. """
        if record_storici:
            # Trova l'ultima data presente nei record storici
            ultima_data_record = max(datetime.fromisoformat(r["data"]).date() for r in record_storici)
            # Prende la data di oggi
            oggi = date.today()
            # Se l'ultima data è precedente a oggi, rigenera i dati storici
            if ultima_data_record < oggi:
                st.info("I dati storici non sono aggiornati. Rigenerazione in corso...")
                data_inizio = oggi.replace(year=oggi.year - 5)
                record_storici = self.generatore_storico.genera_dati_storici(data_inizio, oggi)
                self.generatore_storico.salva_dati_storici(record_storici)
                st.success("Dati storici rigenerati e salvati in 'historical_data.json'.")
        else:
            # Se non ci sono dati storici, li genera
            st.info("Nessun dato storico trovato. Generazione in corso...")
            oggi = date.today()
            data_inizio = oggi.replace(year=oggi.year - 5)
            record_storici = self.generatore_storico.genera_dati_storici(data_inizio, oggi)
            self.generatore_storico.salva_dati_storici(record_storici)
            st.success("Dati storici generati e salvati in 'historical_data.json'.")
        return record_storici

    def unisci_dati(self, record_storici, record_manuali):
        """ Unisce i record storici e manuali; i record manuali sovrascrivono quelli storici se hanno la stessa data e lo stesso tipo. """
        # Creo un dizionario dove la chiave è la tupla (data, tipo)
        combinati = {}
        for r in record_storici:
            key = self.elaboratore_dati.chiave_record(r)
            # Aggiungo il record solo se la chiave non esiste già
            if key not in combinati:
                combinati[key] = r

        # I record manuali sovrascrivono quelli storici se hanno la stessa data e lo stesso tipo
        for r in record_manuali:
            key = self.elaboratore_dati.chiave_record(r)
            combinati[key] = r

        record_finali = list(combinati.values())
        return record_finali

class GestoreLayoutPagina:
    """ Classe per la gestione del layout della pagina Streamlit; questa classe gestisce la configurazione della pagina, la visualizzazione dell'header e del footer e la creazione della griglia per i grafici. """
    def __init__(self):
        self.configura_pagina()
        self.configura_markdown()

    def configura_pagina(self):
        """ Configura le impostazioni della pagina Streamlit. """
        st.set_page_config(layout="wide", page_title="Fi.Co? S.Vi.To.! A Fishing Company Simulation and Visualization Tool - Ver. 1.0")

    def configura_markdown(self):
        """ Configura gli stili CSS personalizzati per la pagina. """
        st.markdown("""
            <style>
                .cell-container {
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    height: 100%;
                }
                div[data-testid="stDataFrameContainer"] {
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                }
                .map-legend-container {
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                    height: 100%;
                }
            </style>
        """, unsafe_allow_html=True)

    def visualizza_header(self):
        """ Visualizza l'header della pagina."""
        st.markdown(
            "<h2 style='text-align:center; font-weight:bold;'>Fi.Co? S.Vi.To.! A Fishing Company Simulation and Visualization Tool</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<h3 style='text-align:center; font-weight:italic;'>Ver. 1.0</h3>",
            unsafe_allow_html=True
        )

    def crea_griglia(self):
        """ Crea la griglia per i grafici. """
        row1, row2 = st.columns(3), st.columns(3)
        return row1, row2

    def visualizza_contenitore_cella(self):
        """ Visualizza il contenitore per una cella della griglia. """
        st.markdown('<div class="cell-container">', unsafe_allow_html=True)

    def chiudi_contenitore_cella(self):
        """ Chiude il contenitore per una cella della griglia. """
        st.markdown('</div>', unsafe_allow_html=True)

    def visualizza_footer(self):
        """ Visualizza il footer della pagina. """
        st.markdown('</div>', unsafe_allow_html=True)

class GestoreSidebar:
    """ Classe per la gestione della sidebar di Streamlit. """
    def __init__(self, generatore_storico, gestore_input_manuale, gestore_dati):
        """ Inizializza il GestoreSidebar. """
        self.generatore_storico = generatore_storico
        self.gestore_input_manuale = gestore_input_manuale
        self.gestore_dati = gestore_dati

    def visualizza_sidebar(self):
        """ Visualizza la sidebar con i controlli per la generazione dei dati e l'input manuale. """
        with st.sidebar:
            st.header("Generazione Dati")
            # Bottone per rigenerare i dati storici
            if st.button("Rigenera Dati Storici"):
                oggi = date.today()
                data_inizio = oggi.replace(year=oggi.year - 5)
                record_storici = self.generatore_storico.genera_dati_storici(data_inizio, oggi)
                self.generatore_storico.salva_dati_storici(record_storici)
                st.success("Dati storici rigenerati e salvati in 'historical_data.json'.")

            st.markdown("---")
            st.header("Input dei Manuale Campioni")
            # Visualizza l'interfaccia per l'input manuale
            self.gestore_input_manuale.render_input_manuali()
            # Visualizza i record manuali inseriti
            self.gestore_input_manuale.viz_record_manuali()
            # Bottone per resettare i campioni manuali
            if st.button("Reset dei Campioni Manuali"):
                self.gestore_input_manuale.reset_record_manuali()
            
            # Aggiungo un controllo per aggiornare record_finali
            if "manual_records" in st.session_state:
                record_finali = self.gestore_dati.unisci_dati(self.gestore_dati.carica_dati(), st.session_state["manual_records"])
                st.session_state["record_finali"] = record_finali

            st.markdown("---")