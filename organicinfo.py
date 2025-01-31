"""
Contains the info for exobiology for the Artemis Scanner Tracker.
Such as prices for different types of organic scans and colonial range.
"""

import math

# Update 14.01 prices
vistagenomicsprices = {
    "Fonticulua Fluctus": 20000000,
    "Tussock Stigmasis": 19010800,
    "Stratum Tectonicas": 19010800,
    "Fonticulua Segmentatus": 19010800,
    "Concha Biconcavis": 19010800,
    "Stratum Cucumisis": 16202800,
    "Recepta Deltahedronix": 16202800,
    "Fumerola Extremus": 16202800,
    "Clypeus Speculumi": 16202800,
    "Cactoida Vermis": 16202800,
    "Tussock Virgam": 14313700,
    "Recepta Conditivus": 14313700,
    "Recepta Umbrux": 12934900,
    "Osseus Discus": 12934900,
    "Aleoida Gravis": 12934900,
    "Tubus Cavas": 11873200,
    "Clypeus Margaritus": 11873200,
    "Frutexa Flammasis": 10326000,
    "Osseus Pellebantus": 9739000,
    "Clypeus Lacrimam": 8418000,
    "Bacterium Informem": 8418000,
    "Tussock Triticum": 7774700,
    "Tubus Compagibus": 7774700,
    "Frutexa Acus": 7774700,
    "Concha Aureolas": 7774700,
    "Bacterium Volu": 7774700,
    "Fumerola Nitris": 7500900,
    "Aleoida Arcus": 7252500,
    "Tussock Capillum": 7025800,
    "Fumerola Carbosis": 6284600,
    "Fumerola Aquatis": 6284600,
    "Electricae Radialem": 6284600,
    "Electricae Pluma": 6284600,
    "Aleoida Coronamus": 6284600,
    "Frutexa Sponsae": 5988000,
    "Tussock Pennata": 5853800,
    "Tubus Sororibus": 5727600,
    "Fonticulua Upupam": 5727600,
    "Bacterium Nebulus": 5289900,
    "Bacterium Scopulum": 4934500,
    "Bacterium Omentum": 4638900,
    "Concha Renibus": 4572400,
    "Tussock Serrati": 4447100,
    "Osseus Fractus": 4027800,
    "Bacterium Verrata": 3897000,
    "Fungoida Bullarum": 3703200,
    "Cactoida Pullulanta": 3667600,
    "Cactoida Cortexum": 3667600,
    "Tussock Caputus": 3472400,
    "Aleoida Spica": 3385200,
    "Aleoida Laminiae": 3385200,
    "Fungoida Gelata": 3330300,
    "Tussock Albata": 3252500,
    "Tussock Ventusa": 3227700,
    "Osseus Pumice": 3156300,
    "Fonticulua Lapida": 3111000,
    "Stratum Laminamus": 2788300,
    "Fungoida Stabitis": 2680300,
    "Tubus Rosarium": 2637500,
    "Stratum Frigus": 2637500,
    "Cactoida Peperatis": 2483600,
    "Cactoida Lapis": 2483600,
    "Stratum Excutitus": 2448900,
    "Stratum Araneamus": 2448900,
    "Tubus Conifer": 2415500,
    "Osseus Spiralis": 2404700,
    "Concha Labiata": 2352400,
    "Bacterium Tela": 1949000,
    "Tussock Ignis": 1849000,
    "Frutexa Flabellum": 1808900,
    "Fonticulua Digitos": 1804100,
    "Tussock Divisa": 1766600,
    "Tussock Cultro": 1766600,
    "Tussock Catena": 1766600,
    "Bacterium Cerbrus": 1689800,
    "Fungoida Setisis": 1670100,
    "Bacterium Alcyoneum": 1658500,
    "Frutexa Collum": 1639800,
    "Frutexa Metallicum": 1632500,
    "Frutexa Fera": 1632500,
    "Amphora Plant": 1628800,
    "Crystalline Shards": 1628800,
    "Viride Brain Tree": 1593700,
    "Roseum Brain Tree": 1593700,
    "Puniceum Brain Tree": 1593700,
    "Ostrinum Brain Tree": 1593700,
    "Lividum Brain Tree": 1593700,
    "Lindigoticum Brain Tree": 1593700,
    "Gypseeum Brain Tree": 1593700,
    "Aureum Brain Tree": 1593700,
    "Viride Sinuous Tubers": 1514500,
    "Violaceum Sinuous Tubers": 1514500,
    "Lindigoticum Sinuous Tubers": 1514500,
    "Blatteum Sinuous Tubers": 1514500,
    "Roseum Sinuous Tubers": 1514500,
    "Albidum Sinuous Tubers": 1514500,
    "Prasinum Sinuous Tubers": 1514500,
    "Caeruleum Sinuous Tubers": 1514500,
    "Rubeum Bioluminescent Anemone": 1499900,
    "Roseum Bioluminescent Anemone": 1499900,
    "Roseum Anemone": 1499900,
    "Puniceum Anemone": 1499900,
    "Prasinum Bioluminescent Anemone": 1499900,
    "Luteolum Anemone": 1499900,
    "Croceum Anemone": 1499900,
    "Blatteum Bioluminescent Anemone": 1499900,
    "Osseus Cornibus": 1483000,
    "Bark Mounds": 1471900,
    "Stratum Paleas": 1362000,
    "Stratum Limaxus": 1362000,
    "Bacterium Bullaris": 1152500,
    "Bacterium Aurasus": 1000000,
    "Tussock Propagito": 1000000,
    "Fonticulua Campestris": 1000000,
    "Tussock Pennatis": 1000000,
    "Bacterium Vesicula": 1000000,
    "Bacterium Acies": 1000000
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

# Translations for Genus
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


def getvistagenomicprices():
    """Get price table."""
    return vistagenomicsprices


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
    """Compute the bearing to lat2, lon2 from the pos lat1, lon1."""
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

    # Adjustment to get the same bearing numbers as in E:D
    # Otherwise switches sign at 180 degrees
    if result < 0:
        result += 360

    return result
