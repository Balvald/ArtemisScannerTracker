"""
Contains the info for exobiology for the Artemis Scanner Tracker.

Such as prices for different types of organic scans and colonial range.
"""

import math

# new prices, only missing sinouos tubers and amphora plant
u14vistagenomicsprices = {
    "Fonticulua Fluctus": 16777215,
    "Tussock Stigmasis": 16777215,
    "Stratum Tectonicas": 16777215,
    "Fonticulua Segmentatus": 16777215,
    "Concha Biconcavis": 16777215,
    "Stratum Cucumisis": 16777215,
    "Recepta Deltahedronix": 16777215,
    "Fumerola Extremus": 16777215,
    "Clypeus Speculumi": 16777215,
    "Cactoida Vermis": 16777215,
    "Tussock Virgam": 16777215,
    "Recepta Conditivus": 16777215,
    "Recepta Umbrux": 16777215,
    "Osseus Discus": 16777215,
    "Aleoida Gravis": 16777215,
    "Tubus Sororibus": 9701800,
    "Clypeus Margaritus": 16777215,
    "Frutexa Flammasis": 15387600,
    "Osseus Pellebantus": 14698600,
    "Clypeus Lacrimam": 13114000,
    "Bacterium Informem": 13114000,
    "Tussock Triticum": 12323000,
    "Tubus Rosarium": 5287900,
    "Frutexa Acus": 12323000,
    "Concha Aureolas": 12323000,
    "Bacterium Volu": 12323000,
    "Fumerola Nitris": 11982000,
    "Aleoida Arcus": 11670300,
    "Tussock Capillum": 11383900,
    "Fumerola Carbosis": 10432700,
    "Fumerola Aquatis": 10432700,
    "Electricae Radialem": 10432700,
    "Electricae Pluma": 10432700,
    "Aleoida Coronamus": 10432700,
    "Frutexa Sponsae": 10045400,
    "Tussock Pennata": 9868700,
    "Tubus Conifer": 4936300,
    "Fonticulua Upupam": 9701800,
    "Bacterium Nebulus": 9116600,
    "Bacterium Scopulum": 8633800,
    "Bacterium Omentum": 8226200,
    "Concha Renibus": 8133800,
    "Tussock Serrati": 7958800,
    "Osseus Fractus": 7365300,
    "Bacterium Verrata": 7177500,
    "Fungoida Bullarum": 6896600,
    "Cactoida Pullulanta": 6844700,
    "Cactoida Cortexum": 6844700,
    "Tussock Caputus": 6557900,
    "Aleoida Spica": 6428600,
    "Aleoida Laminiae": 6428600,
    "Fungoida Gelata": 6346900,
    "Tussock Albata": 6230500,
    "Tussock Ventusa": 6193300,
    "Osseus Pumice": 6085800,
    "Fonticulua Lapida": 6017400,
    "Stratum Laminamus": 5523100,
    "Fungoida Stabitis": 5355000,
    "Tubus Cavas": 16777215,
    "Stratum Frigus": 5287900,
    "Cactoida Peperatis": 5044900,
    "Cactoida Lapis": 5044900,
    "Stratum Excutitus": 4989600,
    "Stratum Araneamus": 4989600,
    "Osseus Spiralis": 4919000,
    "Concha Labiata": 4835200,
    "Bacterium Tela": 4173100,
    "Tussock Ignis": 4004600,
    "Frutexa Flabellum": 3936600,
    "Fonticulua Digitos": 3928300,
    "Tussock Divisa": 3864400,
    "Tussock Cultro": 3864400,
    "Tussock Catena": 3864400,
    "Bacterium Cerbrus": 3732200,
    "Fungoida Setisis": 3698100,
    "Bacterium Alcyoneum": 3678100,
    "Frutexa Collum": 3645500,
    "Frutexa Metallicum": 3632700,
    "Frutexa Fera": 3632700,
    "Crystalline Shards": 3626400,
    "Amphora Plant": 3626400,
    "Viride Brain Tree": 3565100,
    "Roseum Brain Tree": 3565100,
    "Puniceum Brain Tree": 3565100,
    "Ostrinum Brain Tree": 3565100,
    "Lividum Brain Tree": 3565100,
    "Lindigoticum Brain Tree": 3565100,
    "Gypseeum Brain Tree": 3565100,
    "Aureum Brain Tree": 3565100,
    "Viride Sinuous Tubers": 3425600,
    "Violaceum Sinuous Tubers": 3425600,
    "Roseum Sinuous Tubers": 3425600,
    "Prasinum Sinuous Tubers": 3425600,
    "Lindigoticum Sinuous Tubers": 3425600,
    "Caeruleum Sinuous Tubers": 3425600,
    "Blatteum Sinuous Tubers": 3425600,
    "Albidum Sinuous Tubers": 3425600,
    "Rubeum Bioluminescent Anemone": 3399800,
    "Roseum Bioluminescent Anemone": 3399800,
    "Roseum Anemone": 3399800,
    "Puniceum Anemone": 3399800,
    "Prasinum Bioluminescent Anemone": 3399800,
    "Luteolum Anemone": 3399800,
    "Croceum Anemone": 3399800,
    "Blatteum Bioluminescent Anemone": 3399800,
    "Osseus Cornibus": 3369700,
    "Bark Mounds": 3350000,
    "Tubus Compagibus": 12323000,
    "Stratum Paleas": 3152500,
    "Stratum Limaxus": 3152500,
    "Bacterium Bullaris": 2766300,
    "Bacterium Aurasus": 2414700,
    "Tussock Propagito": 2194200,
    "Fonticulua Campestris": 1956100,
    "Tussock Pennatis": 1832900,
    "Bacterium Vesicula": 1725400,
    "Bacterium Acies": 1500000
}

# pre U14 prices for vista genomics - spare table for when values change again.
vistagenomicsprices = {
    "Fonticulua Fluctus": 900000,
    "Tussock Stigmasis": 806300,
    "Stratum Tectonicas": 806300,
    "Fonticulua Segmentatus": 806300,
    "Concha Biconcavis": 806300,
    "Stratum Cucumisis": 711500,
    "Recepta Deltahedronix": 711500,
    "Fumerola Extremus": 711500,
    "Clypeus Speculumi": 711500,
    "Cactoida Vermis": 711500,
    "Tussock Virgam": 645700,
    "Recepta Conditivus": 645700,
    "Recepta Umbrux": 596500,
    "Osseus Discus": 596500,
    "Aleoida Gravis": 596500,
    "Tubus Sororibus": 557800,
    "Clypeus Margaritus": 557800,
    "Frutexa Flammasis": 500100,
    "Osseus Pellebantus": 477700,
    "Clypeus Lacrimam": 426200,
    "Bacterium Informem": 426200,
    "Tussock Triticum": 400500,
    "Tubus Rosarium": 400500,
    "Frutexa Acus": 400500,
    "Concha Aureolas": 400500,
    "Bacterium Volu": 400500,
    "Fumerola Nitris": 389400,
    "Aleoida Arcus": 379300,
    "Tussock Capillum": 370000,
    "Fumerola Carbosis": 339100,
    "Fumerola Aquatis": 339100,
    "Electricae Radialem": 339100,
    "Electricae Pluma": 339100,
    "Aleoida Coronamus": 339100,
    "Frutexa Sponsae": 326500,
    "Tussock Pennata": 320700,
    "Tubus Conifer": 315300,
    "Fonticulua Upupam": 315300,
    "Bacterium Nebulus": 296300,
    "Bacterium Scopulum": 280600,
    "Bacterium Omentum": 267400,
    "Concha Renibus": 264300,
    "Tussock Serrati": 258700,
    "Osseus Fractus": 239400,
    "Bacterium Verrata": 233300,
    "Fungoida Bullarum": 224100,
    "Cactoida Pullulanta": 222500,
    "Cactoida Cortexum": 222500,
    "Tussock Caputus": 213100,
    "Aleoida Spica": 208900,
    "Aleoida Laminiae": 208900,
    "Fungoida Gelata": 206300,
    "Tussock Albata": 202500,
    "Tussock Ventusa": 201300,
    "Osseus Pumice": 197800,
    "Fonticulua Lapida": 195600,
    "Stratum Laminamus": 179500,
    "Fungoida Stabitis": 174000,
    "Tubus Cavas": 171900,
    "Stratum Frigus": 171900,
    "Cactoida Peperatis": 164000,
    "Cactoida Lapis": 164000,
    "Stratum Excutitus": 162200,
    "Stratum Araneamus": 162200,
    "Osseus Spiralis": 159900,
    "Concha Labiata": 157100,
    "Bacterium Tela": 135600,
    "Tussock Ignis": 130100,
    "Frutexa Flabellum": 127900,
    "Fonticulua Digitos": 127700,
    "Tussock Divisa": 125600,
    "Tussock Cultro": 125600,
    "Tussock Catena": 125600,
    "Bacterium Cerbrus": 121300,
    "Fungoida Setisis": 120200,
    "Bacterium Alcyoneum": 119500,
    "Frutexa Collum": 118500,
    "Frutexa Metallicum": 118100,
    "Frutexa Fera": 118100,
    "Crystalline Shards": 117900,
    "Amphora Plant": 117900,
    "Viride Brain Tree": 115900,
    "Roseum Brain Tree": 115900,
    "Puniceum Brain Tree": 115900,
    "Ostrinum Brain Tree": 115900,
    "Lividum Brain Tree": 115900,
    "Lindigoticum Brain Tree": 115900,
    "Gypseeum Brain Tree": 115900,
    "Aureum Brain Tree": 115900,
    "Viride Sinuous Tubers": 111300,
    "Violaceum Sinuous Tubers": 111300,
    "Roseum Sinuous Tubers": 111300,
    "Prasinum Sinuous Tubers": 111300,
    "Lindigoticum Sinuous Tubers": 111300,
    "Caeruleum Sinuous Tubers": 111300,
    "Blatteum Sinuous Tubers": 111300,
    "Albidum Sinuous Tubers": 111300,
    "Rubeum Bioluminescent Anemone": 110500,
    "Roseum Bioluminescent Anemone": 110500,
    "Roseum Anemone": 110500,
    "Puniceum Anemone": 110500,
    "Prasinum Bioluminescent Anemone": 110500,
    "Luteolum Anemone": 110500,
    "Croceum Anemone": 110500,
    "Blatteum Bioluminescent Anemone": 110500,
    "Osseus Cornibus": 109500,
    "Bark Mounds": 108900,
    "Tubus Compagibus": 102700,
    "Stratum Paleas": 102500,
    "Stratum Limaxus": 102500,
    "Bacterium Bullaris": 89900,
    "Bacterium Aurasus": 78500,
    "Tussock Propagito": 71300,
    "Fonticulua Campestris": 63600,
    "Tussock Pennatis": 59600,
    "Bacterium Vesicula": 56100,
    "Bacterium Acies": 50000
}

# Journal name translation

organicnamesjournaltolocal = {
    "$codex_ent_fonticulus_05_name;": "Fonticulua Fluctus",
    "$codex_ent_tussocks_13_name;": "Tussock Stigmasis",
    "$codex_ent_stratum_07_name;": "Stratum Tectonicas",
    "$codex_ent_fonticulus_01_name;": "Fonticulua Segmentatus",
    "$codex_ent_conchas_04_name;": "Concha Biconcavis",
    "$codex_ent_stratum_06_name;": "Stratum Cucumisis",
    "$codex_ent_recepta_02_name;": "Recepta Deltahedronix",
    "$codex_ent_fumerolas_02_name;": "Fumerola Extremus",
    "$codex_ent_clypeus_03_name;": "Clypeus Speculumi",
    "$codex_ent_cactoid_03_name;": "Cactoida Vermis",
    "$codex_ent_tussocks_14_name;": "Tussock Virgam",
    "$codex_ent_recepta_03_name;": "Recepta Conditivus",
    "$codex_ent_recepta_01_name;": "Recepta Umbrux",
    "$codex_ent_osseus_02_name;": "Osseus Discus",
    "$codex_ent_aleoids_05_name;": "Aleoida Gravis",
    "$codex_ent_tubus_02_name;": "Tubus Sororibus",
    "$codex_ent_clypeus_02_name;": "Clypeus Margaritus",
    "$codex_ent_shrubs_04_name;": "Frutexa Flammasis",
    "$codex_ent_osseus_06_name;": "Osseus Pellebantus",
    "$codex_ent_clypeus_01_name;": "Clypeus Lacrimam",
    "$codex_ent_bacterial_08_name;": "Bacterium Informem",
    "$codex_ent_tussocks_12_name;": "Tussock Triticum",
    "$codex_ent_tubus_04_name;": "Tubus Rosarium",
    "$codex_ent_shrubs_02_name;": "Frutexa Acus",
    "$codex_ent_conchas_02_name;": "Concha Aureolas",
    "$codex_ent_bacterial_09_name;": "Bacterium Volu",
    "$codex_ent_fumerolas_03_name;": "Fumerola Nitris",
    "$codex_ent_aleoids_01_name;": "Aleoida Arcus",
    "$codex_ent_tussocks_15_name;": "Tussock Capillum",
    "$codex_ent_fumerolas_01_name;": "Fumerola Carbosis",
    "$codex_ent_fumerolas_04_name;": "Fumerola Aquatis",
    "$codex_ent_electricae_02_name;": "Electricae Radialem",
    "$codex_ent_electricae_01_name;": "Electricae Pluma",
    "$codex_ent_aleoids_02_name;": "Aleoida Coronamus",
    "$codex_ent_shrubs_06_name;": "Frutexa Sponsae",
    "$codex_ent_tussocks_01_name;": "Tussock Pennata",
    "$codex_ent_tubus_01_name;": "Tubus Conifer",
    "$codex_ent_fonticulus_03_name;": "Fonticulua Upupam",
    "$codex_ent_bacterial_02_name;": "Bacterium Nebulus",
    "$codex_ent_bacterial_03_name;": "Bacterium Scopulum",
    "$codex_ent_bacterial_11_name;": "Bacterium Omentum",
    "$codex_ent_conchas_01_name;": "Concha Renibus",
    "$codex_ent_tussocks_07_name;": "Tussock Serrati",
    "$codex_ent_osseus_01_name;": "Osseus Fractus",
    "$codex_ent_bacterial_13_name;": "Bacterium Verrata",
    "$codex_ent_fungoids_03_name;": "Fungoida Bullarum",
    "$codex_ent_cactoid_04_name;": "Cactoida Pullulanta",
    "$codex_ent_cactoid_01_name;": "Cactoida Cortexum",
    "$codex_ent_tussocks_11_name;": "Tussock Caputus",
    "$codex_ent_aleoids_03_name;": "Aleoida Spica",
    "$codex_ent_aleoids_04_name;": "Aleoida Laminiae",
    "$codex_ent_fungoids_04_name;": "Fungoida Gelata",
    "$codex_ent_tussocks_08_name;": "Tussock Albata",
    "$codex_ent_tussocks_02_name;": "Tussock Ventusa",
    "$codex_ent_osseus_04_name;": "Osseus Pumice",
    "$codex_ent_fonticulus_04_name;": "Fonticulua Lapida",
    "$codex_ent_stratum_03_name;": "Stratum Laminamus",
    "$codex_ent_fungoids_02_name;": "Fungoida Stabitis",
    "$codex_ent_tubus_03_name;": "Tubus Cavas",
    "$codex_ent_stratum_08_name;": "Stratum Frigus",
    "$codex_ent_cactoid_05_name;": "Cactoida Peperatis",
    "$codex_ent_cactoid_02_name;": "Cactoida Lapis",
    "$codex_ent_stratum_01_name;": "Stratum Excutitus",
    "$codex_ent_stratum_04_name;": "Stratum Araneamus",
    "$codex_ent_osseus_03_name;": "Osseus Spiralis",
    "$codex_ent_conchas_03_name;": "Concha Labiata",
    "$codex_ent_bacterial_07_name;": "Bacterium Tela",
    "$codex_ent_tussocks_03_name;": "Tussock Ignis",
    "$codex_ent_shrubs_01_name;": "Frutexa Flabellum",
    "$codex_ent_fonticulus_06_name;": "Fonticulua Digitos",
    "$codex_ent_tussocks_10_name;": "Tussock Divisa",
    "$codex_ent_tussocks_04_name;": "Tussock Cultro",
    "$codex_ent_tussocks_05_name;": "Tussock Catena",
    "$codex_ent_bacterial_12_name;": "Bacterium Cerbrus",
    "$codex_ent_fungoids_01_name;": "Fungoida Setisis",
    "$codex_ent_bacterial_06_name;": "Bacterium Alcyoneum",
    "$codex_ent_shrubs_07_name;": "Frutexa Collum",
    "$codex_ent_shrubs_03_name;": "Frutexa Metallicum",
    "$codex_ent_shrubs_05_name;": "Frutexa Fera",
    "$codex_ent_ground_struct_ice_name;": "Crystalline Shards",
    "$codex_ent_vents_name;": "Amphora Plant",
    "$codex_ent_seedabcd_03_name;": "Viride Brain Tree",
    "$codex_ent_seed_name;": "Roseum Brain Tree",
    "$codex_ent_seedefgh_02_name;": "Puniceum Brain Tree",
    "$codex_ent_seedabcd_02_name;": "Ostrinum Brain Tree",
    "$codex_ent_seedefgh_name;": "Lividum Brain Tree",
    "$codex_ent_seedefgh_03_name;": "Lindigoticum Brain Tree",
    "$codex_ent_seedabcd_01_name;": "Gypseeum Brain Tree",
    "$codex_ent_seedefgh_01_name;": "Aureum Brain Tree",
    "$codex_ent_tubeefgh_03_name;": "Viride Sinuous Tubers",
    "$codex_ent_tubeefgh_02_name;": "Violaceum Sinuous Tubers",
    "$codex_ent_tube_name;": "Roseum Sinuous Tubers",
    "$codex_ent_tubeabcd_01_name;": "Prasinum Sinuous Tubers",
    "$codex_ent_tubeefgh_01_name;": "Lindigoticum Sinuous Tubers",
    "$codex_ent_tubeabcd_03_name;": "Caeruleum Sinuous Tubers",
    "$codex_ent_tubeefgh_name;": "Blatteum Sinuous Tubers",
    "$codex_ent_tubeabcd_02_name;": "Albidum Sinuous Tubers",
    "$codex_ent_sphereefgh_01_name;": "Rubeum Bioluminescent Anemone",
    "$codex_ent_sphereefgh_03_name;": "Roseum Bioluminescent Anemone",
    "$codex_ent_sphereabcd_03_name;": "Roseum Anemone",
    "$codex_ent_sphereabcd_02_name;": "Puniceum Anemone",
    "$codex_ent_sphereefgh_02_name;": "Prasinum Bioluminescent Anemone",
    "$codex_ent_sphere_name;": "Luteolum Anemone",
    "$codex_ent_sphereabcd_01_name;": "Croceum Anemone",
    "$codex_ent_sphereefgh_name;": "Blatteum Bioluminescent Anemone",
    "$codex_ent_osseus_05_name;": "Osseus Cornibus",
    "$codex_ent_cone_name;": "Bark Mounds",
    "$codex_ent_tubus_05_name;": "Tubus Compagibus",
    "$codex_ent_stratum_02_name;": "Stratum Paleas",
    "$codex_ent_stratum_05_name;": "Stratum Limaxus",
    "$codex_ent_bacterial_10_name;": "Bacterium Bullaris",
    "$codex_ent_bacterial_01_name;": "Bacterium Aurasus",
    "$codex_ent_tussocks_09_name;": "Tussock Propagito",
    "$codex_ent_fonticulus_02_name;": "Fonticulua Campestris",
    "$codex_ent_tussocks_06_name;": "Tussock Pennatis",
    "$codex_ent_bacterial_05_name;": "Bacterium Vesicula",
    "$codex_ent_bacterial_04_name;": "Bacterium Acies"
}


genusnamesjournaltolocal = {
    "$Codex_Ent_Aleoids_Genus_Name;": "Aleoida",
    "$Codex_Ent_Vents_Name;": "Amphora Plant",
    "$Codex_Ent_Sphere_Name;": "Anemone",
    "$Codex_Ent_Bacterial_Genus_Name;": "Bacterium",
    "$Codex_Ent_Cone_Name;": "Bark Mound",
    "$Codex_Ent_Brancae_Name;": "Brain Tree",
    "$Codex_Ent_Cactoid_Genus_Name;": "Cactoida",
    "$Codex_Ent_Conchas_Genus_Name;": "Concha",
    "$Codex_Ent_Clypeus_Genus_Name;": "Clypeus",
    "$Codex_Ent_Ground_Struct_Ice_Name;": "Crystalline Shards",
    "$Codex_Ent_Electricae_Genus_Name;": "Electricae",
    "$Codex_Ent_Fonticulus_Genus_Name;": "Fonticulua",
    "$Codex_Ent_Shrubs_Genus_Name;": "Frutexa",
    "$Codex_Ent_Fumerolas_Genus_Name;": "Fumerola",
    "$Codex_Ent_Fungoids_Genus_Name;": "Fungoida",
    "$Codex_Ent_Osseus_Genus_Name;": "Osseus",
    "$Codex_Ent_Recepta_Genus_Name;": "Recepta",
    "$Codex_Ent_Tube_Name;": "Sinuous Tubers",
    "$Codex_Ent_Stratum_Genus_Name;": "Stratum",
    "$Codex_Ent_Tubus_Genus_Name;": "Tubus",
    "$Codex_Ent_Tussocks_Genus_Name;": "Tussock"
}


# Colonial ranges in m.
clonalcolonialranges = {
    "Brain Tree": 100,
    "Bark Mound": 100,
    "Anemone": 100,
    "Sinuous Tubers": 100,
    "Aleoida": 150,
    "Bacterium": 500,
    "Cactoida": 300,
    "Clypeus": 150,
    "Concha": 150,
    "Electricae": 1000,
    "Fonticulua": 500,
    "Fumerola": 100,
    "Fungoida": 300,
    "Osseus": 800,
    "Recepta": 150,
    "Stratum": 500,
    "Tubus": 800,
    "Frutexa": 150,
    "Tussock": 200,
    "Crystalline Shards": 100,  # According to fandom. Gotta check it.
    "Amphora Plant": 100
}


def getu14vistagenomicprices():
    """Get price table."""
    return u14vistagenomicsprices


def getclonalcolonialranges(name: str) -> int:
    """Get clonal colonial ranges in m."""
    return clonalcolonialranges[name]


def genusgeneraltolocalised(name: str) -> str:
    """
    Translate journal name to localised name for organic scan.

    expects the full journal name with preceding "$"
    """
    return genusnamesjournaltolocal[name]


def generaltolocalised(name: str) -> str:
    """
    Translate journal name to localised name for organic scan.

    expects the full journal name with preceding "$" in all lowercase letters
    """
    return organicnamesjournaltolocal[name]


def computedistanceangle(lat1: float, long1: float, lat2: float, long2: float) -> float:
    """Compute the angle between two positions on a sphere."""
    result = math.acos(math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) +
                       math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                       math.cos(math.radians(long2 - long1)))
    return result


def computedistance(lat1: float, long1: float, lat2: float, long2: float, r: float) -> float:
    """Compute distance between two points (lat1, long1), (lat2, long2) on a planet with radius r."""
    angle = computedistanceangle(lat1, long1, lat2, long2)
    return angle * r


def bearing(lat1: float, lon1: float, lat2: float, lon2: float):
    # Convert latitude and longitude to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Compute the parameters for atan2
    x = math.sin(lon2 - lon1) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)

    # Compute the bearing in radians
    theta = math.atan2(x, y)

    # Return the bearing in degrees
    result = math.degrees(theta)
    if result < 0:
        result += 360

    return result
