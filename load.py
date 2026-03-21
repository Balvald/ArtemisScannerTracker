"""Artemis Scanner Tracker v0.3.3 - dev by Balvald."""

import json
import logging
import os
import tkinter as tk
from typing import Optional

import eventhandling
import organicinfo as orgi
import ui

# Own Modules
from AST import ArtemisScannerTracker

# EDMC specific imports
try:
    import myNotebook as nb  # type: ignore  # noqa: N813
    from config import appname  # type: ignore

    testmode = False
except ImportError:
    import tkinter.ttk as nb  # type: ignore

    testmode = True

frame: Optional[tk.Frame] = None

# Shows debug fields in preferences when True

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

PLUGIN_NAME = "AST"

AST_VERSION = "v0.3.3"

AST_REPO = "Balvald/ArtemisScannerTracker"

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-"

firstdashboard = True
firstsystemevent = True

not_yet_sold_data = {}
sold_exobiology = {}
currententrytowrite = {}
cmdrstates = {}

plugin = None

# Gonna need the files directory to store data for full
# tracking of all the biological things that the CMDR scans.
directory, filename = os.path.split(os.path.realpath(__file__))

filenames = ["/soldexplodata.json", "/notsoldexplodata.json",
             "/soldbiodata.json", "/notsoldbiodata.json",
             "/cmdrstates.json"]

if not testmode:
    for file in filenames:
        if not os.path.exists(directory + file):
            f = open(directory + file, "w", encoding="utf8")
            f.write(r"{}")
            f.close()
        elif file == "/soldbiodata.json" or file == "/notsoldbiodata.json":
            # (not)soldbiodata file already exists
            with open(directory + file, "r+", encoding="utf8") as f:
                test = json.load(f)
                if type([]) == type(test):  # noqa: E721
                    # we have an old version of the (not)soldbiodata.json
                    # clear it, have the user do the journal crawling again.
                    logger.warning(f"Found old {file} format")
                    logger.warning("Clearing file...")
                    f.seek(0)
                    f.write(r"{}")
                    f.truncate()


# load notyetsolddata and cmdrstates

with open(directory + "/notsoldbiodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_data = json.load(f)

with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_explo = json.load(f)

with open(directory + "/soldexplodata.json", "r+", encoding="utf8") as f:
    sold_explo = json.load(f)

with open(directory + "/cmdrstates.json", "r+", encoding="utf8") as f:
    cmdrstates = json.load(f)


# region eventhandling

def dashboard_entry(cmdr: str, is_beta, entry) -> None:  # noqa: CCR001
    """
    React to changes in the CMDRs status (Movement for CCR feature).

    :param cmdr: The current ED Commander
    :param is_beta: Is the game currently in beta
    :param entry: full excerpt from status.json
    """
    # TODO: Move most of this into AST.py class

    global plugin, firstdashboard

    if plugin.AST_debug.get():
        logger.debug("Called Dashboard ...")

    if plugin.AST_in_Legacy is True:
        # We're in legacy we don't update anything through dashboard entries
        return

    # flag determines if we have to rebuild the ui at the end.
    flag = plugin.handle_possible_cmdr_change(cmdr)

    if firstdashboard:
        firstdashboard = False
        plugin.on_preferences_closed(cmdr, is_beta)
        if plugin.AST_debug.get():
            logger.debug("Prepared for First Dashboard")

    if "PlanetRadius" in entry.keys():
        currentbody = plugin.AST_current_body.get()
        # flag = True
        # We found a PlanetRadius again, this means we are near a planet.
        if plugin.AST_debug.get():
            logger.debug("On planet")
        if currentbody != entry["BodyName"]:
            # Body we are currently at isn't the one we currently assume
            currentbody = entry["BodyName"]
            plugin.AST_current_body.set(entry["BodyName"])
            flag = True

        if not plugin.AST_near_planet:
            # We just came into range of a planet again.
            if plugin.AST_debug.get():
                logger.debug(f"just realized we approach a planet, nearplanet: {plugin.AST_near_planet}")
            flag = True
        if currentbody not in ["", None, "None"]:
            if plugin.AST_debug.get():
                logger.debug(plugin.AST_bios_on_planet)
            try:
                plugin.AST_num_bios_on_planet = plugin.AST_bios_on_planet[currentbody]
            except (KeyError, TypeError):
                # Nothing found at currently closest planet
                if plugin.AST_debug.get():
                    logger.warning(f"No amount of bio signals found for body; {currentbody} with key: {currentbody}")

        plugin.AST_near_planet = True
        plugin.AST_current_radius = entry["PlanetRadius"]
        plugin.AST_current_pos_vector[0] = entry["Latitude"]
        plugin.AST_current_pos_vector[1] = entry["Longitude"]
        plugin.AST_current_pos_vector[2] = entry["Heading"]
        if plugin.AST_current_pos_vector[2] < 0:
            # Frontier gives us different value intervals for headings in the status.json
            # Within a vehicle (srv, ship) its (0, 360) but on foot it is (-180, 180) ffs!
            # With this change we force every bearing to be in the (0, 360) interval
            plugin.AST_current_pos_vector[2] += 360
        text = "lat: " + str(round(plugin.AST_current_pos_vector[0], 2)) + \
               ", long: " + str(round(plugin.AST_current_pos_vector[1], 2)) + ", B:" + \
               str(plugin.AST_current_pos_vector[2])  # + ", " + str(plugin.AST_current_radius)
        plugin.AST_current_pos.set(text)

        if plugin.AST_current_scan_progress.get() in ["1/3", "2/3"] and plugin.AST_scan_1_pos_vector[0] is not None:
            distance1 = orgi.computedistance(plugin.AST_current_pos_vector[0],
                                             plugin.AST_current_pos_vector[1],
                                             plugin.AST_scan_1_pos_vector[0],
                                             plugin.AST_scan_1_pos_vector[1],
                                             plugin.AST_current_radius)
            plugin.AST_scan_1_pos_dist.set(str(round(distance1))
                                           + " m / " + str(plugin.AST_CCR.get()) + " m, B:" +
                                           str(round(orgi.bearing(plugin.AST_current_pos_vector[0],
                                                                  plugin.AST_current_pos_vector[1],
                                                                  plugin.AST_scan_1_pos_vector[0],
                                                                  plugin.AST_scan_1_pos_vector[1]), 2)))
            olddist1check = plugin.AST_scan_1_dist_green
            plugin.AST_scan_1_dist_green = False
            if plugin.AST_CCR.get() < distance1:
                plugin.AST_scan_1_dist_green = True
            if olddist1check != plugin.AST_scan_1_dist_green:
                flag = True
        if plugin.AST_current_scan_progress.get() in ["1/3", "2/3"] and plugin.AST_scan_2_pos_vector[0] is not None:
            distance2 = orgi.computedistance(plugin.AST_current_pos_vector[0],
                                             plugin.AST_current_pos_vector[1],
                                             plugin.AST_scan_2_pos_vector[0],
                                             plugin.AST_scan_2_pos_vector[1],
                                             plugin.AST_current_radius)
            plugin.AST_scan_2_pos_dist.set(str(round(distance2, 2))
                                           + " m / " + str(plugin.AST_CCR.get()) + " m, B:" +
                                           str(round(orgi.bearing(plugin.AST_current_pos_vector[0],
                                                                  plugin.AST_current_pos_vector[1],
                                                                  plugin.AST_scan_2_pos_vector[0],
                                                                  plugin.AST_scan_2_pos_vector[1]), 2)))
            olddist2check = plugin.AST_scan_2_dist_green
            plugin.AST_scan_2_dist_green = False
            if plugin.AST_CCR.get() < distance2:
                plugin.AST_scan_2_dist_green = True
            if olddist2check != plugin.AST_scan_2_dist_green:
                flag = True
    else:
        if plugin.AST_near_planet:
            # Switch happened, we went too far from the planet to get any reference from it.
            flag = True
            if plugin.AST_debug.get():
                logger.debug(f"just realized we approach a planet, nearplanet: {plugin.AST_near_planet}")
        plugin.AST_num_bios_on_planet = 0
        plugin.AST_near_planet = False
        plugin.AST_current_radius = None
        plugin.AST_current_pos_vector[0] = None
        plugin.AST_current_pos_vector[1] = None
        plugin.AST_current_pos_vector[2] = None
        plugin.AST_current_pos.set("No reference point")

    if plugin.AST_debug.get():
        logger.debug(f"nearplanet is now: {plugin.AST_near_planet}, will rebuild UI: {flag}")

    if (((plugin.AST_last_scan_body.get() == "")
         or (plugin.AST_last_scan_body.get() == "None"))):
        plugin.AST_last_scan_body.set(currentbody)

    if flag:
        if not plugin.AST_near_planet:
            plugin.AST_current_body.set("")
        plugin.on_preferences_closed(cmdr, is_beta)
        # ui.rebuild_ui(plugin, cmdr) is already done in on_preferences_closed


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry, state) -> None:  # noqa: CCR001
    """
    React accordingly to events in the journal.

    Scan Organic events tell us what we have scanned.
    Scan Type of these events can tell us the progress of the scan.
    Add the value of a finished Scan to the tally
    :param cmdr: The current ED Commander
    :param is_beta: Is the game currently in beta
    :param system: Current system, if known
    :param station: Current station, if any
    :param entry: the current Journal entry
    :param state: More info about the commander, their ship, and their cargo
    """
    global plugin, firstsystemevent

    if plugin.AST_debug.get():
        logger.debug(entry)
        logger.debug(f"Current event is {entry['event']}")
        logger.debug(f"Current state Gameversion {state['GameVersion']}")
        logger.debug(f"State of AST_in_Legacy variable: {plugin.AST_in_Legacy}")

    if ((int(state["GameVersion"][0]) < 4) and (plugin.AST_in_Legacy is False)):
        # We're in Legacy, we'll not change the state of anything through journal entries.
        plugin.AST_in_Legacy = True
        return
    else:
        plugin.AST_in_Legacy = False

    if plugin.AST_debug.get():
        logger.debug("Got past Version check")

    # flag determines if we have to rebuild the ui at the end.
    flag = plugin.handle_possible_cmdr_change(cmdr)
    if plugin.AST_debug.get():
        logger.debug("Handled possible CMDR change")

    # TODO: Check if upon death in 4.0 Horizons do we lose Exobiodata.
    # Probably?

    # Dying while in Frontline solutions CZ does not have a Resurrect event.
    # Also doesn't lose the Exobiology data.

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        flag = True
        plugin.notyetsolddata[cmdr] = eventhandling.resurrection_event(plugin)

    if entry["event"] == "ScanOrganic":
        if plugin.AST_debug.get():
            logger.debug("Encountered Scan Organic Event")
        flag = True
        if plugin.AST_debug.get():
            logger.debug("Calling eventhandler")
        eventhandling.bioscan_event(cmdr, is_beta, entry, plugin, currententrytowrite)
        if plugin.AST_debug.get():
            logger.debug("Finished handling ScanOrganic Event")

    if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
        flag = True
        eventhandling.system_body_change_event(cmdr, entry, plugin)

    if entry["event"] == "SellOrganicData":
        flag = True
        eventhandling.biosell_event(cmdr, entry, plugin)

    if entry["event"] == "SAASignalsFound":
        if plugin.AST_debug.get():
            logger.debug(entry)
        eventhandling.SAASignalsFound_event(entry, plugin)
        flag = True

    if entry["event"] == "FSSDiscoveryScan":
        # FSS Discovery Scan
        # System name, BodyCount, NonBodyCount
        # Progress shows how far we finished the FSS Scan already.
        # If we have Progress 1.0 we have found all bodies in the system.
        # TODO Check if we never get Scan events with ScanType AutoScan or
        # Detailed once we reached this.
        # If so we really might want to ask some database for all the bodies in the system
        # and add them as already found and sold data.
        # { "timestamp":"2025-08-24T14:10:32Z", "event":"FSSDiscoveryScan",
        #   "Progress":0.186954, "BodyCount":11, "NonBodyCount":0,
        #   "SystemName":"Synuefe PK-V b48-0", "SystemAddress":672027125153 }
        print(entry)

    if entry["event"] == "FSSAllBodiesFound":
        # found all bodies in system
        # Doesn't appear in already known systems.
        # Is actually kind of useless as we will end up with FSSDiscoveryScan with Progress 1.0
        # more often enough anyway and that event has all the info we get from this event aswell.
        # (this one actually has less info)
        # TODO Remove this later.
        # { "timestamp":"2025-08-24T14:08:31Z",
        #   "event":"FSSAllBodiesFound",
        #   "SystemName":"Synuefe GX-K c24-11",
        #   "SystemAddress":3107710603986, "Count":3 }
        print(entry)

    if entry["event"] == "Scan":
        if entry["ScanType"] == "AutoScan":
            # AutoScan
            if "Cluster" not in entry["BodyName"]:
                # Ignore Cluster scans so we should only get Stars or starlike objects
                # { "timestamp":"2025-08-24T14:20:10Z", "event":"Scan", "ScanType":"AutoScan",
                # "BodyName":"Synuefe GX-K c24-3 A", "BodyID":1, "Parents":[ {"Null":0} ],
                # "StarSystem":"Synuefe GX-K c24-3", "SystemAddress":908687348434,
                # "DistanceFromArrivalLS":0.000000, "StarType":"G", "Subclass":5,
                # "StellarMass":0.882813, "Radius":603914240.000000,
                # "AbsoluteMagnitude":5.321030, "Age_MY":2080,
                # "SurfaceTemperature":5538.000000, "Luminosity":"Vab",
                # "SemiMajorAxis":406617200374.603271, "Eccentricity":0.055510,
                # "OrbitalInclination":77.703166, "Periapsis":40.601332,
                # "OrbitalPeriod":638497835.397720, "AscendingNode":93.603429,
                # "MeanAnomaly":21.500488, "RotationPeriod":270961.664832,
                # "AxialTilt":0.000000, "WasDiscovered":false, "WasMapped":false }
                print(entry)
                # Add Star to notsoldexplodata
                # check if we already have this entry in sold_explodata
                with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
                    notsoldexplodata = json.load(f)
                    plugin.notyetsoldexplo[cmdr].append({"type": "star",
                                                         "system": entry["StarSystem"],
                                                         "body": entry["BodyName"],
                                                         "fss": True,
                                                         "dss": None})

                    notsoldexplodata = plugin.notyetsoldexplo
                    f.seek(0)
                    json.dump(notsoldexplodata, f, indent=4)
                    f.truncate()

        if entry["ScanType"] == "Detailed":
            # { "timestamp":"2025-08-24T14:17:28Z", "event":"Scan", "ScanType":"Detailed",
            # "BodyName":"Synuefe PK-V b48-0 7", "BodyID":8, "Parents":[ {"Star":0} ],
            # "StarSystem":"Synuefe PK-V b48-0", "SystemAddress":672027125153,
            # "DistanceFromArrivalLS":3541.510279, "TidalLock":false, "TerraformState":"",
            # "PlanetClass":"Icy body", "Atmosphere":"thin neon atmosphere",
            # "AtmosphereType":"Neon", "AtmosphereComposition":[
            # { "Name":"Neon", "Percent":99.314926 },
            # { "Name":"Helium", "Percent":0.685068 } ],
            # "Volcanism":"water magma volcanism",
            # "MassEM":0.511434, "Radius":6310153.000000,
            # "SurfaceGravity":5.119400, "SurfaceTemperature":35.006001,
            # "SurfacePressure":313.713379,
            # "Landable":true,
            # "Materials":[ { "Name":"sulphur", "Percent":22.743006 },
            # { "Name":"carbon", "Percent":19.124514 },
            # { "Name":"iron", "Percent":15.989780 },
            # { "Name":"phosphorus", "Percent":12.243841 },
            # { "Name":"nickel", "Percent":12.094001 },
            # { "Name":"chromium", "Percent":7.191136 },
            # { "Name":"zinc", "Percent":4.345424 },
            # { "Name":"selenium", "Percent":3.559472 },
            # { "Name":"niobium", "Percent":1.092816 },
            # { "Name":"molybdenum", "Percent":1.044123 },
            # { "Name":"technetium", "Percent":0.571890 } ],
            # "Composition":{ "Ice":0.667525, "Rock":0.222052, "Metal":0.110423 },
            # "SemiMajorAxis":1057057976722.717285, "Eccentricity":0.004564,
            # "OrbitalInclination":-2.422081, "Periapsis":175.671089,
            # "OrbitalPeriod":962838661.670685, "AscendingNode":-111.238039,
            # "MeanAnomaly":195.056850, "RotationPeriod":174289.784540,
            # "AxialTilt":0.870975, "WasDiscovered":false, "WasMapped":false }
            print(entry)
            # Add Planet to notsoldexplodata
            # check if we already have this entry in sold_explodata
            with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
                notsoldexplodata = json.load(f)
                not_found = True

                for scan in plugin.notyetsoldexplo[cmdr]:
                    if (scan["body"] == entry["BodyName"] and scan["system"] == entry["StarSystem"]):
                        not_found = False
                        break

                if not_found:
                    plugin.notyetsoldexplo[cmdr].append({"type": "planet",
                                                         "system": entry["StarSystem"],
                                                         "body": entry["BodyName"],
                                                         "fss": True,
                                                         "dss": False})

                notsoldexplodata = plugin.notyetsoldexplo
                f.seek(0)
                json.dump(notsoldexplodata, f, indent=4)
                f.truncate()

    if entry["event"] == "SAAScanComplete":
        # SAAScanComplete
        # { "timestamp":"2025-08-24T14:17:28Z",
        # "event":"SAAScanComplete",
        # "BodyName":"Synuefe PK-V b48-0 7",
        # "SystemAddress":672027125153, "BodyID":8,
        # "ProbesUsed":3, "EfficiencyTarget":7 }
        print(entry)
        # find the scan in plugin.notyetsoldexplo and mark it as dss = true
        with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
            notsoldexplodata = json.load(f)
            not_found = True
            for scan in plugin.notyetsoldexplo[cmdr]:
                if (scan["body"] == entry["BodyName"]):
                    if scan["dss"] is False:
                        scan["dss"] = True
                    break
            if not_found:
                plugin.notyetsoldexplo[cmdr].append({"type": "planet",
                                                     "system": entry["StarSystem"],
                                                     "body": entry["BodyName"],
                                                     "fss": False,
                                                     "dss": True})
                # We didn't have the dss scan before so we sell just the dss scan.
                # but we might have had the fss scan before.

            notsoldexplodata = plugin.notyetsoldexplo
            f.seek(0)
            json.dump(notsoldexplodata, f, indent=4)
            f.truncate()

    if entry["event"] == "SAASignalsFound":
        # SAASignalsFound
        # { "timestamp":"2025-08-24T14:17:28Z", "event":"SAASignalsFound",
        # "BodyName":"Synuefe PK-V b48-0 7", "SystemAddress":672027125153,
        # "BodyID":8, "Signals":[ { "Type":"$SAA_SignalType_Biological;",
        # "Type_Localised":"Biological", "Count":1 },
        # { "Type":"$SAA_SignalType_Geological;", "Type_Localised":"Geological", "Count":2 } ],
        # "Genuses":[ { "Genus":"$Codex_Ent_Bacterial_Genus_Name;",
        # "Genus_Localised":"Bacterium" } ] }
        print(entry)
        # for AST codex maybe?
        pass

        # Sell events

        if entry["event"] == "SellExplorationData":
            with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
                notsoldexplodata = json.load(f)

                with open(directory + "/soldexplodata.json", "r+", encoding="utf8") as fs:
                    soldexplodata = json.load(fs)

                    # SellExplorationData
                    # { "timestamp":"2025-08-24T14:38:03Z",
                    # "event":"SellExplorationData", "Systems":[ "Synuefe GX-K c24-11" ],
                    # "Discovered":[  ], "BaseValue":3440, "Bonus":0, "TotalEarnings":3096 }

                    for system in entry["Systems"]:
                        firstletter = system[0].lower()
                        if firstletter not in alphabet:
                            firstletter = "-"
                        if ((system not in plugin.sold_explo[cmdr][firstletter].keys()
                                and (system[0].lower() == firstletter or firstletter == "-"))):
                            plugin.sold_explo[cmdr][firstletter][system] = []

                        for data in plugin.notyetsoldexplo[cmdr]:
                            if data["system"] == system:
                                print("We sold data in system")
                                print(system)

                                not_found = True
                                for i in range(len(plugin.sold_explo[cmdr][firstletter][system])):
                                    if plugin.sold_explo[cmdr][firstletter][system][i]["body"] == data["body"]:
                                        not_found = False
                                        if data["fss"] or plugin.sold_explo[cmdr][firstletter][system][i]["fss"]:
                                            plugin.sold_explo[cmdr][firstletter][system][i]["fss"] = True
                                        if data["dss"] or plugin.sold_explo[cmdr][firstletter][system][i]["dss"]:
                                            plugin.sold_explo[cmdr][firstletter][system][i]["dss"] = True
                                        break

                                if not_found:
                                    plugin.sold_explo[cmdr][firstletter][system].append(data)

                        plugin.notyetsoldexplo[cmdr] = [data for data
                                                        in plugin.notyetsoldexplo[cmdr]
                                                        if data["system"] != system]

                        soldexplodata = plugin.soldexplo
                        notsoldexplodata = plugin.notyetsoldexplo
                        f.seek(0)
                        json.dump(notsoldexplodata, f, indent=4)
                        f.truncate()
                        fs.seek(0)
                        json.dump(soldexplodata, fs, indent=4)
                        fs.truncate()

        if entry["event"] == "MultiSellExplorationData":
            # MultiSellExplorationData
            # { "timestamp":"2025-08-24T14:38:55Z", "event":"MultiSellExplorationData",
            # "Discovered":[ { "SystemName":"Synuefe PK-V b48-0", "NumBodies":11 },
            # { "SystemName":"Synuefe GX-K c24-3", "NumBodies":1 },
            # { "SystemName":"Col 285 Sector RN-K c8-10", "NumBodies":1 },
            # { "SystemName":"Col 285 Sector BP-Y b14-1", "NumBodies":1 } ],
            # "BaseValue":17235, "Bonus":0, "TotalEarnings":15513 }
            print(entry)
            with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
                notsoldexplodata = json.load(f)

                with open(directory + "/soldexplodata.json", "r+", encoding="utf8") as fs:
                    soldexplodata = json.load(fs)

                    for systementry in entry["Discovered"]:
                        system = systementry["SystemName"]
                        firstletter = system[0].lower()
                        if firstletter not in alphabet:
                            firstletter = "-"
                        if ((system not in plugin.sold_explo[cmdr][firstletter].keys()
                                and (system[0].lower() == firstletter or firstletter == "-"))):
                            plugin.sold_explo[cmdr][firstletter][system] = []

                        for data in plugin.notyetsoldexplo[cmdr]:
                            if data["system"] == system:

                                not_found = True
                                for i in range(len(plugin.sold_explo[cmdr][firstletter][system])):
                                    if plugin.sold_explo[cmdr][firstletter][system][i]["body"] == data["body"]:
                                        not_found = False
                                        if data["fss"] or plugin.sold_explo[cmdr][firstletter][system][i]["fss"]:
                                            plugin.sold_explo[cmdr][firstletter][system][i]["fss"] = True
                                        if data["dss"] or plugin.sold_explo[cmdr][firstletter][system][i]["dss"]:
                                            plugin.sold_explo[cmdr][firstletter][system][i]["dss"] = True
                                        break

                                if not_found:
                                    plugin.sold_explo[cmdr][firstletter][system].append(data)

                        plugin.notyetsoldexplo[cmdr] = [data for data
                                                        in plugin.notyetsoldexplo[cmdr]
                                                        if data["system"] != system]

                    soldexplodata = plugin.soldexplo
                    notsoldexplodata = plugin.notyetsoldexplo
                    f.seek(0)
                    json.dump(notsoldexplodata, f, indent=4)
                    f.truncate()
                    fs.seek(0)
                    json.dump(soldexplodata, fs, indent=4)
                    fs.truncate()

    if flag:
        # save most recent relevant state so in case of crash of the system
        # we still have a proper record as long as it finishes saving below.
        plugin.on_preferences_closed(cmdr, is_beta)


# endregion


plugin = ArtemisScannerTracker(AST_VERSION, AST_REPO, PLUGIN_NAME,
                               directory, cmdrstates,
                               not_yet_sold_data, sold_exobiology, not_yet_sold_explo, sold_explo)


def plugin_start3(plugin_dir: str) -> str:
    """
    Handle start up of the plugin.

    See PLUGINS.md#startup
    """
    pluginname = plugin.on_load()
    return pluginname


def plugin_stop() -> None:
    """
    Handle shutdown of the plugin.

    See PLUGINS.md#shutdown
    """
    plugin.on_unload()
    return


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    """
    Handle preferences tab for the plugin.

    See PLUGINS.md#configuration
    """
    preferenceframe = plugin.setup_preferences(parent, cmdr, is_beta)
    return preferenceframe


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Handle any changed preferences for the plugin.

    See PLUGINS.md#configuration
    """
    ui.rebuild_ui(plugin, cmdr)

    plugin.on_preferences_closed(cmdr, is_beta)
    return


def plugin_app(parent: tk.Frame) -> tk.Frame:
    """
    Set up the UI of the plugin.

    See PLUGINS.md#display
    """
    global frame
    frame = plugin.setup_main_ui(parent)
    return frame
