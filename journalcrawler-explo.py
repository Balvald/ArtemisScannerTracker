"""
Here resides the journalcrawler that can read through all the journal files.

It retraces all exobiology scans and sell actions.
"""

import json
import os

# Own Modules
from organicinfo import generaltolocalised, getvistagenomicprices


# This goes through a folder of journals that it'll parse
# and check for analysed bio signals and the selling of it.

# This version still assumes that the CMDR will always sell
# the data in full once its sold.
# It currently does not account for the case where the CMDR
# sells the data only for a single system and then dies with the
# rest of the data still unsold.
# Losing said exobiology data.
# In this case the lost data is assumed as sold by this script.

# For best results you can put your whole selection of journals
# downloaded from Journal limpet into the journaldir


alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-"


def get_date(f_name: str, logger: any) -> str:
    """
    Get the date from a filename in form of a stanardized string.

    Format is: YYYY-MM-DD HH:MM:SS
    """
    if "CAPIJournal" in f_name:
        # This is a journal file from journal limpet
        year = "20" + f_name[12:14]
        month = f_name[14:16]
        day = f_name[16:18]
        hour = f_name[18:20]
        minute = f_name[20:22]
        second = f_name[22:24]
        # logger.debug(f"{f_name}: {year}-{month}-{day} {hour}:{minute}:{second}")
        version = "Journal Limpet"

    elif "-" in f_name:
        # This is a 4.X journal file
        year = f_name[8:12]
        month = f_name[13:15]
        day = f_name[16:18]
        hour = f_name[19:21]
        minute = f_name[21:23]
        second = f_name[23:25]
        # logger.debug(f"{f_name}: {year}-{month}-{day} {hour}:{minute}:{second}")
        version = "4.X"

    else:
        # This is a 3.X journal file
        year = "20" + f_name[8:10]
        month = f_name[10:12]
        day = f_name[12:14]
        hour = f_name[14:16]
        minute = f_name[16:18]
        second = f_name[18:20]
        # logger.debug(f"{f_name}: {year}-{month}-{day} {hour}:{minute}:{second}")
        version = "3.X"

    return [f"{year}-{month}-{day}T{hour}:{minute}:{second}Z", version]


def build_explodata_json(logger: any, journaldir: str) -> int:  # noqa: CCR001
    """Build a soldexplodata.json and a notsoldexplodata.

    These files include all exploration scans that the player sold or can sell.
    Also return the value of still unsold scans.
    """
    logger.debug("start logging")

    directory, sourcename = os.path.split(os.path.realpath(__file__))

    cmdr = ""
    currentsystem = ""
    currentbody = ""

    totalcmdrlist = []

    currententrytowrite = {}

    logger.debug(directory)

    sold_exploration = {}
    possibly_sold_data = {}

    if not os.path.exists(directory + "/soldexplodata.json"):
        f = open(directory + "/soldexplodata.json", "w", encoding="utf8")
        f.write(r"{}")
        f.close()

    with open(directory + "/soldexplodata.json", "r", encoding="utf8") as f:
        sold_exploration = json.load(f)
        # logger.debug(sold_exobiology)
        # logger.debug(len(sold_exobiology))
        pass

    if not os.path.exists(directory + "/notsoldexplodata.json"):
        f = open(directory + "/notsoldexplodata.json", "w", encoding="utf8")
        f.write(r"{}")
        f.close()

    edlogs = []

    # Order from os.listdir might depend on filesystem.
    for f in os.listdir(journaldir):
        if f.endswith(".log"):
            edlogs.append([get_date(f, logger), f])

    logger.debug(edlogs)

    # Sorting by date
    edlogs.sort(key=lambda x: x[0][0])

    logger.debug(edlogs)

    # version 3.8 files are only relevant if they are from 2021-05-18 till 2022-11-30
    logger.debug(directory)

    for filename in edlogs:
        if filename[0][1] == "3.X":
            if filename[0][0] < "2021-05-17T23:59:59Z" or filename[0][0] > "2022-11-31T00:00:00Z":
                logger.debug(f"Skipping 3.X file; date: {filename[0][0]} name {filename[1]}")
                continue

        f = os.path.join(journaldir, filename[1])
        logger.debug("Current file: " + f)
        # checking if it is a file
        if os.path.isfile(f):
            file = open(f, "r", encoding="utf8")
            lines = file.readlines()

            linepos = 1
            for line in lines:

                read_old_journal_limpet_event = False

                try:
                    entry = json.loads(line)

                    if entry["event"] in ["LoadGame", "Commander"]:
                        if entry["event"] == "Commander":
                            cmdr = entry["Name"]
                        else:
                            if filename[0][1] == "Journal Limpet":
                                if "gameversion" not in entry.keys():
                                    read_old_journal_limpet_event = True
                                else:
                                    if int(entry["gameversion"][0]) < 4:
                                        read_old_journal_limpet_event = True
                                    else:
                                        read_old_journal_limpet_event = False

                            cmdr = entry["Commander"]

                        if cmdr != "" and cmdr is not None and cmdr not in totalcmdrlist:
                            totalcmdrlist.append(cmdr)

                        if cmdr != "" and cmdr is not None and cmdr not in sold_exploration.keys():
                            sold_exploration[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
                            # logger.debug(sold_exobiology)

                        if cmdr != "" and cmdr not in possibly_sold_data.keys():
                            possibly_sold_data[cmdr] = []

                    if read_old_journal_limpet_event:
                        continue

                    if entry["event"] in ["Location", "Embark",
                                          "Disembark", "Touchdown",
                                          "Liftoff", "FSDJump"]:
                        try:
                            currentsystem = entry["StarSystem"]
                            currentbody = entry["Body"]
                        except KeyError:
                            # Was playing in old Horizons so
                            # Touchdown and Liftoff don't have body nor system
                            logger.debug("We've encountered a KeyError in the code "
                                         + "for updating the current system and body.")
                            logger.debug(entry)
                    """
                    if entry["event"] == "ScanOrganic":
                        # logger.debug("Scan organic Event!")
                        if entry["ScanType"] in ["Sample", "Analyse"]:
                            if entry["ScanType"] == "Analyse":
                                logger.debug("Scan Organic Event Type: Analyse")
                                try:
                                    currententrytowrite["species"] = generaltolocalised(entry["Species"].lower())
                                    currententrytowrite["system"] = currentsystem
                                    currententrytowrite["body"] = currentbody
                                    if currententrytowrite not in possibly_sold_data[cmdr]:
                                        possibly_sold_data[cmdr].append(currententrytowrite)
                                    currententrytowrite = {}
                                    continue
                                except KeyError as e:
                                    logger.error("Coulnd't find Species in Analyse event, Skipping")
                                    logger.error(e)
                                    logger.error(entry)
                    """

                    if entry["event"] == "FSSDiscoveryScan":
                        # FSS Discovery Scan
                        # System name, BodyCount, NonBodyCount
                        # Progress shows how far we finished the FSS Scan already.
                        # { "timestamp":"2025-08-24T14:10:32Z", "event":"FSSDiscoveryScan", "Progress":0.186954, "BodyCount":11, "NonBodyCount":0, "SystemName":"Synuefe PK-V b48-0", "SystemAddress":672027125153 }
                        print(entry)

                    if entry["event"] == "FSSAllBodiesFound":
                        # found all bodies in system
                        # { "timestamp":"2025-08-24T14:08:31Z", "event":"FSSAllBodiesFound", "SystemName":"Synuefe GX-K c24-11", "SystemAddress":3107710603986, "Count":3 }
                        print(entry)
                        pass

                    if entry["event"] == "Scan":
                        if entry["ScanType"] == "AutoScan":
                            # AutoScan
                            if "Cluster" not in entry["BodyName"]:
                                # Ignore Cluster scans so we should only get Stars or starlike objects
                                # { "timestamp":"2025-08-24T14:20:10Z", "event":"Scan", "ScanType":"AutoScan", "BodyName":"Synuefe GX-K c24-3 A", "BodyID":1, "Parents":[ {"Null":0} ], "StarSystem":"Synuefe GX-K c24-3", "SystemAddress":908687348434, "DistanceFromArrivalLS":0.000000, "StarType":"G", "Subclass":5, "StellarMass":0.882813, "Radius":603914240.000000, "AbsoluteMagnitude":5.321030, "Age_MY":2080, "SurfaceTemperature":5538.000000, "Luminosity":"Vab", "SemiMajorAxis":406617200374.603271, "Eccentricity":0.055510, "OrbitalInclination":77.703166, "Periapsis":40.601332, "OrbitalPeriod":638497835.397720, "AscendingNode":93.603429, "MeanAnomaly":21.500488, "RotationPeriod":270961.664832, "AxialTilt":0.000000, "WasDiscovered":false, "WasMapped":false }
                                print(entry)
                                # Add Star to notsoldexplodata
                                # check if we already have this entry in sold_explodata
                                possibly_sold_data[cmdr].append({"type": "star",
                                                                 "system": entry["StarSystem"],
                                                                 "body": entry["BodyName"],
                                                                 "dss": False})
                                pass
                        if entry["ScanType"] == "Detailed":
                            # { "timestamp":"2025-08-24T14:17:28Z", "event":"Scan", "ScanType":"Detailed", "BodyName":"Synuefe PK-V b48-0 7", "BodyID":8, "Parents":[ {"Star":0} ], "StarSystem":"Synuefe PK-V b48-0", "SystemAddress":672027125153, "DistanceFromArrivalLS":3541.510279, "TidalLock":false, "TerraformState":"", "PlanetClass":"Icy body", "Atmosphere":"thin neon atmosphere", "AtmosphereType":"Neon", "AtmosphereComposition":[ { "Name":"Neon", "Percent":99.314926 }, { "Name":"Helium", "Percent":0.685068 } ], "Volcanism":"water magma volcanism", "MassEM":0.511434, "Radius":6310153.000000, "SurfaceGravity":5.119400, "SurfaceTemperature":35.006001, "SurfacePressure":313.713379, "Landable":true, "Materials":[ { "Name":"sulphur", "Percent":22.743006 }, { "Name":"carbon", "Percent":19.124514 }, { "Name":"iron", "Percent":15.989780 }, { "Name":"phosphorus", "Percent":12.243841 }, { "Name":"nickel", "Percent":12.094001 }, { "Name":"chromium", "Percent":7.191136 }, { "Name":"zinc", "Percent":4.345424 }, { "Name":"selenium", "Percent":3.559472 }, { "Name":"niobium", "Percent":1.092816 }, { "Name":"molybdenum", "Percent":1.044123 }, { "Name":"technetium", "Percent":0.571890 } ], "Composition":{ "Ice":0.667525, "Rock":0.222052, "Metal":0.110423 }, "SemiMajorAxis":1057057976722.717285, "Eccentricity":0.004564, "OrbitalInclination":-2.422081, "Periapsis":175.671089, "OrbitalPeriod":962838661.670685, "AscendingNode":-111.238039, "MeanAnomaly":195.056850, "RotationPeriod":174289.784540, "AxialTilt":0.870975, "WasDiscovered":false, "WasMapped":false }
                            print(entry)
                            # Add Planet to notsoldexplodata
                            # check if we already have this entry in sold_explodata
                            not_found = True

                            for scan in possibly_sold_data[cmdr]:
                                if (scan["body"] == entry["BodyName"] and scan["system"] == entry["StarSystem"]):
                                    not_found = False
                                    break

                            if not_found:
                                possibly_sold_data[cmdr].append({"type": "planet",
                                                                 "system": entry["StarSystem"],
                                                                 "body": entry["BodyName"],
                                                                 "dss": False})
                            pass

                    if entry["event"] == "SAAScanComplete":
                        # SAAScanComplete
                        # { "timestamp":"2025-08-24T14:17:28Z", "event":"SAAScanComplete", "BodyName":"Synuefe PK-V b48-0 7", "SystemAddress":672027125153, "BodyID":8, "ProbesUsed":3, "EfficiencyTarget":7 }
                        print(entry)
                        # find the scan in possibly_sold_data and mark it as dss = true
                        for scan in possibly_sold_data[cmdr]:
                            if (scan["body"] == entry["BodyName"]):
                                if scan["dss"] is False:
                                    scan["dss"] = True
                                break
                        pass

                    if entry["event"] == "SAASignalsFound":
                        # SAASignalsFound
                        # { "timestamp":"2025-08-24T14:17:28Z", "event":"SAASignalsFound", "BodyName":"Synuefe PK-V b48-0 7", "SystemAddress":672027125153, "BodyID":8, "Signals":[ { "Type":"$SAA_SignalType_Biological;", "Type_Localised":"Biological", "Count":1 }, { "Type":"$SAA_SignalType_Geological;", "Type_Localised":"Geological", "Count":2 } ], "Genuses":[ { "Genus":"$Codex_Ent_Bacterial_Genus_Name;", "Genus_Localised":"Bacterium" } ] }
                        print(entry)
                        # for AST codex maybe?
                        pass

                    if entry["event"] == "Resurrect":
                        # Reset - player was unable to sell before death
                        logger.debug("We died")
                        possibly_sold_data[cmdr] = []

                    # Sell events

                    if entry["event"] == "SellExplorationData":
                        # SellExplorationData
                        # { "timestamp":"2025-08-24T14:38:03Z", "event":"SellExplorationData", "Systems":[ "Synuefe GX-K c24-11" ], "Discovered":[  ], "BaseValue":3440, "Bonus":0, "TotalEarnings":3096 }
                        print(entry)
                        for system in entry["Systems"]:
                            firstletter = system[0].lower()
                            if firstletter not in alphabet:
                                firstletter = "-"
                            if ((system not in sold_exploration[cmdr][firstletter].keys()
                                 and (system[0].lower() == firstletter or firstletter == "-"))):
                                sold_exploration[cmdr][firstletter][system] = []

                            for data in possibly_sold_data[cmdr]:
                                if data["system"] == system:
                                    if data not in sold_exploration[cmdr][firstletter][system]:
                                        sold_exploration[cmdr][firstletter][system].append(data)
                            possibly_sold_data[cmdr] = [data for data in possibly_sold_data[cmdr] if data["system"] != system]
                        pass

                    if entry["event"] == "MultiSellExplorationData":
                        # MultiSellExplorationData
                        # { "timestamp":"2025-08-24T14:38:55Z", "event":"MultiSellExplorationData", "Discovered":[ { "SystemName":"Synuefe PK-V b48-0", "NumBodies":11 }, { "SystemName":"Synuefe GX-K c24-3", "NumBodies":1 }, { "SystemName":"Col 285 Sector RN-K c8-10", "NumBodies":1 }, { "SystemName":"Col 285 Sector BP-Y b14-1", "NumBodies":1 } ], "BaseValue":17235, "Bonus":0, "TotalEarnings":15513 }
                        print(entry)
                        for systementry in entry["Discovered"]:
                            system = systementry["SystemName"]
                            firstletter = system[0].lower()
                            if firstletter not in alphabet:
                                firstletter = "-"
                            if ((system not in sold_exploration[cmdr][firstletter].keys()
                                 and (system[0].lower() == firstletter or firstletter == "-"))):
                                sold_exploration[cmdr][firstletter][system] = []

                            for data in possibly_sold_data[cmdr]:
                                if data["system"] == system:
                                    if data not in sold_exploration[cmdr][firstletter][system]:
                                        sold_exploration[cmdr][firstletter][system].append(data)
                            possibly_sold_data[cmdr] = [data for data in possibly_sold_data[cmdr] if data["system"] != system]
                        pass

                    """
                    if entry["event"] == "SellOrganicData":
                        logger.debug("SellOrganicData event!")
                        currentbatch = {}
                        # Lets create a more human readable list of different types
                        # of sold biodata to see how we can continue from there.
                        for sold in entry["BioData"]:
                            if sold["Species_Localised"] in currentbatch.keys():
                                currentbatch[sold["Species_Localised"]] += 1
                            else:
                                currentbatch[sold["Species_Localised"]] = 1
                        bysystem = {}
                        for biodata in possibly_sold_data[cmdr]:
                            if biodata["system"] in bysystem.keys():
                                if (biodata["species"] in bysystem[biodata["system"]].keys()):
                                    bysystem[biodata["system"]][biodata["species"]] += 1
                                else:
                                    bysystem[biodata["system"]][biodata["species"]] = 1
                            else:
                                bysystem[biodata["system"]] = {}
                                bysystem[biodata["system"]][biodata["species"]] = 1
                        soldbysystempossible = {}
                        logger.debug("bysystem:")
                        logger.debug(bysystem)
                        logger.debug("Currentbatch:")
                        logger.debug(currentbatch)
                        # input()

                        # Get every system
                        for system in bysystem:
                            # and we assume every system to be the one that was possibly sold from
                            soldbysystempossible[system] = True
                            for species in currentbatch:
                                if species not in bysystem[system].keys():
                                    # Species that we are selling does not appear in its bysystem structure
                                    # so it cant be the system that we sold from
                                    soldbysystempossible[system] = False
                                    # since we found out the system can't be the one we sold we break here
                                    # and continue with the next system
                                    break
                                if soldbysystempossible[system] is False:
                                    continue
                                # Checking if we have any systems that have too few of a certain species
                                if bysystem[system][species] < currentbatch[species]:
                                    soldbysystempossible[system] = False
                                    break

                        # this is still not perfect because it cannot be.
                        # if the player sells the data by system and 2 systems
                        # have the same amount of the same species then no one
                        # can tell which system was actually sold at
                        # vista genomics.
                        # In described case whatever is the first system we
                        # encounter through iteration will be chosen as the
                        # system that was sold.
                        thesystem = ""
                        for system in soldbysystempossible:
                            if soldbysystempossible[system] is True:
                                # We always take the first system that is possible
                                # If there are two we cannot tell which one was
                                # sold. Though it should not really matter
                                # as long as the CMDR hasn't died right
                                # after without selling the data aswell.
                                thesystem = system
                                break

                        # An eligible system was found and we selected the first
                        if thesystem != "":
                            logger.debug("CMDR sold by system: " + thesystem)
                            i = 0
                            while i < len(possibly_sold_data[cmdr]):
                                # For the case when we are done when we havent sold everything
                                done = True
                                for species in currentbatch:
                                    if currentbatch[species] != 0:
                                        done = False
                                if done:
                                    break

                                logger.debug(" i = " + str(i))

                                firstletter = possibly_sold_data[cmdr][i]["system"][0].lower()
                                if firstletter not in alphabet:
                                    firstletter = "-"
                                # Checking here more granularily
                                # which data was sold.
                                # We do know though that
                                # the specifc data was sold only
                                # in one system that at this point
                                # is saved in the variable "thesystem"
                                logger.debug("possibly sold data")
                                # logger.debug(possibly_sold_data[cmdr])
                                logger.debug("current batch")
                                logger.debug(currentbatch)

                                if ((thesystem not in sold_exobiology[cmdr][firstletter].keys()
                                     and (thesystem[0].lower() == firstletter or firstletter == "-"))):
                                    sold_exobiology[cmdr][firstletter][thesystem] = []

                                check = (possibly_sold_data[cmdr][i]["system"] == thesystem
                                         and possibly_sold_data[cmdr][i]
                                         not in sold_exobiology[cmdr][firstletter][thesystem]
                                         and possibly_sold_data[cmdr][i]["species"] in currentbatch.keys())
                                if check:
                                    if currentbatch[possibly_sold_data[cmdr][i]["species"]] > 0:
                                        logger.debug("We append in specific system")
                                        sold_exobiology[cmdr][firstletter][thesystem].append(
                                            possibly_sold_data[cmdr][i])
                                        currentbatch[possibly_sold_data[cmdr][i]["species"]] -= 1
                                        thing = possibly_sold_data[cmdr].pop(i)
                                        logger.debug("Sold:")
                                        logger.debug(thing)
                                        logger.debug(" i = " + str(i))
                                        continue
                                    else:
                                        logger.error("currentbatch has negative amount for some species"
                                                     + " this is a problem")
                                i += 1
                        else:
                            logger.debug("CMDR sold the whole batch.")
                            logger.debug("possibly sold data")
                            logger.debug(possibly_sold_data[cmdr])
                            logger.debug("current batch")
                            logger.debug(currentbatch)

                            for data in possibly_sold_data[cmdr]:
                                firstletter = data["system"][0].lower()
                                if firstletter not in alphabet:
                                    firstletter = "-"

                                if ((data["system"] not in sold_exobiology[cmdr][firstletter].keys()
                                     and (data["system"][0].lower() == firstletter or firstletter == "-"))):
                                    sold_exobiology[cmdr][firstletter][data["system"]] = []

                                if data["species"] not in currentbatch.keys():
                                    continue

                                if ((data not in sold_exobiology[cmdr][firstletter][data["system"]]
                                     and currentbatch[data["species"]] > 0)):
                                    currentbatch[data["species"]] -= 1

                                    logger.debug("We append single bit of whole batch")
                                    sold_exobiology[cmdr][firstletter][data["system"]].append(data)
                                    logger.debug("We appended single bit of whole batch")
                            possibly_sold_data[cmdr] = []
                    """

                except json.JSONDecodeError as e:
                    logger.error(f"JSONDecodeError: Corrupt journal line found in {filename[1]} at {linepos}")
                    logger.error(f"Corrupt line: {line}")
                    logger.error(f"JSONDecodeError: {e}")
                    logger.error("Skipping Line")

                linepos += 1

            file.close()

    logger.debug("Saving file now")

    solddata = None

    with open(directory + "/soldexplodata.json", "r+", encoding="utf8") as f:
        solddata = json.load(f)

        for currentcmdr in totalcmdrlist:
            if currentcmdr not in solddata.keys():
                solddata[currentcmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
            if sold_exploration[currentcmdr] != []:
                for letter in sold_exploration[currentcmdr].keys():
                    for system in sold_exploration[currentcmdr][letter]:
                        if system not in solddata[currentcmdr][letter].keys():
                            solddata[currentcmdr][letter][system] = []
                        for item in sold_exploration[currentcmdr][letter][system]:
                            alreadylogged = False
                            for loggeditem in solddata[currentcmdr][letter][system]:
                                if loggeditem["body"] == item["body"]:
                                    if loggeditem["type"] == item["type"]:
                                        alreadylogged = True
                                        continue
                            if not alreadylogged:
                                solddata[currentcmdr][letter][system].append(item)
                sold_exploration[currentcmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
        f.seek(0)
        json.dump(solddata, f, indent=4)
        f.truncate()

    notsolddata = None

    with open(directory + "/notsoldexplodata.json", "r+", encoding="utf8") as f:
        notsolddata = json.load(f)
        for currentcmdr in totalcmdrlist:
            if currentcmdr not in notsolddata.keys():
                notsolddata[currentcmdr] = []
            if len(notsolddata[currentcmdr]) > 0:
                possibly_sold_data[currentcmdr].extend(notsolddata[currentcmdr])
                notsolddata[currentcmdr] = []
            for element in possibly_sold_data[currentcmdr]:
                try:
                    if element in solddata[currentcmdr][element["system"][0].lower()][element["system"]]:
                        continue
                except KeyError:
                    # Yay KeyError this means the element is not in there! woo
                    pass
                if element not in notsolddata[currentcmdr]:
                    notsolddata[currentcmdr].append(element)
        f.seek(0)
        json.dump(notsolddata, f, indent=4)
        f.truncate()

    unsoldvalues = {}

    vistagenomicsprices = getvistagenomicprices()

    for cmdr in notsolddata.keys():
        unsoldvalue = 0

        for element in notsolddata[cmdr]:
            print(element)
            # Don't have prices for stars and planets yet
            # TODO get prices for stars and planets
            # unsoldvalue += vistagenomicsprices[element["species"]]
        unsoldvalues[cmdr] = unsoldvalue

    logger.debug("Done with journalcrawling!")

    return unsoldvalues


# to use it as standalone

class Loggingthing:
    """Points all logger calls to print."""

    def __init__(self) -> None:
        """Point all logger calls to print."""
        self.info = print
        self.debug = print
        self.warning = print
        self.error = print


if __name__ == "__main__":
    logger = Loggingthing()
    directory, sourcename = os.path.split(os.path.realpath(__file__))
    journaldir = directory + "/journals/"
    build_explodata_json(logger, journaldir)
    # journaldir = "<Path>"
    # build_explodata_json(logger, journaldir)
