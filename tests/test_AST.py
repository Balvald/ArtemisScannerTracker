"""Tests for the ArtemisScannerTracker module."""

import json
import os
import sys
import tkinter as tk

import pytest

# import numpy as np

# Add parent directory to path
directory, filename = os.path.split(os.path.realpath(__file__))
sys.path.append(directory[:-5])

# Own Modules
from AST import ArtemisScannerTracker as AST  # noqa: E402 N817
import ui as ui_module  # noqa: E402

# import eventhandling

root = tk.Tk()
root.withdraw()  # <== this prevented garbage window.

cmdrstates = {}
notsold = {}
sold = {}


class FakeTree:
    """Minimal Treeview stand-in for tree rebuild tests."""

    def __init__(self) -> None:
        """Initialize the in-memory tree structure."""
        self.nodes = {}
        self.children = {"": []}

    def delete(self, *items: int) -> None:
        """Delete one or more nodes from the fake tree."""
        if not items:
            self.nodes.clear()
            self.children = {"": []}
            return
        for item in items:
            parent = self.nodes.get(item, {}).get("parent")
            if parent in self.children and item in self.children[parent]:
                self.children[parent].remove(item)
            self.nodes.pop(item, None)
            self.children.pop(item, None)

    def get_children(self, item: int | str = "") -> list:
        """Return child node ids for the requested parent."""
        return list(self.children.get(item, []))

    def insert(self, parent: int | str, index: str, text: str = "", values=None, iid=None, open: bool = False):
        """Insert a new node into the fake tree."""
        node_id = iid if iid is not None else len(self.nodes)
        self.nodes[node_id] = {
            "text": text,
            "values": list(values or []),
            "parent": parent,
            "open": open,
        }
        self.children.setdefault(parent, []).append(node_id)
        self.children.setdefault(node_id, [])
        return node_id

    def move(self, item: int, parent: int | str, index: str) -> None:
        """Move a node to a new parent."""
        old_parent = self.nodes[item]["parent"]
        if old_parent in self.children and item in self.children[old_parent]:
            self.children[old_parent].remove(item)
        self.nodes[item]["parent"] = parent
        self.children.setdefault(parent, []).append(item)

    def item(self, item: int, **kwargs) -> dict:
        """Get or update a fake tree node."""
        if kwargs:
            self.nodes[item].update(kwargs)
        return self.nodes[item]


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


def test_init_json_files():  # noqa: CCR001
    """Initialize json files."""
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
                if type([]) == type(test):  # noqa: E721
                    # we have an old version of the (not)soldbiodata.json
                    # clear it, have the user do the journal crawling again.
                    print(f"Found old {file} format")
                    print("Clearing file...")
                    f.seek(0)
                    f.write(r"{}")
                    f.truncate()


def test_AST_on_load() -> None:  # noqa: N802
    """Test the on_load method."""
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


def test_AST_setup_preferences() -> None:  # noqa: N802
    """Test setup_preferences."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    notebook = tk.ttk.Notebook(root)
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


def test_AST_setup_main_ui() -> None:  # noqa: N802
    """Test setup_main_ui."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_ex_tree_rebuild_explo_flattens_body_rows() -> None:
    """Exploration tree should render one row per body with type data merged in."""
    ui_module.data_explo = {
        "Jameson": [["Sol", "37 Capricorni A", "Star", True, False, 1234, True]],
    }
    ui_module.full_ex_tree_explo = None

    tree = FakeTree()

    ui_module.ex_tree_rebuild_explo(tree, "Jameson", "")

    assert tree.get_children("") == [0]
    assert tree.item(0)["text"] == "Sol"
    assert tree.item(0)["values"] == [1, "", "", "", "1/1"]

    assert tree.get_children(0) == [1]
    assert tree.item(1)["text"] == "37 Capricorni A"
    assert tree.item(1)["values"] == ["Star", "True", "False", 1234, "1/1"]
    assert tree.get_children(1) == []


def test_AST_on_preferences_closed() -> None:  # noqa: N802
    """Test the on_preferences_closed method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_AST_handle_possible_cmdr_change() -> None:  # noqa: N802
    """Test the handle_possible_cmdr_change method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_AST_forcehideshow() -> None:  # noqa: N802
    """Test the forcehideshow method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_AST_switchhidesoldexobio() -> None:  # noqa: N802
    """Test the switchhidesoldexobio method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_AST_update_scan_plant() -> None:  # noqa: N802
    """Test the update_scan_plant method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_AST_reset() -> None:  # noqa: N802
    """Test the reset method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_AST_on_unload() -> None:  # noqa: N802
    """Test the on_unload method."""
    print(f"Running test: {sys._getframe(  ).f_code.co_name}.")
    parent = tk.Tk()
    notebook = tk.ttk.Notebook(parent)
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


def test_cleanup() -> None:
    """Cleanup test environment."""
    # directory, filename = os.path.split(os.path.realpath(__file__))
    # filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]
    for file in filenames:
        if os.path.exists(directory + file):
            os.remove(directory + file)


if __name__ == "__main__":

    print("Cleanup")
    test_cleanup()

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
    test_cleanup()
    print("Done.")
