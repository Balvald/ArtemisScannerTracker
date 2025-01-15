"""Artemis Scanner Tracker Class"""

import logging
import os
import requests
import threading
import tkinter as tk
from typing import Optional
# Own modules
import saving
import ui
import organicinfo as orgi
from journalcrawler import build_biodata_json

# try to import config and notebook, if it fails we are in testmode
try:
    testmode = False
    import myNotebook as nb  # type: ignore
    from config import appname, config  # type: ignore
except ImportError:
    import tkinter.ttk as nb  # type: ignore

    class config_replacement():
        def __init__(self) -> None:
            self.storage = {"AST_debug": "0",
                            "AST_hide_fullscan": "0",
                            "AST_hide_species": "0",
                            "AST_hide_progress": "0",
                            "AST_hide_last_system": "0",
                            "AST_hide_last_body": "0",
                            "AST_hide_system": "0",
                            "AST_hide_body": "0",
                            "AST_hide_value": "0",
                            "AST_hide_sold_bio": "0",
                            "AST_hide_CCR": "0",
                            "AST_hide_after_selling": "0",
                            "AST_hide_after_full_scan": "0",
                            "AST_hide_value_when_zero": "0",
                            "AST_hide_CODEX_button": "0",
                            "AST_shorten_value": "0",
                            "AST_after_selling": "0",
                            "AST_hide_scans_in_system": "0",
                            "AST_last_CMDR": "Jameson",
                            "AST_value": "0"}

        def get_int(self, key: str) -> int:
            return int(self.storage[key])

        def get_str(self, key: str) -> str:
            return str(self.storage[key])

        def set(self, key: str, value: any) -> None:
            self.storage[key] = value

    config = config_replacement()

    testmode = True

if not testmode:
    logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")
else:
    logger = logging.getLogger(f"{os.path.basename(os.path.dirname(__file__))}")


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
        self.AST_hide_CODEX_button: Optional[tk.IntVar] = tk.IntVar(value=config.get_int("AST_hide_CODEX_button"))

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

        self.AST_bios_on_planet = {}
        self.AST_num_bios_on_planet = 0

        self.rawvalue = int(config.get_int("AST_value"))

        if self.rawvalue is None:
            self.rawvalue = 0

        self.AST_value: Optional[tk.StringVar] = tk.StringVar(value=((f"{self.rawvalue:,} Cr.")))

        self.updateavailable = False

        self.thread = None
        self.codexthread = None
        self.newwindowrequested = False
        self.searchthread = None

        if not testmode:
            response = requests.get(f"https://api.github.com/repos/{AST_REPO}/releases/latest", timeout=20)

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
        self.newwindowrequested = True
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
                            "Hide scanned/sold species in system", "Hide AST Codex Button", line,
                            "Autom. hide values after selling all", "Autom. hide unsold value when 0 Cr."]
        checkboxlistright = ["Hide value of unsold Scans", "Hide scan progress",
                             "Hide body of last Scan", "Hide current Body",
                             "Hide clonal colonial distances", "Empty", line,
                             "Autom. hide values after finished scan", "Force hide/show autom. hidden"]

        variablelistleft = [self.AST_hide_fullscan, self.AST_hide_species,
                            self.AST_hide_last_system, self.AST_hide_system,
                            self.AST_hide_sold_bio, self.AST_hide_CODEX_button, line, self.AST_hide_after_selling,
                            self.AST_hide_value_when_zero]
        variablelistright = [self.AST_hide_value, self.AST_hide_progress,
                             self.AST_hide_last_body, self.AST_hide_body,
                             self.AST_hide_CCR, line, line,
                             self.AST_hide_after_full_scan]

        for i in range(max(len(checkboxlistleft), len(checkboxlistright))):
            if i < len(checkboxlistleft):
                if checkboxlistleft[i] == line:
                    ui.prefs_label(frame, line, current_row, 0, tk.W)
                elif checkboxlistleft[i] == "Empty":
                    pass
                else:
                    ui.prefs_tickbutton(frame, checkboxlistleft[i], variablelistleft[i], current_row, 0, tk.W)
            if i < len(checkboxlistright):
                if checkboxlistright[i] == line:
                    ui.prefs_label(frame, line, current_row, 1, tk.W)
                    current_row += 1
                elif checkboxlistright[i] == "Empty":
                    pass
                elif checkboxlistright[i] == "Force hide/show autom. hidden":
                    ui.prefs_button(frame, checkboxlistright[i], self.forcehideshow, current_row, 1, tk.W)
                    current_row += 1
                else:
                    ui.prefs_tickbutton(frame, checkboxlistright[i], variablelistright[i], current_row, 1, tk.W)
            current_row += 1

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        ui.prefs_tickbutton(frame, "Shorten credit values", self.AST_shorten_value, current_row, 0, tk.W)

        current_row += 1

        ui.prefs_label(frame, line, current_row, 0, tk.W)
        ui.prefs_label(frame, line, current_row, 1, tk.W)

        current_row += 1

        text = "Scan game journals for exobiology"
        ui.prefs_button(frame, text, self.buildsoldbiodatajsonworker, current_row, 0, tk.W)
        text = "Scan local journal folder for exobiology"
        ui.prefs_button(frame, text, self.buildsoldbiodatajsonlocalworker, current_row, 1, tk.W)

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
            self.AST_value.set(ui.shortcreditstring(self.rawvalue))
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
        config.set("AST_hide_CODEX_button", int(self.AST_hide_CODEX_button.get()))

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

    def buildsoldbiodatajsonlocalworker(self) -> None:
        self.thread = threading.Thread(target=self.buildsoldbiodatajsonlocal, name="buildsoldbiodatajsonlocal")
        self.thread.start()
        # self.thread.join()
        # self.thread = None
        pass

    def buildsoldbiodatajsonlocal(self) -> None:
        """Build the soldbiodata.json using the neighboring journalcrawler.py searching through local journal folder."""
        global logger
        directory, filename = os.path.split(os.path.realpath(__file__))

        self.rawvalue = build_biodata_json(logger, os.path.join(directory, "journals"))[self.AST_current_CMDR]

    def buildsoldbiodatajsonworker(self) -> None:
        self.thread = threading.Thread(target=self.buildsoldbiodatajson, name="buildsoldbiodatajson")
        self.thread.start()
        # self.thread.join()
        # self.thread = None
        pass

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

    def update_last_scan_plant(self, entry) -> tuple[str, int]:
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
            worthstring = ui.shortcreditstring(plantworth)
        self.AST_last_scan_plant.set(plantname + " (Worth: " + worthstring + ")")
        return plantname, plantworth

    def handle_possible_cmdr_change(self, cmdr: str) -> bool:
        print(self.AST_current_CMDR)
        if self.AST_current_CMDR != cmdr and self.AST_current_CMDR != "" and self.AST_current_CMDR is not None:  # cmdr != ""
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

    def show_codex_window_worker(self) -> None:
        logger.warning("show_codex_window_worker")
        # check if the thread is already running
        if self.codexthread is not None:
            if self.codexthread.is_alive():
                # logger.warning("show_codex_window_worker: thread is already running")
                # force close the thread
                self.newwindowrequested = True
                self.codexthread.join()
                self.newwindowrequested = False
                ui.set_data_init(False)

                # logger.warning("show_codex_window_worker: thread is already running: joined")
        self.codexthread = threading.Thread(target=self.show_codex_window_thread, name="show_codex_window")
        self.codexthread.start()
        # ui.show_codex_window(self, self.AST_current_CMDR)
        # ui.rebuild_ui(self, self.AST_current_CMDR)

    def show_codex_window_thread(self) -> None:
        ui.show_codex_window(self, self.AST_current_CMDR)
        # ui.rebuild_ui(self, self.AST_current_CMDR)

    def debug_config(self) -> any:
        """Return the current configuration only used for testing purposes where we return an instance of config_replacement."""
        return config
