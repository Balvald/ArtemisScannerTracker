"""AST saving/loading helper functions."""

import json
import logging
import os

# EDMC specific imports
try:
    testmode = False
    from config import appname  # type: ignore
except ImportError:
    testmode = True

if not testmode:
    logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")
else:
    logger = logging.getLogger(f"{os.path.basename(os.path.dirname(__file__))}")


def save_cmdr(cmdr, plugin) -> None:  # noqa: CCR001
    """Save information specific to the cmdr in the cmdrstates.json."""
    if cmdr not in plugin.CMDR_states.keys():
        plugin.CMDR_states[cmdr] = ["None", "None", "None", "0/3", "None", 0, 0, [None, None], [None, None]]

    try:
        ast_last_scan_plant = plugin.AST_last_scan_plant.get()
    except AttributeError:
        ast_last_scan_plant = "None"

    try:
        ast_last_scan_system = plugin.AST_last_scan_system.get()
    except AttributeError:
        ast_last_scan_system = "None"

    try:
        ast_last_scan_body = plugin.AST_last_scan_body.get()
    except AttributeError:
        ast_last_scan_body = "None"

    try:
        ast_current_scan_progress = plugin.AST_current_scan_progress.get()
    except AttributeError:
        ast_current_scan_progress = "0/3"

    try:
        ast_state = plugin.AST_state.get()
    except AttributeError:
        ast_state = "None"

    try:
        rawvalue = plugin.rawvalue
    except AttributeError:
        rawvalue = 0

    try:
        ast_ccr = plugin.AST_CCR.get()
    except AttributeError:
        ast_ccr = 0

    try:
        ast_scan_1_pos_vector = plugin.AST_scan_1_pos_vector
        if ast_scan_1_pos_vector == "None":
            ast_scan_1_pos_vector = [None, None]
    except AttributeError:
        ast_scan_1_pos_vector = [None, None]

    try:
        ast_scan_2_pos_vector = plugin.AST_scan_2_pos_vector
        if ast_scan_2_pos_vector == "None":
            ast_scan_2_pos_vector = [None, None]
    except AttributeError:
        ast_scan_2_pos_vector = [None, None]

    valuelist = [ast_last_scan_plant, ast_last_scan_system, ast_last_scan_body,
                 ast_current_scan_progress, ast_state, rawvalue,
                 ast_ccr, ast_scan_1_pos_vector, ast_scan_2_pos_vector]

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
