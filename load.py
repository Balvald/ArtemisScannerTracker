"""
Artemis Scanner Tracker by Balvald.

created from the EDMC example plugin.
"""

import json
import logging
import os
import tkinter as tk
from theme import theme  # type: ignore # noqa: N813
from typing import Optional

import myNotebook as nb  # type: ignore # noqa: N813
from config import appname, config  # type: ignore

# globals as part of the plugin class?
frame: Optional[tk.Frame] = None

PLUGIN_NAME = "AST"

# Gonna need the files directory to store data for full
# tracking of all the biological things that the CMDR scans.
directory, filename = os.path.split(os.path.realpath(__file__))

if not os.path.exists(directory + "\\soldbiodata.json"):
    firstrun = True
    f = open(directory + "\\soldbiodata.json", "w", encoding="utf8")
    f.write(r"[]")
    f.close()

if not os.path.exists(directory + "\\notsoldbiodata.json"):
    firstrun = True
    f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
    f.write(r"[]")
    f.close()

not_yet_sold_data = []
sold_exobiology = []
currententrytowrite = {}
# placeholder sample.
lastsample = {"species": "Thargoid", "system": "Polaris", "body": "Raxxla"}

# load notyetsolddata

with open(directory + "\\notsoldbiodata.json", "r+", encoding="utf8") as f:
    not_yet_sold_data = json.load(f)

# Shows debug fields in preferences when True
debug = False

logger = logging.getLogger(f"{appname}.{PLUGIN_NAME}")

vistagenomicsprices = {
    "Fonticulua Fluctus": 900000,
    "Tussock Stigmasis": 806300,
    "Stratum Tectonicas": 806300,
    "Fonticulua Segmentatus": 806300,
    "Concha Biconcavis": 806300,
    "Stratum Cucumisis": 711500,
    "Recepta Deltahedronix": 711500,
    "Fumerola Extremus": 711500,
    "Clypeus Speculumi": 711500,
    "Cactoida Vermis": 711500,
    "Tussock Virgam": 645700,
    "Recepta Conditivus": 645700,
    "Recepta Umbrux": 596500,
    "Osseus Discus": 596500,
    "Aleoida Gravis": 596500,
    "Tubus Sororibus": 557800,
    "Clypeus Margaritus": 557800,
    "Frutexa Flammasis": 500100,
    "Osseus Pellebantus": 477700,
    "Clypeus Lacrimam": 426200,
    "Bacterium Informem": 426200,
    "Tussock Triticum": 400500,
    "Tubus Rosarium": 400500,
    "Frutexa Acus": 400500,
    "Concha Aureolas": 400500,
    "Bacterium Volu": 400500,
    "Fumerola Nitris": 389400,
    "Aleoida Arcus": 379300,
    "Tussock Capillum": 370000,
    "Fumerola Carbosis": 339100,
    "Fumerola Aquatis": 339100,
    "Electricae Radialem": 339100,
    "Electricae Pluma": 339100,
    "Aleoida Coronamus": 339100,
    "Frutexa Sponsae": 326500,
    "Tussock Pennata": 320700,
    "Tubus Conifer": 315300,
    "Fonticulua Upupam": 315300,
    "Bacterium Nebulus": 296300,
    "Bacterium Scopulum": 280600,
    "Bacterium Omentum": 267400,
    "Concha Renibus": 264300,
    "Tussock Serrati": 258700,
    "Osseus Fractus": 239400,
    "Bacterium Verrata": 233300,
    "Fungoida Bullarum": 224100,
    "Cactoida Pullulanta": 222500,
    "Cactoida Cortexum": 222500,
    "Tussock Caputus": 213100,
    "Aleoida Spica": 208900,
    "Aleoida Laminiae": 208900,
    "Fungoida Gelata": 206300,
    "Tussock Albata": 202500,
    "Tussock Ventusa": 201300,
    "Osseus Pumice": 197800,
    "Fonticulua Lapida": 195600,
    "Stratum Laminamus": 179500,
    "Fungoida Stabitis": 174000,
    "Tubus Cavas": 171900,
    "Stratum Frigus": 171900,
    "Cactoida Peperatis": 164000,
    "Cactoida Lapis": 164000,
    "Stratum Excutitus": 162200,
    "Stratum Araneamus": 162200,
    "Osseus Spiralis": 159900,
    "Concha Labiata": 157100,
    "Bacterium Tela": 135600,
    "Tussock Ignis": 130100,
    "Frutexa Flabellum": 127900,
    "Fonticulua Digitos": 127700,
    "Tussock Divisa": 125600,
    "Tussock Cultro": 125600,
    "Tussock Catena": 125600,
    "Bacterium Cerbrus": 121300,
    "Fungoida Setisis": 120200,
    "Bacterium Alcyoneum": 119500,
    "Frutexa Collum": 118500,
    "Frutexa Metallicum": 118100,
    "Frutexa Fera": 118100,
    "Crystalline Shards": 117900,
    "Amphora Plant": 117900,
    "Viride Brain Tree": 115900,
    "Roseum Brain Tree": 115900,
    "Puniceum Brain Tree": 115900,
    "Ostrinum Brain Tree": 115900,
    "Lividum Brain Tree": 115900,
    "Lindigoticum Brain Tree": 115900,
    "Gypseeum Brain Tree": 115900,
    "Aureum Brain Tree": 115900,
    "Viride Sinuous Tubers": 111300,
    "Violaceum Sinuous Tubers": 111300,
    "Roseum Sinuous Tubers": 111300,
    "Prasinum Sinuous Tubers": 111300,
    "Lindigoticum Sinuous Tubers": 111300,
    "Caeruleum Sinuous Tubers": 111300,
    "Blatteum Sinuous Tubers": 111300,
    "Albidum Sinuous Tubers": 111300,
    "Rubeum Bioluminescent Anemone": 110500,
    "Roseum Bioluminescent Anemone": 110500,
    "Roseum Anemone": 110500,
    "Puniceum Anemone": 110500,
    "Prasinum Bioluminescent Anemone": 110500,
    "Luteolum Anemone": 110500,
    "Croceum Anemone": 110500,
    "Blatteum Bioluminescent Anemone": 110500,
    "Osseus Cornibus": 109500,
    "Bark Mounds": 108900,
    "Tubus Compagibus": 102700,
    "Stratum Paleas": 102500,
    "Stratum Limaxus": 102500,
    "Bacterium Bullaris": 89900,
    "Bacterium Aurasus": 78500,
    "Tussock Propagito": 71300,
    "Fonticulua Campestris": 63600,
    "Tussock Pennatis": 59600,
    "Bacterium Vesicula": 56100,
    "Bacterium Acies": 50000
}


class ArtemisScannerTracker:
    """Artemis Scanner Tracker plugin class."""

    def __init__(self) -> None:
        """Initialize the plugin by getting values from the config file."""
        # Be sure to use names that wont collide in our config variables
        # Bools for show hide checkboxes
        self.AST_hide_fullscan: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_fullscan"))
        self.AST_hide_species: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_species"))
        self.AST_hide_progress: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_progress"))
        self.AST_hide_last_system: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_last_system"))
        self.AST_hide_last_body: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_last_body"))
        self.AST_hide_system: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_system"))
        self.AST_hide_body: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_body"))
        self.AST_hide_value: Optional[tk.IntVar] = tk.IntVar(
            value=config.get_int("AST_hide_value"))

        # Artemis Scanner State infos
        self.AST_last_scan_plant: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_last_scan_plant")))
        self.AST_last_scan_system: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_last_scan_system")))
        self.AST_last_scan_body: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_last_scan_body")))
        self.AST_current_scan_progress: Optional[tk.StringVar] = tk.StringVar(
            value=(
                str(config.get_int("AST_current_scan_progress")) + str("/3")))
        self.AST_current_system: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_current_system")))
        self.AST_current_body: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_current_body")))
        self.AST_state: Optional[tk.StringVar] = tk.StringVar(
            value=str(config.get_str("AST_state")))
        self.AST_value: Optional[tk.StringVar] = tk.StringVar(
            value=(str(config.get_int("AST_value")) + str(" Cr.")))

        logger.info("ArtemisScannerTracker instantiated")

    def on_load(self) -> str:
        """
        on_load is called by plugin_start3 below.

        It is the first point EDMC interacts with our code
        after loading our module.

        :return: The name of the plugin, which will be used by EDMC for logging
                 and for the settings window
        """
        return PLUGIN_NAME

    def on_unload(self) -> None:
        """
        on_unload is called by plugin_stop below.

        It is the last thing called before EDMC shuts down.
        Note that blocking code here will hold the shutdown process.
        """
        self.on_preferences_closed("", False)  # Save our prefs

    def setup_preferences(self, parent: nb.Notebook,
                          cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
        """
        setup_preferences is called by plugin_prefs below.

        It is where we can setup our
        own settings page in EDMC's settings window.
        Our tab is defined for us.

        :param parent: the tkinter parent that our
                       returned Frame will want to inherit from
        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        :return: The frame to add to the settings window
        """
        current_row = 0
        frame = nb.Frame(parent)

        nb.Label(frame, text="Artemis Scanner Tracker by Balvald").grid(
            row=current_row, sticky=tk.W)
        current_row += 1

        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, sticky=tk.W)
        current_row += 1

        nb.Checkbutton(
            frame,
            text="Hide Full Status",
            variable=self.AST_hide_fullscan).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Scanned Value",
            variable=self.AST_hide_value).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        nb.Checkbutton(
            frame,
            text="Hide Species",
            variable=self.AST_hide_species).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Scan Progress",
            variable=self.AST_hide_progress).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        nb.Checkbutton(
            frame,
            text="Hide System of last Scan",
            variable=self.AST_hide_last_system).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Body of last Scan",
            variable=self.AST_hide_last_body).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        nb.Checkbutton(
            frame,
            text="Hide Current System",
            variable=self.AST_hide_system).grid(
            row=current_row, column=0, sticky="W")
        nb.Checkbutton(
            frame,
            text="Hide Current Body",
            variable=self.AST_hide_body).grid(
            row=current_row, column=1, sticky="W")
        current_row += 1
        if debug:
            # setup debug fields for the scanner.
            nb.Label(frame, text="Species").grid(row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_last_scan_plant).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="System of last Scan").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_last_scan_system).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="Body of last Scan").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_last_scan_body).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="Scan progress").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_current_scan_progress).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

            nb.Label(frame, text="Scanned Value").grid(
                row=current_row, sticky=tk.W)
            nb.Entry(frame, textvariable=self.AST_value).grid(
                row=current_row, column=1, sticky=tk.W)
            current_row += 1

        nb.Label(
            frame,
            text="For these preferences to take effect please restart"
            + " EDMC after closing the settings").grid(
            row=current_row, sticky=tk.W)
        current_row += 1
        nb.Label(
            frame,
            text="___________________________________________________________"
        ).grid(row=current_row, sticky=tk.W)
        current_row += 1

        nb.Label(
            frame,
            text="To reset the state of the plugin press the button below"
        ).grid(row=current_row, sticky=tk.W)
        current_row += 1
        nb.Label(
            frame,
            text="WARNING: Info that is reset can not be restored.").grid(
            row=current_row, sticky=tk.W)
        current_row += 2
        nb.Button(
            frame,
            text="RESET",
            command=self.reset).grid(
            row=current_row, sticky=tk.W)
        current_row += 1

        return frame

    def on_preferences_closed(self, cmdr: str, is_beta: bool) -> None:
        """
        on_preferences_closed is called by prefs_changed below.

        It is called when the preferences dialog is dismissed by the user.

        :param cmdr: The current ED Commander
        :param is_beta: Whether or not EDMC is currently marked as in beta mode
        """
        config.set("AST_current_scan_progress", int(
            self.AST_current_scan_progress.get()[0]))
        config.set("AST_last_scan_system", str(
            self.AST_last_scan_system.get()))
        config.set("AST_last_scan_body", str(self.AST_last_scan_body.get()))
        config.set("AST_last_scan_plant", str(self.AST_last_scan_plant.get()))
        config.set("AST_state", str(self.AST_state.get()))
        config.set("AST_value", int(self.AST_value.get().split(" ")[0]))

        config.set("AST_hide_value", int(self.AST_hide_value.get()))
        config.set("AST_hide_fullscan", int(self.AST_hide_fullscan.get()))
        config.set("AST_hide_species", int(self.AST_hide_species.get()))
        config.set("AST_hide_progress", int(self.AST_hide_progress.get()))
        config.set("AST_hide_last_system", int(
            self.AST_hide_last_system.get()))
        config.set("AST_hide_last_body", int(self.AST_hide_last_body.get()))
        config.set("AST_hide_system", int(self.AST_hide_system.get()))
        config.set("AST_hide_body", int(self.AST_hide_body.get()))

        logger.debug("ArtemisScannerTracker saved preferences")

    def setup_main_ui(self, parent: tk.Frame) -> tk.Frame:  # noqa: CCR001
        """
        Create our entry on the main EDMC UI.

        This is called by plugin_app below.

        :param parent: EDMC main window Tk
        :return: Our frame
        """
        current_row = 12
        frame = tk.Frame(parent)

        if self.AST_hide_body.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Current Body:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_current_body).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_system.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Current System:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_current_system).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_value.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Scanned Value:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_value).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_last_body.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Body of last Scan:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_last_scan_body).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_last_system.get() != 1:
            current_row -= 1
            tk.Label(frame, text="System of last Scan:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_last_scan_system).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_progress.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Scan Progress:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_current_scan_progress).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_species.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Species:").grid(row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_last_scan_plant).grid(
                row=current_row, column=1, sticky=tk.W)

        if self.AST_hide_fullscan.get() != 1:
            current_row -= 1
            tk.Label(frame, text="Last Exobiology Scan:").grid(
                row=current_row, sticky=tk.W)
            tk.Label(frame, textvariable=self.AST_state).grid(
                row=current_row, column=1, sticky=tk.W)

        return frame

    def reset(self):
        """Reset function of the Reset Button."""
        self.AST_current_scan_progress.set("0/3")
        self.AST_last_scan_system.set("None")
        self.AST_last_scan_body.set("None")
        self.AST_last_scan_plant.set("None")
        self.AST_state.set("None")
        self.AST_value.set("0 Cr.")


def journal_entry(cmdr, is_beta,  # noqa: CCR001
                  system, station,
                  entry, state):
    """
    React accordingly to events in the journal.

    Scan Organic events tell us what we have scanned.
    Scan Type of these events can tell us the progress of the scan.
    Add the value of a finished Scan to the tally
    :param cmdr: The current ED Commander
    :param is_beta: Whether or not EDMC is currently marked as in beta mode
    :param system: current system? unused
    :param station: unused
    :param entry: the current Journal entry
    :param state: unused
    """

    # TODO: Refactor this behemoth into more manageable helper functions
    # so it allows for easier additions later.

    global currententrytowrite, not_yet_sold_data, lastsample, sold_exobiology

    flag = False

    if entry["event"] == "Resurrect":
        # Reset - player was unable to sell before death
        not_yet_sold_data = []

    if entry["event"] == "ScanOrganic":
        flag = True

        plugin.AST_last_scan_plant.set(entry["Species_Localised"])

        # In the eventuality that the user started EMDC after
        # the "Location" event happens and directly scans a plant
        # these lines wouldn"t be able to do anything but to
        # set the System and body of the last Scan to "None"
        plugin.AST_last_scan_system.set(plugin.AST_current_system.get())
        plugin.AST_last_scan_body.set(plugin.AST_current_body.get())

        if entry["ScanType"] == "Log":
            plugin.AST_current_scan_progress.set("1/3")
        elif entry["ScanType"] in ["Sample", "Analyse"]:
            if (entry["ScanType"] == "Analyse"):

                if plugin.AST_value.get() == "None":
                    plugin.AST_value.set("0 Cr.")
                # Somehow we get here twice for each 3rd scan. idfk
                newvalue = int(plugin.AST_value.get().split(" ")[0]) + \
                    int(vistagenomicsprices[entry["Species_Localised"]])
                plugin.AST_value.set(str(newvalue) + " Cr.")
                # Found some cases where the analyse happened
                # seemingly directly after a log.
                plugin.AST_current_scan_progress.set("3/3")
                currententrytowrite["species"] = entry["Species_Localised"]
                currententrytowrite["system"] = plugin.AST_current_system.get()
                currententrytowrite["body"] = plugin.AST_current_body.get()
                if currententrytowrite not in not_yet_sold_data:
                    # If there is no second Sample scantype event
                    # we have to save the data here.
                    not_yet_sold_data.append(currententrytowrite)
                    file = directory + "\\notsoldbiodata.json"
                    with open(file, "r+", encoding="utf8") as f:
                        notsolddata = json.load(f)
                        notsolddata.append(currententrytowrite)
                        f.seek(0)
                        json.dump(notsolddata, f, indent=4)
                    currententrytowrite = {}
                    lastsample = {"species": "Thargoid",
                                  "system": "Polaris",
                                  "body": "Raxxla"}
            else:
                plugin.AST_current_scan_progress.set("2/3")
                lastsample["species"] = entry["Species_Localised"]
                lastsample["system"] = plugin.AST_current_system.get()
                lastsample["body"] = plugin.AST_current_body.get()
        else:
            # Something is horribly wrong if we end up here
            # If anyone ever sees "Excuse me what the fuck"
            # we know they added a new ScanType, that we might need to handle
            plugin.AST_current_scan_progress.set("Excuse me what the fuck")

    if entry["event"] in ["Location", "Embark",
                          "Disembark", "Touchdown",
                          "Liftoff", "FSDJump"]:
        flag = True
        try:
            # Get current system name and body from events that need to happen.
            plugin.AST_current_system.set(entry["StarSystem"])
            plugin.AST_current_body.set(entry["Body"])
        except KeyError:
            # Could throw a KeyError in old Horizons versions
            pass

        # To fix the aforementioned eventuality where the systems end up
        # being "None" we update the last scan location
        # When the CMDR gets another journal entry that tells us
        # the players location.
        if ((plugin.AST_last_scan_system.get() == "None")
                or (plugin.AST_last_scan_body.get() == "None")):
            plugin.AST_last_scan_system.set(entry["StarSystem"])
            plugin.AST_last_scan_body.set(entry["Body"])

    if entry["event"] == "SellOrganicData":
        flag = True
        soldvalue = 0
        currentbatch = {}

        for sold in entry["BioData"]:
            if sold["Species_Localised"] in currentbatch.keys():
                currentbatch[sold["Species_Localised"]] += 1
            else:
                currentbatch[sold["Species_Localised"]] = 1
            soldvalue += sold["Value"]
            # If I add a counter for all biodata sold
            # I would also need to look at biodata["Bonus"]
            # -> Nah its impossible to track bonus while not sold yet
            # Could only be used for a profit since last reset
            # metric.
        bysystem = {}
        for biodata in not_yet_sold_data:
            if biodata["system"] in bysystem.keys():
                if (biodata["species"]
                        in bysystem[biodata["system"]].keys()):
                    bysystem[
                        biodata["system"]][biodata["species"]] += 1
                else:
                    bysystem[biodata["system"]][biodata["species"]] = 1
            else:
                bysystem[biodata["system"]] = {}
                bysystem[biodata["system"]][biodata["species"]] = 1
        soldbysystempossible = {}
        for system in bysystem:
            soldbysystempossible[system] = True
            for species in currentbatch:
                if species not in bysystem[system].keys():
                    soldbysystempossible[system] = False
                    break
            if soldbysystempossible[system] is False:
                continue
            for species in bysystem[system]:
                if bysystem[system][species] < currentbatch[species]:
                    soldbysystempossible[system] = False
                    break

        # this is still not perfect because it cannot be.
        # if the player sells the data by system and 2 systems
        # have the same amount of the same species then no one can tell
        # which system was actually sold at vista genomics.
        # In described case whatever is the first system we encounter
        # through iteration will be chosen as the system that was sold.
        thesystem = ""
        for system in soldbysystempossible:
            if soldbysystempossible[system] is True:
                # We always take the first system that is possible
                # If there are two we cannot tell which one was sold
                # Though it should not really matter as long as
                # the CMDR hasn't died right after without selling
                # the data aswell.
                thesystem = system
                break

        if thesystem != "":
            print("CMDR sold by system: " + thesystem)
            i = 0
            while i < len(not_yet_sold_data):
                # Checking here more granularily which data was sold
                # We do know though that the specifc data was sold only
                # in one system that at this point is saved in
                # the variable"thesystem"
                if (not_yet_sold_data[i]["system"] == thesystem
                        and not_yet_sold_data[i]
                        not in sold_exobiology):
                    if currentbatch[
                            not_yet_sold_data[i]["species"]] > 0:
                        sold_exobiology.append(not_yet_sold_data[i])
                        currentbatch[not_yet_sold_data[i]
                                     ["species"]] -= 1
                        not_yet_sold_data.pop(i)
                        continue
                    else:
                        print("Not all data from a single system "
                              + "were sold. This means the CMDR "
                              + "sold a singular bit of data")
                i += 1
            f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
            f.write(r"[]")
            f.close()
            if not_yet_sold_data != []:
                file = directory + "\\notsoldbiodata.json"
                with open(file, "r+", encoding="utf8") as f:
                    notsolddata = json.load(f)
                    for data in not_yet_sold_data:
                        notsolddata.append(data)
                    f.seek(0)
                    json.dump(notsolddata, f, indent=4)

        else:
            print("CMDR sold the whole batch.")
            for data in not_yet_sold_data:
                if (data not in sold_exobiology
                        and currentbatch[
                            data["species"]] > 0):
                    currentbatch[data["species"]] -= 1
                    sold_exobiology.append(data)
            not_yet_sold_data = []
            f = open(directory + "\\notsoldbiodata.json", "w", encoding="utf8")
            f.write(r"[]")
            f.close()

        # Remove the value of what was sold from
        # the amount of the Scanned value.
        # Specifically so that the plugin still keeps track properly,
        # when the player sells on a by system basis.
        plugin.AST_value.set(
            str(int(plugin.AST_value.get().split(" ")[0])
                - soldvalue) + " Cr.")

        # No negative value of biodata could still be unsold on the Scanner
        # This means that there was data on the Scanner that
        # the plugin was unable to record by not being active.
        if int(plugin.AST_value.get().split(" ")[0]) < 0:
            plugin.AST_value.set("0 Cr.")
        # Now write the data into the local file
        file = directory + "\\soldbiodata.json"
        with open(file, "r+", encoding="utf8") as f:
            solddata = json.load(f)
            if sold_exobiology != []:
                for item in sold_exobiology:
                    solddata.append(item)
                sold_exobiology = []
            f.seek(0)
            json.dump(solddata, f, indent=4)

    if flag:
        # we changed a value so we update line.
        plugin.AST_state.set(
            plugin.AST_last_scan_plant.get()
            + " (" + plugin.AST_current_scan_progress.get()
            + ") on: " + plugin.AST_last_scan_body.get())

        # save most recent relevant state so in case of crash of the system
        # we still have a proper record as long as it finishes saving below.
        plugin.on_preferences_closed(cmdr, is_beta)


plugin = ArtemisScannerTracker()


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


def plugin_prefs(parent: nb.Notebook,
                 cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
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
