"""
Here resides the journalcrawler that can read through all the journal files.

It retraces all exobiology scans and sell actions.
"""

import json
import os

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
    """Get the date from a filename in form of a stanardized string.

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


def build_biodata_json(logger: any, journaldir: str) -> int:
    """Build a soldbiodata.json and a notsoldbiodata that includes all sold organic scans that the player sold.

    Also return the value of still unsold scans.
    """
    # logger.debug = print

    logger.debug("start logging")

    directory, sourcename = os.path.split(os.path.realpath(__file__))

    cmdr = ""
    currentsystem = ""
    currentbody = ""

    totalcmdrlist = []

    currententrytowrite = {}

    logger.debug(directory)

    sold_exobiology = {}
    possibly_sold_data = {}

    if not os.path.exists(directory + "\\soldbiodata.json"):
        f = open(directory + "\\soldbiodata.json", "w", encoding="utf8")
        f.write(r"{}")
        f.close()

    with open(directory + "\\soldbiodata.json", "r", encoding="utf8") as f:
        sold_exobiology = json.load(f)
        # logger.debug(sold_exobiology)
        # logger.debug(len(sold_exobiology))
        pass

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
            for line in lines:

                read_old_journal_limpet_event = False
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

                    if cmdr != "" and cmdr is not None and cmdr not in sold_exobiology.keys():
                        sold_exobiology[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
                        logger.debug(sold_exobiology)

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
                if entry["event"] == "ScanOrganic":
                    # logger.debug("Scan organic Event!")
                    if entry["ScanType"] in ["Sample", "Analyse"]:
                        if entry["ScanType"] == "Analyse":
                            logger.debug("Scan Organic Event Type: Analyse")
                            currententrytowrite["species"] = generaltolocalised(entry["Species"].lower())
                            currententrytowrite["system"] = currentsystem
                            currententrytowrite["body"] = currentbody
                            if currententrytowrite not in possibly_sold_data[cmdr]:
                                possibly_sold_data[cmdr].append(currententrytowrite)
                            currententrytowrite = {}
                            continue

                if entry["event"] == "Resurrect":
                    # Reset - player was unable to sell before death
                    logger.debug("We died")
                    possibly_sold_data[cmdr] = []

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
                            logger.debug(possibly_sold_data[cmdr])
                            logger.debug("current batch")
                            logger.debug(currentbatch)

                            if (thesystem not in sold_exobiology[cmdr][firstletter].keys()
                               and (thesystem[0].lower() == firstletter or firstletter == "-")):
                                sold_exobiology[cmdr][firstletter][thesystem] = []

                            check = (possibly_sold_data[cmdr][i]["system"] == thesystem
                                     and possibly_sold_data[cmdr][i]
                                     not in sold_exobiology[cmdr][firstletter][thesystem]
                                     and possibly_sold_data[cmdr][i]["species"] in currentbatch.keys())
                            if check:
                                if currentbatch[possibly_sold_data[cmdr][i]["species"]] > 0:
                                    logger.debug("We append in specific system")
                                    sold_exobiology[cmdr][firstletter][thesystem].append(possibly_sold_data[cmdr][i])
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

                            if (data["system"] not in sold_exobiology[cmdr][firstletter].keys()
                               and (data["system"][0].lower() == firstletter or firstletter == "-")):
                                sold_exobiology[cmdr][firstletter][data["system"]] = []

                            if data["species"] not in currentbatch.keys():
                                continue

                            if (data not in sold_exobiology[cmdr][firstletter][data["system"]]
                               and currentbatch[data["species"]] > 0):
                                currentbatch[data["species"]] -= 1

                                logger.debug("We append single bit of whole batch")
                                sold_exobiology[cmdr][firstletter][data["system"]].append(data)
                                logger.debug("We appended single bit of whole batch")
                        possibly_sold_data[cmdr] = []

            file.close()

    logger.debug("Saving file now")

    solddata = None

    with open(directory + "\\soldbiodata.json", "r+", encoding="utf8") as f:
        solddata = json.load(f)

        for currentcmdr in totalcmdrlist:
            if currentcmdr not in solddata.keys():
                solddata[currentcmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
            if sold_exobiology[currentcmdr] != []:
                for letter in sold_exobiology[currentcmdr].keys():
                    for system in sold_exobiology[currentcmdr][letter]:
                        if system not in solddata[currentcmdr][letter].keys():
                            solddata[currentcmdr][letter][system] = []
                        for item in sold_exobiology[currentcmdr][letter][system]:
                            alreadylogged = False
                            for loggeditem in solddata[currentcmdr][letter][system]:
                                if loggeditem["body"] == item["body"]:
                                    if loggeditem["species"] == item["species"]:
                                        alreadylogged = True
                                        continue
                            if not alreadylogged:
                                solddata[currentcmdr][letter][system].append(item)
                sold_exobiology[currentcmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
        f.seek(0)
        json.dump(solddata, f, indent=4)
        f.truncate()

    notsolddata = None

    with open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8") as f:
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
            unsoldvalue += vistagenomicsprices[element["species"]]
        unsoldvalues[cmdr] = unsoldvalue

    logger.debug("Done with journalcrawling!")

    return unsoldvalues


# to use it as standalone
"""
class loggingthing:
    def __init__(self):
        self.info = print
        self.debug = print
        self.warning = print
        self.error = print
        pass


if __name__ == "__main__":
    logger = loggingthing()
    directory, sourcename = os.path.split(os.path.realpath(__file__))
    journaldir = directory + "\\journals\\"
    build_biodata_json(logger, journaldir)
    journaldir = "<Path>"
    build_biodata_json(logger, journaldir)
"""
