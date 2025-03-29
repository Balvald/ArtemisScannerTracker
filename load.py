"""Artemis Scanner Tracker v0.3.2 by Balvald."""

import json
import logging
import os
import tkinter as tk
from typing import Optional

import eventhandling
import organicinfo as orgi
import ui

# Own Modules
from AST import ArtemisScannerTracker

# EDMC specific imports
try:
    import myNotebook as nb  # type: ignore  # noqa: N813
    from config import appname  # type: ignore

    testmode = False
except ImportError:
    import tkinter.ttk as nb  # type: ignore

    testmode = True

frame: Optional[tk.Frame] = None

# Shows debug fields in preferences when True

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

PLUGIN_NAME = "AST"

AST_VERSION = "v0.3.3"

AST_REPO = "Balvald/ArtemisScannerTracker"

firstdashboard = True
firstsystemevent = True

not_yet_sold_data = {}
sold_exobiology = {}
currententrytowrite = {}
cmdrstates = {}

plugin = None

# Gonna need the files directory to store data for full
# tracking of all the biological things that the CMDR scans.
directory, filename = os.path.split(os.path.realpath(__file__))

filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]

if not testmode:
    for file in filenames:
        if not os.path.exists(directory + file):
            f = open(directory + file, "w", encoding="utf8")
            f.write(r"{}")
            f.close()
        elif file == "/soldbiodata.json" or file == "/notsoldbiodata.json":
            # (not)soldbiodata file already exists
            with open(directory + file, "r+", encoding="utf8") as f:
                test = json.load(f)
                if type([]) == type(test):  # noqa: E721
                    # we have an old version of the (not)soldbiodata.json
                    # clear it, have the user do the journal crawling again.
                    logger.warning(f"Found old {file} format")
                    logger.warning("Clearing file...")
                    f.seek(0)
                    f.write(r"{}")
                    f.truncate()


# load notyetsolddata and cmdrstates

with open(directory + "/notsoldbiodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_data = json.load(f)

with open(directory + "/cmdrstates.json", "r+", encoding="utf8") as f:
    cmdrstates = json.load(f)


# region eventhandling

def dashboard_entry(cmdr: str, is_beta, entry) -> None:  # noqa: CCR001
    """
    React to changes in the CMDRs status (Movement for CCR feature).

    :param cmdr: The current ED Commander
    :param is_beta: Is the game currently in beta
    :param entry: full excerpt from status.json
    """
    # TODO: Move most of this into AST.py class

    global plugin, firstdashboard

    if plugin.AST_debug.get():
        logger.debug("Called Dashboard ...")

    if plugin.AST_in_Legacy is True:
        # We're in legacy we don't update anything through dashboard entries
        return

    # flag determines if we have to rebuild the ui at the end.
    flag = plugin.handle_possible_cmdr_change(cmdr)

    if firstdashboard:
        firstdashboard = False
        plugin.on_preferences_closed(cmdr, is_beta)
        if plugin.AST_debug.get():
            logger.debug("Prepared for First Dashboard")

    if "PlanetRadius" in entry.keys():
        currentbody = plugin.AST_current_body.get()
        # flag = True
        # We found a PlanetRadius again, this means we are near a planet.
        if plugin.AST_debug.get():
            logger.debug("On planet")
        if currentbody != entry["BodyName"]:
            # Body we are currently at isn't the one we currently assume
            currentbody = entry["BodyName"]
            plugin.AST_current_body.set(entry["BodyName"])
            flag = True

        if not plugin.AST_near_planet:
            # We just came into range of a planet again.
            if plugin.AST_debug.get():
                logger.debug(f"just realized we approach a planet, nearplanet: {plugin.AST_near_planet}")
            flag = True
        if currentbody not in ["", None, "None"]:
            if plugin.AST_debug.get():
                logger.debug(plugin.AST_bios_on_planet)
            try:
                plugin.AST_num_bios_on_planet = plugin.AST_bios_on_planet[currentbody]
            except (KeyError, TypeError):
                # Nothing found at currently closest planet
                if plugin.AST_debug.get():
                    logger.warning(f"No amount of bio signals found for body; {currentbody} with key: {currentbody}")

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
        text = "lat: " + str(round(plugin.AST_current_pos_vector[0], 2)) + \
               ", long: " + str(round(plugin.AST_current_pos_vector[1], 2)) + ", B:" + \
               str(plugin.AST_current_pos_vector[2])  # + ", " + str(plugin.AST_current_radius)
        plugin.AST_current_pos.set(text)

        if plugin.AST_current_scan_progress.get() in ["1/3", "2/3"] and plugin.AST_scan_1_pos_vector[0] is not None:
            distance1 = orgi.computedistance(plugin.AST_current_pos_vector[0],
                                             plugin.AST_current_pos_vector[1],
                                             plugin.AST_scan_1_pos_vector[0],
                                             plugin.AST_scan_1_pos_vector[1],
                                             plugin.AST_current_radius)
            plugin.AST_scan_1_pos_dist.set(str(round(distance1))
                                           + " m / " + str(plugin.AST_CCR.get()) + " m, B:" +
                                           str(round(orgi.bearing(plugin.AST_current_pos_vector[0],
                                                                  plugin.AST_current_pos_vector[1],
                                                                  plugin.AST_scan_1_pos_vector[0],
                                                                  plugin.AST_scan_1_pos_vector[1]), 2)))
            olddist1check = plugin.AST_scan_1_dist_green
            plugin.AST_scan_1_dist_green = False
            if plugin.AST_CCR.get() < distance1:
                plugin.AST_scan_1_dist_green = True
            if olddist1check != plugin.AST_scan_1_dist_green:
                flag = True
        if plugin.AST_current_scan_progress.get() in ["1/3", "2/3"] and plugin.AST_scan_2_pos_vector[0] is not None:
            distance2 = orgi.computedistance(plugin.AST_current_pos_vector[0],
                                             plugin.AST_current_pos_vector[1],
                                             plugin.AST_scan_2_pos_vector[0],
                                             plugin.AST_scan_2_pos_vector[1],
                                             plugin.AST_current_radius)
            plugin.AST_scan_2_pos_dist.set(str(round(distance2, 2))
                                           + " m / " + str(plugin.AST_CCR.get()) + " m, B:" +
                                           str(round(orgi.bearing(plugin.AST_current_pos_vector[0],
                                                                  plugin.AST_current_pos_vector[1],
                                                                  plugin.AST_scan_2_pos_vector[0],
                                                                  plugin.AST_scan_2_pos_vector[1]), 2)))
            olddist2check = plugin.AST_scan_2_dist_green
            plugin.AST_scan_2_dist_green = False
            if plugin.AST_CCR.get() < distance2:
                plugin.AST_scan_2_dist_green = True
            if olddist2check != plugin.AST_scan_2_dist_green:
                flag = True
    else:
        if plugin.AST_near_planet:
            # Switch happened, we went too far from the planet to get any reference from it.
            flag = True
            if plugin.AST_debug.get():
                logger.debug(f"just realized we approach a planet, nearplanet: {plugin.AST_near_planet}")
        plugin.AST_num_bios_on_planet = 0
        plugin.AST_near_planet = False
        plugin.AST_current_radius = None
        plugin.AST_current_pos_vector[0] = None
        plugin.AST_current_pos_vector[1] = None
        plugin.AST_current_pos_vector[2] = None
        plugin.AST_current_pos.set("No reference point")

    if plugin.AST_debug.get():
        logger.debug(f"nearplanet is now: {plugin.AST_near_planet}, will rebuild UI: {flag}")

    if (((plugin.AST_last_scan_body.get() == "")
         or (plugin.AST_last_scan_body.get() == "None"))):
        plugin.AST_last_scan_body.set(currentbody)

    if flag:
        if not plugin.AST_near_planet:
            plugin.AST_current_body.set("")
        plugin.on_preferences_closed(cmdr, is_beta)
        # ui.rebuild_ui(plugin, cmdr) is already done in on_preferences_closed


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry, state) -> None:  # noqa: CCR001
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
    global plugin, firstsystemevent

    if plugin.AST_debug.get():
        logger.debug(entry)
        logger.debug(f"Current event is {entry['event']}")
        logger.debug(f"Current state Gameversion {state['GameVersion']}")
        logger.debug(f"State of AST_in_Legacy variable: {plugin.AST_in_Legacy}")

    if ((int(state["GameVersion"][0]) < 4) and (plugin.AST_in_Legacy is False)):
        # We're in Legacy, we'll not change the state of anything through journal entries.
        plugin.AST_in_Legacy = True
        return
    else:
        plugin.AST_in_Legacy = False

    if plugin.AST_debug.get():
        logger.debug("Got past Version check")

    # flag determines if we have to rebuild the ui at the end.
    flag = plugin.handle_possible_cmdr_change(cmdr)
    if plugin.AST_debug.get():
        logger.debug("Handled possible CMDR change")

    # TODO: Check if upon death in 4.0 Horizons do we lose Exobiodata.
    # Probably?

    # Dying while in Frontline solutions CZ does not have a Resurrect event.
    # Also doesn't lose the Exobiology data.

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        flag = True
        plugin.notyetsolddata[cmdr] = eventhandling.resurrection_event(plugin)

    if entry["event"] == "ScanOrganic":
        if plugin.AST_debug.get():
            logger.debug("Encountered Scan Organic Event")
        flag = True
        if plugin.AST_debug.get():
            logger.debug("Calling eventhandler")
        eventhandling.bioscan_event(cmdr, is_beta, entry, plugin, currententrytowrite)
        if plugin.AST_debug.get():
            logger.debug("Finished handling ScanOrganic Event")

    if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
        flag = True
        eventhandling.system_body_change_event(cmdr, entry, plugin)

    if entry["event"] == "SellOrganicData":
        flag = True
        eventhandling.biosell_event(cmdr, entry, plugin)

    if entry["event"] == "SAASignalsFound":
        if plugin.AST_debug.get():
            logger.debug(entry)
        eventhandling.SAASignalsFound_event(entry, plugin)
        flag = True

    if flag:
        # save most recent relevant state so in case of crash of the system
        # we still have a proper record as long as it finishes saving below.
        plugin.on_preferences_closed(cmdr, is_beta)


# endregion


plugin = ArtemisScannerTracker(AST_VERSION, AST_REPO, PLUGIN_NAME,
                               directory, cmdrstates,
                               not_yet_sold_data, sold_exobiology)


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
    ui.rebuild_ui(plugin, cmdr)

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
