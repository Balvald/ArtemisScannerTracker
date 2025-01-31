import json
import os
import sys
import tkinter as tk
import tkinter.ttk as nb

import pytest

# import numpy as np

# Add parent directory to path
directory, filename = os.path.split(os.path.realpath(__file__))
sys.path.append(directory[:-5])

# Own Modules
from AST import ArtemisScannerTracker as AST  # noqa: E402

# import eventhandling

root = tk.Tk()
root.withdraw()  # <== this prevented garbage window.

cmdrstates = {}
notsold = {}
sold = {}

filenames = ["/soldbiodata.json", "/notsoldbiodata.json", "/cmdrstates.json"]

bad_event = {
    "timestamp": "2022-10-24T00:00:00Z",
    "event": "ScanOrganic",
    "ScanType": "Analyse",
    "SystemAddress": 0,
    "Body": 0,
}

good_event = {
    "timestamp": "2022-10-24T00:00:00Z",
    "event": "ScanOrganic",
    "ScanType": "Analyse",
    "SystemAddress": 0,
    "Body": 0,
    "Genus": "$Codex_Ent_Osseus_Genus_Name;",
    "Species": "$codex_ent_osseus_05_name;",
    "Genus_Localised": "Osseus",
    "Species_Localised": "Osseus Cornibus",
}


def test_init_json_files():
    directory, filename = os.path.split(os.path.realpath(__file__))
    filenames = ["/soldbiodata.json", "/notsoldbiodata.json", "/cmdrstates.json"]
    # Create anew.
    for file in filenames:
        if not os.path.exists(directory + file):
            f = open(directory + file, "w", encoding="utf8")
            f.write(r"{}")
            f.close()
        elif file == "/soldbiodata.json" or file == "/notsoldbiodata.json":
            # (not)soldbiodata file already exists
            with open(directory + file, "r+", encoding="utf8") as f:
                test = json.load(f)
                if type([]) == type(test):  # noqa E721
                    # we have an old version of the (not)soldbiodata.json
                    # clear it, have the user do the journal crawling again.
                    print(f"Found old {file} format")
                    print("Clearing file...")
                    f.seek(0)
                    f.write(r"{}")
                    f.truncate()


def test_AST_on_load():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    assert ast.on_load() == "AST"


def test_AST_setup_preferences():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    notebook = nb.Notebook(root)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.setup_preferences(notebook, "Jameson", False)
    assert True


def test_AST_setup_main_ui():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.setup_main_ui(parent)
    assert True


def test_AST_on_preferences_closed():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    ast.on_preferences_closed("Jameson", False)
    assert True


def test_AST_handle_possible_cmdr_change():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "test",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "test", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    ast.AST_current_CMDR = "Jameson"
    assert ast.AST_current_CMDR == "Jameson"
    ast.handle_possible_cmdr_change("test")
    assert ast.AST_current_CMDR == "test"
    ast.handle_possible_cmdr_change("a")
    assert ast.AST_current_CMDR == "a"
    ast.handle_possible_cmdr_change("b")
    assert ast.AST_current_CMDR == "b"
    ast.handle_possible_cmdr_change("b")
    assert ast.AST_current_CMDR == "b"
    ast.handle_possible_cmdr_change("test")
    assert ast.AST_current_CMDR == "test"
    ast.on_preferences_closed("test", False)
    ast.on_unload()


def test_AST_forcehideshow():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    ast.AST_after_selling.set(False)
    ast.forcehideshow()
    assert ast.AST_after_selling.get() == 1
    ast.forcehideshow()
    assert ast.AST_after_selling.get() == 0


def test_AST_switchhidesoldexobio():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    ast.AST_hide_scans_in_system.set(False)
    ast.switchhidesoldexobio()
    assert ast.AST_hide_scans_in_system.get() == 1
    ast.switchhidesoldexobio()
    assert ast.AST_hide_scans_in_system.get() == 0


def test_AST_update_scan_plant():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    ast.AST_hide_scans_in_system.set(False)
    with pytest.raises(Exception) as e_info:  # noqa: F841
        ast.update_last_scan_plant(bad_event)
    ast.update_last_scan_plant(good_event)
    assert good_event["Species_Localised"] in ast.AST_last_scan_plant.get()


def test_AST_reset():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    ast.AST_hide_scans_in_system.set(False)
    ast.reset()
    assert ast.rawvalue == 0
    assert ast.AST_scan_1_pos_vector == [None, None]
    assert ast.AST_scan_2_pos_vector == [None, None]


def test_AST_on_unload():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = nb.Notebook(parent)
    ast = AST(
        "Jameson",
        "Balvald/ArtemisScannerTracker",
        "AST",
        directory,
        cmdrstates,
        notsold,
        sold,
    )
    ast.frame = tk.Frame(parent)
    config = ast.debug_config()
    print(config.storage)
    ast.setup_preferences(notebook, "Jameson", False)
    ast.AST_CCR.set(100)
    ast.AST_scan_1_pos_vector = [0, 0]
    ast.AST_scan_2_pos_vector = [0, 0]
    # ast.AST_current_CMDR = "test"
    # ast.AST_last_CMDR = "test"
    config = ast.debug_config()
    print(config.storage)
    ast.handle_possible_cmdr_change("Jameson")
    # ast.on_preferences_closed("test", False)
    config = ast.debug_config()
    print(config.storage)
    ast.on_unload()
    print(config.storage)
    # assert (config.get_str("AST_last_CMDR") == "Jameson")


def test_Cleanup():
    # directory, filename = os.path.split(os.path.realpath(__file__))
    # filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]
    for file in filenames:
        if os.path.exists(directory + file):
            os.remove(directory + file)


if __name__ == "__main__":

    print("Cleanup")
    test_Cleanup()

    print("Initializing json files")
    test_init_json_files()

    # The test functions start with the prefix "test_" and
    # are followed by a comment that describes what the test is supposed to test.

    # on_load()
    test_AST_on_load()
    # on_load() returns "AST" and __init__ finishes without error

    # setup_preferences()
    test_AST_setup_preferences()
    # check that setup_preferences() finishes without error

    # setup_main_ui
    test_AST_setup_main_ui()
    # check that setup_main_ui() finishes without error

    # handle_possible_cmdr_change
    test_AST_handle_possible_cmdr_change()
    # check that handle_possible_cmdr_change() does indeed change the cmdr

    # on_preferences_closed
    test_AST_on_preferences_closed()

    # forcehideshow
    test_AST_forcehideshow()

    # switchhidesoldexobio
    test_AST_switchhidesoldexobio()

    # update_last_scan_plant
    test_AST_update_scan_plant()

    # reset
    test_AST_reset()

    # on_unload
    test_AST_on_unload()

    # clipboard()
    # clipboard() cannot be properly tested for functionality
    # instead it is just tested for running without error

    # journal crawling methods:
    # buildsoldbiodatajsonlocalworker
    # buildsoldbiodatajsonlocal
    # buildsoldbiodatajsonworker
    # buildsoldbiodatajson

    # Codex window methods:
    # show_codex_window_worker
    # show_codex_window_thread

    print("Tests complete.")

    print("Cleaning up...")

    # Clear files in test environment first
    test_Cleanup()
    print("Done.")
