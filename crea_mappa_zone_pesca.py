# Fi.Co? S.Vi.To.! A Fishing Company Simulation and Visualization Tool - Ver. 1.0"- crea_mappa_zone_pesca.py

import fiona
import geopandas as gpd
from shapely.geometry import Polygon, Point
import folium

class GestoreMappa:
    ''' Classe per la gestione della mappa delle zone di pesca. '''
    def __init__(self, percorso_gpkg):
        self.percorso_gpkg = percorso_gpkg

    def carica_eez_ita(self, nome_livello=None):
        ''' Carica i confini delle Zone Economiche Esclusive (EEZ) italiane da un file GeoPackage. '''
        if nome_livello is None:
            nome_livello = fiona.listlayers(self.percorso_gpkg)[0]
        eez = gpd.read_file(self.percorso_gpkg, layer=nome_livello)
        eez_italiane = eez[
            eez["EEZ1"].str.contains("Italian", na=False) |
            eez["EEZ2"].str.contains("Italian", na=False)
        ]
        return eez_italiane

    # 
    def suddividi_eez_ita(self, eez_italiane):
        ''' Suddivide le EEZ sudddivido i mari italiani e creo dei poligoni semplificati che vanno in overlay sulla mappa delle terre; faccio la differenza con le terre emerse (non funziona, da rivedere). '''
        zone = [
            {"nome_zona": "Adriatico", "geometria": Polygon([(12, 46.5), (19, 46.5), (19, 40), (12, 40)])},
            {"nome_zona": "Tirreno", "geometria": Polygon([(8, 44), (12, 44), (12, 37), (8, 37)])},
            {"nome_zona": "Ionio", "geometria": Polygon([(12, 40), (20, 40), (20, 34), (12, 34)])},
            {"nome_zona": "Mediterraneo Occidentale", "geometria": Polygon([(0, 46.5), (12, 46.5), (12, 44), (8, 44), (8, 37), (12, 37), (12, 34), (0, 34)])},
            {"nome_zona": "Mediterraneo Centrale", "geometria": Polygon([(19, 46.5), (30, 46.5), (30, 34), (20, 34), (20, 40), (19, 40)])}
        ]
        # Creo un GeoDataFrame dalla lista delle zone
        gdf = gpd.GeoDataFrame(zone, geometry="geometria", crs="EPSG:4326")
        return gdf
    
    def trova_punti_etichette(self, geom, posizione):
        ''' Trova un punto adatto per posizionare un'etichetta all'interno o vicino a una geometria. '''
        minx, miny, maxx, maxy = geom.bounds
        # creo un piccolo spostamento e, nel caso la posizione sia in basso a sinistra o in alto a destra, sposto di più le eitchette per renderel sempre visibili
        eps_x = (maxx - minx) * 0.02
        eps_y = (maxy - miny) * 0.02
        if posizione == "bottom_right":
            candidate = Point(maxx, miny)
            if not geom.contains(candidate):
                candidate = Point(maxx - eps_x, miny + eps_y)
            return candidate
        elif posizione == "top_left":
            candidate = Point(minx, maxy)
            if not geom.contains(candidate):
                candidate = Point(minx + eps_x, maxy - eps_y)
            return candidate
        else:
            return geom.representative_point()

    def crea_mappa_custom(self, gdf, conti_zone, schema_colori=["blue", "red"]):
        ''' Creo una mappa personalizzata con Folium, mostrando le zone e il numero di campioni per zona; per mediterraneo centrale ed occidentale, ho previsto degli spostamenti dell'etichetta per renderal ben visibile. '''
        
        # Verifico che il GeoDataFrame non sia vuoto
        if gdf is None or gdf.empty:
            print("Attenzione: GeoDataFrame è di tipo None o vuoto. Restituisco un mappa di default.")
            m = folium.Map(
                location=[40.5, 13.5],
                zoom_start=5,
                tiles="CartoDB.DarkMatter",
                max_bounds=False,
                min_zoom=5,
                max_zoom=5,
                zoom_control=False,
                dragging=False
            )
            return m

        # Verifico che la colonna zone_name esista veramente
        if 'nome_zona' not in gdf.columns:
            print("Errore: non è possibile trovare la colonna'nome_zona' nel GeoDataFrame.")
            return folium.Map(
                location=[40.5, 13.5],
                zoom_start=5,
                tiles="CartoDB.DarkMatter",
                max_bounds=False,
                min_zoom=5,
                max_zoom=5,
                zoom_control=False,
                dragging=False
            )

        # Verifico che zone counts non sia None ne un dizionario
        if conti_zone is None or not isinstance(conti_zone, dict):
            print("Errore: conti_zone è di tipo None o non è un dizionario.")
            conti_zone = {}

        # Create SampleCount column, handling missing zone
        gdf["ConteggioCampioni"] = gdf["nome_zona"].map(lambda x: conti_zone.get(x, 0))
        
        # Calcola il minimo e il massimo dei conteggi
        min_count = gdf["ConteggioCampioni"].min() if len(gdf) > 0 else 0
        max_count = gdf["ConteggioCampioni"].max() if len(gdf) > 0 else 0

        m = folium.Map(
            location=[40.5, 13.5],
            zoom_start=5,
            tiles="CartoDB.DarkMatter",
            max_bounds=False,
            min_zoom=5,
            max_zoom=5,
            zoom_control=False,
            dragging=False
        )
        if not gdf.empty:
            bounds = gdf.total_bounds
            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

        for _, row in gdf.iterrows():
            count = row["ConteggioCampioni"]
            # Gestione del caso in cui tutti i conteggi siano uguali
            if max_count == min_count:
                color = "#0E1117"  # Colore fisso se tutti i conteggi sono uguali
            else:
                # Crea la colormap con vmin e vmax basati sui valori minimi e massimi
                colormap = folium.LinearColormap(schema_colori, vmin=min_count, vmax=max_count)
                color = colormap(count)
            zone_name = row["nome_zona"]

            folium.GeoJson(
                row["geometria"],
                style_function=lambda feature, c=color: {
                    "fillColor": c,
                    "color": "white",
                    "weight": 1,
                    "fillOpacity": 0.3,
                },
                tooltip=f"{zone_name}: {count} campioni"
            ).add_to(m)

            # Calcola il punto in cui posizionare l'etichetta e determina l'ancoraggio CSS appropriato; spostamento maggiore per i due mediterranei
            if zone_name == "Mediterraneo Occidentale":
                label_point = self.trova_punti_etichette(row["geometria"], "bottom_right")
                transform_str = "translate(-800%, -100%)"
            elif zone_name == "Mediterraneo Centrale":
                label_point = self.trova_punti_etichette(row["geometria"], "top_left")
                transform_str = "translate(+100%, +20%)"
            else:
                label_point = row["geometria"].representative_point()
                transform_str = "translate(-50%, -50%)"
            
            # Aggiunge un marker con un DivIcon che usa il transform_str determinato
            folium.Marker(
                location=[label_point.y, label_point.x],
                icon=folium.DivIcon(
                    html=f'''
                    <div style="text-align: center; color: white; font-weight: bold; font-size: 14px; transform: {transform_str};">
                        {zone_name}<br>{count}
                    </div>
                    '''
                )
            ).add_to(m)

        return m

    # Calcola il numero di campioni per ciascuna zona basandosi su una proprietà 'zona' presente in ogni prodotto.
    def conta_campioni_zone(self, prodotti, colonna_zona="zona"):
        ''' Calcolo il numero di campioni per ciascuna zona. '''
        conteggi = {}
        for prodotto in prodotti:
            nome_zona = prodotto.get(colonna_zona, None)
            if nome_zona:
                conteggi[nome_zona] = conteggi.get(nome_zona, 0) + 1
        return conteggi
