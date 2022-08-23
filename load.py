"""
Example EDMC plugin.
It adds a single button to the EDMC interface that displays the number of times it has been clicked.
"""

# TODO modify implementation to have a basic tracker for the current state of the Artemis' suit scanner.

import logging
import tkinter as tk
from typing import Optional

import myNotebook as nb  # noqa: N813
from config import appname, config

# This **MUST** match the name of the folder the plugin is in.
PLUGIN_NAME = "ArtemisScannerTracker"

logger = logging.getLogger(f"{appname}.{PLUGIN_NAME}")

class ArtemisScannerTracker:
    """
    First iteration is still the example Click counter plugin.

    Observation: the value that the plugin tracks is being saved and retrieved wenn closing and opening EDMC! that great yay C:

    ClickCounter implements the EDMC plugin interface.
    It adds a button to the EDMC UI that displays the number of times it has been clicked, and a preference to set
    the number directly.
    """

    def __init__(self) -> None:
        # Be sure to use names that wont collide in our config variables
        self.last_scan_plant: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('last_scan_plant')))
        self.last_scan_system: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('last_scan_system')))
        self.last_scan_body: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('last_scan_body')))
        self.current_scan_progress: Optional[tk.StringVar] = tk.StringVar(value=(str(config.get_int('current_scan_progress')) + str("/3")))
        self.current_system: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('current_system')))
        self.current_body: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('current_body')))
        logger.info("ArtemisScannerTracker instantiated")

    def on_load(self) -> str:
        """
        on_load is called by plugin_start3 below.
        It is the first point EDMC interacts with our code after loading our module.
        :return: The name of the plugin, which will be used by EDMC for logging and for the settings window
        """
        return PLUGIN_NAME

    def on_unload(self) -> None:
        """
        on_unload is called by plugin_stop below.
        It is the last thing called before EDMC shuts down. Note that blocking code here will hold the shutdown process.
        """
        self.on_preferences_closed("", False)  # Save our prefs

    def setup_preferences(self, parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
        """
        setup_preferences is called by plugin_prefs below.
        It is where we can setup our own settings page in EDMC's settings window. Our tab is defined for us.
        :param parent: the tkinter parent that our returned Frame will want to inherit from
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :return: The frame to add to the settings window
        """
        current_row = 0
        frame = nb.Frame(parent)

        # setup debug fields for the scanner.
        nb.Label(frame, text='Species').grid(row=current_row)
        nb.Entry(frame, textvariable=self.last_scan_plant).grid(row=current_row, column=1)
        current_row += 1  # Always increment our row counter, makes for far easier tkinter design.
        
        nb.Label(frame, text='System of last Scan').grid(row=current_row)
        nb.Entry(frame, textvariable=self.last_scan_system).grid(row=current_row, column=1)
        current_row += 1
        
        nb.Label(frame, text='Body of last Scan').grid(row=current_row)
        nb.Entry(frame, textvariable=self.last_scan_body).grid(row=current_row, column=1)
        current_row += 1

        nb.Label(frame, text='Scan progress').grid(row=current_row)
        nb.Entry(frame, textvariable=self.current_scan_progress).grid(row=current_row, column=1)
        current_row += 1

        return frame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.
        It is called when the preferences dialog is dismissed by the user.
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        # You need to cast to `int` here to store *as* an `int`, so that
        # `config.get_int()` will work for re-loading the value.
        config.set('current_scan_progress', int(self.current_scan_progress.get()[0])) # type: ignore
        config.set('last_scan_system', str(self.last_scan_system.get()))
        config.set('last_scan_body', str(self.last_scan_body.get()))
        config.set('last_scan_plant', str(self.last_scan_plant.get()))

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.
        This is called by plugin_app below.
        :param parent: EDMC main window Tk
        :return: Our frame
        """
        current_row = 12
        frame = tk.Frame(parent)
        button = tk.Button(
            frame,
            text="Increment",
            command=lambda: self.current_scan_progress.set(str((int(self.current_scan_progress.get()[0]) + 1) % 4) + str("/3"))  # type: ignore
        )
        resetbutton = tk.Button(
            frame,
            text="Reset",
            command=lambda: self.current_scan_progress.set(str("0/3"))
              # type: ignore
        )
        #button.grid(row=current_row) # commented out -> no button to be shown
        current_row -= 1
        #resetbutton.grid(row=current_row)
        current_row -= 1
        tk.Label(frame, text="Current Body:").grid(row=current_row)
        tk.Label(frame, textvariable=self.current_body).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Current System:").grid(row=current_row)
        tk.Label(frame, textvariable=self.current_system).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Body of last Scan:").grid(row=current_row)
        tk.Label(frame, textvariable=self.last_scan_body).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="System of last Scan:").grid(row=current_row)
        tk.Label(frame, textvariable=self.last_scan_system).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Scan Progress:").grid(row=current_row)
        tk.Label(frame, textvariable=self.current_scan_progress).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Species:").grid(row=current_row)
        tk.Label(frame, textvariable=self.last_scan_plant).grid(row=current_row, column=1)
        return frame

    def increment_scan_progress(self):
        self.current_scan_progress.set(str((int(self.current_scan_progress.get()[0]) + 1) % 4) + str("/3"))

    
def journal_entry(cmdr, is_beta, system, station, entry, state):
        """
        react accordingly to ScanOrganic event
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :param system: ?
        :param station: ?
        :param entry: the current Journal entry
        :param state: ?
        """
        if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
            # Get current system name and body from events that needs to happen.
            plugin.current_system.set(entry["StarSystem"])
            plugin.current_body.set(entry["Body"])
        
        if entry["event"] == "ScanOrganic":
            plugin.last_scan_plant.set(entry["Species_Localised"])
            plugin.last_scan_system.set(plugin.current_system.get())
            plugin.last_scan_body.set(plugin.current_body.get())
            if entry["ScanType"] == "Log":
                plugin.current_scan_progress.set("1/3")
            elif entry["ScanType"] == "Sample":
                plugin.current_scan_progress.set("2/3")
            elif entry["ScanType"] == "Analyse":
                plugin.current_scan_progress.set("3/3")
            else:
                plugin.current_scan_progress.set("Excuse me what the fuck") #Somethings horibly wrong if we end up here


plugin = ArtemisScannerTracker()


def plugin_start3(plugin_dir: str) -> str:
    """
    Handle start up of the plugin.
    See PLUGINS.md#startup
    """
    return plugin.on_load()


def plugin_stop() -> None:
    """
    Handle shutdown of the plugin.
    See PLUGINS.md#shutdown
    """
    return plugin.on_unload()


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    """
    Handle preferences tab for the plugin.
    See PLUGINS.md#configuration
    """
    return plugin.setup_preferences(parent, cmdr, is_beta)


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Handle any changed preferences for the plugin.
    See PLUGINS.md#configuration
    """
    return plugin.on_preferences_closed(cmdr, is_beta)


def plugin_app(parent: tk.Frame) -> Optional[tk.Frame]:
    """
    Set up the UI of the plugin.
    See PLUGINS.md#display
    """
    return plugin.setup_main_ui(parent)
