"""Artemis Scanner Tracker v0.2.7 dev by Balvald."""

import json
import logging
import os
import tkinter as tk
from typing import Optional

import myNotebook as nb  # type: ignore
from config import appname  # type: ignore

import eventhandling
import ui
import organicinfo as orgi
from AST import ArtemisScannerTracker

frame: Optional[tk.Frame] = None

# Shows debug fields in preferences when True
debug = False

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")

PLUGIN_NAME = "AST"

AST_VERSION = "v0.2.7 dev"

AST_REPO = "Balvald/ArtemisScannerTracker"

firstdashboard = True

not_yet_sold_data = {}
sold_exobiology = {}
currententrytowrite = {}
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


# region eventhandling

def dashboard_entry(cmdr: str, is_beta, entry) -> None:
    """
    React to changes in the CMDRs status (Movement for CCR feature).

    :param cmdr: The current ED Commander
    :param is_beta: Is the game currently in beta
    :param entry: full excerpt from status.json
    """
    global plugin, firstdashboard

    if plugin.AST_in_Legacy is True:
        # We're in legacy we don't update anything through dashboard entries
        return

    flag = plugin.handle_possible_cmdr_change(cmdr)

    if firstdashboard:
        firstdashboard = False
        plugin.on_preferences_closed(cmdr, is_beta)

    if "PlanetRadius" in entry.keys():
        currentbody = plugin.AST_current_body.get()
        # We found a PlanetRadius again, this means we are near a planet.
        if not plugin.AST_near_planet:
            # We just came into range of a planet again.
            flag = True
        if currentbody not in ["", None, "None"]:
            if plugin.debug:
                logger.debug(plugin.AST_bios_on_planet)
            plugin.AST_num_bios_on_planet = plugin.AST_bios_on_planet[
                currentbody.replace(plugin.AST_current_system.get(), "")[1:]]
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
        plugin.AST_num_bios_on_planet = 0
        plugin.AST_near_planet = False
        plugin.AST_current_radius = None
        plugin.AST_current_pos_vector[0] = None
        plugin.AST_current_pos_vector[1] = None
        plugin.AST_current_pos_vector[2] = None
        plugin.AST_current_pos.set("No reference point")

    if flag:
        ui.rebuild_ui(plugin, cmdr)


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry, state) -> None:
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
    global plugin

    if (int(state["GameVersion"][0]) < 4) and (plugin.AST_in_Legacy is False):
        # We're in Legacy, we'll not change the state of anything through journal entries.
        plugin.AST_in_Legacy = True
        return
    else:
        plugin.AST_in_Legacy = False

    flag = plugin.handle_possible_cmdr_change(cmdr)

    if plugin.AST_current_system.get() != system:
        plugin.AST_current_system.set(system)
        plugin.AST_bios_on_planet = plugin.ask_canonn_nicely(system)
        flag = True

    if plugin.AST_current_system.get() == "" or plugin.AST_current_system.get() == "None":
        plugin.AST_current_system.set(str(system))
        plugin.AST_bios_on_planet = plugin.ask_canonn_nicely(system)

    # TODO: Check if upon death in 4.0 Horizons do we lose Exobiodata.
    # Probably?
    # Check how real death differs from frontline solutions ground combat zone death.
    # Yes it does. Frontline solutions does not have a Resurrect event.

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        flag = True
        plugin.notyetsolddata[cmdr] = eventhandling.resurrection_event(plugin)

    if entry["event"] == "ScanOrganic":
        flag = True
        eventhandling.bioscan_event(cmdr, is_beta, entry, plugin, currententrytowrite)

    if entry["event"] in ["Location", "Embark", "Disembark", "Touchdown", "Liftoff", "FSDJump"]:
        flag = True
        eventhandling.system_body_change_event(cmdr, entry, plugin)

    if entry["event"] == "SellOrganicData":
        flag = True
        eventhandling.biosell_event(cmdr, entry, plugin)

    if entry["event"] == "SAASignalsFound":
        eventhandling.SAASignalsFound_event(entry, plugin)

    if flag:
        # save most recent relevant state so in case of crash of the system
        # we still have a proper record as long as it finishes saving below.
        plugin.on_preferences_closed(cmdr, is_beta)


# endregion


plugin = ArtemisScannerTracker(AST_VERSION, AST_REPO, PLUGIN_NAME,
                               directory, filename, cmdrstates,
                               debug, not_yet_sold_data, sold_exobiology)


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
