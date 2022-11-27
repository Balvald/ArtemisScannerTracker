"""test."""
import json
import os

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

def build_biodata_json(gamejournaldir, logger):
    """test."""
    directory, filename = os.path.split(os.path.realpath(__file__))

    journaldir = os.path.join(directory, "journals")

    if gamejournaldir is True:
        journaldir = str(os.environ['USERPROFILE']) + \
            "\\Saved Games\\Frontier Developments\\Elite Dangerous"

    currentsystem = ""
    currentbody = ""

    currententrytowrite = {}

    logger.info(directory)

    sold_exobiology = []
    possibly_sold_data = []

    if not os.path.exists(directory + "\\soldbiodata.json"):
        f = open(directory + "\\soldbiodata.json", "w", encoding="utf8")
        f.write(r"[]")
        f.close()

    with open(directory + "\\soldbiodata.json", "r", encoding="utf8") as f:
        sold_exobiology = json.load(f)
        # logger.info(sold_exobiology)
        # logger.info(len(sold_exobiology))
        pass

    edlogs = [f for f in os.listdir(journaldir) if f.endswith(".log")]

    for filename in edlogs:
        f = os.path.join(journaldir, filename)
        logger.info("Current file: " + f)
        # checking if it is a file
        if os.path.isfile(f):
            file = open(f, "r", encoding="utf8")
            lines = file.readlines()
            for line in lines:
                entry = json.loads(line)

                if entry["event"] in ["Location", "Embark",
                                      "Disembark", "Touchdown",
                                      "Liftoff", "FSDJump"]:
                    try:
                        currentsystem = entry["StarSystem"]
                        currentbody = entry["Body"]
                    except KeyError:
                        # Was playing in old Horizons so
                        # Touchdown and Liftoff don't have body nor system
                        logger.info("We've encountered a KeyError in the code "
                                    + "for updating the current system and body.")
                        logger.info(entry)
                if entry["event"] == "ScanOrganic":
                    if entry["ScanType"] in ["Sample", "Analyse"]:
                        if entry["ScanType"] == "Analyse":
                            currententrytowrite["species"] = entry["Species_Localised"]
                            currententrytowrite["system"] = currentsystem
                            currententrytowrite["body"] = currentbody
                            if currententrytowrite not in possibly_sold_data:
                                possibly_sold_data.append(currententrytowrite)
                            currententrytowrite = {}
                            continue

                if entry["event"] == "Resurrect":
                    # Reset - player was unable to sell before death
                    logger.info("We died")
                    possibly_sold_data = []

                if entry["event"] == "SellOrganicData":
                    currentbatch = {}
                    # Lets create a more human readable list of different types
                    # of sold biodata to see how we can continue from there.
                    for sold in entry["BioData"]:
                        if sold["Species_Localised"] in currentbatch.keys():
                            currentbatch[sold["Species_Localised"]] += 1
                        else:
                            currentbatch[sold["Species_Localised"]] = 1
                    bysystem = {}
                    for biodata in possibly_sold_data:
                        if biodata["system"] in bysystem.keys():
                            if (biodata["species"] in bysystem[biodata["system"]].keys()):
                                bysystem[biodata["system"]][biodata["species"]] += 1
                            else:
                                bysystem[biodata["system"]][biodata["species"]] = 1
                        else:
                            bysystem[biodata["system"]] = {}
                            bysystem[biodata["system"]][biodata["species"]] = 1
                    soldbysystempossible = {}
                    logger.info("bysystem:")
                    logger.info(bysystem)
                    logger.info("Currentbatch:")
                    logger.info(currentbatch)
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
                        logger.info("CMDR sold by system: " + thesystem)
                        i = 0
                        while i < len(possibly_sold_data):
                            # For the case when we are done when we havent sold everything
                            done = True
                            for species in currentbatch:
                                if currentbatch[species] != 0:
                                    done = False
                            if done:
                                break

                            logger.info(" i = " + str(i))
                            # Checking here more granularily
                            # which data was sold.
                            # We do know though that
                            # the specifc data was sold only
                            # in one system that at this point
                            # is saved in the variable "thesystem"
                            logger.info("possibly sold data")
                            logger.info(possibly_sold_data)
                            logger.info("current batch")
                            logger.info(currentbatch)

                            check = (possibly_sold_data[i]["system"] == thesystem
                                     and possibly_sold_data[i] not in sold_exobiology
                                     and possibly_sold_data[i]["species"] in currentbatch.keys())
                            if check:
                                if currentbatch[possibly_sold_data[i]["species"]] > 0:
                                    sold_exobiology.append(possibly_sold_data[i])
                                    currentbatch[possibly_sold_data[i]["species"]] -= 1
                                    thing = possibly_sold_data.pop(i)
                                    logger.info("Sold:")
                                    logger.info(thing)
                                    logger.info(" i = " + str(i))
                                    continue
                                else:
                                    logger.info("Not all data from a single system "
                                                + "were sold. This means the CMDR "
                                                + "sold a singular bit of data")
                            i += 1
                    else:
                        logger.info("CMDR sold the whole batch.")
                        logger.info("possibly sold data")
                        logger.info(possibly_sold_data)
                        logger.info("current batch")
                        logger.info(currentbatch)
                        for data in possibly_sold_data:
                            if (data not in sold_exobiology and currentbatch[data["species"]] > 0):
                                currentbatch[data["species"]] -= 1
                                sold_exobiology.append(data)
                        possibly_sold_data = []

            file.close()

    logger.info("Saving file now")

    with open(directory + "\\soldbiodata.json", "r+", encoding="utf8") as f:
        # f.write(json.dumps(sold_exobiology))
        # Same as below but creates smaller filesizes
        # and aren't as human readable
        f.write(json.dumps(sold_exobiology, indent=4))
        f.close()
