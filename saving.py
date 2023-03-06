import json


def save_cmdr(cmdr, plugin, directory, cmdrstates) -> None:
    """Save information specific to the cmdr in the cmdrstates.json."""
    # global plugin, directory

    if cmdr not in cmdrstates.keys():
        cmdrstates[cmdr] = ["None", "None", "None", "0/3", "None", 0, "None", "None", "None"]

    valuelist = [plugin.AST_last_scan_plant.get(), plugin.AST_last_scan_system.get(), plugin.AST_last_scan_body.get(),
                 plugin.AST_current_scan_progress.get(), plugin.AST_state.get(), plugin.rawvalue,
                 plugin.AST_CCR.get(), plugin.AST_scan_1_pos_vector.copy(), plugin.AST_scan_2_pos_vector.copy()]

    for i in range(len(cmdrstates[cmdr])):
        cmdrstates[cmdr][i] = valuelist[i]

    file = directory + "\\cmdrstates.json"

    open(file, "r+", encoding="utf8").close()
    with open(file, "r+", encoding="utf8") as f:
        f.seek(0)
        json.dump(cmdrstates, f, indent=4)
        f.truncate()


def load_cmdr(cmdr, plugin, directory, cmdrstates) -> None:
    """Load information about a cmdr from cmdrstates.json."""
    # global cmdrstates, plugin
    file = directory + "\\cmdrstates.json"

    with open(file, "r+", encoding="utf8") as f:
        cmdrstates = json.load(f)

    plugin.AST_last_scan_plant.set(cmdrstates[cmdr][0])
    plugin.AST_last_scan_system.set(cmdrstates[cmdr][1])
    plugin.AST_last_scan_body.set(cmdrstates[cmdr][2])
    plugin.AST_current_scan_progress.set(cmdrstates[cmdr][3])
    plugin.AST_state.set(cmdrstates[cmdr][4])
    plugin.rawvalue = int(str(cmdrstates[cmdr][5]).split(" ")[0].replace(",", ""))
    plugin.AST_CCR.set(cmdrstates[cmdr][6])
    plugin.AST_scan_1_pos_vector = cmdrstates[cmdr][7]
    plugin.AST_scan_2_pos_vector = cmdrstates[cmdr][8]
