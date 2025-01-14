import os
import sys
import json
import tkinter as tk
import tkinter.ttk as nb
# import numpy as np

directory, filename = os.path.split(os.path.realpath(__file__))
sys.path.append(directory[:-5])
from AST import ArtemisScannerTracker as AST  # noqa: E402

root = tk.Tk()
root.withdraw()  # <== this prevented garbage window.

cmdrstates = {}
notsold = {}
sold = {}

filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]

"""bad_event = {"timestamp": "2022-10-24T00:00:00Z",
             "event": "ScanOrganic",
             "ScanType": "Analyse",
             "SystemAddress": 0,
             "Body": 0}


def test_survive_bad_event():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")

    assert (True is True)

    # np.testing.assert_allclose()
"""

def test_init_json_files():
    # directory, filename = os.path.split(os.path.realpath(__file__))
    # filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]
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
    ast = AST("test", "Balvald/ArtemisScannerTracker", "AST",
              directory, cmdrstates, notsold, sold)
    assert (ast.on_load() == "AST")


def test_AST_setup_preferences():
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    notebook = nb.Notebook(root)
    ast = AST("test", "Balvald/ArtemisScannerTracker", "AST",
              directory, cmdrstates, notsold, sold)
    ast.setup_preferences(notebook, "Balvald", False)
    assert (True is True)


def test_Cleanup():
    # directory, filename = os.path.split(os.path.realpath(__file__))
    # filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]
    for file in filenames:
        if os.path.exists(directory + file):
            os.remove(directory + file)


if __name__ == '__main__':

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

    # on_unload



    # on_preferences_closed




    # setup_main_ui
    


    # reset



    # forcehideshow



    # switchhidesoldexobio



    # update_last_scan_plant



    # handle_possible_cmdr_change



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