"""
Artemis Scanner Tracker by Balvald.

created from the EDMC example plugin.
"""

import json
import logging
import os
import tkinter as tk
from typing import Optional

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname, config  # type: ignore
from theme import theme  # type: ignore # noqa: N813

from journalcrawler import build_biodata_json
from organicinfo import getvistagenomicprices

# globals as part of the plugin class?
frame: Optional[tk.Frame] = None

PLUGIN_NAME = "AST"

# Gonna need the files directory to store data for full
# tracking of all the biological things that the CMDR scans.
directory, filename = os.path.split(os.path.realpath(__file__))

if not os.path.exists(directory + "\\soldbiodata.json"):
    firstrun = True
    f = open(directory + "\\soldbiodata.json", "w", encoding="utf8")
    f.write(r"[]")
    f.close()

if not os.path.exists(directory + "\\notsoldbiodata.json"):
    firstrun = True
    f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
    f.write(r"[]")
    f.close()

not_yet_sold_data = []
sold_exobiology = []
currententrytowrite = {}

plugin = None

# load notyetsolddata

with open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_data = json.load(f)

# Shows debug fields in preferences when True
debug = False

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

vistagenomicsprices = getvistagenomicprices()


class ArtemisScannerTracker:
    """Artemis Scanner Tracker plugin class."""

    def __init__(self) -> None:
        """Initialize the plugin by getting values from the config file."""
        # Be sure to use names that wont collide in our config variables
        # Bools for show hide checkboxes
        self.AST_hide_fullscan: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_fullscan"))
        self.AST_hide_species: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_species"))
        self.AST_hide_progress: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_progress"))
        self.AST_hide_last_system: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_last_system"))
        self.AST_hide_last_body: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_last_body"))
        self.AST_hide_system: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_system"))
        self.AST_hide_body: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_body"))
        self.AST_hide_value: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_value"))

        # Artemis Scanner State infos
        self.AST_last_scan_plant: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_last_scan_plant")))
        self.AST_last_scan_system: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_last_scan_system")))
        self.AST_last_scan_body: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_last_scan_body")))
        self.AST_current_scan_progress: Optional[tk.StringVar] = tk.StringVar(
            value=(str(config.get_int("AST_current_scan_progress")) + str("/3")))
        self.AST_current_system: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_current_system")))
        self.AST_current_body: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_current_body")))
        self.AST_state: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_state")))
        self.AST_value: Optional[tk.StringVar] = tk.StringVar(
            value=(str(config.get_int("AST_value")) + str(" Cr.")))

        logger.info("ArtemisScannerTracker instantiated")

    def on_load(self) -> str:
        """
        on_load is called by plugin_start3 below.

        It is the first point EDMC interacts with our code
        after loading our module.

        :return: The name of the plugin, which will be used by EDMC for logging
                 and for the settings window
        """
        return PLUGIN_NAME

    def on_unload(self) -> None:
        """
        on_unload is called by plugin_stop below.

        It is the last thing called before EDMC shuts down.
        Note that blocking code here will hold the shutdown process.
        """
        self.on_preferences_closed("", False)  # Save our prefs

    def setup_preferences(self, parent: nb.Notebook,
                          cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
        """
        setup_preferences is called by plugin_prefs below.

        It is where we can setup our
        own settings page in EDMC's settings window.
        Our tab is defined for us.

        :param parent: the tkinter parent that our
                       returned Frame will want to inherit from
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :return: The frame to add to the settings window
        """
        current_row = 0
        frame = nb.Frame(parent)

        nb.Label(frame, text="Artemis Scanner Tracker dev v0.1.2 by Balvald").grid(
            row=current_row, sticky=tk.W)
        current_row += 1
        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, sticky=tk.W)

        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, column=1, sticky=tk.W)

        current_row += 1

        nb.Checkbutton(
            frame,
            text="Hide Full Status",
            variable=self.AST_hide_fullscan).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Unsold Scans Value",
            variable=self.AST_hide_value).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        nb.Checkbutton(
            frame,
            text="Hide Species",
            variable=self.AST_hide_species).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Scan Progress",
            variable=self.AST_hide_progress).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        nb.Checkbutton(
            frame,
            text="Hide System of last Scan",
            variable=self.AST_hide_last_system).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Body of last Scan",
            variable=self.AST_hide_last_body).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        nb.Checkbutton(
            frame,
            text="Hide Current System",
            variable=self.AST_hide_system).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Current Body",
            variable=self.AST_hide_body).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        if debug:
            # setup debug fields for the scanner.
            nb.Label(frame, text="Species").grid(row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_last_scan_plant).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="System of last Scan").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_last_scan_system).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="Body of last Scan").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_last_scan_body).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="Scan progress").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_current_scan_progress).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="Scanned Value").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_value).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, sticky=tk.W)

        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, column=1, sticky=tk.W)

        current_row += 1

        nb.Button(
            frame,
            text="Scan game journals for sold exobiology",
            command=self.buildsoldbiodatajson).grid(
            row=current_row, column=0, sticky=tk.W)

        nb.Button(
            frame,
            text="Scan local journal folder for sold exobiology",
            command=self.buildsoldbiodatajsonlocal).grid(
            row=current_row, column=1, sticky=tk.W)

        current_row += 1

        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, sticky=tk.W)

        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, column=1, sticky=tk.W)

        current_row += 1

        nb.Label(
            frame,
            text="To reset the status, body, system and species"
        ).grid(row=current_row, sticky=tk.W)
        current_row += 1
        nb.Label(
            frame,
            text="of the last scan press the button below").grid(
            row=current_row, sticky=tk.W)
        current_row += 2
        nb.Button(
            frame,
            text="RESET",
            command=self.reset).grid(
            row=current_row, sticky=tk.W)
        current_row += 1

        return frame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.

        It is called when the preferences dialog is dismissed by the user.

        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        config.set("AST_current_scan_progress", int(
            self.AST_current_scan_progress.get()[0]))
        config.set("AST_last_scan_system", str(
            self.AST_last_scan_system.get()))
        config.set("AST_last_scan_body", str(self.AST_last_scan_body.get()))
        config.set("AST_last_scan_plant", str(self.AST_last_scan_plant.get()))
        config.set("AST_state", str(self.AST_state.get()))
        config.set("AST_value", int(self.AST_value.get().split(" ")[0]))

        config.set("AST_hide_value", int(self.AST_hide_value.get()))
        config.set("AST_hide_fullscan", int(self.AST_hide_fullscan.get()))
        config.set("AST_hide_species", int(self.AST_hide_species.get()))
        config.set("AST_hide_progress", int(self.AST_hide_progress.get()))
        config.set("AST_hide_last_system", int(
            self.AST_hide_last_system.get()))
        config.set("AST_hide_last_body", int(self.AST_hide_last_body.get()))
        config.set("AST_hide_system", int(self.AST_hide_system.get()))
        config.set("AST_hide_body", int(self.AST_hide_body.get()))

        logger.debug("ArtemisScannerTracker saved preferences")

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.

        This is called by plugin_app below.

        :param parent: EDMC main window Tk
        :return: Our frame
        """
        global frame

        frame = tk.Frame(parent)

        rebuild_ui(self)

        return frame

    def reset(self):
        """Reset function of the Reset Button."""
        self.AST_current_scan_progress.set("0/3")
        self.AST_last_scan_system.set("None")
        self.AST_last_scan_body.set("None")
        self.AST_last_scan_plant.set("None")
        self.AST_state.set("None")
        self.AST_value.set("0 Cr.")

    def buildsoldbiodatajsonlocal(self):
        """Build the soldbiodata.json using the neighboring journalcrawler.py searching through local journal folder."""
        # Always uses the game journal directory
        global logger
        build_biodata_json(False, logger)

    def buildsoldbiodatajson(self):
        """Build the soldbiodata.json using the neighboring journalcrawler.py."""
        # Always uses the game journal directory
        global logger
        build_biodata_json(True, logger)


def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    React accordingly to events in the journal.

    Scan Organic events tell us what we have scanned.
    Scan Type of these events can tell us the progress of the scan.
    Add the value of a finished Scan to the tally
    :param cmdr: The current ED Commander
    :param is_beta: Whether or not EDMC is currently marked as in beta mode
    :param system: current system? unused
    :param station: unused
    :param entry: the current Journal entry
    :param state: unused
    """
    global plugin

    flag = False

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        resurrection_event()

    if entry["event"] == "ScanOrganic":
        flag = True
        bioscan_event(entry)

    if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
        flag = True
        system_body_change_event(entry)

    if entry["event"] == "SellOrganicData":
        flag = True
        biosell_event(entry)

    if flag:
        # we changed a value so we update line.
        plugin.AST_state.set(
            plugin.AST_last_scan_plant.get()
            + " (" + plugin.AST_current_scan_progress.get()
            + ") on: " + plugin.AST_last_scan_body.get())

        # save most recent relevant state so in case of crash of the system
        # we still have a proper record as long as it finishes saving below.
        plugin.on_preferences_closed(cmdr, is_beta)


def resurrection_event():
    """Handle resurrection event aka dying."""
    global not_yet_sold_data
    not_yet_sold_data = []
    pass


def bioscan_event(entry):
    """Handle the ScanOrganic event."""
    global currententrytowrite, plugin
    plugin.AST_last_scan_plant.set(entry["Species_Localised"])

    # In the eventuality that the user started EMDC after
    # the "Location" event happens and directly scans a plant
    # these lines wouldn"t be able to do anything but to
    # set the System and body of the last Scan to "None"
    plugin.AST_last_scan_system.set(plugin.AST_current_system.get())
    plugin.AST_last_scan_body.set(plugin.AST_current_body.get())

    if entry["ScanType"] == "Log":
        plugin.AST_current_scan_progress.set("1/3")
    elif entry["ScanType"] in ["Sample", "Analyse"]:
        if (entry["ScanType"] == "Analyse"):

            if plugin.AST_value.get() == "None":
                plugin.AST_value.set("0 Cr.")
            # Somehow we get here twice for each 3rd scan. idfk
            newvalue = int(plugin.AST_value.get().split(" ")[0]) + \
                int(vistagenomicsprices[entry["Species_Localised"]])
            plugin.AST_value.set(str(newvalue) + " Cr.")
            # Found some cases where the analyse happened
            # seemingly directly after a log.
            plugin.AST_current_scan_progress.set("3/3")
            currententrytowrite["species"] = entry["Species_Localised"]
            currententrytowrite["system"] = plugin.AST_current_system.get()
            currententrytowrite["body"] = plugin.AST_current_body.get()
            if currententrytowrite not in not_yet_sold_data:
                # If there is no second Sample scantype event
                # we have to save the data here.
                not_yet_sold_data.append(currententrytowrite)
                file = directory + "\\notsoldbiodata.json"
                with open(file, "r+", encoding="utf8") as f:
                    notsolddata = json.load(f)
                    notsolddata.append(currententrytowrite)
                    f.seek(0)
                    json.dump(notsolddata, f, indent=4)
                currententrytowrite = {}
        else:
            plugin.AST_current_scan_progress.set("2/3")
    else:
        # Something is horribly wrong if we end up here
        # If anyone ever sees "Excuse me what the fuck"
        # we know they added a new ScanType, that we might need to handle
        plugin.AST_current_scan_progress.set("Excuse me what the fuck")


def system_body_change_event(entry):
    """Handle all events that give a tell in which system we are or on what planet we are on."""
    global plugin
    try:
        # Get current system name and body from events that need to happen.
        plugin.AST_current_system.set(entry["StarSystem"])
        plugin.AST_current_body.set(entry["Body"])
    except KeyError:
        # Could throw a KeyError in old Horizons versions
        pass

    # To fix the aforementioned eventuality where the systems end up
    # being "None" we update the last scan location
    # When the CMDR gets another journal entry that tells us
    # the players location.
    if ((plugin.AST_last_scan_system.get() == "None") or (plugin.AST_last_scan_body.get() == "None")):
        plugin.AST_last_scan_system.set(entry["StarSystem"])
        plugin.AST_last_scan_body.set(entry["Body"])


def biosell_event(entry):
    """Handle the SellOrganicData event."""
    global currententrytowrite, not_yet_sold_data, sold_exobiology
    soldvalue = 0

    logger.info('called biosell_event')

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
        # Could only be used for a profit since last reset
        # metric.
    # build by system dict, has the form of {<system> : {<species> : <amount>}}
    logger.info(f'Value that was sold: {soldvalue}')
    bysystem = {}
    for biodata in not_yet_sold_data:
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
        while i < len(not_yet_sold_data):
            # Check if were done with the batch we sold yet
            done = True
            for species in currentbatch:
                if currentbatch[species] > 0:
                    done = False
            if done:
                break

            # Checking here more granularily which data was sold
            # We do know though that the specifc data was sold only
            # in one system that at this point is saved in
            # the variable"thesystem"
            check = (not_yet_sold_data[i]["system"] == thesystem
                     and not_yet_sold_data[i] not in sold_exobiology
                     and not_yet_sold_data[i]["species"] in currentbatch.keys())
            if check:
                if currentbatch[not_yet_sold_data[i]["species"]] > 0:
                    sold_exobiology.append(not_yet_sold_data[i])
                    currentbatch[not_yet_sold_data[i]["species"]] -= 1
                    not_yet_sold_data.pop(i)
                    continue
            i += 1

        f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
        f.write(r"[]")
        f.close()
        if not_yet_sold_data != []:
            file = directory + "\\notsoldbiodata.json"
            with open(file, "r+", encoding="utf8") as f:
                notsolddata = json.load(f)
                for data in not_yet_sold_data:
                    notsolddata.append(data)
                f.seek(0)
                json.dump(notsolddata, f, indent=4)
    else:
        # CMDR sold the whole batch.
        for data in not_yet_sold_data:
            if (data not in sold_exobiology and currentbatch[data["species"]] > 0):
                currentbatch[data["species"]] -= 1
                sold_exobiology.append(data)
        not_yet_sold_data = []
        # We can already reset to 0 to ensure that after selling all data at once
        # we end up with a reset of the Scanned value metric
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
        f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
        f.write(r"[]")
        f.close()

    # Remove the value of what was sold from
    # the amount of the Scanned value.
    # Specifically so that the plugin still keeps track properly,
    # when the player sells on a by system basis.
    logger.info(f'Removing {soldvalue} from plugin value')
    plugin.AST_value.set(str(int(plugin.AST_value.get().split(" ")[0]) - soldvalue) + " Cr.")

    # No negative value of biodata could still be unsold on the Scanner
    # This means that there was data on the Scanner that
    # the plugin was unable to record by not being active.
    # If the value was reset before we will reset it here again.
    if int(plugin.AST_value.get().split(" ")[0]) < 0:
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
    # Now write the data into the local file
    file = directory + "\\soldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        solddata = json.load(f)
        if sold_exobiology != []:
            for item in sold_exobiology:
                solddata.append(item)
            sold_exobiology = []
        f.seek(0)
        json.dump(solddata, f, indent=4)


plugin = ArtemisScannerTracker()


def rebuild_ui(plugin):
    """Rebuild the UI in case of preferences change."""
    global frame

    # remove all labels from the frame
    for label in frame.winfo_children():
        label.destroy()

    # recreate UI
    current_row = 12

    if plugin.AST_hide_body.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Current Body:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_current_body).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_system.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Current System:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_current_system).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_value.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Unsold Scan Value:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_value).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_last_body.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Body of last Scan:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_last_scan_body).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_last_system.get() != 1:
        current_row -= 1
        tk.Label(frame, text="System of last Scan:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_last_scan_system).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_progress.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Scan Progress:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_current_scan_progress).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_species.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Species:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_last_scan_plant).grid(row=current_row, column=1, sticky=tk.W)

    if plugin.AST_hide_fullscan.get() != 1:
        current_row -= 1
        tk.Label(frame, text="Last Exobiology Scan:").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_state).grid(row=current_row, column=1, sticky=tk.W)

    theme.update(frame)  # Apply theme colours to the frame and its children, including the new widgets


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


def plugin_prefs(parent: nb.Notebook,
                 cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
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
    rebuild_ui(plugin)

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
