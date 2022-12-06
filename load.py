"""Artemis Scanner Tracker v0.1.3 dev by Balvald."""

import json
import logging
import os
import tkinter as tk
from typing import Optional

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname, config  # type: ignore
from theme import theme  # type: ignore

from journalcrawler import build_biodata_json
from organicinfo import generaltolocalised, getu14vistagenomicprices

frame: Optional[tk.Frame] = None


PLUGIN_NAME = "AST"


# Gonna need the files directory to store data for full
# tracking of all the biological things that the CMDR scans.
directory, filename = os.path.split(os.path.realpath(__file__))

if not os.path.exists(directory + "\\soldbiodata.json"):
    firstrun = True
    f = open(directory + "\\soldbiodata.json", "w", encoding="utf8")
    f.write(r"{}")
    f.close()

if not os.path.exists(directory + "\\notsoldbiodata.json"):
    firstrun = True
    f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
    f.write(r"{}")
    f.close()

not_yet_sold_data = {}
sold_exobiology = {}
currententrytowrite = {}
currentcommander = ""

plugin = None

# load notyetsolddata

with open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_data = json.load(f)

# Shows debug fields in preferences when True
debug = False

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

vistagenomicsprices = getu14vistagenomicprices()


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
        self.AST_hide_sold_bio: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_sold_bio"))
        self.AST_hide_CCR: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_CCR"))

        # bool to steer when the CCR feature is visible
        self.AST_near_planet: Optional[tk.StringVar] = False
        # positions as lat long, lat at index 0, long at index 1
        self.AST_current_pos_lat = None
        self.AST_current_pos_long = None
        self.AST_current_pos_head = None
        self.AST_scan_pos_1_lat = None
        self.AST_scan_pos_1_long = None
        self.AST_scan_pos_2_lat = None
        self.AST_scan_pos_2_long = None
        # radius of the most current planet
        self.AST_current_radius: Optional[tk.StringVar] = tk.StringVar(value="")

        self.AST_current_pos: Optional[tk.StringVar] = tk.StringVar(value="")
        self.AST_scan_pos_1: Optional[tk.StringVar] = tk.StringVar(value="")
        self.AST_scan_pos_2: Optional[tk.StringVar] = tk.StringVar(value="")

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

        rawvalue = int(config.get_int("AST_value"))

        self.AST_value: Optional[tk.StringVar] = tk.StringVar(
            value=((f"{rawvalue:,}") + str(" Cr.")))

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
        global currentcommander
        currentcommander = cmdr

        current_row = 0
        frame = nb.Frame(parent)

        nb.Label(frame, text="Artemis Scanner Tracker v0.1.3 dev by Balvald").grid(
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
            text="Hide Value of unsold Scans",
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
        nb.Checkbutton(
            frame,
            text="Hide Scanned/Sold Species in System",
            variable=self.AST_hide_sold_bio).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Clonal Colonial Distances",
            variable=self.AST_hide_CCR).grid(
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

        # for formatting the string with thousands seperators we have to remove them here again.
        config.set("AST_value", int(self.AST_value.get().replace(",", "").split(" ")[0]))

        config.set("AST_hide_value", int(self.AST_hide_value.get()))
        config.set("AST_hide_fullscan", int(self.AST_hide_fullscan.get()))
        config.set("AST_hide_species", int(self.AST_hide_species.get()))
        config.set("AST_hide_progress", int(self.AST_hide_progress.get()))
        config.set("AST_hide_last_system", int(
            self.AST_hide_last_system.get()))
        config.set("AST_hide_last_body", int(self.AST_hide_last_body.get()))
        config.set("AST_hide_system", int(self.AST_hide_system.get()))
        config.set("AST_hide_body", int(self.AST_hide_body.get()))
        config.set("AST_hide_sold_bio", int(self.AST_hide_sold_bio.get()))
        config.set("AST_hide_CCR", int(self.AST_hide_CCR.get()))

        logger.debug("ArtemisScannerTracker saved preferences")

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.

        This is called by plugin_app below.

        :param parent: EDMC main window Tk
        :return: Our frame
        """
        global frame, currentcommander

        frame = tk.Frame(parent)

        rebuild_ui(self, currentcommander)

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
        directory, filename = os.path.split(os.path.realpath(__file__))

        build_biodata_json(logger, os.path.join(directory, "journals"))

    def buildsoldbiodatajson(self):
        """Build the soldbiodata.json using the neighboring journalcrawler.py."""
        # Always uses the game journal directory

        global logger

        build_biodata_json(logger, config.default_journal_dir)


def clipboard():
    """Copy value to clipboard."""
    dummytk = tk.Tk()  # creates a window we don't want
    dummytk.clipboard_clear()
    dummytk.clipboard_append(plugin.AST_value.get()[:-4].replace(",", ""))
    dummytk.destroy()  # destroying it again we don't need full another window everytime we copy to clipboard.


def dashboard_entry(cmdr: str, is_beta, entry):
    """
    React to changes in the CMDRs status (Movement for CCR feature).

    :param cmdr: The current ED Commander
    :param is_beta: Is the game currently in beta
    :param entry: full excerpt from status.json
    """
    # print full excerpt to check everything is there.
    logger.debug(f'Status.json says: {entry}')
    # 'Latitude': -19.506268, 'Longitude': -4.657524, 'Heading': 298,
    # 'Altitude': 1320594, 'BodyName': 'Murato 3 a', 'PlanetRadius': 3741155.5,

    """
    # bool to steer when the CCR feature is visible
    self.AST_near_planet = False
    # positions as lat long, lat at index 0, long at index 1
    self.AST_current_pos_lat = None
    self.AST_current_pos_long = None
    self.AST_current_pos_head = None
    self.AST_scan_pos_1_lat = None
    self.AST_scan_pos_1_long = None
    self.AST_scan_pos_2_lat = None
    self.AST_scan_pos_2_long = None
    # radius of the most current planet
    self.AST_current_radius = None
    """

    global plugin

    if "PlanetRadius" in entry.keys():
        plugin.AST_near_planet = True
        plugin.AST_current_radius = entry["PlanetRadius"]
        plugin.AST_current_pos_lat = entry["Latitude"]
        plugin.AST_current_pos_long = entry["Longitude"]
        plugin.AST_current_pos_head = entry["Heading"]
        text = str(plugin.AST_current_pos_lat) + ", " + str(plugin.AST_current_pos_long) + ", " + \
            str(plugin.AST_current_pos_head) + ", " + str(plugin.AST_current_radius)
        plugin.AST_current_pos.set(text)
    else:
        plugin.AST_near_planet = False
        plugin.AST_current_radius = None
        plugin.AST_current_pos_lat = None
        plugin.AST_current_pos_long = None
        plugin.AST_current_pos_head = None
        plugin.AST_current_pos.set("No reference point")

    # rebuild_ui(plugin, cmdr)


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry, state):
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
    global plugin, currentcommander

    if currentcommander != cmdr:
        currentcommander = cmdr
        rebuild_ui(plugin, cmdr)

    if plugin.AST_current_system.get() == "None":
        plugin.AST_current_system.set(str(system))

    # logger.debug(f'The value cmdr in journal_entry is: {cmdr}')
    # logger.debug(f'The value is_beta in journal_entry is: {is_beta}')
    # logger.debug(f'The value system in journal_entry is: {system}')
    # logger.debug(f'The value station in journal_entry is: {station}')
    # logger.debug(f'The value state in journal_entry is: {state}')

    flag = False

    # Prepare to fix probable bugs before a user might report them:
    # TODO: Do not update anything while not in Live universe of E:D!
    # TODO: Check if upon death in 4.0 Horizons do we lose Exobiodata.
    # TODO: Check how real death differs from frontline solutions ground combat zone death.

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        resurrection_event(cmdr)

    if entry["event"] == "ScanOrganic":
        flag = True
        bioscan_event(cmdr, entry)

    if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
        flag = True
        system_body_change_event(cmdr, entry)

    if entry["event"] == "SellOrganicData":
        flag = True
        biosell_event(cmdr, entry)

    if flag:
        # we changed a value so we update line.
        plugin.AST_state.set(
            plugin.AST_last_scan_plant.get()
            + " (" + plugin.AST_current_scan_progress.get()
            + ") on: " + plugin.AST_last_scan_body.get())

        # save most recent relevant state so in case of crash of the system
        # we still have a proper record as long as it finishes saving below.
        plugin.on_preferences_closed(cmdr, is_beta)


def resurrection_event(cmdr: str):
    """Handle resurrection event aka dying."""
    global not_yet_sold_data
    not_yet_sold_data[cmdr] = []


def bioscan_event(cmdr: str, entry):  # noqa #CCR001
    """Handle the ScanOrganic event."""
    global currententrytowrite, plugin
    plugin.AST_last_scan_plant.set(generaltolocalised(entry["Species"].lower()))

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
            # remove thousand seperators for before casting to int from the AST_value.get()
            newvalue = int(plugin.AST_value.get().replace(",", "").split(" ")[0]) + \
                int(vistagenomicsprices[generaltolocalised(entry["Species"].lower())])
            plugin.AST_value.set(f"{newvalue:,}" + " Cr.")
            # Found some cases where the analyse happened
            # seemingly directly after a log.
            plugin.AST_current_scan_progress.set("3/3")
            currententrytowrite["species"] = generaltolocalised(entry["Species"].lower())
            currententrytowrite["system"] = plugin.AST_current_system.get()
            currententrytowrite["body"] = plugin.AST_current_body.get()
            if currententrytowrite not in not_yet_sold_data[cmdr]:
                # If there is no second Sample scantype event
                # we have to save the data here.
                not_yet_sold_data[cmdr].append(currententrytowrite)
                file = directory + "\\notsoldbiodata.json"
                with open(file, "r+", encoding="utf8") as f:
                    notsolddata = json.load(f)
                    notsolddata.append(currententrytowrite)
                    f.seek(0)
                    json.dump(notsolddata, f, indent=4)
                currententrytowrite = {}
            rebuild_ui(plugin, cmdr)
        else:
            plugin.AST_current_scan_progress.set("2/3")
    else:
        # Something is horribly wrong if we end up here
        # If anyone ever sees "Excuse me what the fuck"
        # we know they added a new ScanType, that we might need to handle
        plugin.AST_current_scan_progress.set("Excuse me what the fuck")


def system_body_change_event(cmdr: str, entry):
    """Handle all events that give a tell in which system we are or on what planet we are on."""
    global plugin

    systemchange = False

    try:
        if plugin.AST_current_system.get() != entry["StarSystem"]:
            systemchange = True
        # Get current system name and body from events that need to happen.
        plugin.AST_current_system.set(entry["StarSystem"])
        plugin.AST_current_body.set(entry["Body"])
    except KeyError:
        # Could throw a KeyError in old Horizons versions
        pass

    if systemchange:
        rebuild_ui(plugin, cmdr)

    # To fix the aforementioned eventuality where the systems end up
    # being "None" we update the last scan location
    # When the CMDR gets another journal entry that tells us
    # the players location.

    if ((plugin.AST_last_scan_system.get() == "None") or (plugin.AST_last_scan_body.get() == "None")):
        plugin.AST_last_scan_system.set(entry["StarSystem"])
        plugin.AST_last_scan_body.set(entry["Body"])


def biosell_event(cmdr: str, entry):  # noqa #CCR001
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
    for biodata in not_yet_sold_data[cmdr]:
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
        while i < len(not_yet_sold_data[cmdr]):
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
            check = (not_yet_sold_data[cmdr][i]["system"] == thesystem
                     and not_yet_sold_data[cmdr][i] not in sold_exobiology[cmdr]
                     and not_yet_sold_data[cmdr][i]["species"] in currentbatch.keys())
            if check:
                if currentbatch[not_yet_sold_data[cmdr][i]["species"]] > 0:
                    sold_exobiology[cmdr].append(not_yet_sold_data[cmdr][i])
                    currentbatch[not_yet_sold_data[cmdr][i]["species"]] -= 1
                    not_yet_sold_data[cmdr].pop(i)
                    continue
            i += 1

        f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
        scanneddata = json.load(f)
        scanneddata[cmdr] = []
        f.seek(0)
        json.dump(scanneddata, f, indent=4)
        f.close()

        if not_yet_sold_data[cmdr] != []:
            file = directory + "\\notsoldbiodata.json"
            with open(file, "r+", encoding="utf8") as f:
                notsolddata = json.load(f)
                for data in not_yet_sold_data[cmdr]:
                    notsolddata[cmdr].append(data)
                f.seek(0)
                json.dump(notsolddata, f, indent=4)

    else:
        # CMDR sold the whole batch.
        for data in not_yet_sold_data[cmdr]:
            if (data not in sold_exobiology[cmdr] and currentbatch[data["species"]] > 0):
                currentbatch[data["species"]] -= 1
                sold_exobiology[cmdr].append(data)
        not_yet_sold_data[cmdr] = []
        # We can already reset to 0 to ensure that after selling all data at once
        # we end up with a reset of the Scanned value metric
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
        f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
        scanneddata = json.load(f)
        scanneddata[cmdr] = []
        f.seek(0)
        json.dump(scanneddata, f, indent=4)
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

        if cmdr not in solddata.keys():
            solddata[cmdr] = []

        if sold_exobiology[cmdr] != []:
            for item in sold_exobiology[cmdr]:
                solddata[cmdr].append(item)
            sold_exobiology[cmdr] = []
        f.seek(0)
        json.dump(solddata, f, indent=4)

    # If we sell the exobiodata in the same system as where we currently are
    # Then we want to remove the "*" around the body names of the newly sold biodata
    # So just rebuild the ui for good measure.
    rebuild_ui(plugin, cmdr)


plugin = ArtemisScannerTracker()


def clear_ui():
    """Remove all labels from this plugin."""
    global frame
    # remove all labels from the frame
    for label in frame.winfo_children():
        label.destroy()


def rebuild_ui(plugin, cmdr: str):  # noqa #CCR001
    """Rebuild the UI in case of preferences change."""
    global frame

    clear_ui()

    # recreate UI
    current_row = 14

    # Clonal Colonial Range here.
    if plugin.AST_hide_CCR.get() != 1:
        # show distances for the last scans.
        tk.Label(frame, text="Currentpos: ").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_current_pos).grid(row=current_row, column=1, sticky=tk.W)

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
        tk.Button(frame, text="📋", command=clipboard).grid(row=current_row, column=2, sticky=tk.E)

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

    # Tracked sold bio scans as the last thing to add to the UI
    if plugin.AST_hide_sold_bio.get() != 1:
        build_sold_bio_ui(plugin, cmdr)

    theme.update(frame)  # Apply theme colours to the frame and its children, including the new widgets


def build_sold_bio_ui(plugin, cmdr: str):  # noqa #CCR001
    # Create a Button to make it shorter?
    soldbiodata = {}
    notsoldbiodata = {}

    file = directory + "\\soldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        soldbiodata = json.load(f)

    file = directory + "\\notsoldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        notsoldbiodata = json.load(f)

    current_row = 15
    tk.Label(frame, text="Scans in this System:").grid(row=current_row, sticky=tk.W)

    # Check if we even got a cmdr yet!
    logger.info(f"Commander: {cmdr}. attempting to access")

    bodylistofspecies = {}

    try:
        for sold in soldbiodata[cmdr]:
            if sold["system"] == plugin.AST_current_system.get():

                bodyname = ""

                # Check if body has a special name or if we have standardized names
                if sold["system"] in sold["body"]:
                    # no special name for planet
                    bodyname = sold["body"].replace(sold["system"], "")[1:]
                else:
                    bodyname = sold["body"]

                if sold["species"] not in bodylistofspecies.keys():
                    bodylistofspecies[sold["species"]] = [[bodyname, True]]
                else:
                    bodylistofspecies[sold["species"]].append([bodyname, True])

    except KeyError:
        # if we don't have the cmdr in the sold data yet we just pass all sold data.
        pass

    try:
        for notsold in notsoldbiodata[cmdr]:
            if notsold["system"] == plugin.AST_current_system.get():

                bodyname = ""

                # Check if body has a special name or if we have standardized names
                if notsold["system"] in notsold["body"]:
                    # no special name for planet
                    bodyname = notsold["body"].replace(notsold["system"], "")[1:]
                else:
                    bodyname = notsold["body"]

                if notsold["species"] not in bodylistofspecies.keys():
                    bodylistofspecies[notsold["species"]] = [[bodyname, False]]
                else:
                    bodylistofspecies[notsold["species"]].append([bodyname, False])

    except KeyError:
        # if we don't have the cmdr in the notsold data yet we just pass.
        pass

    if bodylistofspecies == {}:
        tk.Label(frame, text="None").grid(row=current_row, column=1, sticky=tk.W)

    for species in bodylistofspecies.keys():
        current_row += 1
        tk.Label(frame, text=species).grid(row=current_row, column=0, sticky=tk.W)
        bodies = ""
        for body in bodylistofspecies[species]:
            if body[1]:
                bodies = bodies + body[0] + ", "
            else:
                bodies = bodies + "*" + body[0] + "*, "
        if len(bodies) > 3:
            bodies = bodies[:-2]

        tk.Label(frame, text=bodies).grid(row=current_row, column=1, sticky=tk.W)


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
    rebuild_ui(plugin, cmdr)

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
