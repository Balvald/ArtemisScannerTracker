import tkinter as tk
import myNotebook as nb  # type: ignore # noqa: N813


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
