"""AST event handling functions."""

import json
import logging
import os

# Own modules
import organicinfo as orgi
import saving
import ui

# EDMC specific imports
try:
    from config import appname  # type: ignore
except ImportError:
    appname = "AST"

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-"


def resurrection_event(plugin) -> None:
    """Handle resurrection event aka dying."""
    plugin.rawvalue = 0
    plugin.AST_value.set("0 Cr.")
    plugin.AST_current_scan_progress.set("0/3")
    return []


def bioscan_event(cmdr: str, is_beta, entry, plugin, currententrytowrite) -> None:  # noqa: CCR001
    """Handle the ScanOrganic event."""
    if plugin.AST_debug.get():
        logger.debug("Handling ScanOrganic event.")

    # In the eventuality that the user started EMDC after
    # the "Location" event happens and directly scans a plant
    # these lines wouldn"t be able to do anything but to
    # set the System and body of the last Scan to "None"
    old_ast_last_scan_system = plugin.AST_last_scan_system.get()
    old_ast_last_scan_body = plugin.AST_last_scan_body.get()
    old_ast_last_scan_plant = str(plugin.AST_last_scan_plant.get().split(" (Worth: ")[0])

    plugin.AST_last_scan_system.set(plugin.AST_current_system.get())
    plugin.AST_last_scan_body.set(plugin.AST_current_body.get())
    plantname, plantworth = plugin.update_last_scan_plant(entry)

    if entry["ScanType"] == "Log":
        if plugin.AST_debug.get():
            logger.debug("Found Log")

        plugin.AST_current_scan_progress.set("1/3")
        plugin.AST_CCR.set(orgi.getclonalcolonialranges(orgi.genusgeneraltolocalised(entry["Genus"])))
        plugin.AST_scan_1_pos_vector[0] = plugin.AST_current_pos_vector[0]
        plugin.AST_scan_1_pos_vector[1] = plugin.AST_current_pos_vector[1]
        plugin.AST_scan_2_pos_vector = [None, None]
        plugin.AST_scan_2_pos_dist.set("")
        if plugin.AST_debug.get():
            logger.info("Set Everything for finishing the Log Scantype")
            logger.info("Running on preferences closed")
        # plugin.on_preferences_closed(cmdr, is_beta)
    elif entry["ScanType"] in ["Sample", "Analyse"]:
        if (entry["ScanType"] == "Analyse"):
            if plugin.AST_debug.get():
                logger.debug("Analyse Event!")

            plugin.rawvalue += int(plantworth)

            if plugin.AST_shorten_value.get():
                plugin.AST_value.set(ui.shortcreditstring(plugin.rawvalue))
            else:
                plugin.AST_value.set(f"{plugin.rawvalue:,} Cr.")
            # Found some cases where the analyse happened
            # seemingly directly after a log.
            plugin.AST_current_scan_progress.set("3/3")
            # clear the scan locations to [None, None]
            plugin.AST_scan_1_pos_vector = [None, None]
            plugin.AST_scan_2_pos_vector = [None, None]
            plugin.AST_scan_1_dist_green = False
            plugin.AST_scan_2_dist_green = False
            plugin.AST_CCR.set(0)
            plugin.AST_scan_1_pos_dist.set("")
            plugin.AST_scan_2_pos_dist.set("")
            currententrytowrite["species"] = plantname
            currententrytowrite["system"] = plugin.AST_current_system.get()
            currententrytowrite["body"] = plugin.AST_current_body.get()
            if cmdr not in plugin.notyetsolddata.keys():
                plugin.notyetsolddata[cmdr] = []
            if plugin.AST_debug.get():
                logger.debug("Checking if currententrytowrite is already in notyetsolddata")
                logger.debug(f"currententrytowrite: {currententrytowrite}")
                logger.debug(f"notyetsolddata: {plugin.notyetsolddata[cmdr]}")
            if currententrytowrite not in plugin.notyetsolddata[cmdr]:
                # If there is no second Sample scantype event
                # we have to save the data here.
                if plugin.AST_debug.get():
                    logger.debug("Saving data to notsoldbiodata.json")
                plugin.notyetsolddata[cmdr].append(currententrytowrite.copy())
                file = plugin.AST_DIR + "/notsoldbiodata.json"
                with open(file, "r+", encoding="utf8") as f:
                    notsolddata = json.load(f)
                    if cmdr not in notsolddata.keys():
                        notsolddata[cmdr] = []
                    notsolddata[cmdr].append(currententrytowrite.copy())
                    f.seek(0)
                    json.dump(notsolddata, f, indent=4)
                    f.truncate()
                currententrytowrite = {}
        else:
            if plugin.AST_debug.get():
                logger.debug("Found Sample event")
            notthesame = (not (old_ast_last_scan_system == plugin.AST_last_scan_system.get()
                          and old_ast_last_scan_body == plugin.AST_last_scan_body.get()
                          and old_ast_last_scan_plant == str(plugin.AST_last_scan_plant.get().split(" (Worth: ")[0])))
            # Check if we already have scan progress 2/3 with same species on the same body.
            # case 1: "0/3" not the same -> clear 1st distance change 2nd
            # case 2: "0/3" same -> change 2nd distance
            # case 3: "1/3" not the same -> clear 1st distance change 2nd
            # case 4: "1/3" same -> change 2nd distance
            # case 5: "2/3" not the same -> clear 1st distance change 2nd
            # case 6: "2/3" same -> no changing!
            # case 7: "3/3" not the same -> clear 1st distance change 2nd
            # case 8: "3/3" same -> clear 1st distance change 2nd

            if (plugin.AST_current_scan_progress.get() != "2/3"):
                # case 1, 2, 3, 4, 7, 8 change second distance
                plugin.AST_scan_2_pos_vector[0] = plugin.AST_current_pos_vector[0]
                plugin.AST_scan_2_pos_vector[1] = plugin.AST_current_pos_vector[1]

            # clear 1st distance when not the same body and species as previous scan.

            if (plugin.AST_current_scan_progress.get() == "3/3"):
                # case 7, 8 clear 1st distance
                plugin.AST_scan_1_pos_vector = [None, None]
                plugin.AST_scan_1_pos_dist.set("")

            if notthesame:
                # case 1, 3, 5, 7 clear first distance
                plugin.AST_scan_1_pos_vector = [None, None]
                plugin.AST_scan_1_pos_dist.set("")
                if (plugin.AST_current_scan_progress.get() == "2/3"):
                    # case 5 change second distance
                    plugin.AST_scan_2_pos_vector[0] = plugin.AST_current_pos_vector[0]
                    plugin.AST_scan_2_pos_vector[1] = plugin.AST_current_pos_vector[1]

            plugin.AST_current_scan_progress.set("2/3")
            plugin.AST_CCR.set(orgi.getclonalcolonialranges(orgi.genusgeneraltolocalised(entry["Genus"])))
    else:
        # Something is horribly wrong if we end up here
        # If anyone ever sees this
        # we know they added a new ScanType, that we might need to handle
        plugin.AST_current_scan_progress.set("Excuse me what the fuck ¯\\(°_o)/¯")

    plugin.AST_after_selling.set(0)

    if plugin.AST_hide_after_full_scan.get() == 1 and plugin.AST_current_scan_progress.get() == "3/3":
        plugin.AST_after_selling.set(1)

    # We now need to rebuild regardless how far we progressed
    plugin.on_preferences_closed(cmdr, is_beta)
    # ui.rebuild_ui(plugin, cmdr)


def system_body_change_event(cmdr: str, entry, plugin) -> None:  # noqa: CCR001
    """Handle all events that give a tell in which system we are or on what planet we are on."""
    systemchange = False

    try:
        if plugin.AST_current_system.get() != entry["StarSystem"]:
            systemchange = True
        # Get current system name and body from events that need to happen.
        plugin.AST_current_system.set(entry["StarSystem"])
        # Change of body is handled in dashboard updates.
        if systemchange:
            plugin.AST_current_body.set("")
    except KeyError:
        # Could throw a KeyError in old Horizons versions
        pass

    if systemchange:
        ui.rebuild_ui(plugin, cmdr)

    # To fix the aforementioned eventuality where the systems end up
    # being "None" we update the last scan location
    # When the CMDR gets another journal entry that tells us
    # the players location.

    # Check if it is obsolete if we use the dashboard entry for current body.
    # So that at any time we end up with the most current body.

    if (((plugin.AST_last_scan_system.get() == "")
         or (plugin.AST_last_scan_system.get() == "None"))):
        plugin.AST_last_scan_system.set(entry["StarSystem"])
        # plugin.AST_last_scan_body.set(entry["Body"])

    if plugin.CMDR_states[cmdr][1] == "" or plugin.CMDR_states[cmdr][2] == "":
        plugin.CMDR_states[cmdr][1] = plugin.AST_last_scan_system.get()
        plugin.CMDR_states[cmdr][2] = plugin.AST_last_scan_body.get()
        saving.save_cmdr(cmdr, plugin)


def biosell_event(cmdr: str, entry, plugin) -> None:  # noqa: CCR001
    """Handle the SellOrganicData event."""
    soldvalue = 0

    logger.info('called biosell_event')

    if cmdr != "" and cmdr is not None and cmdr not in plugin.soldexobiology.keys():
        plugin.soldexobiology[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}

    # currentbatch describes which species we are selling.
    # currentbatch has the form: {<species> : <amount> , ....}
    currentbatch = {}

    for sold in entry["BioData"]:
        if sold["Species_Localised"] in currentbatch.keys():
            # found that we are selling at least two of the same species
            currentbatch[sold["Species_Localised"]] += 1
        else:
            currentbatch[sold["Species_Localised"]] = 1
        # Adding the value of the sold species to the tally
        soldvalue += sold["Value"]
        # If I add a counter for all biodata sold
        # I would also need to look at biodata["Bonus"]
        # -> Nah its impossible to track bonus while not sold yet
        # Could only be used for a profit since last reset metric.
    # build by system dict, has the form of {<system> : {<species> : <amount>}}
    logger.info(f'Value that was sold: {soldvalue}')
    bysystem = {}
    if cmdr not in plugin.notyetsolddata.keys():
        plugin.notyetsolddata[cmdr] = []
    for biodata in plugin.notyetsolddata[cmdr]:
        if biodata["system"] in bysystem.keys():
            # We already know the system
            if (biodata["species"] in bysystem[biodata["system"]].keys()):
                # We also have found the same species before
                # We've found atleast 2
                bysystem[biodata["system"]][biodata["species"]] += 1
            else:
                # Species was not catologued in the bysystem structure
                bysystem[biodata["system"]][biodata["species"]] = 1
        else:
            # create new entry for the system and add the single species to it
            bysystem[biodata["system"]] = {}
            bysystem[biodata["system"]][biodata["species"]] = 1

    # Create a structure to check which system might be the one that we are selling
    soldbysystempossible = {}

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
    logger.info(f'All possible systems: {soldbysystempossible}')
    # this is still not perfect because it cannot be.
    # if the player sells the data by system and 2 systems
    # have the same amount of the same species then no one can tell
    # which system was actually sold at vista genomics.
    # In described case whatever is the first system we encounter
    # through iteration will be chosen as the system that was sold.
    thesystem = ""

    amountpossiblesystems = sum(1 for value in soldbysystempossible.values() if value is True)

    for system in soldbysystempossible:
        if soldbysystempossible[system] is True:
            if amountpossiblesystems > 1:
                logger.warning('More than one system could have been the one getting sold.')
                logger.warning('Please sell all other data before your next death.')
                logger.warning('Otherwise the soldbiodata.json may have uncatchable discrepancies.')
            # We always take the first system that is possible
            # If there are two we cannot tell which one was sold
            # Though it should not really matter as long as
            # the CMDR hasn't died right after without selling
            # the data aswell.
            thesystem = system
            logger.info(f'Likely system that was sold from: {thesystem}')
            break

    if thesystem != "":
        # CMDR sold by system.
        i = 0
        while i < len(plugin.notyetsolddata[cmdr]):
            # Check if were done with the batch we sold yet
            done = True
            for species in currentbatch:
                if currentbatch[species] > 0:
                    done = False
            if done:
                break

            firstletter = plugin.notyetsolddata[cmdr][i]["system"][0].lower()
            if firstletter not in alphabet:
                firstletter = "-"
            # Checking here more granularily which data was sold
            # We do know though that the specifc data was sold only
            # in one system that at this point is saved in
            # the variable"thesystem"
            if (thesystem not in plugin.soldexobiology[cmdr][firstletter].keys()
               and (thesystem[0].lower() == firstletter or firstletter == "-")):
                plugin.soldexobiology[cmdr][firstletter][thesystem] = []

            check = (plugin.notyetsolddata[cmdr][i]["system"] == thesystem
                     and plugin.notyetsolddata[cmdr][i]
                     not in plugin.soldexobiology[cmdr][firstletter][thesystem]
                     and plugin.notyetsolddata[cmdr][i]["species"] in currentbatch.keys())

            if check:
                if currentbatch[plugin.notyetsolddata[cmdr][i]["species"]] > 0:
                    plugin.soldexobiology[cmdr][firstletter][thesystem].append(plugin.notyetsolddata[cmdr][i])
                    currentbatch[plugin.notyetsolddata[cmdr][i]["species"]] -= 1
                    plugin.notyetsolddata[cmdr].pop(i)
                    continue
            i += 1

        f = open(plugin.AST_DIR + "/notsoldbiodata.json", "r+", encoding="utf8")
        scanneddata = json.load(f)
        scanneddata[cmdr] = []
        f.seek(0)
        json.dump(scanneddata, f, indent=4)
        f.truncate()
        f.close()

        if plugin.notyetsolddata[cmdr] != []:
            file = plugin.AST_DIR + "/notsoldbiodata.json"
            with open(file, "r+", encoding="utf8") as f:
                notsolddata = json.load(f)
                for data in plugin.notyetsolddata[cmdr]:
                    notsolddata[cmdr].append(data)
                f.seek(0)
                json.dump(notsolddata, f, indent=4)
                f.truncate()

    else:
        # CMDR sold the whole batch.
        for data in plugin.notyetsolddata[cmdr]:
            firstletter = data["system"][0].lower()
            if firstletter not in alphabet:
                firstletter = "-"

            if (data["system"] not in plugin.soldexobiology[cmdr][firstletter].keys()
               and (data["system"][0].lower() == firstletter or firstletter == "-")):
                plugin.soldexobiology[cmdr][firstletter][data["system"]] = []

            if data["species"] not in currentbatch.keys():
                continue

            if (data not in plugin.soldexobiology[cmdr][firstletter][data["system"]]
               and currentbatch[data["species"]] > 0):
                currentbatch[data["species"]] -= 1
                plugin.soldexobiology[cmdr][firstletter][data["system"]].append(data)
        plugin.notyetsolddata[cmdr] = []
        # We can already reset to 0 to ensure that after selling all data at once
        # we end up with a reset of the Scanned value metric
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
        plugin.rawvalue = 0
        f = open(plugin.AST_DIR + "/notsoldbiodata.json", "r+", encoding="utf8")
        scanneddata = json.load(f)
        scanneddata[cmdr] = []
        f.seek(0)
        json.dump(scanneddata, f, indent=4)
        f.truncate()
        f.close()

    # Remove the value of what was sold from
    # the amount of the Scanned value.
    # Specifically so that the plugin still keeps track properly,
    # when the player sells on a by system basis.
    logger.info(f'Removing {soldvalue} from plugin value')
    plugin.rawvalue -= soldvalue
    # newvalue = int(plugin.AST_value.get().replace(",", "").split(" ")[0]) - soldvalue
    if plugin.AST_shorten_value.get():
        plugin.AST_value.set(ui.shortcreditstring(plugin.rawvalue))
    else:
        plugin.AST_value.set(f"{plugin.rawvalue:,} Cr.")

    # No negative value of biodata could still be unsold on the Scanner
    # This means that there was data on the Scanner that
    # the plugin was unable to record by not being active.
    # If the value was reset before we will reset it here again.
    if int(plugin.rawvalue) < 0:
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
        plugin.rawvalue = 0
    # Now write the data into the local file
    file = plugin.AST_DIR + "/soldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        solddata = json.load(f)

        if cmdr not in solddata.keys():
            solddata[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}

        if plugin.soldexobiology[cmdr] != []:
            for letter in plugin.soldexobiology[cmdr]:
                for system in plugin.soldexobiology[cmdr][letter]:
                    if system not in solddata[cmdr][letter].keys():
                        solddata[cmdr][letter][system] = []
                    for item in plugin.soldexobiology[cmdr][letter][system]:
                        solddata[cmdr][letter][system].append(item)
            plugin.soldexobiology[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
        f.seek(0)
        json.dump(solddata, f, indent=4)
        f.truncate()

    # After selling all the unsold value we finished selling and things switch to hiding things if
    # we are in autohiding mode
    if (plugin.rawvalue == 0 and plugin.AST_hide_after_selling.get() == 1):
        plugin.AST_after_selling.set(1)

    # If we sell the exobiodata in the same system as where we currently are
    # Then we want to remove the "*" around the body names of the newly sold biodata
    # So just rebuild the ui for good measure.
    ui.rebuild_ui(plugin, cmdr)


def SAASignalsFound_event(entry, plugin) -> None:  # noqa: CCR001 N802
    """Handle the SAASignalsFound event."""
    if plugin.AST_debug.get():
        logger.debug(f"iterating over entry {entry}")
    for i in range(len(entry["Signals"])):
        if plugin.AST_debug.get():
            logger.debug(f"iterating over {entry['Signals'][i]}")
            logger.debug(f"Type: {entry['Signals'][i]['Type']}")
        if entry["Signals"][i]["Type"] == "$SAA_SignalType_Biological;":
            if plugin.AST_debug.get():
                logger.debug(f"bio signal on {entry['BodyName']} - increasing count to {entry['Signals'][i]['Count']}")
            plugin.AST_bios_on_planet[entry["BodyName"]] = entry["Signals"][i]["Count"]
