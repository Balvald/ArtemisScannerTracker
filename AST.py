"""Artemis Scanner Tracker Class"""

import logging
import os
import requests
import tkinter as tk
from typing import Optional

import myNotebook as nb  # type: ignore
from config import appname, config  # type: ignore

import saving
import ui
import organicinfo as orgi
from journalcrawler import build_biodata_json


logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")


class ArtemisScannerTracker:
    """Artemis Scanner Tracker plugin class."""

    def __init__(self, AST_VERSION: str, AST_REPO: str, PLUGIN_NAME: str,
                 directory: str, cmdrstates: dict, notyetsolddata: dict, soldexobiology: dict) -> None:
        """Initialize the plugin by getting values from the config file."""

        self.AST_VERSION = AST_VERSION
        self.AST_REPO = AST_REPO
        self.PLUGIN_NAME = PLUGIN_NAME
        self.AST_DIR = directory
        self.CMDR_states = cmdrstates

        self.frame = None

        self.notyetsolddata = notyetsolddata
        self.soldexobiology = soldexobiology

        self.AST_in_Legacy = False

        self.AST_debug: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_debug"))

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
        self.AST_hide_after_selling: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_after_selling"))
        self.AST_hide_after_full_scan: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_after_full_scan"))
        self.AST_hide_value_when_zero: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_value_when_zero"))

        # option for shorterned numbers
        self.AST_shorten_value: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_shorten_value"))

        # bool to steer when the CCR feature is visible
        self.AST_near_planet = False

        # positions as lat long, lat at index 0, long at index 1
        self.AST_current_pos_vector = [None, None, None]
        self.AST_scan_1_pos_vector = [None, None]
        self.AST_scan_2_pos_vector = [None, None]

        self.AST_CCR: Optional[tk.IntVar] = tk.IntVar(value=0)

        # value to steer the autohiding functionality
        self.AST_after_selling: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_after_selling"))

        # hide feature for Scans in the system for the button:
        self.AST_hide_scans_in_system: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_scans_in_system"))

        # radius of the most current planet
        self.AST_current_radius: Optional[tk.StringVar] = tk.StringVar(value="")

        self.AST_current_pos: Optional[tk.StringVar] = tk.StringVar(value="")
        self.AST_scan_1_pos_dist: Optional[tk.StringVar] = tk.StringVar(value="")
        self.AST_scan_2_pos_dist: Optional[tk.StringVar] = tk.StringVar(value="")

        self.AST_current_CMDR = ""
        # last Commander
        self.AST_last_CMDR: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str("AST_last_CMDR")))

        self.AST_scan_1_dist_green = False
        self.AST_scan_2_dist_green = False

        # Artemis Scanner State infos
        self.AST_last_scan_plant: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_last_scan_system: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_last_scan_body: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_current_scan_progress: Optional[tk.StringVar] = tk.StringVar(value=())
        self.AST_current_system: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_current_body: Optional[tk.StringVar] = tk.StringVar(value=str())
        self.AST_state: Optional[tk.StringVar] = tk.StringVar(value=str())

        self.AST_bios_on_planet = None
        self.AST_num_bios_on_planet = 0

        self.rawvalue = int(config.get_int("AST_value"))

        if self.rawvalue is None:
            self.rawvalue = 0

        self.AST_value: Optional[tk.StringVar] = tk.StringVar(value=((f"{self.rawvalue:,} Cr.")))

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
        on_load is called by plugin_start3 in load.py.

        It is the first point EDMC interacts with our code
        after loading our module.

        :return: The name of the plugin, which will be used by EDMC for logging
                 and for the settings window
        """
        return self.PLUGIN_NAME

    def on_unload(self) -> None:
        """
        on_unload is called by plugin_stop in load.py.

        It is the last thing called before EDMC shuts down.
        Note that blocking code here will hold the shutdown process.
        """
        self.on_preferences_closed("", False)  # Save our prefs

    def setup_preferences(self, parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
        """
        setup_preferences is called by plugin_prefs in load.py.

        It is where we can setup our
        own settings page in EDMC's settings window.
        Our tab is defined for us.

        :param parent: the tkinter parent that our returned Frame will want to inherit from
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :return: The frame to add to the settings window
        """
        self.AST_current_CMDR = cmdr
        if self.AST_current_CMDR != "" and self.AST_current_CMDR is not None:
            saving.load_cmdr(cmdr, self)

        line = "_____________________________________________________"

        current_row = 0
        frame = nb.Frame(parent)

        ui.prefs_label(frame, f"Artemis Scanner Tracker {self.AST_VERSION} by Balvald", current_row, 0, tk.W)

        current_row += 1

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        checkboxlistleft = ["Hide full status", "Hide species",
                            "Hide system of last Scan", "Hide current system",
                            "Hide scanned/sold species in system", line,
                            "Autom. hide values after selling all", "Autom. hide unsold value when 0 Cr."]
        checkboxlistright = ["Hide value of unsold Scans", "Hide scan progress",
                             "Hide body of last Scan", "Hide current Body",
                             "Hide clonal colonial distances", line,
                             "Autom. hide values after finished scan", "Force hide/show autom. hidden"]

        variablelistleft = [self.AST_hide_fullscan, self.AST_hide_species,
                            self.AST_hide_last_system, self.AST_hide_system,
                            self.AST_hide_sold_bio, line, self.AST_hide_after_selling,
                            self.AST_hide_value_when_zero]
        variablelistright = [self.AST_hide_value, self.AST_hide_progress,
                             self.AST_hide_last_body, self.AST_hide_body,
                             self.AST_hide_CCR, line,
                             self.AST_hide_after_full_scan]

        for i in range(max(len(checkboxlistleft), len(checkboxlistright))):
            if i < len(checkboxlistleft):
                if checkboxlistleft[i] == line:
                    ui.prefs_label(frame, line, current_row, 0, tk.W)
                else:
                    ui.prefs_tickbutton(frame, checkboxlistleft[i], variablelistleft[i], current_row, 0, tk.W)
            if i < len(checkboxlistright):
                if checkboxlistright[i] == line:
                    ui.prefs_label(frame, line, current_row, 1, tk.W)
                    current_row += 1
                    continue
                if checkboxlistright[i] == "Force hide/show autom. hidden":
                    ui.prefs_button(frame, checkboxlistright[i], self.forcehideshow, current_row, 1, tk.W)
                    current_row += 1
                    continue
                ui.prefs_tickbutton(frame, checkboxlistright[i], variablelistright[i], current_row, 1, tk.W)
            current_row += 1

        """        if self.AST_debug.get():

            debuglistleft = ["species", "System of last Scan",
                             "Body of last Scan", "Scan progress",
                             "Scanned Value"]
            debuglistright = [self.AST_last_scan_plant, self.AST_last_scan_system,
                              self.AST_last_scan_body, self.AST_current_scan_progress,
                              self.AST_value]

            for i in range(max(len(debuglistleft), len(debuglistright))):
                if i < len(debuglistleft):
                    ui.prefs_label(frame, debuglistleft[i], current_row, 0, tk.W)
                if i < len(debuglistright):
                    ui.prefs_entry(frame, debuglistright[i], current_row, 1, tk.W)
                current_row += 1"""

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        ui.prefs_tickbutton(frame, "Shorten credit values", self.AST_shorten_value, current_row, 0, tk.W)

        current_row += 1

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        text = "Scan game journals for exobiology"
        ui.prefs_button(frame, text, self.buildsoldbiodatajson, current_row, 0, tk.W)
        text = "Scan local journal folder for exobiology"
        ui.prefs_button(frame, text, self.buildsoldbiodatajsonlocal, current_row, 1, tk.W)

        current_row += 1

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        text = "To reset the status, body, system and species"
        ui.prefs_label(frame, text, current_row, 0, tk.W)

        current_row += 1

        text = "of the last scan press the button below"
        ui.prefs_label(frame, text, current_row, 0, tk.W)

        current_row += 1

        ui.prefs_button(frame, "RESET", self.reset, current_row, 0, tk.W)

        current_row += 1

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        ui.prefs_tickbutton(frame, "Debug Mode", self.AST_debug, current_row, 0, tk.W)

        return frame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed in load.py.

        It is called when the preferences dialog is dismissed by the user.

        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """

        if self.AST_current_CMDR != "" and self.AST_current_CMDR is not None:
            saving.save_cmdr(self.AST_current_CMDR, self)
        if self.AST_current_CMDR != cmdr and cmdr != "" and cmdr is not None:
            self.AST_current_CMDR = cmdr
            saving.load_cmdr(self.AST_current_CMDR, self)

        # Update last scan plant for switch of the shortening value option
        self.update_last_scan_plant(None)

        if self.AST_shorten_value.get():
            self.AST_value.set(self.shortcreditstring(self.rawvalue))
        else:
            self.AST_value.set(f"{self.rawvalue:,} Cr.")

        worth = self.AST_last_scan_plant.get().split(" (")[1]
        self.AST_state.set(str(self.AST_last_scan_plant.get().split(" (")[0]) + " (" +
                           self.AST_current_scan_progress.get() + ") on: " +
                           self.AST_last_scan_body.get() + " (" + str(worth))

        config.set("AST_debug", int(self.AST_debug.get()))

        config.set("AST_value", int(self.rawvalue))

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
        config.set("AST_hide_after_selling", int(self.AST_hide_after_selling.get()))
        config.set("AST_hide_after_full_scan", int(self.AST_hide_after_full_scan.get()))
        config.set("AST_hide_value_when_zero", int(self.AST_hide_value_when_zero.get()))

        config.set("AST_shorten_value", int(self.AST_shorten_value.get()))

        config.set("AST_after_selling", int(self.AST_after_selling.get()))

        config.set("AST_hide_scans_in_system", int(self.AST_hide_scans_in_system.get()))

        if self.AST_debug.get():
            logger.debug(f"Currently last Commander is: {cmdr}")

        config.set("AST_last_CMDR", str(cmdr))

        if self.AST_debug.get():
            logger.debug("ArtemisScannerTracker saved preferences")

        ui.rebuild_ui(self, cmdr)

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.

        This is called by plugin_app in load.py.

        :param parent: EDMC main window Tk
        :return: Our frame
        """

        try:
            saving.load_cmdr(self.AST_last_CMDR.get(), self)
        except KeyError:
            # last Commander saved is just not known
            pass

        self.frame = tk.Frame(parent)

        ui.rebuild_ui(self, self.AST_current_CMDR)

        return self.frame

    def reset(self) -> None:
        """Reset function of the Reset Button."""
        self.AST_current_scan_progress.set("0/3")
        self.AST_last_scan_system.set("")
        self.AST_last_scan_body.set("")
        self.AST_last_scan_plant.set("None")
        self.AST_state.set("None")
        self.rawvalue = 0
        self.AST_value.set("0 Cr.")
        self.AST_scan_1_pos_vector = [None, None]
        self.AST_scan_2_pos_vector = [None, None]

    def clipboard(self) -> None:
        """Copy value to clipboard."""
        dummytk = tk.Tk()  # creates a window we don't want
        dummytk.clipboard_clear()
        dummytk.clipboard_append(self.rawvalue)
        dummytk.destroy()  # destroying it again we don't need another full window everytime we copy to clipboard.

    def forcehideshow(self) -> None:
        """Force plugin to show values when Auto hide is on."""
        state = self.AST_after_selling.get()
        self.AST_after_selling.set(int(not (state)))
        ui.rebuild_ui(self, self.AST_current_CMDR)

    def switchhidesoldexobio(self) -> None:
        """Switch the ui button to expand and collapse the list of sold/scanned exobiology."""
        state = self.AST_hide_scans_in_system.get()
        self.AST_hide_scans_in_system.set(int(not (state)))
        ui.rebuild_ui(self, self.AST_current_CMDR)

    def buildsoldbiodatajsonlocal(self) -> None:
        """Build the soldbiodata.json using the neighboring journalcrawler.py searching through local journal folder."""
        global logger
        directory, filename = os.path.split(os.path.realpath(__file__))

        self.rawvalue = build_biodata_json(logger, os.path.join(directory, "journals"))[self.AST_current_CMDR]

    def buildsoldbiodatajson(self) -> None:
        """Build the soldbiodata.json using the neighboring journalcrawler.py."""
        # Always uses the game journal directory

        global logger

        # this the actual path from the config.
        journaldir = config.get_str('journaldir')

        if journaldir in [None, "", "None"]:
            # config.default_journal_dir is a fallback that won't work in a linux context
            journaldir = config.default_journal_dir

        self.rawvalue = build_biodata_json(logger, journaldir)[self.AST_current_CMDR]

    def ask_canonn_nicely(self, system: str):
        """Ask Canonn how many biological signals are on any planets"""
        if self.AST_debug.get():
            logger.debug(f"Asking Canonn for Info about: {system}")
        response = requests.get(
            f"https://us-central1-canonn-api-236217.cloudfunctions.net/query/getSystemPoi?system={system}")
        data = response.json()
        if self.AST_debug.get():
            logger.debug(f"Retrieved data: {data}")
        dict_of_biological_counts = {}
        try:
            for body in data["SAAsignals"]:
                if body["hud_category"] != "Biology":
                    continue
                dict_of_biological_counts[body["body"]] = body["count"]
        except KeyError:
            # If there are no SAAsignals to search through
            pass
        return dict_of_biological_counts

    def shortcreditstring(self, number):
        """Create string given given number of credits with SI symbol prefix and money unit e.g. KCr. MCr. GCr. TCr."""
        if number is None:
            return "N/A"
        prefix = ["", "K", "M", "G", "T", "P", "E", "Z", "Y", "R", "Q"]
        fullstring = f"{number:,}"
        prefixindex = fullstring.count(",")
        if prefixindex <= 0:
            # no unit prefix -> write the already short number
            return fullstring + " Cr."
        if prefixindex >= len(prefix):
            # Game probably won't be able to handle it if someone sold this at once.
            return "SELL ALREADY! WE RAN OUT OF SI PREFIXES (╯°□°）╯︵ ┻━┻"
        unit = " " + prefix[prefixindex] + "Cr."
        index = fullstring.find(",") + 1
        fullstring = fullstring[:index].replace(",", ".")+fullstring[index:].replace(",", "")
        fullstring = f"{round(float(fullstring), (4-index+1)):.6f}"[:5]
        if fullstring[1] == ".":
            fullstring = fullstring[0] + "," + fullstring[2:]
            unit = " " + prefix[prefixindex-1] + "Cr."
        return fullstring + unit

    def update_last_scan_plant(self, entry):
        """."""
        plantname = str(self.AST_last_scan_plant.get().split(" (Worth: ")[0])
        if entry is not None:
            plantname = orgi.generaltolocalised(entry["Species"].lower())
        try:
            plantworth = orgi.vistagenomicsprices[plantname]
            worthstring = f"{plantworth:,} Cr."
        except KeyError:
            plantworth = None
            worthstring = "N/A"
        if self.AST_shorten_value.get():
            worthstring = self.shortcreditstring(plantworth)
        self.AST_last_scan_plant.set(plantname + " (Worth: " + worthstring + ")")
        return plantname, plantworth

    def handle_possible_cmdr_change(self, cmdr: str):
        if self.AST_current_CMDR != cmdr and self.AST_current_CMDR != "" and self.AST_current_CMDR is not None:
            # Check if new and old Commander are in the cmdrstates file.
            saving.save_cmdr(self.AST_current_CMDR, self)
            # New Commander not in cmdr states file.
            if cmdr not in self.CMDR_states.keys():
                # completely new cmdr theres nothing to load
                self.CMDR_states[cmdr] = ["None", "None", "None", "0/3", "None", 0, "None", "None", "None"]
            else:
                # Load cmdr from cmdr states.
                if cmdr is not None and cmdr != "":
                    saving.load_cmdr(cmdr, self)
            # Set new Commander to current CMDR
            self.AST_current_CMDR = cmdr

            return True

        return False
