import streamlit as st
import json
import random
import os
from datetime import date, timedelta
from business_logic import ElaboratoreDati

##### GENERATORE INPUT MANUALI #####
class GestoreInputManuale:
    ''' Gestisce l'input manuale dei campioni di pesca da parte dell'utente. '''
    def __init__(self, zone=None, species=None):
        # Creo le opzioni predefinite per le tendine
        self.zone = zone or ["Adriatico", "Tirreno", "Ionio", "Mediterraneo Centrale", "Mediterraneo Occidentale"]
        self.SPECIE = species or ["Acciuga", "Sardina", "Tonno rosso", "Pesce spada"]

    def render_input_manuali(self):
        ''' Visualizza l'interfaccia utente per l'inserimento manuale dei dati dei campioni e salva il campione inserito nella sessione e nel file JSON. '''
        st.subheader("Inserimento Dati Manuali")
        # Selettore della data del campione
        data_record = st.date_input("Data del Campione", value=date.today())
        # Selettore della zona di pesca
        zona = st.selectbox("Zona di pesca", options=self.zone)
        # Selettore della specie (Tipo di pesce)
        tipo = st.selectbox("Tipo di Pesce", options=self.SPECIE)
        # Inserimento del peso del campione (Kg.)
        kg = st.number_input("Peso del Campione (Kg.)", min_value=0.0, value=100.0, step=0.5)
        # Selettore del livello di stress (1 = poco stressato, 3 = molto stressato)
        stress = st.selectbox("Livello di Stress", options=[1, 2, 3],
                            format_func=lambda x: {1: "poco stressato", 2: "moderato", 3: "molto stressato"}.get(x))
        # Selettore dell'età della coltura
        eta = st.selectbox("Età della Coltura", options=["giovane", "in età", "tardivo"])
        # Selettore dell'omogeneità del campione
        omogeneita = st.selectbox("Omogeneità del Campione", options=[1, 2, 3],
                                format_func=lambda x: {1: "omogeneo", 2: "poco omogeneo", 3: "disomogeneo"}.get(x))
        # Selettore del tipo di produzione: Allevamento o Selvatico
        allevamento_selvatico = st.selectbox("Tipo (Allevamento/Selvatico)", options=["selvatico", "allevamento"])
        # Inserimento manuale del prezzo medio (€/kg)
        prezzo_medio = st.number_input("Prezzo Medio (€/kg)", min_value=0.0, value=2.50, step=0.01)
        # Bottone per salvare il campione manuale
        if st.button("Salva Campione Manuale"):
            # Calcolo di scarto e netto qui, con randomizzazione**
            scarto_pct = random.uniform(0.25, 0.35)  # Scarto tra 25% e 35%
            scarto = round(kg * scarto_pct, 2)
            netto = round(kg - scarto, 2)

            meteo = round(random.uniform(0.3, 1.0), 2)
            # bindo tutto in un nuovo record
            nuovo_record = {
                "data": data_record.isoformat(),
                "zona": zona,
                "kg": round(kg, 2),
                "tipo": tipo,
                "prezzo_medio": round(prezzo_medio, 2),
                "stress": stress,
                "eta_coltura": eta,
                "omogeneita": omogeneita,
                "allevamento_selvatico": allevamento_selvatico,
                "meteo": meteo,  
                "scarto": scarto,  
                "netto": netto    
            }
            if "manual_records" not in st.session_state:
                st.session_state["manual_records"] = []            
            # Aggiungo il nuovo record alla lista
            st.session_state["manual_records"].append(nuovo_record)            
            # Gestisco i duplicati
            elaboratore_dati = ElaboratoreDati()
            combinati = {elaboratore_dati.chiave_record(r): r for r in st.session_state["manual_records"]}
            st.session_state["manual_records"] = list(combinati.values())
            self.salva_record_manuali(st.session_state["manual_records"])
            st.success("Campione manuale salvato con successo!")    
    
    def viz_record_manuali(self):
        ''' Visualizza i record manuali inseriti dall'utente. '''
        st.subheader("Campioni Manuali Inseriti")
        if "manual_records" in st.session_state and st.session_state["manual_records"]:
            st.dataframe(st.session_state["manual_records"])
        else:
            st.write("Nessun campione manuale inserito finora.")

    def reset_record_manuali(self):
        ''' Resetta la lista dei record manuali, cancellando tutti i campioni inseriti. '''
        st.session_state["manual_records"] = []
        self.salva_record_manuali(st.session_state["manual_records"])
        st.success("Campioni manuali cancellati.")

    def salva_record_manuali(self, records, filename="manual_data.json"):
        ''' Salva i record manuali in un file JSON. '''
        elaboratore_dati = ElaboratoreDati()
        # Creo un dizionario per gestire i duplicati
        combinati = {elaboratore_dati.chiave_record(r): r for r in records}
        
        # Converto il dizionario in una lista di record
        records_unici = list(combinati.values())
        
        with open(filename, "w") as f:
            json.dump(records_unici, f, indent=2)

    def carica_record_manuali(self, filename="manual_data.json"):
        ''' Carica i record manuali da un file JSON. '''
        if os.path.exists(filename):
            with open(filename, "r") as f:
                records = json.load(f)
                elaboratore_dati = ElaboratoreDati()
                combinati = {elaboratore_dati.chiave_record(r): r for r in records}
                return list(combinati.values())
        return []
    
##### GENERATORE DATI STORICI #####
class GeneratoreDatiStorici:
    ''' Genera dati storici simulati per i campioni di pesca. '''
    def __init__(self, zone=None, species=None, historical_prices=None):
        ''' Inizializza il GeneratoreDatiStorici con le zone, le specie e i prezzi storici predefiniti. '''
        # setto le costanti di configurazione
        self.zone = zone or ["Adriatico", "Tirreno", "Ionio", "Mediterraneo Centrale", "Mediterraneo Occidentale"]
        self.SPECIE = species or ["Acciuga", "Sardina", "Tonno rosso", "Pesce spada"]
        # creo un archivio storico dei prezzi basato sulle medie del report ISTAT
        self.PREZZI_STORICI = historical_prices or {
            "Acciuga": {"2018": 2.50, "2019": 2.72, "2020": 2.88, "2021": 2.51, "2022": 2.40},
            "Sardina": {"2018": 0.95, "2019": 0.96, "2020": 0.98, "2021": 0.99, "2022": 1.01},
            "Tonno rosso": {"2018": 5.20, "2019": 5.43, "2020": 5.50, "2021": 5.91, "2022": 5.09},
            "Pesce spada": {"2018": 7.00, "2019": 7.25, "2020": 7.30, "2021": 7.35, "2022": 8.43}
        }

    def genera_indice_meteo(self):
        ''' Genera un indice meteo giornaliero casuale. '''
        return round(random.uniform(0.3, 1.0), 2)

    def genera_peso(self, species, meteo):
        ''' Simula il peso (Kg.) del campione in base alla specie e all'indice meteo. '''
        peso_base = {
            "Acciuga": 1000,
            "Sardina": 1500,
            "Tonno rosso": 800,
            "Pesce spada": 700
        }
        # Le condizioni meteo influenzano il peso: condizioni migliori (indice alto) portano a pesi maggiori
        peso = peso_base[species] * (0.9 + meteo * 0.2)
        # Aggiungo una componente casuale per rendere la simulazione più realistica
        peso += random.uniform(-5, 5)
        return round(peso, 2)

    def genera_stress(self, meteo):
        ''' Simula il livello di stress del campione in base all'indice meteo. '''
        # il meteo influenza lo stress (meteo < 0.5)
        if meteo < 0.5:
            return random.choice([1, 2])
        else:
            return random.choice([0, 1])

    def genera_eta(self):
        ''' Genera l'età del campione in modo casuale. '''
        return random.choice(["giovane", "medio", "tardivo"])

    def genera_omogeneita(self):
        ''' Genera l'omogeneità del campione in modo casuale. '''
        return random.choice([1, 2, 3])  # 1=disomogeneo, 2=mediamente omogeneo, 3=omogeneo

    def genera_allevamento(self):
        ''' Genera il tipo di produzione (allevamento/selvatico) in modo casuale. '''
        return random.choices(["selvatico", "allevamento"], weights=[80, 20])[0]

    def genera_prezzo(self, species, year):
        ''' Genera il prezzo medio del campione in base alla specie e all'anno. '''
        prezzo = self.PREZZI_STORICI.get(species, {})
        # Se non sono disponibili dati per l'anno specifico, usiamo il dato più recente (2022)
        return prezzo.get(str(year), prezzo.get("2022"))

    def genera_dati_storici(self, data_inizio, data_fine):
        ''' Genera il database storico su base giornaliera. '''
        records = []
        data_corrente = data_inizio

        while data_corrente <= data_fine:
            meteo = self.genera_indice_meteo()

            for species in self.SPECIE:
                # Assegna una zona random per ogni campione, invece che una sola zona per l'intera giornata
                zona = random.choice(self.zone)
                
                # Se meteo è molto sfavorevole (indice < 0.5), c'è una probabilità di saltare il campione
                skip_chance = max(0, 0.5 - meteo)  # più basso è meteo, maggiore è skip_chance
                if random.random() < skip_chance:
                    continue

                weight = self.genera_peso(species, meteo)
                stress = self.genera_stress(meteo)
                age = self.genera_eta()
                omogeneity = self.genera_omogeneita()
                farming = self.genera_allevamento()
                base_price = self.genera_prezzo(species, data_corrente.year)
                variation = random.uniform(-0.1, 0.1) * base_price 
                price = round(base_price + variation, 2)

                # Calcolo di scarto e netto qui, con randomizzazione
                scarto_pct = random.uniform(0.25, 0.35)  # Scarto tra 25% e 35%
                scarto = round(weight * scarto_pct, 2)
                netto = round(weight - scarto, 2)
                # bindo tutto in un nuovo record
                record = {
                    "data": data_corrente.isoformat(),
                    "zona": zona,
                    "kg": weight,
                    "tipo": species,
                    "prezzo_medio": price,
                    "stress": stress,
                    "eta_coltura": age,
                    "omogeneita": omogeneity,
                    "allevamento_selvatico": farming,
                    "meteo": meteo,
                    "scarto": scarto, 
                    "netto": netto 
                }
                records.append(record)

            data_corrente += timedelta(days=1)

        return records

    def salva_dati_storici(self, records, filename="historical_data.json"):
        ''' Salva i dati storici generati in un file JSON. '''
        with open(filename, "w") as f:
            json.dump(records, f, indent=2)

# Con main posso usarlo anche standalone per generare un archivio sotrico su 5 anni
if __name__ == "__main__":
    generator = GeneratoreDatiStorici()
    today = date.today()
    start_date = today.replace(year=today.year - 5)
    historical_records = generator.genera_dati_storici(start_date, today)
    generator.salva_dati_storici(historical_records)
    print("Database storico generato e salvato in 'historical_data.json'.")
