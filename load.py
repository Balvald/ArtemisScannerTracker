"""
Artemis Scanner Tracker by Balvald
created from the EDMC example plugin.
"""

import logging
from pickle import FALSE
import tkinter as tk
from typing import Optional

import myNotebook as nb  # noqa: N813
from config import appname, config

# This **MUST** match the name of the folder the plugin is in.
PLUGIN_NAME = "ArtemisScannerTracker"

# Shows debug fields in preferences when True
debug = False

logger = logging.getLogger(f"{appname}.{PLUGIN_NAME}")

class ArtemisScannerTracker:

    def __init__(self) -> None:
        # Be sure to use names that wont collide in our config variables
        self.AST_last_scan_plant: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('AST_last_scan_plant')))
        self.AST_last_scan_system: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('AST_last_scan_system')))
        self.AST_last_scan_body: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('AST_last_scan_body')))
        self.AST_current_scan_progress: Optional[tk.StringVar] = tk.StringVar(value=(str(config.get_int('AST_current_scan_progress')) + str("/3")))
        self.AST_current_system: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('AST_current_system')))
        self.AST_current_body: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('AST_current_body')))
        self.AST_state: Optional[tk.StringVar] = tk.StringVar(value=str(config.get_str('AST_state')))
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

        # TODO create useful preferences for the plugin: i.e. tick boxes to show or hide certain info like current system and body and a Reset state button.
        # and remove the debug fields, where the user could just put anything in.

        if debug:
            # setup debug fields for the scanner.
            nb.Label(frame, text='Species').grid(row=current_row)
            nb.Entry(frame, textvariable=self.AST_last_scan_plant).grid(row=current_row, column=1)
            current_row += 1  # Always increment our row counter, makes for far easier tkinter design.
            
            nb.Label(frame, text='System of last Scan').grid(row=current_row)
            nb.Entry(frame, textvariable=self.AST_last_scan_system).grid(row=current_row, column=1)
            current_row += 1
            
            nb.Label(frame, text='Body of last Scan').grid(row=current_row)
            nb.Entry(frame, textvariable=self.AST_last_scan_body).grid(row=current_row, column=1)
            current_row += 1

            nb.Label(frame, text='Scan progress').grid(row=current_row)
            nb.Entry(frame, textvariable=self.AST_current_scan_progress).grid(row=current_row, column=1)
            current_row += 1

        return frame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.
        It is called when the preferences dialog is dismissed by the user.
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        config.set('AST_current_scan_progress', int(self.AST_current_scan_progress.get()[0]))
        config.set('AST_last_scan_system', str(self.AST_last_scan_system.get()))
        config.set('AST_last_scan_body', str(self.AST_last_scan_body.get()))
        config.set('AST_last_scan_plant', str(self.AST_last_scan_plant.get()))
        config.set('AST_state', str(self.AST_state.get()))
        logger.info("ArtemisScannerTracker saved")

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:
        """
        Create our entry on the main EDMC UI.
        This is called by plugin_app below.
        :param parent: EDMC main window Tk
        :return: Our frame
        """
        current_row = 12
        frame = tk.Frame(parent)
        """
        old buttons
        button = tk.Button(
            frame,
            text="Increment",
            command=lambda: self.AST_current_scan_progress.set(str((int(self.AST_current_scan_progress.get()[0]) + 1) % 4) + str("/3"))
        )
        resetbutton = tk.Button(
            frame,
            text="Reset",
            command=lambda: self.AST_current_scan_progress.set(str("0/3"))
        )
        #button.grid(row=current_row) # commented out -> no button to be shown
        current_row -= 1
        #resetbutton.grid(row=current_row)
        current_row -= 1
        """
        tk.Label(frame, text="Current Body:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_current_body).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Current System:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_current_system).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Body of last Scan:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_last_scan_body).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="System of last Scan:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_last_scan_system).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Scan Progress:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_current_scan_progress).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Species:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_last_scan_plant).grid(row=current_row, column=1)
        current_row -= 1
        tk.Label(frame, text="Last Exobioligy Scan:").grid(row=current_row)
        tk.Label(frame, textvariable=self.AST_state).grid(row=current_row, column=1)
        return frame
    
def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    react accordingly to ScanOrganic event
    :param cmdr: The current ED Commander
    :param is_beta: Whether or not EDMC is currently marked as in beta mode
    :param system: current system? unused
    :param station: unused
    :param entry: the current Journal entry
    :param state: unused
    """

    flag = False

    if entry["event"] == "ScanOrganic":
        flag = True
        plugin.AST_last_scan_plant.set(entry["Species_Localised"])
        # In the eventuality that the user started EMDC after the "Location" event happens and directly scans a plant
        # these lines wouldn't be able to do anything but to set the System and body of the last Scan to "None"
        plugin.AST_last_scan_system.set(plugin.AST_current_system.get())
        plugin.AST_last_scan_body.set(plugin.AST_current_body.get())
        if entry["ScanType"] == "Log":
            plugin.AST_current_scan_progress.set("1/3")
        elif entry["ScanType"] == "Sample":
            plugin.AST_current_scan_progress.set("2/3")
        elif entry["ScanType"] == "Analyse":
            plugin.AST_current_scan_progress.set("3/3")
        else:
            plugin.AST_current_scan_progress.set("Excuse me what the fuck") #Somethings horibly wrong if we end up here

    if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
        flag = True
        # Get current system name and body from events that needs to happen.
        plugin.AST_current_system.set(entry["StarSystem"])
        plugin.AST_current_body.set(entry["Body"])
        # To fix the aforementioned eventuality where the systems end up being "None" we update the last scan location
        # When the CMDR gets another journal entry that tells us the players location.
        if ((plugin.AST_last_scan_system.get() == "None") or (plugin.AST_last_scan_body.get() == "None")):
            plugin.AST_last_scan_system.set(entry["StarSystem"])
            plugin.AST_last_scan_body.set(entry["Body"])

    if flag:
        # we changed a value so we update line.
        plugin.AST_state.set(plugin.AST_last_scan_plant.get() + " (" + plugin.AST_current_scan_progress.get() + ") on: " + plugin.AST_last_scan_body.get())


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
