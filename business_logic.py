# Fi.Co? S.Vi.To.! A Fishing Company Simulation and Visualization Tool - Ver. 1.0"- business_logic.py

from collections import defaultdict

class ElaboratoreDati:
    ''' Classe per l'elaborazione dei dati relativi ai campioni di pesca. '''
    def __init__(self):
        pass

    def chiave_record(self, record):
        ''' Crea una chiave univoca per ogni record basata su data e tipo; la zona viene ignorata. '''
        return (record.get("data"), record.get("tipo"))

    # calcolo netto e scarto per tipo (per footer e indicatori)
    def calcola_netto_scarto(self, records):
        ''' Calcola il netto e lo scarto per ogni tipo di pesce. '''
        risultato = defaultdict(lambda: {"netto": 0, "scarto": 0})
        for r in records:
            tipo = r.get("tipo", "Altro")
            risultato[tipo]["netto"] += float(r.get("netto", 0))
            risultato[tipo]["scarto"] += float(r.get("scarto", 0))
        risultato["Totale"] = {"netto": sum(v["netto"] for v in risultato.values()), "scarto": sum(v["scarto"] for v in risultato.values())}
        return dict(risultato)

    # calcolo differenze % tra simulato e storico 
    def calcola_delta_footer(self, original, simulated):
        ''' Calcola le differenze percentuali tra i dati originali e simulati. '''
        def percent_change(orig, sim):
            ''' Calcola la variazione percentuale tra due valori. '''
            if orig == 0:
                return 0
            return round(((sim - orig) / orig) * 100, 2)

        delta = {
            "scarto_pct": percent_change(original.get("scarto", 0), simulated.get("scarto", 0)),
            "costo_produzione": percent_change(original.get("costo", 0), simulated.get("costo", 0)),
            "utile_lordo": percent_change(original.get("utile", 0), simulated.get("utile", 0)),
            "qualita": percent_change(original.get("qualita", 0), simulated.get("qualita", 0))
        }
        return delta

    # Pulizia dei record storici
    def prepara_dati_storici(self, records):
        ''' Prepara i dati storici, calcolando qualità, utile, prezzo finale e costo. '''
        preparati = []
        for r in records:
            r_copy = r.copy()

            kg = float(r_copy.get("kg", 0))
            # CHECK: mi assicuro che il che prezzo_medio sia sempre un numero, anche se non presente nel record originale
            prezzo_medio = float(r_copy.get("prezzo_medio", 0)) if r_copy.get("prezzo_medio") is not None else 1.0 #aggiunto fallback a 1.0
            omogeneita = int(r_copy.get("omogeneita", 1))
            stress = int(r_copy.get("stress", 1))

            # leggo scarto e netto
            scarto = float(r_copy.get("scarto", 0))
            netto = float(r_copy.get("netto", 0))

            # LOGICA: QUALITÀ: 3 + omogeneità - stress, min 0 max 5
            qualita = r_copy.get("qualita")
            if qualita is None:
                qualita = max(0, min(5.0, 3 + omogeneita - stress))

            # normalizzo UTILE lordo e PREZZO finale per €/kg se presenti come totali
            utile = r_copy.get("utile")
            prezzo_finale = r_copy.get("prezzo_finale")

            if utile is not None:
                utile = float(utile)
                if utile > 100: 
                    utile = utile / netto
            else:
                utile = prezzo_medio * 0.25

            if prezzo_finale is not None:
                prezzo_finale = float(prezzo_finale)
                if prezzo_finale > 100:
                    prezzo_finale = prezzo_finale / netto
            else:
                prezzo_finale = 0

            r_copy["scarto"] = round(scarto, 2)
            r_copy["netto"] = round(netto, 2)
            r_copy["kg"] = round(netto + scarto, 2)
            r_copy["prezzo_medio"] = prezzo_medio
            r_copy["qualita"] = round(float(qualita), 2)
            r_copy["utile"] = round(utile, 2)
            r_copy["prezzo_finale"] = round(prezzo_finale, 2)
            r_copy["costo"] = round(prezzo_medio, 2) 

            preparati.append(r_copy)

        return preparati


    # Simulazione
    def applica_simulazione_ai_record(self, records, riciclo_scarti_pct, lavorazione_intensiva_pct):
        ''' Applica la simulazione ai record, modificando scarto, netto, costo, utile, prezzo finale e qualità. '''
        # Se gli slider sono entrambi a zero, restituisco una copia dei dati originali
        if riciclo_scarti_pct == 0 and lavorazione_intensiva_pct == 0:
            return [r.copy() for r in records]

        simulated = []
        for r in records:
            r_copy = r.copy()

            kg = float(r_copy.get("kg", 0))
            prezzo_medio = float(r_copy.get("prezzo_medio", 0)) or 1.0  # evita 0
            # leggo netto e scarto
            scarto = float(r_copy.get("scarto", 0))
            netto = float(r_copy.get("netto", 0))

            # LOGICA: lo scarto si riduce se il riciclo aumenta (fino al -12%)
            scarto_pct = scarto / kg 
            scarto_pct = scarto_pct - (riciclo_scarti_pct / 100) * 0.12
            scarto = kg * scarto_pct
            netto = kg - scarto

            # LOGICA: il costo aumenta se riciclo sale (fino a +10%) e diminuisce con la lavorazione intensiva (-20%)
            costo_produzione = prezzo_medio * (1 + (riciclo_scarti_pct / 100) * 0.1 - (lavorazione_intensiva_pct / 100) * 0.2)

            # LOGICA: l'utile lordo aumenta fino a +20% con la lavorazione intensiva
            utile_lordo = r_copy.get("utile") * (1 + (lavorazione_intensiva_pct / 100) * 0.2)

            # LOGICA: calcolo il prezzo finale simulato
            prezzo_finale = costo_produzione + utile_lordo

            # LOGICA: la qualita' diminuisce fino a -1 con la lavorazione intensiva
            qualita = 3 + int(r_copy.get("omogeneita", 1)) - int(r_copy.get("stress", 0)) - (lavorazione_intensiva_pct / 100)
            qualita = max(0, min(5, round(qualita, 2)))

            r_copy.update({
                "scarto": round(scarto, 2),
                "netto": round(netto, 2),
                "costo": round(costo_produzione, 2),
                "utile": round(utile_lordo, 2),
                "prezzo_finale": round(prezzo_finale, 2),
                "qualita": qualita
            })

            simulated.append(r_copy)

        return simulated

    # Calcolo i costi medi di produzione, utile lordo e prezzo finale per tipo di pesce.
    def calcola_sommario_costi(self, records):
        ''' Calcola i costi medi di produzione, l'utile lordo e il prezzo finale per tipo di pesce. '''
        cost_summary = {}
        for r in records:
            tipo = r.get("tipo", "Altro")
            prezzo_fonte = float(r.get("prezzo_medio", 0)) if r.get("prezzo_medio") is not None else 1.0 
            costo_produzione = float(r.get("costo", prezzo_fonte)) if r.get("costo") is not None else prezzo_fonte
            raw_utile = r.get("utile", None)
            if raw_utile is None or raw_utile == 0:
                utile_lordo = costo_produzione * 0.25 
            else:
                utile_lordo = float(raw_utile)
            prezzo_finale = costo_produzione + utile_lordo

            if tipo not in cost_summary:
                cost_summary[tipo] = {
                    "costo_produzione": 0,
                    "utile_lordo": 0,
                    "prezzo_finale": 0,
                    "count": 0
                }

            cost_summary[tipo]["costo_produzione"] += costo_produzione
            cost_summary[tipo]["utile_lordo"] += utile_lordo
            cost_summary[tipo]["prezzo_finale"] += prezzo_finale
            cost_summary[tipo]["count"] += 1

        for tipo in cost_summary:
            count = cost_summary[tipo]["count"]
            cost_summary[tipo]["costo_produzione"] /= count
            cost_summary[tipo]["utile_lordo"] /= count
            cost_summary[tipo]["prezzo_finale"] /= count

        # Calcola la media generale
        if cost_summary:
            media_costo = sum(v["costo_produzione"] for v in cost_summary.values()) / len(cost_summary)
            media_utile = sum(v["utile_lordo"] for v in cost_summary.values()) / len(cost_summary)
            media_prezzo = sum(v["prezzo_finale"] for v in cost_summary.values()) / len(cost_summary)
            cost_summary["Media"] = {
                "costo_produzione": media_costo,
                "utile_lordo": media_utile,
                "prezzo_finale": media_prezzo,
                "count": len(cost_summary)
            }
        else:
            cost_summary["Media"] = {
                "costo_produzione": 0,
                "utile_lordo": 0,
                "prezzo_finale": 0,
                "count": 0
            }

        return cost_summary

    def calcola_indice_qualita(self, records):
        ''' Calcola l'indice di qualità per ogni tipo di pesce e un indice globale. '''
        qualita_per_tipo = {}
        for r in records:
            tipo = r.get("tipo", "Altro")
            qualita = float(r.get("qualita", 0))

            if tipo not in qualita_per_tipo:
                qualita_per_tipo[tipo] = {
                    "tot": 0,
                    "count": 0
                }

            qualita_per_tipo[tipo]["tot"] += qualita
            qualita_per_tipo[tipo]["count"] += 1

        for tipo in qualita_per_tipo:
            tot = qualita_per_tipo[tipo]["tot"]
            count = qualita_per_tipo[tipo]["count"]
            qualita_per_tipo[tipo] = round(tot / count, 2) if count else 0

        totale = sum(qualita_per_tipo[t] for t in qualita_per_tipo)
        count = len(qualita_per_tipo)
        qualita_per_tipo["globale"] = round(totale / count, 2) if count else 0

        return qualita_per_tipo

    def calculate_daily_metrics(self, records):
        ''' Calcola le metriche giornaliere (quantità, prezzo medio, qualità media). '''
        total_kg = sum(float(r.get("kg", 0)) for r in records)
        prezzo_medio = sum(float(r.get("prezzo_medio", 0)) for r in records) / len(records) if records else 0
        qualita_media = sum(float(r.get("qualita", 0)) for r in records) / len(records) if records else 0
        return {
            "quantita": round(total_kg, 2),
            "prezzo_medio": round(prezzo_medio, 2),
            "qualita_media": round(qualita_media, 2)
        }

    def calcola_e_simula_dati(self, prepared_records, riciclo_slider_value, lavorazione_slider_value):
        ''' Calcola e simula i dati, applicando la simulazione ai record preparati. '''
        simulated_records = self.applica_simulazione_ai_record(
            prepared_records,
            riciclo_scarti_pct=riciclo_slider_value,
            lavorazione_intensiva_pct=lavorazione_slider_value
        )

        return prepared_records, simulated_records
