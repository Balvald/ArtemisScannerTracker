"""AST saving/loading helper functions"""

import json
import logging
import os

try:
    testmode = False
    from config import appname  # type: ignore
except ImportError:
    testmode = True

if not testmode:
    logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")
else:
    logger = logging.getLogger(f"{os.path.basename(os.path.dirname(__file__))}")


def save_cmdr(cmdr, plugin) -> None:
    """Save information specific to the cmdr in the cmdrstates.json."""

    if cmdr not in plugin.CMDR_states.keys():
        plugin.CMDR_states[cmdr] = ["None", "None", "None", "0/3", "None", 0, 0, [None, None], [None, None]]

    try:
        AST_last_scan_plant = plugin.AST_last_scan_plant.get()
    except AttributeError:
        AST_last_scan_plant = "None"

    try:
        AST_last_scan_system = plugin.AST_last_scan_system.get()
    except AttributeError:
        AST_last_scan_system = "None"

    try:
        AST_last_scan_body = plugin.AST_last_scan_body.get()
    except AttributeError:
        AST_last_scan_body = "None"

    try:
        AST_current_scan_progress = plugin.AST_current_scan_progress.get()
    except AttributeError:
        AST_current_scan_progress = "0/3"

    try:
        AST_state = plugin.AST_state.get()
    except AttributeError:
        AST_state = "None"

    try:
        rawvalue = plugin.rawvalue
    except AttributeError:
        rawvalue = 0

    try:
        AST_CCR = plugin.AST_CCR.get()
    except AttributeError:
        AST_CCR = 0

    try:
        AST_scan_1_pos_vector = plugin.AST_scan_1_pos_vector
        if AST_scan_1_pos_vector == "None":
            AST_scan_1_pos_vector = [None, None]
    except AttributeError:
        AST_scan_1_pos_vector = [None, None]

    try:
        AST_scan_2_pos_vector = plugin.AST_scan_2_pos_vector
        if AST_scan_2_pos_vector == "None":
            AST_scan_2_pos_vector = [None, None]
    except AttributeError:
        AST_scan_2_pos_vector = [None, None]

    valuelist = [AST_last_scan_plant, AST_last_scan_system, AST_last_scan_body,
                 AST_current_scan_progress, AST_state, rawvalue,
                 AST_CCR, AST_scan_1_pos_vector, AST_scan_2_pos_vector]

    if plugin.AST_debug.get():
        logger.debug(f"Saving CMDR states: {valuelist} for CMDR: {cmdr}")

    for i in range(len(plugin.CMDR_states[cmdr])):
        plugin.CMDR_states[cmdr][i] = valuelist[i]

    file = plugin.AST_DIR + "/cmdrstates.json"

    open(file, "r+", encoding="utf8").close()
    with open(file, "r+", encoding="utf8") as f:
        f.seek(0)
        json.dump(plugin.CMDR_states, f, indent=4)
        f.truncate()


def load_cmdr(cmdr, plugin) -> None:
    """Load information about a cmdr from cmdrstates.json."""

    file = plugin.AST_DIR + "/cmdrstates.json"

    with open(file, "r+", encoding="utf8") as f:
        plugin.CMDR_states = json.load(f)

    try:
        plugin.AST_last_scan_plant.set(plugin.CMDR_states[cmdr][0])
        plugin.AST_last_scan_system.set(plugin.CMDR_states[cmdr][1])
        plugin.AST_last_scan_body.set(plugin.CMDR_states[cmdr][2])
        plugin.AST_current_scan_progress.set(plugin.CMDR_states[cmdr][3])
        plugin.AST_state.set(plugin.CMDR_states[cmdr][4])
        plugin.rawvalue = int(str(plugin.CMDR_states[cmdr][5]).split(" ")[0].replace(",", ""))
        plugin.AST_CCR.set(plugin.CMDR_states[cmdr][6])
        plugin.AST_scan_1_pos_vector = plugin.CMDR_states[cmdr][7]
        plugin.AST_scan_2_pos_vector = plugin.CMDR_states[cmdr][8]
    except KeyError:
        plugin.AST_last_scan_plant.set("None")
        plugin.AST_last_scan_system.set("None")
        plugin.AST_last_scan_body.set("None")
        plugin.AST_current_scan_progress.set("0/3")
        plugin.AST_state.set("None")
        plugin.rawvalue = 0
        plugin.AST_CCR.set(0)
        plugin.AST_scan_1_pos_vector = [None, None]
        plugin.AST_scan_2_pos_vector = [None, None]
