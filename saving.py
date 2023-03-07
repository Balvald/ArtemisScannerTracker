"""AST saving/loading helper functions"""

import json


def save_cmdr(cmdr, plugin) -> None:
    """Save information specific to the cmdr in the cmdrstates.json."""

    if cmdr not in plugin.CMDR_states.keys():
        plugin.CMDR_states[cmdr] = ["None", "None", "None", "0/3", "None", 0, "None", "None", "None"]

    valuelist = [plugin.AST_last_scan_plant.get(), plugin.AST_last_scan_system.get(), plugin.AST_last_scan_body.get(),
                 plugin.AST_current_scan_progress.get(), plugin.AST_state.get(), plugin.rawvalue,
                 plugin.AST_CCR.get(), plugin.AST_scan_1_pos_vector.copy(), plugin.AST_scan_2_pos_vector.copy()]

    for i in range(len(plugin.CMDR_states[cmdr])):
        plugin.CMDR_states[cmdr][i] = valuelist[i]

    file = plugin.AST_DIR + "\\cmdrstates.json"

    open(file, "r+", encoding="utf8").close()
    with open(file, "r+", encoding="utf8") as f:
        f.seek(0)
        json.dump(plugin.CMDR_states, f, indent=4)
        f.truncate()


def load_cmdr(cmdr, plugin) -> None:
    """Load information about a cmdr from cmdrstates.json."""

    file = plugin.AST_DIR + "\\cmdrstates.json"

    with open(file, "r+", encoding="utf8") as f:
        plugin.CMDR_states = json.load(f)

    plugin.AST_last_scan_plant.set(plugin.CMDR_states[cmdr][0])
    plugin.AST_last_scan_system.set(plugin.CMDR_states[cmdr][1])
    plugin.AST_last_scan_body.set(plugin.CMDR_states[cmdr][2])
    plugin.AST_current_scan_progress.set(plugin.CMDR_states[cmdr][3])
    plugin.AST_state.set(plugin.CMDR_states[cmdr][4])
    plugin.rawvalue = int(str(plugin.CMDR_states[cmdr][5]).split(" ")[0].replace(",", ""))
    plugin.AST_CCR.set(plugin.CMDR_states[cmdr][6])
    plugin.AST_scan_1_pos_vector = plugin.CMDR_states[cmdr][7]
    plugin.AST_scan_2_pos_vector = plugin.CMDR_states[cmdr][8]
