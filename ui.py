"""AST UI functions"""

import json
import logging
import os
import tkinter as tk

from organicinfo import getvistagenomicprices

import myNotebook as nb  # type: ignore
from config import appname  # type: ignore
from theme import theme  # type: ignore
from ttkHyperlinkLabel import HyperlinkLabel  # type: ignore


directory, filename = os.path.split(os.path.realpath(__file__))

logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")


# region ui shorthand definitions


def prefs_label(frame, text, row: int, col: int, sticky) -> None:
    """Create label for the preferences of the plugin."""
    nb.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)


def prefs_entry(frame, textvariable, row: int, col: int, sticky) -> None:
    """Create an entry field for the preferences of the plugin."""
    nb.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)


def prefs_button(frame, text, command, row: int, col: int, sticky) -> None:
    """Create a button for the prefereces of the plugin."""
    nb.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)


def prefs_tickbutton(frame, text, variable, row: int, col: int, sticky) -> None:
    """Create a tickbox for the preferences of the plugin."""
    nb.Checkbutton(frame, text=text, variable=variable).grid(row=row, column=col, sticky=sticky)


def label(frame, text, row: int, col: int, sticky) -> None:
    """Create a label for the ui of the plugin."""
    tk.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)


def entry(frame, textvariable, row: int, col: int, sticky) -> None:
    """Create a label that displays the content of a textvariable for the ui of the plugin."""
    tk.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)


def colourlabel(frame, text: str, row: int, col: int, colour: str, sticky) -> None:
    """Create a label with coloured text for the ui of the plugin."""
    tk.Label(frame, text=text, fg=colour).grid(row=row, column=col, sticky=sticky)


def colourentry(frame, textvariable, row: int, col: int, colour: str, sticky) -> None:
    """Create a label that displays the content of a textvariable for the ui of the plugin."""
    tk.Label(frame, textvariable=textvariable, fg=colour).grid(row=row, column=col, sticky=sticky)


def button(frame, text, command, row: int, col: int, sticky) -> None:
    """Create a button for the ui of the plugin."""
    tk.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)

# endregion


def shortcreditstring(number) -> str:
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


data = {}
soldbiodata_file = directory + "/soldbiodata.json"
notsoldbiodata_file = directory + "/notsoldbiodata.json"

vistagenomicprices = getvistagenomicprices()
# region ui shorthand definitions

with open(soldbiodata_file, "r+", encoding="utf8") as f:
    soldbiodata = json.load(f)

with open(notsoldbiodata_file, "r+", encoding="utf8") as f:
    notsoldbiodata = json.load(f)

# logger.warning(f"Sold Bio Data: {soldbiodata}")
# logger.warning(f"Not Sold Bio Data: {notsoldbiodata}")

logger.warning("transcribing into data ...")

for cmdr in notsoldbiodata.keys():
    data[cmdr] = []
    if cmdr != cmdr:
        continue
    for item in notsoldbiodata[cmdr]:
        data[cmdr].append([item["system"], item["body"], item["species"],
                           shortcreditstring(vistagenomicprices[item["species"]]), "No"])

logger.warning("Finished transcribing not sold data.")

for cmdr in soldbiodata.keys():
    data[cmdr] = []
    for letter in soldbiodata[cmdr].keys():
        logger.warning(f"Letter: {letter}")
        for system in soldbiodata[cmdr][letter].keys():
            for item in soldbiodata[cmdr][letter][system]:
                data[cmdr].append([system, item["body"], item["species"],
                                   shortcreditstring(vistagenomicprices[item["species"]]), "Yes"])

logger.warning("Finished transcribing sold data.")


def show_codex_window(plugin, cmdr: str):

    global data, vistagenomicprices

    new_window = tk.Tk()
    new_window.title("Codex")

    columns = ["System", "Body", "Species", "Value", "Sold"]

    tree = tk.ttk.Treeview(new_window, columns=columns, show="headings")
    tree.heading("System", text="System")
    tree.heading("Body", text="Body")
    tree.heading("Species", text="Species")
    tree.heading("Value", text="Value")
    tree.heading("Sold", text="Sold")

    for item in data[cmdr]:
        tree.insert("", tk.END, values=item)

    tree.grid(row=0, column=0, sticky="nsew")

    scrollbar = tk.Scrollbar(new_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="nsew")

    new_window.mainloop()


def clear_ui(frame) -> None:
    """Remove all labels from this plugin."""
    # remove all labels from the frame
    for label in frame.winfo_children():
        label.destroy()


def rebuild_ui(plugin, cmdr: str) -> None:
    """Rebuild the UI in case of preferences change."""

    if plugin.AST_debug.get():
        logger.debug("Rebuilding UI ...")

    clear_ui(plugin.frame)

    # recreate UI
    current_row = 0

    if plugin.updateavailable:
        latest = f"github.com/{plugin.AST_REPO}/releases/latest"
        HyperlinkLabel(plugin.frame, text="Update available!",
                       url=latest, underline=True).grid(row=current_row, sticky=tk.W)
        current_row += 1

    uielementcheck = [plugin.AST_hide_fullscan.get(), plugin.AST_hide_species.get(), plugin.AST_hide_progress.get(),
                      plugin.AST_hide_last_system.get(), plugin.AST_hide_last_body.get(), plugin.AST_hide_value.get(),
                      plugin.AST_hide_system.get(), plugin.AST_hide_body.get()]
    uielementlistleft = ["Last Exobiology Scan:", "Last Species:", "Scan Progress:",
                         "System of last Scan:", "Body of last Scan:", "Unsold Scan Value:",
                         "Current System:", "Current Body:"]
    uielementlistright = [plugin.AST_state, plugin.AST_last_scan_plant, plugin.AST_current_scan_progress,
                          plugin.AST_last_scan_system, plugin.AST_last_scan_body, plugin.AST_value,
                          plugin.AST_current_system, plugin.AST_current_body]
    uielementlistextra = [None, None, None, None, None, "clipboardbutton", None, None]

    skipafterselling = ["Last Exobiology Scan:", "Last Species:", "Scan Progress:",
                        "System of last Scan:", "Body of last Scan:"]

    for i in range(max(len(uielementlistleft), len(uielementlistright))):
        if uielementcheck[i] != 1:
            if plugin.AST_after_selling.get() != 0:
                if uielementlistleft[i] in skipafterselling:
                    continue
            # Check when we hide the value of unsold scans when it is 0
            if uielementlistleft[i] == "Unsold Scan Value:":
                if (plugin.AST_hide_value_when_zero.get() == 1
                   and int(plugin.rawvalue) == 0):
                    continue
            # Hide when system is the same as the current one.
            if (uielementlistleft[i] in ["System of last Scan:", "Body of last Scan:"]
               and (plugin.AST_hide_after_selling.get() == 1 or plugin.AST_hide_after_full_scan.get() == 1)):
                if uielementlistright[i].get() == uielementlistright[i+3].get():
                    continue
            if i < len(uielementlistleft):
                label(plugin.frame, uielementlistleft[i], current_row, 0, tk.W)
            if i < len(uielementlistright):
                entry(plugin.frame, uielementlistright[i], current_row, 1, tk.W)
            if uielementlistextra[i] == "clipboardbutton":
                button(plugin.frame, "📋", plugin.clipboard, current_row, 2, tk.E)
            current_row += 1

    # Clonal Colonial Range here.
    if plugin.AST_hide_CCR.get() != 1 and plugin.AST_near_planet is True:
        # show distances for the last scans.
        colour = "red"
        if plugin.AST_current_scan_progress.get() in ["0/3", "3/3"]:
            colour = None
        if plugin.AST_scan_1_dist_green:
            colour = "green"
        colourlabel(plugin.frame, "Distance to Scan #1: ", current_row, 0, colour, tk.W)
        colourentry(plugin.frame, plugin.AST_scan_1_pos_dist, current_row, 1, colour, tk.W)
        current_row += 1
        colour = "red"
        if plugin.AST_current_scan_progress.get() in ["0/3", "1/3", "3/3"]:
            colour = None
        if plugin.AST_scan_2_dist_green:
            colour = "green"
        colourlabel(plugin.frame, "Distance to Scan #2: ", current_row, 0, colour, tk.W)
        colourentry(plugin.frame, plugin.AST_scan_2_pos_dist, current_row, 1, colour, tk.W)
        current_row += 1
        colour = None
        if ((plugin.AST_scan_1_dist_green
             and plugin.AST_current_scan_progress.get() == "1/3")
            or (plugin.AST_scan_1_dist_green
                and plugin.AST_scan_2_dist_green
                and plugin.AST_current_scan_progress.get() == "2/3")):
            colour = "green"
        colourlabel(plugin.frame, "Current Position: ", current_row, 0, colour, tk.W)
        colourentry(plugin.frame, plugin.AST_current_pos, current_row, 1, colour, tk.W)
        current_row += 1

    if plugin.AST_debug.get():
        logger.debug("Building AST sold/scanned exobio ...")

    button(plugin.frame, " Open Codex ", plugin.show_codex_window, current_row, 0, tk.W)
    current_row += 1

    # Tracked sold bio scans as the last thing to add to the UI
    if plugin.AST_hide_sold_bio.get() != 1:
        build_sold_bio_ui(plugin, cmdr, current_row)

    theme.update(plugin.frame)  # Apply theme colours to the frame and its children, including the new widgets


def build_sold_bio_ui(plugin, cmdr: str, current_row) -> None:
    soldbiodata = {}
    notsoldbiodata = {}

    file = plugin.AST_DIR + "/soldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        soldbiodata = json.load(f)

    file = plugin.AST_DIR + "/notsoldbiodata.json"
    with open(file, "r+", encoding="utf8") as f:
        notsoldbiodata = json.load(f)

    label(plugin.frame, "Scans in this System:", current_row, 0, tk.W)

    if cmdr == "" or cmdr is None or cmdr == "None":
        return

    # Check if we even got a cmdr yet!
    if plugin.AST_debug.get():
        logger.info(f"In build_sold_bio_ui: Commander: {cmdr}. attempting to access")
        # logger.info(f"data: {soldbiodata[cmdr]}.")
        # logger.info(f"data: {notsoldbiodata}.")

    bodylistofspecies = {}
    try:
        firstletter = plugin.AST_current_system.get()[0].lower()
    except IndexError:
        label(plugin.frame, "None", current_row, 1, tk.W)
        # length of string is 0. there is no current system yet.
        # So there is no reason to do anything
        return

    count = 0
    count_from_planet = 0
    currentbody = plugin.AST_current_body.get().replace(plugin.AST_current_system.get(), "")[1:]
    if plugin.AST_debug.get():
        logger.debug(plugin.AST_num_bios_on_planet)

    try:
        if plugin.AST_current_system.get() in soldbiodata[cmdr][firstletter].keys():
            for sold in soldbiodata[cmdr][firstletter][plugin.AST_current_system.get()]:
                bodyname = ""

                # Check if body has a special name or if we have standardized names
                if sold["system"] in sold["body"]:
                    # no special name for planet
                    bodyname = sold["body"].replace(sold["system"], "")[1:]
                else:
                    bodyname = sold["body"]

                if sold["species"] not in bodylistofspecies.keys():
                    bodylistofspecies[sold["species"]] = [[bodyname, True]]
                else:
                    bodylistofspecies[sold["species"]].append([bodyname, True])

                if plugin.AST_debug.get():
                    logger.debug(f"{bodyname} checked and this is the current: {currentbody}")

                if currentbody == bodyname:
                    count_from_planet += 1
                count += 1
    except KeyError:
        # if we don't have the cmdr in the sold data yet we just pass all sold data.
        pass

    try:
        for notsold in notsoldbiodata[cmdr]:
            if notsold["system"] == plugin.AST_current_system.get():

                bodyname = ""

                # Check if body has a special name or if we have standardized names
                if notsold["system"] in notsold["body"]:
                    # no special name for planet
                    bodyname = notsold["body"].replace(notsold["system"], "")[1:]
                else:
                    bodyname = notsold["body"]

                if notsold["species"] not in bodylistofspecies.keys():
                    bodylistofspecies[notsold["species"]] = [[bodyname, False]]
                else:
                    bodylistofspecies[notsold["species"]].append([bodyname, False])

                if plugin.AST_debug.get():
                    logger.debug(f"{bodyname} checked and this is the current: {currentbody}")

                if currentbody == bodyname:
                    count_from_planet += 1
                count += 1
    except KeyError:
        # if we don't have the cmdr in the notsold data yet we just pass.
        pass

    if bodylistofspecies == {}:
        count = "None"

    if plugin.AST_debug.get():
        logger.debug(f"bios on planet: {plugin.AST_num_bios_on_planet}, and nearplanet: {plugin.AST_near_planet}")

    if plugin.AST_num_bios_on_planet != 0 and (plugin.AST_near_planet is True):
        # whole thing gets coloured green.
        # Easier and a bigger indicator that we scanned everythong on the planet.
        colour = "green"
        if count_from_planet < plugin.AST_num_bios_on_planet:
            colour = None
        test = (len(str(count))*"   ") + "   On this Body: " + f"{count_from_planet}/{plugin.AST_num_bios_on_planet}"
        if plugin.AST_debug.get():
            logger.debug("Writing Label")
        colourlabel(plugin.frame, test, current_row, 1, colour, tk.E)

    # calling this number after the label for "On this Body: x/y" so it hopefully is just drawn over
    # the constant padding added in the string above.
    label(plugin.frame, count, current_row, 1, tk.W)

    # skip
    if plugin.AST_hide_scans_in_system.get() != 0:
        button(plugin.frame, " ▼ ", plugin.switchhidesoldexobio, current_row, 2, tk.W)
    else:
        button(plugin.frame, " ▲ ", plugin.switchhidesoldexobio, current_row, 2, tk.W)

        sortedspecieslist = sorted(bodylistofspecies.keys())

        for species in sortedspecieslist:
            bodylist = [item[0] for item in bodylistofspecies[species]]
            current_row += 1
            bodies = ""
            for body in bodylistofspecies[species]:
                if body[1]:
                    bodies = bodies + body[0] + ", "
                else:
                    bodies = bodies + "*" + body[0] + "*, "
            while (bodies[-1] == "," or bodies[-1] == " "):
                bodies = bodies[:-1]

            colour = None

            if plugin.AST_debug.get():
                logger.debug(f"current body {plugin.AST_current_body.get()}, the string we check" +
                             f"{currentbody}" +
                             f"and body list of species {bodylistofspecies[species]}")
                logger.debug(f"{bodylist}")

            # already defined the same way?
            # currentbody = plugin.AST_current_body.get().replace(plugin.AST_current_system.get(), "")[1:]

            if currentbody in bodylist:
                colour = "green"

            colourlabel(plugin.frame, species, current_row, 0, colour, tk.W)
            label(plugin.frame, bodies, current_row, 1, tk.W)
