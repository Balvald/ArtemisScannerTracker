"""Artemis Scanner Tracker v0.2.0 by Balvald."""

import json
import logging
import os
import tkinter as tk
from typing import Optional

import myNotebook as nb  # type: ignore # noqa: N813
import requests
from config import appname, config  # type: ignore
from theme import theme  # type: ignore
from ttkHyperlinkLabel import HyperlinkLabel  # type: ignore

import organicinfo as orgi
from journalcrawler import build_biodata_json

frame: Optional[tk.Frame] = None

# Shows debug fields in preferences when True
debug = False

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

PLUGIN_NAME = "AST"

AST_VERSION = "v0.2.0"

AST_REPO = "Balvald/ArtemisScannerTracker"

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-"

vistagenomicsprices = orgi.getvistagenomicprices()

firstdashboard = True

not_yet_sold_data = {}
sold_exobiology = {}
currententrytowrite = {}
currentcommander = ""
cmdrstates = {}

plugin = None

# Gonna need the files directory to store data for full
# tracking of all the biological things that the CMDR scans.
directory, filename = os.path.split(os.path.realpath(__file__))

filenames = ["\\soldbiodata.json", "\\notsoldbiodata.json",  "\\cmdrstates.json"]

for file in filenames:
    if not os.path.exists(directory + file):
        f = open(directory + file, "w", encoding="utf8")
        f.write(r"{}")
        f.close()
    elif file == "\\soldbiodata.json" or file == "\\notsoldbiodata.json":
        # (not)soldbiodata file already exists
        with open(directory + file, "r+", encoding="utf8") as f:
            test = json.load(f)
            if type([]) == type(test):
                # we have an old version of the (not)soldbiodata.json
                # clear it, have the user do the journal crawling again.
                logger.warning(f"Found old {file} format")
                logger.warning("Clearing file...")
                f.seek(0)
                f.write(r"{}")
                f.truncate()

# load notyetsolddata

with open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_data = json.load(f)

with open(directory + "\\cmdrstates.json", "r+", encoding="utf8") as f:
    cmdrstates = json.load(f)


class ArtemisScannerTracker:
    """Artemis Scanner Tracker plugin class."""

    def __init__(self) -> None:
        """Initialize the plugin by getting values from the config file."""
        self.AST_in_Legacy: Optional[bool] = False

        # Be sure to use names that wont collide in our config variables
        # Bools for show hide checkboxes

        self.AST_hide_fullscan: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_fullscan"))
        self.AST_hide_species: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_species"))
        self.AST_hide_progress: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_progress"))
        self.AST_hide_last_system: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_last_system"))
        self.AST_hide_last_body: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_last_body"))
        self.AST_hide_system: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_system"))
        self.AST_hide_body: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_body"))
        self.AST_hide_value: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_value"))
        self.AST_hide_sold_bio: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_sold_bio"))
        self.AST_hide_CCR: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_CCR"))

        # bool to steer when the CCR feature is visible
        self.AST_near_planet: Optional[tk.BooleanVar] = False

        # positions as lat long, lat at index 0, long at index 1
        self.AST_current_pos_vector = [None, None, None]
        self.AST_scan_1_pos_vector = [None, None]
        self.AST_scan_2_pos_vector = [None, None]

        self.AST_CCR: Optional[tk.IntVar] = tk.IntVar(value=0)

        # radius of the most current planet
        self.AST_current_radius: Optional[tk.StringVar] = tk.StringVar(value="")

        self.AST_current_pos: Optional[tk.StringVar] = tk.StringVar(value="")
        self.AST_scan_1_pos_dist: Optional[tk.StringVar] = tk.StringVar(value="")
        self.AST_scan_2_pos_dist: Optional[tk.StringVar] = tk.StringVar(value="")

        # last Commander
        self.AST_last_CMDR: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str("AST_last_CMDR")))

        # Artemis Scanner State infos
        self.AST_last_scan_plant: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_last_scan_system: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_last_scan_body: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_current_scan_progress: Optional[tk.StringVar] = tk.StringVar(value=())
        self.AST_current_system: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_current_body: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_state: Optional[tk.StringVar] = tk.StringVar(value=str())

        rawvalue = int(config.get_int("AST_value"))

        self.AST_value: Optional[tk.StringVar] = tk.StringVar(
            value=((f"{rawvalue:,}") + str(" Cr.")))

        self.updateavailable = False

        response = requests.get(f"https://api.github.com/repos/{AST_REPO}/releases/latest")

        if response.ok:
            data = response.json()

            if AST_VERSION != data['tag_name']:
                self.updateavailable = True
        else:
            logger.error("Check for update failed!")

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

    def setup_preferences(self, parent: nb.Notebook,  # noqa #CCR001
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
        if currentcommander != "" and currentcommander is not None:
            load_cmdr(cmdr)

        line = "___________________________________________________________"

        current_row = 0
        frame = nb.Frame(parent)

        prefs_label(frame, "Artemis Scanner Tracker v0.2.0 by Balvald", current_row, 0, tk.W)

        current_row += 1

        prefs_label(frame, line, current_row, 0, tk.W)
        prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        checkboxlistleft = ["Hide Full Status", "Hide Species",
                            "Hide System of last Scan", "Hide Current System",
                            "Hide Scanned/Sold Species in System"]
        checkboxlistright = ["Hide Value of unsold Scans", "Hide Scan Progress",
                             "Hide Body of last Scan", "Hide Current Body",
                             "Hide Clonal Colonial Distances"]

        variablelistleft = [self.AST_hide_fullscan, self.AST_hide_species,
                            self.AST_hide_last_system, self.AST_hide_system,
                            self.AST_hide_sold_bio]
        variablelistright = [self.AST_hide_value, self.AST_hide_progress,
                             self.AST_hide_last_body, self.AST_hide_body,
                             self.AST_hide_CCR]

        for i in range(max(len(checkboxlistleft), len(checkboxlistright))):
            if i < len(checkboxlistleft):
                prefs_tickbutton(frame, checkboxlistleft[i], variablelistleft[i], current_row, 0, tk.W)
            if i < len(checkboxlistright):
                prefs_tickbutton(frame, checkboxlistright[i], variablelistright[i], current_row, 1, tk.W)
            current_row += 1

        if debug:

            debuglistleft = ["Species", "System of last Scan",
                             "Body of last Scan", "Scan progress",
                             "Scanned Value"]
            debuglistright = [self.AST_last_scan_plant, self.AST_last_scan_system,
                              self.AST_last_scan_body, self.AST_current_scan_progress,
                              self.AST_value]

            for i in range(max(len(debuglistleft), len(debuglistright))):
                if i < len(debuglistleft):
                    prefs_label(frame, debuglistleft[i], current_row, 0, tk.W)
                if i < len(debuglistright):
                    prefs_entry(frame, debuglistright[i], current_row, 0, tk.W)
                current_row += 1

        prefs_label(frame, line, current_row, 0, tk.W)
        prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        text = "Scan game journals for sold exobiology"
        prefs_button(frame, text, self.buildsoldbiodatajson, current_row, 0, tk.W)
        text = "Scan local journal folder for sold exobiology"
        prefs_button(frame, text, self.buildsoldbiodatajsonlocal, current_row, 1, tk.W)

        current_row += 1

        prefs_label(frame, line, current_row, 0, tk.W)
        prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        text = "To reset the status, body, system and species"
        prefs_label(frame, text, current_row, 0, tk.W)

        current_row += 1

        text = "of the last scan press the button below"
        prefs_label(frame, text, current_row, 0, tk.W)

        current_row += 1

        prefs_button(frame, "RESET", self.reset, current_row, 0, tk.W)

        current_row += 1

        return frame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.

        It is called when the preferences dialog is dismissed by the user.

        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        global currentcommander
        if currentcommander != "" and currentcommander is not None:
            save_cmdr(currentcommander)
        if currentcommander != cmdr and cmdr != "" and cmdr is not None:
            currentcommander = cmdr
            load_cmdr(currentcommander)

        # for formatting the string with thousands seperators we have to remove them here again.
        config.set("AST_value", int(self.AST_value.get().replace(",", "").split(" ")[0]))

        """        config.set("AST_CCR", int(self.AST_CCR.get()))"""

        config.set("AST_hide_value", int(self.AST_hide_value.get()))
        config.set("AST_hide_fullscan", int(self.AST_hide_fullscan.get()))
        config.set("AST_hide_species", int(self.AST_hide_species.get()))
        config.set("AST_hide_progress", int(self.AST_hide_progress.get()))
        config.set("AST_hide_last_system", int(self.AST_hide_last_system.get()))
        config.set("AST_hide_last_body", int(self.AST_hide_last_body.get()))
        config.set("AST_hide_system", int(self.AST_hide_system.get()))
        config.set("AST_hide_body", int(self.AST_hide_body.get()))
        config.set("AST_hide_sold_bio", int(self.AST_hide_sold_bio.get()))
        config.set("AST_hide_CCR", int(self.AST_hide_CCR.get()))

        logger.info(f"Currently last Commander is: {cmdr}")

        config.set("AST_last_CMDR", str(cmdr))

        logger.debug("ArtemisScannerTracker saved preferences")

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.

        This is called by plugin_app below.

        :param parent: EDMC main window Tk
        :return: Our frame
        """
        global frame, currentcommander

        try:
            load_cmdr(self.AST_last_CMDR.get())
        except KeyError:
            # last Commander saved is just not known
            pass

        frame = tk.Frame(parent)

        rebuild_ui(self, currentcommander)

        return frame

    def reset(self):
        """Reset function of the Reset Button."""
        self.AST_current_scan_progress.set("0/3")
        self.AST_last_scan_system.set("")
        self.AST_last_scan_body.set("")
        self.AST_last_scan_plant.set("None")
        self.AST_state.set("None")
        self.AST_value.set("0 Cr.")

    def clipboard(self):
        """Copy value to clipboard."""
        dummytk = tk.Tk()  # creates a window we don't want
        dummytk.clipboard_clear()
        dummytk.clipboard_append(plugin.AST_value.get()[:-4].replace(",", ""))
        dummytk.destroy()  # destroying it again we don't need full another window everytime we copy to clipboard.

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


# region eventhandling

def dashboard_entry(cmdr: str, is_beta, entry):  # noqa #CCR001
    """
    React to changes in the CMDRs status (Movement for CCR feature).

    :param cmdr: The current ED Commander
    :param is_beta: Is the game currently in beta
    :param entry: full excerpt from status.json
    """
    global plugin, currentcommander, firstdashboard

    if plugin.AST_in_Legacy is True:
        # We're in legacy we don't update anything through dashboard entries
        return

    flag = False

    if currentcommander != cmdr and currentcommander != "" and currentcommander is not None:
        # Check if new and old Commander are in the cmdrstates file.
        save_cmdr(currentcommander)
        # New Commander not in cmdr states file.
        if cmdr not in cmdrstates.keys():
            # completely new cmdr theres nothing to load
            cmdrstates[cmdr] = ["None", "None", "None", "0/3", "None", "0 Cr.", "None", "None", "None"]
        else:
            if cmdr is not None and cmdr != "":
                load_cmdr(cmdr)

        # Set new Commander to currentcommander
        currentcommander = cmdr

        flag = True

    if firstdashboard:
        firstdashboard = False
        plugin.on_preferences_closed(cmdr, is_beta)

    if "PlanetRadius" in entry.keys():
        # We found a PlanetRadius again, this means we are near a planet.
        if not plugin.AST_near_planet:
            # We just came into range of a planet again.
            flag = True
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
        text = "lat: " + str(plugin.AST_current_pos_vector[0]) + \
               ", long: " + str(plugin.AST_current_pos_vector[1]) + ", B:" + \
               str(plugin.AST_current_pos_vector[2])  # + ", " + str(plugin.AST_current_radius)
        plugin.AST_current_pos.set(text)

        if plugin.AST_current_scan_progress.get() in ["1/3", "2/3"] and plugin.AST_scan_1_pos_vector[0] is not None:
            plugin.AST_scan_1_pos_dist.set(str(round(orgi.computedistance(plugin.AST_current_pos_vector[0],
                                                                          plugin.AST_current_pos_vector[1],
                                                                          plugin.AST_scan_1_pos_vector[0],
                                                                          plugin.AST_scan_1_pos_vector[1],
                                                                          plugin.AST_current_radius), 2))
                                           + " m / " + str(plugin.AST_CCR.get()) + " m, B:" +
                                           str(round(orgi.bearing(plugin.AST_current_pos_vector[0],
                                                                  plugin.AST_current_pos_vector[1],
                                                                  plugin.AST_scan_1_pos_vector[0],
                                                                  plugin.AST_scan_1_pos_vector[1]), 2)))
        if plugin.AST_current_scan_progress.get() == "2/3" and plugin.AST_scan_1_pos_vector[0] is not None:
            plugin.AST_scan_2_pos_dist.set(str(round(orgi.computedistance(plugin.AST_current_pos_vector[0],
                                                                          plugin.AST_current_pos_vector[1],
                                                                          plugin.AST_scan_2_pos_vector[0],
                                                                          plugin.AST_scan_2_pos_vector[1],
                                                                          plugin.AST_current_radius), 2))
                                           + " m / " + str(plugin.AST_CCR.get()) + " m, B:" +
                                           str(round(orgi.bearing(plugin.AST_current_pos_vector[0],
                                                                  plugin.AST_current_pos_vector[1],
                                                                  plugin.AST_scan_2_pos_vector[0],
                                                                  plugin.AST_scan_2_pos_vector[1]), 2)))
    else:
        if plugin.AST_near_planet:
            # Switch happened we went too far from the planet to get any reference from it.
            flag = True
        plugin.AST_near_planet = False
        plugin.AST_current_radius = None
        plugin.AST_current_pos_vector[0] = None
        plugin.AST_current_pos_vector[1] = None
        plugin.AST_current_pos_vector[2] = None
        plugin.AST_current_pos.set("No reference point")

    if flag:
        rebuild_ui(plugin, cmdr)


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry, state):  # noqa #CCR001
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

    if (int(state["GameVersion"][0]) < 4) and (plugin.AST_in_Legacy is False):
        # We're in Legacy, we'll not change the state of anything through journal entries.
        plugin.AST_in_Legacy = True
        return
    else:
        plugin.AST_in_Legacy = False

    if currentcommander != cmdr and currentcommander != "" and currentcommander is not None:
        # Check if new and old Commander are in the cmdrstates file.
        save_cmdr(currentcommander)
        # New Commander not in cmdr states file.
        if cmdr not in cmdrstates.keys():
            # completely new cmdr theres nothing to load
            cmdrstates[cmdr] = ["None", "None", "None", "0/3", "None", "0 Cr.", "None", "None", "None"]
        else:
            # Load cmdr from cmdr states.
            if cmdr is not None:
                load_cmdr(cmdr)
        # Set new Commander to currentcommander
        currentcommander = cmdr

        rebuild_ui(plugin, cmdr)

    if plugin.AST_current_system.get() != system:
        plugin.AST_current_system.set(system)
        rebuild_ui(plugin, cmdr)

    if plugin.AST_current_system.get() == "" or plugin.AST_current_system.get() == "None":
        plugin.AST_current_system.set(str(system))

    flag = False

    # Prepare to fix probable bugs before a user might report them:

    # TODO: Check if upon death in 4.0 Horizons do we lose Exobiodata.
    # TODO: Check how real death differs from frontline solutions ground combat zone death.

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        resurrection_event(cmdr)

    if entry["event"] == "ScanOrganic":
        flag = True
        bioscan_event(cmdr, is_beta, entry)

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


def bioscan_event(cmdr: str, is_beta, entry):  # noqa #CCR001
    """Handle the ScanOrganic event."""
    global currententrytowrite, plugin
    plugin.AST_last_scan_plant.set(orgi.generaltolocalised(entry["Species"].lower()))

    # In the eventuality that the user started EMDC after
    # the "Location" event happens and directly scans a plant
    # these lines wouldn"t be able to do anything but to
    # set the System and body of the last Scan to "None"
    plugin.AST_last_scan_system.set(plugin.AST_current_system.get())
    plugin.AST_last_scan_body.set(plugin.AST_current_body.get())

    if entry["ScanType"] == "Log":
        plugin.AST_current_scan_progress.set("1/3")
        plugin.AST_CCR.set(orgi.getclonalcolonialranges(orgi.genusgeneraltolocalised(entry["Genus"])))
        plugin.AST_scan_1_pos_vector[0] = plugin.AST_current_pos_vector[0]
        plugin.AST_scan_1_pos_vector[1] = plugin.AST_current_pos_vector[1]
        plugin.on_preferences_closed(cmdr, is_beta)
    elif entry["ScanType"] in ["Sample", "Analyse"]:
        if (entry["ScanType"] == "Analyse"):

            if (plugin.AST_value.get() == "None"
               or plugin.AST_value.get() == ""
               or plugin.AST_value.get() is None):
                plugin.AST_value.set("0 Cr.")
            # remove thousand seperators for before casting to int from the AST_value.get()
            newvalue = int(plugin.AST_value.get().replace(",", "").split(" ")[0]) + \
                int(vistagenomicsprices[orgi.generaltolocalised(entry["Species"].lower())])
            plugin.AST_value.set(f"{newvalue:,}" + " Cr.")
            # Found some cases where the analyse happened
            # seemingly directly after a log.
            plugin.AST_current_scan_progress.set("3/3")
            # clear the scan locations to [None, None]
            plugin.AST_scan_1_pos_vector = [None, None]
            plugin.AST_scan_2_pos_vector = [None, None]
            plugin.AST_CCR.set(0)
            plugin.AST_scan_1_pos_dist.set("")
            plugin.AST_scan_2_pos_dist.set("")
            currententrytowrite["species"] = orgi.generaltolocalised(entry["Species"].lower())
            currententrytowrite["system"] = plugin.AST_current_system.get()
            currententrytowrite["body"] = plugin.AST_current_body.get()
            if cmdr not in not_yet_sold_data.keys():
                not_yet_sold_data[cmdr] = []
            if currententrytowrite not in not_yet_sold_data[cmdr]:
                # If there is no second Sample scantype event
                # we have to save the data here.
                not_yet_sold_data[cmdr].append(currententrytowrite)
                file = directory + "\\notsoldbiodata.json"
                with open(file, "r+", encoding="utf8") as f:
                    notsolddata = json.load(f)
                    if cmdr not in notsolddata.keys():
                        notsolddata[cmdr] = []
                    notsolddata[cmdr].append(currententrytowrite)
                    f.seek(0)
                    json.dump(notsolddata, f, indent=4)
                    f.truncate()
                currententrytowrite = {}
        else:
            plugin.AST_current_scan_progress.set("2/3")
            plugin.AST_CCR.set(orgi.getclonalcolonialranges(orgi.genusgeneraltolocalised(entry["Genus"])))
            plugin.AST_scan_2_pos_vector[0] = plugin.AST_current_pos_vector[0]
            plugin.AST_scan_2_pos_vector[1] = plugin.AST_current_pos_vector[1]
    else:
        # Something is horribly wrong if we end up here
        # If anyone ever sees "Excuse me what the fuck"
        # we know they added a new ScanType, that we might need to handle
        plugin.AST_current_scan_progress.set("Excuse me what the fuck")

    # We now need to rebuild regardless how far we progressed
    rebuild_ui(plugin, cmdr)


def system_body_change_event(cmdr: str, entry):  # noqa #CCR001
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

    if (((plugin.AST_last_scan_system.get() == "")
         or (plugin.AST_last_scan_body.get() == "")
         or (plugin.AST_last_scan_system.get() == "None")
         or (plugin.AST_last_scan_body.get() == "None"))):
        plugin.AST_last_scan_system.set(entry["StarSystem"])
        plugin.AST_last_scan_body.set(entry["Body"])

    if cmdrstates[cmdr][1] == "" or cmdrstates[cmdr][2] == "":
        cmdrstates[cmdr][1] = plugin.AST_last_scan_system.get()
        cmdrstates[cmdr][2] = plugin.AST_last_scan_body.get()
        save_cmdr(cmdr)


def biosell_event(cmdr: str, entry):  # noqa #CCR001
    """Handle the SellOrganicData event."""
    global currententrytowrite, not_yet_sold_data, sold_exobiology
    soldvalue = 0

    logger.info('called biosell_event')

    if cmdr != "" and cmdr is not None and cmdr not in sold_exobiology.keys():
        sold_exobiology[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}

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
    if cmdr not in not_yet_sold_data.keys():
        not_yet_sold_data[cmdr] = []
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

            """if cmdr not in sold_exobiology.keys():
                sold_exobiology[cmdr] = []"""
            firstletter = not_yet_sold_data[cmdr][i]["system"][0].lower()
            if firstletter not in alphabet:
                firstletter = "-"
            # Checking here more granularily which data was sold
            # We do know though that the specifc data was sold only
            # in one system that at this point is saved in
            # the variable"thesystem"
            if (thesystem not in sold_exobiology[cmdr][firstletter].keys()
               and (thesystem[0].lower() == firstletter or firstletter == "-")):
                sold_exobiology[cmdr][firstletter][thesystem] = []

            """check = (not_yet_sold_data[cmdr][i]["system"] == thesystem
                     and not_yet_sold_data[cmdr][i] not in sold_exobiology[cmdr]
                     and not_yet_sold_data[cmdr][i]["species"] in currentbatch.keys())"""

            check = (not_yet_sold_data[cmdr][i]["system"] == thesystem
                     and not_yet_sold_data[cmdr][i]
                     not in sold_exobiology[cmdr][firstletter][thesystem]
                     and not_yet_sold_data[cmdr][i]["species"] in currentbatch.keys())

            if check:
                if currentbatch[not_yet_sold_data[cmdr][i]["species"]] > 0:
                    sold_exobiology[cmdr][firstletter][thesystem].append(not_yet_sold_data[cmdr][i])
                    currentbatch[not_yet_sold_data[cmdr][i]["species"]] -= 1
                    not_yet_sold_data[cmdr].pop(i)
                    continue
            i += 1

        f = open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8")
        scanneddata = json.load(f)
        scanneddata[cmdr] = []
        f.seek(0)
        json.dump(scanneddata, f, indent=4)
        f.truncate()
        f.close()

        if not_yet_sold_data[cmdr] != []:
            file = directory + "\\notsoldbiodata.json"
            with open(file, "r+", encoding="utf8") as f:
                notsolddata = json.load(f)
                for data in not_yet_sold_data[cmdr]:
                    notsolddata[cmdr].append(data)
                f.seek(0)
                json.dump(notsolddata, f, indent=4)
                f.truncate()

    else:
        # CMDR sold the whole batch.
        for data in not_yet_sold_data[cmdr]:
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
                sold_exobiology[cmdr][firstletter][data["system"]].append(data)
        not_yet_sold_data[cmdr] = []
        # We can already reset to 0 to ensure that after selling all data at once
        # we end up with a reset of the Scanned value metric
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
        f = open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8")
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
    newvalue = int(plugin.AST_value.get().replace(",", "").split(" ")[0]) - soldvalue
    plugin.AST_value.set(str(f"{newvalue:,}") + " Cr.")

    # No negative value of biodata could still be unsold on the Scanner
    # This means that there was data on the Scanner that
    # the plugin was unable to record by not being active.
    # If the value was reset before we will reset it here again.
    if int(plugin.AST_value.get().replace(",", "").split(" ")[0]) < 0:
        logger.info('Set Unsold Scan Value to 0 Cr')
        plugin.AST_value.set("0 Cr.")
    # Now write the data into the local file
    file = directory + "\\soldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        solddata = json.load(f)

        if cmdr not in solddata.keys():
            solddata[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}

        if sold_exobiology[cmdr] != []:
            for letter in sold_exobiology[cmdr]:
                for system in sold_exobiology[cmdr][letter]:
                    if system not in solddata[cmdr][letter].keys():
                        solddata[cmdr][letter][system] = []
                    for item in sold_exobiology[cmdr][letter][system]:
                        solddata[cmdr][letter][system].append(item)
            sold_exobiology[cmdr] = {alphabet[i]: {} for i in range(len(alphabet))}
        f.seek(0)
        json.dump(solddata, f, indent=4)
        f.truncate()

    # If we sell the exobiodata in the same system as where we currently are
    # Then we want to remove the "*" around the body names of the newly sold biodata
    # So just rebuild the ui for good measure.
    rebuild_ui(plugin, cmdr)

# endregion


plugin = ArtemisScannerTracker()


# region saving/loading


def save_cmdr(cmdr):
    """Save information specific to the cmdr in the cmdrstates.json."""
    global plugin, directory

    if cmdr not in cmdrstates.keys():
        cmdrstates[cmdr] = ["None", "None", "None", "0/3", "None", "0 Cr.", "None", "None", "None"]

    cmdrstates[cmdr][0] = plugin.AST_last_scan_plant.get()
    cmdrstates[cmdr][1] = plugin.AST_last_scan_system.get()
    cmdrstates[cmdr][2] = plugin.AST_last_scan_body.get()
    cmdrstates[cmdr][3] = plugin.AST_current_scan_progress.get()
    cmdrstates[cmdr][4] = plugin.AST_state.get()
    cmdrstates[cmdr][5] = plugin.AST_value.get()
    cmdrstates[cmdr][6] = plugin.AST_CCR.get()
    cmdrstates[cmdr][7] = plugin.AST_scan_1_pos_vector.copy()
    cmdrstates[cmdr][8] = plugin.AST_scan_2_pos_vector.copy()

    file = directory + "\\cmdrstates.json"

    open(file, "r+", encoding="utf8").close()
    with open(file, "r+", encoding="utf8") as f:
        f.seek(0)
        json.dump(cmdrstates, f, indent=4)
        f.truncate()


def load_cmdr(cmdr):
    """Load information about a cmdr from cmdrstates.json."""
    global cmdrstates, plugin
    file = directory + "\\cmdrstates.json"

    with open(file, "r+", encoding="utf8") as f:
        cmdrstates = json.load(f)

    plugin.AST_last_scan_plant.set(cmdrstates[cmdr][0])
    plugin.AST_last_scan_system.set(cmdrstates[cmdr][1])
    plugin.AST_last_scan_body.set(cmdrstates[cmdr][2])
    plugin.AST_current_scan_progress.set(cmdrstates[cmdr][3])
    plugin.AST_state.set(cmdrstates[cmdr][4])
    plugin.AST_value.set(cmdrstates[cmdr][5])
    plugin.AST_CCR.set(cmdrstates[cmdr][6])
    plugin.AST_scan_1_pos_vector = cmdrstates[cmdr][7]
    plugin.AST_scan_2_pos_vector = cmdrstates[cmdr][8]

# endregion


# region UI


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
    current_row = 0

    if plugin.updateavailable:
        latest = "github.com/Balvald/ArtemisScannerTracker/releases/latest"
        HyperlinkLabel(frame, text="Update available!", url=latest, underline=True).grid(row=current_row, sticky=tk.W)
        current_row += 1

    uielementcheck = [plugin.AST_hide_fullscan.get(), plugin.AST_hide_species.get(), plugin.AST_hide_progress.get(),
                      plugin.AST_hide_last_system.get(), plugin.AST_hide_last_body.get(), plugin.AST_hide_value.get(),
                      plugin.AST_hide_system.get(), plugin.AST_hide_body.get()]
    uielementlistleft = ["Last Exobiology Scan:", "Last Species:", "Scan Progress:",
                         "System of last Scan:", "Body of last Scan:", "Unsold Scan Value:",
                         "Current System:", "Current Body:"]
    uielementlistright = [plugin.AST_state, plugin.AST_last_scan_plant, plugin.AST_current_scan_progress,
                          plugin.AST_last_scan_system, plugin.AST_last_scan_body, plugin.AST_value,
                          plugin.AST_current_system, plugin.AST_current_body]
    uielementlistextra = [None, None, None, None, None, "clipboardbutton", None, None]

    for i in range(max(len(uielementlistleft), len(uielementlistright))):
        if uielementcheck[i] != 1:
            if i < len(uielementlistleft):
                ui_label(frame, uielementlistleft[i], current_row, 0, tk.W)
            if i < len(uielementlistright):
                ui_entry(frame, uielementlistright[i], current_row, 1, tk.W)
            if uielementlistextra[i] == "clipboardbutton":
                ui_button(frame, "📋", plugin.clipboard, current_row, 2, tk.E)
            current_row += 1

    # Clonal Colonial Range here.
    if plugin.AST_hide_CCR.get() != 1 and plugin.AST_near_planet is True:
        # show distances for the last scans.
        tk.Label(frame, text="Distance to Scan #1: ").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_scan_1_pos_dist).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        tk.Label(frame, text="Distance to Scan #2: ").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_scan_2_pos_dist).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1
        tk.Label(frame, text="Currentpos: ").grid(row=current_row, sticky=tk.W)
        tk.Label(frame, textvariable=plugin.AST_current_pos).grid(row=current_row, column=1, sticky=tk.W)
        current_row += 1

    # Tracked sold bio scans as the last thing to add to the UI
    if plugin.AST_hide_sold_bio.get() != 1:
        build_sold_bio_ui(plugin, cmdr, current_row)

    theme.update(frame)  # Apply theme colours to the frame and its children, including the new widgets


def build_sold_bio_ui(plugin, cmdr: str, current_row):  # noqa #CCR001
    # Create a Button to make it shorter?
    soldbiodata = {}
    notsoldbiodata = {}

    file = directory + "\\soldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        soldbiodata = json.load(f)

    file = directory + "\\notsoldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        notsoldbiodata = json.load(f)

    tk.Label(frame, text="Scans in this System:").grid(row=current_row, sticky=tk.W)

    if cmdr == "":
        return

    # Check if we even got a cmdr yet!
    # logger.info(f"Commander: {cmdr}. attempting to access")
    # logger.info(f"data: {soldbiodata[cmdr]}.")
    # logger.info(f"data: {notsoldbiodata}.")

    bodylistofspecies = {}

    firstletter = plugin.AST_current_system.get()[0].lower()

    try:
        if plugin.AST_current_system.get() in soldbiodata[cmdr][firstletter].keys():
            for sold in soldbiodata[cmdr][firstletter][plugin.AST_current_system.get()]:
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
        while (bodies[-1] == "," or bodies[-1] == " "):
            bodies = bodies[:-1]

        tk.Label(frame, text=bodies).grid(row=current_row, column=1, sticky=tk.W)


def prefs_label(frame, text, row: int, col: int, sticky) -> None:
    """Create label for the preferences of the plugin."""
    nb.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)


def prefs_entry(frame, textvariable, row: int, col: int, sticky) -> None:
    """Create an entry field for the preferences of the plugin."""
    nb.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)


def prefs_button(frame, text, command, row: int, col: int, sticky) -> None:
    """Create a button for the prefereces of the plugin."""
    nb.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)


def prefs_tickbutton(frame, text, variable, row: int, col: int, sticky) -> None:
    """Create a tickbox for the preferences of the plugin."""
    nb.Checkbutton(frame, text=text, variable=variable).grid(row=row, column=col, sticky=sticky)


def ui_label(frame, text, row: int, col: int, sticky) -> None:
    """Create a label for the ui of the plugin."""
    tk.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)


def ui_entry(frame, textvariable, row: int, col: int, sticky) -> None:
    """Create a label that displays the content of a textvariable for the ui of the plugin."""
    tk.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)


def ui_button(frame, text, command, row: int, col: int, sticky) -> None:
    """Create a button for the ui of the plugin."""
    tk.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)

# endregion


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
