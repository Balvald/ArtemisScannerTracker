"""AST UI functions."""

import gc
import json
import logging
import os
import sys
import threading
import tkinter as tk

# Own modules
from organicinfo import getvistagenomicprices

# EDMC specific imports
try:
    from config import appname, config  # type: ignore
    import myNotebook as nb  # type: ignore  # noqa: N813
    from theme import theme  # type: ignore
    from ttkHyperlinkLabel import HyperlinkLabel  # type: ignore
    testmode = False
except ImportError:
    import tkinter.ttk as nb  # type: ignore
    # from ttkHyperlinkLabel import HyperlinkLabel  # type: ignore
    appname = "AST"
    testmode = True

try:
    logger = logging.getLogger(f"{appname}.{os.path.basename(os.path.dirname(__file__))}")
except NameError:
    logger = logging.getLogger(f"{os.path.basename(os.path.dirname(__file__))}")

directory, filename = os.path.split(os.path.realpath(__file__))

# region ASTTheme

tk_to_ttk_migration = True

try:
    from theme import _Theme  # type: ignore

    # Just yoinked this from EDMC's own theme.py from ElSaico's ttk branch
    if sys.platform == 'win32':
        import win32con
        import win32gui
        from winrt.microsoft.ui.interop import get_window_id_from_window
        from winrt.microsoft.ui.windowing import AppWindow
        from winrt.windows.ui import Colors
        from ctypes import windll
        FR_PRIVATE = 0x10
        fonts_loaded = windll.gdi32.AddFontResourceExW(str(config.respath_path / 'EUROCAPS.TTF'), FR_PRIVATE, 0)
        if fonts_loaded < 1:
            logger.error('Unable to load Euro Caps font for Transparent theme')

    elif sys.platform == 'linux':
        from ctypes import POINTER, Structure, byref, c_char_p, c_int, c_long, c_uint, c_ulong, c_void_p, cdll
        XID = c_ulong 	# from X.h: typedef unsigned long XID
        Window = XID
        Atom = c_ulong
        Display = c_void_p  # Opaque

        PropModeReplace = 0
        PropModePrepend = 1
        PropModeAppend = 2

        # From xprops.h
        MWM_HINTS_FUNCTIONS = 1 << 0
        MWM_HINTS_DECORATIONS = 1 << 1
        MWM_HINTS_INPUT_MODE = 1 << 2
        MWM_HINTS_STATUS = 1 << 3
        MWM_FUNC_ALL = 1 << 0
        MWM_FUNC_RESIZE = 1 << 1
        MWM_FUNC_MOVE = 1 << 2
        MWM_FUNC_MINIMIZE = 1 << 3
        MWM_FUNC_MAXIMIZE = 1 << 4
        MWM_FUNC_CLOSE = 1 << 5
        MWM_DECOR_ALL = 1 << 0
        MWM_DECOR_BORDER = 1 << 1
        MWM_DECOR_RESIZEH = 1 << 2
        MWM_DECOR_TITLE = 1 << 3
        MWM_DECOR_MENU = 1 << 4
        MWM_DECOR_MINIMIZE = 1 << 5
        MWM_DECOR_MAXIMIZE = 1 << 6

        class MotifWmHints(Structure):
            """MotifWmHints structure."""

            _fields_ = [
                ('flags', c_ulong),
                ('functions', c_ulong),
                ('decorations', c_ulong),
                ('input_mode', c_long),
                ('status', c_ulong),
            ]

        # workaround for https://github.com/EDCD/EDMarketConnector/issues/568
        if not os.getenv("EDMC_NO_UI"):
            try:
                xlib = cdll.LoadLibrary('libX11.so.6')
                XInternAtom = xlib.XInternAtom
                XInternAtom.argtypes = [POINTER(Display), c_char_p, c_int]
                XInternAtom.restype = Atom
                XChangeProperty = xlib.XChangeProperty
                XChangeProperty.argtypes = [POINTER(Display), Window, Atom, Atom, c_int,
                                            c_int, POINTER(MotifWmHints), c_int]
                XChangeProperty.restype = c_int
                XFlush = xlib.XFlush
                XFlush.argtypes = [POINTER(Display)]
                XFlush.restype = c_int
                XOpenDisplay = xlib.XOpenDisplay
                XOpenDisplay.argtypes = [c_char_p]
                XOpenDisplay.restype = POINTER(Display)
                XQueryTree = xlib.XQueryTree
                XQueryTree.argtypes = [POINTER(Display), Window, POINTER(
                    Window), POINTER(Window), POINTER(Window), POINTER(c_uint)]
                XQueryTree.restype = c_int
                dpy = xlib.XOpenDisplay(None)
                if not dpy:
                    raise Exception("Can't find your display, can't continue")

                motif_wm_hints_property = XInternAtom(dpy, b'_MOTIF_WM_HINTS', False)
                motif_wm_hints_normal = MotifWmHints(
                    MWM_HINTS_FUNCTIONS | MWM_HINTS_DECORATIONS,
                    MWM_FUNC_RESIZE | MWM_FUNC_MOVE | MWM_FUNC_MINIMIZE | MWM_FUNC_CLOSE,
                    MWM_DECOR_BORDER | MWM_DECOR_RESIZEH | MWM_DECOR_TITLE | MWM_DECOR_MENU | MWM_DECOR_MINIMIZE,
                    0, 0
                )
                motif_wm_hints_dark = MotifWmHints(MWM_HINTS_FUNCTIONS | MWM_HINTS_DECORATIONS,
                                                   MWM_FUNC_RESIZE | MWM_FUNC_MOVE | MWM_FUNC_MINIMIZE | MWM_FUNC_CLOSE,
                                                   0, 0, 0)
            except Exception:
                if __debug__:
                    print_exc()  # type: ignore  # noqa: F821

                dpy = None

    # Redefining Theme Class to fit the needs of the independent window in this plugin.
    # _Theme is a class from EDMC's theme.py from ElSaico's ttk branch

    class ASTTheme(_Theme):
        """Theme class for the AST Codex window."""

        def __init__(self, root):
            """Initialise the theme."""
            super().__init__()
            super().initialize(root)

        def apply(self) -> None:  # noqa: CCR001
            """Apply the theme to AST Codex Window."""
            logger.info('Applying theme')
            theme = config.get_str('theme_name').lower()
            if theme not in self.packages.keys():
                theme = 'light'
                config.set('theme_name', theme.capitalize())
            else:
                theme = theme.lower()
            transparent = config.get_bool('transparent')

            try:
                self.root.tk.call('ttk::setTheme', self.packages[theme])
                # load colors from the current theme into self.colors
                self.load_colors()
                # call tk_setPalette to apply the theme to all widgets
                # these are mostly tk widgets or tk widgets that are part of more complex ttk widgets
                self.root.tk.call('tk_setPalette',
                                  'activeBackground', self.colors['-selectbg'],
                                  'activeForeground', self.colors['-selectfg'],
                                  'background', self.colors['-bg'],
                                  'foreground', self.colors['-fg'],
                                  'highlightColor', self.colors['-highlight'],
                                  'highlightBackground', self.colors['-bg'],
                                  'selectBackground', self.colors['-selectbg'],
                                  'selectForeground', self.colors['-selectfg'],
                                  'disabledForeground', self.colors['-disabledfg'],
                                  'insertBackground', self.colors['-fg'],
                                  'selectColor', self.colors['-selectbg'],
                                  'troughColor', self.colors['-bg'])
                # Because tk.Radiobutton and tk.Checkbutton cannot be properly read with the settings of the
                # tk_setPalette call we have to additionally force a fitting theme for them.
                self._force_theme()
            except tk.TclError:
                logger.exception(f'Failure setting theme: {self.packages[theme]}')

            if self.active == theme and self.active_transparent == transparent:
                return self.active, self.active_transparent  # Don't need to mess with the window manager
            self.active = theme
            self.active_transparent = transparent

            self.root.withdraw()
            self.root.update_idletasks()  # Size gets recalculated here
            if sys.platform == 'win32':
                hwnd = win32gui.GetParent(self.root.winfo_id())
                window = AppWindow.get_from_window_id(get_window_id_from_window(hwnd))

                window.title_bar.extends_content_into_title_bar = True

                if transparent:
                    self.set_title_buttons_background(Colors.transparent)
                    window.title_bar.background_color = Colors.transparent
                    window.title_bar.inactive_background_color = Colors.transparent
                    window.title_bar.button_hover_background_color = Colors.transparent
                    # TODO prevent loss of focus when hovering the title bar area
                    # # fixed by transparent_move,
                    # we just don't regain focus when hovering over the title bar,
                    # we have to hover over some visible widget first.
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                           win32con.WS_EX_APPWINDOW | win32con.WS_EX_LAYERED)  # Add to taskbar
                    self.binds['<Enter>'] = self.root.bind('<Enter>', self.transparent_move)
                    self.binds['<FocusIn>'] = self.root.bind('<FocusIn>', self.transparent_move)
                    self.binds['<Leave>'] = self.root.bind('<Leave>', self.transparent_move)
                    self.binds['<FocusOut>'] = self.root.bind('<FocusOut>', self.transparent_move)
                else:
                    self.set_title_buttons_background(self.hex_to_rgb(
                        self.style.lookup('TButton', 'background')))
                    window.title_bar.background_color = self.hex_to_rgb(
                        self.style.lookup('TButton', 'background'))
                    window.title_bar.inactive_background_color = self.hex_to_rgb(
                        self.style.lookup('TButton', 'background'))
                    window.title_bar.button_hover_background_color = self.hex_to_rgb(
                        self.style.lookup('TButton', 'selectbackground'))
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_APPWINDOW)  # Add to taskbar
                    for event, bind in self.binds.items():
                        # try:
                        self.root.unbind(event, bind)
                        # except tk.TclError as e:
                        #     logger.error(f"tk.TclError when trying to unbind: {e}")
                    self.binds.clear()
            else:
                if dpy:
                    xroot = Window()
                    parent = Window()
                    children = Window()
                    nchildren = c_uint()
                    XQueryTree(dpy,
                               self.root.winfo_id(),
                               byref(xroot),
                               byref(parent),
                               byref(children),
                               byref(nchildren))
                    if theme == 'light':
                        wm_hints = motif_wm_hints_normal
                    else:  # anything but light
                        wm_hints = motif_wm_hints_dark

                    XChangeProperty(
                        dpy, parent, motif_wm_hints_property, motif_wm_hints_property, 32, PropModeReplace, wm_hints, 5
                    )

                    XFlush(dpy)

            self.root.deiconify()
            self.root.wait_visibility()  # need main window to be displayed before returning

            if not self.minwidth:
                self.minwidth = self.root.winfo_width()  # Minimum width = width on first creation
                self.root.minsize(self.minwidth, -1)

            return self.active, self.active_transparent

except Exception as e:
    logger.error(f"Error: {e}")

    tk_to_ttk_migration = False

# endregion

filenames = ["/soldbiodata.json", "/notsoldbiodata.json",  "/cmdrstates.json"]

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
                logger.warning(f"Found old {file} format")
                logger.warning("Clearing file...")
                f.seek(0)
                f.write(r"{}")
                f.truncate()

# region tk/ttk shorthand definitions


def prefs_label(frame, text, row: int, col: int, sticky) -> tk.ttk.Label:
    """Create label for the preferences of the plugin."""
    global tk_to_ttk_migration
    if tk_to_ttk_migration:
        tk.ttk.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)
    else:
        nb.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)


def prefs_entry(frame, textvariable, row: int, col: int, sticky) -> tk.ttk.Label:
    """Create an entry field for the preferences of the plugin."""
    global tk_to_ttk_migration
    if tk_to_ttk_migration:
        tk.ttk.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)
    else:
        nb.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)


def prefs_button(frame, text, command, row: int, col: int, sticky) -> tk.ttk.Button:
    """Create a button for the prefereces of the plugin."""
    global tk_to_ttk_migration
    if tk_to_ttk_migration:
        tk.ttk.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)
    else:
        nb.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)


def prefs_tickbutton(frame, text, variable, row: int, col: int, sticky) -> tk.ttk.Checkbutton:
    """Create a tickbox for the preferences of the plugin."""
    global tk_to_ttk_migration
    if tk_to_ttk_migration:
        tk.ttk.Checkbutton(frame, text=text, variable=variable).grid(row=row, column=col, sticky=sticky)
    else:
        nb.Checkbutton(frame, text=text, variable=variable).grid(row=row, column=col, sticky=sticky)


def label(frame, text, row: int, col: int, sticky) -> tk.ttk.Label:
    """Create a label for the ui of the plugin."""
    return tk.ttk.Label(frame, text=text).grid(row=row, column=col, sticky=sticky)


def entry(frame, textvariable, row: int, col: int, sticky) -> tk.ttk.Label:
    """Create a label that displays the content of a textvariable for the ui of the plugin."""
    return tk.ttk.Label(frame, textvariable=textvariable).grid(row=row, column=col, sticky=sticky)


def colourlabel(frame, text: str, row: int, col: int, colour: str, sticky) -> tk.ttk.Label:
    """Create a label with coloured text for the ui of the plugin."""
    global tk_to_ttk_migration
    if tk_to_ttk_migration:
        if colour == "green":
            colour = "AST.green.TLabel"
        elif colour == "red":
            colour = "AST.red.TLabel"
        else:
            colour = "TLabel"
        return tk.ttk.Label(frame, text=text, style=colour).grid(row=row, column=col, sticky=sticky)
    else:
        return tk.Label(frame, text=text, fg=colour).grid(row=row, column=col, sticky=sticky)


def colourentry(frame, textvariable, row: int, col: int, colour: str, sticky) -> tk.ttk.Label:
    """Create a label that displays the content of a textvariable for the ui of the plugin."""
    global tk_to_ttk_migration
    if tk_to_ttk_migration:
        if colour == "green":
            colour = "AST.green.TLabel"
        elif colour == "red":
            colour = "AST.red.TLabel"
        else:
            colour = "TLabel"
        return tk.ttk.Label(frame, textvariable=textvariable, style=colour).grid(row=row, column=col, sticky=sticky)
    else:
        return tk.Label(frame, textvariable=textvariable, fg=colour).grid(row=row, column=col, sticky=sticky)


def button(frame, text, command, row: int, col: int, sticky) -> tk.ttk.Button:
    """Create a button for the ui of the plugin."""
    return tk.ttk.Button(frame, text=text, command=command).grid(row=row, column=col, sticky=sticky)

# endregion

# region AST Codex Window


data = {}
data_initialised = False

soldbiodata_file = directory + "/soldbiodata.json"
notsoldbiodata_file = directory + "/notsoldbiodata.json"

soldbiodata_file_mtime = os.path.getmtime(soldbiodata_file)
notsoldbiodata_file_mtime = os.path.getmtime(notsoldbiodata_file)

full_ex_tree = None


def init_data() -> None:  # noqa: CCR001
    """Initialise the data for the AST Codex window."""
    global data
    global soldbiodata_file
    global notsoldbiodata_file
    global soldbiodata_file_mtime
    global notsoldbiodata_file_mtime
    global data_initialised

    logger.info("Initialising data ...")

    vistagenomicprices = getvistagenomicprices()

    with open(soldbiodata_file, "r+", encoding="utf8") as f:
        soldbiodata = json.load(f)

    soldbiodata_file_mtime = os.path.getmtime(soldbiodata_file)

    with open(notsoldbiodata_file, "r+", encoding="utf8") as f:
        notsoldbiodata = json.load(f)

    notsoldbiodata_file_mtime = os.path.getmtime(notsoldbiodata_file)

    # logger.warning(f"Sold Bio Data: {soldbiodata}")
    # logger.warning(f"Not Sold Bio Data: {notsoldbiodata}")

    logger.warning("transcribing into data ...")

    for cmdr in notsoldbiodata.keys():
        data[cmdr] = []
    for cmdr in soldbiodata.keys():
        data[cmdr] = []

    for cmdr in notsoldbiodata.keys():
        if cmdr != cmdr:
            continue
        for item in notsoldbiodata[cmdr]:
            # logger.warning(f"{item}")
            data[cmdr].append([item["system"], item["body"], item["species"],
                               vistagenomicprices[item["species"]], "No"])

    logger.warning("Finished transcribing not sold data.")
    # logger.warning(f"{data}")

    for cmdr in soldbiodata.keys():
        for letter in soldbiodata[cmdr].keys():
            # logger.warning(f"Letter: {letter}")
            for system in soldbiodata[cmdr][letter].keys():
                for item in soldbiodata[cmdr][letter][system]:
                    data[cmdr].append([system, item["body"], item["species"],
                                       vistagenomicprices[item["species"]], "Yes"])

    logger.warning("Finished transcribing sold data.")
    # logger.warning(f"{data}")

    data_initialised = True


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


def tree_sort_column(tree, col, reverse) -> None:
    """Sort the columns of the Table View."""
    table = [(tree.set(k, col), k) for k in tree.get_children("")]

    if col == "Value":
        table.sort(key=lambda x: int(x[0]), reverse=reverse)
    else:
        table.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(table):
        tree.move(k, "", index)
        val = val

    # reverse sort next time
    tree.heading(col, text=col, command=lambda _col=col:
                 tree_sort_column(tree, _col, not reverse))


def ex_tree_sort_column(tree, col, reverse) -> None:
    """Sort the columns of the Tree View."""
    # in this tree there is only the #0 column
    table = [(tree.item(k)['text'], k) for k in tree.get_children("")]
    table.sort(key=lambda x: str(x[0]), reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(table):
        tree.move(k, "", index)
        val = val

    # reverse sort next time
    tree.heading(col, text="System", command=lambda _col=col:
                 ex_tree_sort_column(tree, _col, not reverse))


def tree_rebuild(tree, cmdr: str) -> None:
    """Rebuild the Table View for the main window."""
    global data
    tree.delete(*tree.get_children())
    try:
        for item in data[cmdr]:
            tree.insert("", tk.END, values=item)
    except KeyError:
        pass


def save_treeview_state(tree) -> None:  # noqa: CCR001
    """Prepare the treeview state for saving."""
    nodes = {}
    parent_of_child = {}

    try:
        for node in tree.get_children():
            # logger.error("system level nodes found.")
            # logger.error(f"Node: {node}")
            nodes[node] = tree.item(node)
            parent_of_child[node] = None
            try:
                for subnode in tree.get_children(node):
                    # logger.error("body level nodes found.")
                    # logger.error(f"Subnode: {subnode}")
                    nodes[subnode] = tree.item(subnode)
                    parent_of_child[subnode] = node
                    try:
                        for subsubnode in tree.get_children(subnode):
                            # logger.error("signal level nodes found.")
                            # logger.error(f"Subsubnode: {subsubnode}")
                            nodes[subsubnode] = tree.item(subsubnode)
                            parent_of_child[subsubnode] = subnode
                    except Exception as e:
                        logger.error(f"Error: {e}: No signal level nodes found.")
                        pass
            except Exception as e:
                logger.error(f"Error: {e}: No body level nodes found.")
                pass
    except Exception as e:
        logger.error(f"Error: {e}: No more signal level nodes found.")
        pass

    return [nodes, parent_of_child]


def load_treeview_state(treevar, tree) -> None:
    """Load the treeview state from a saved state."""
    nodes = treevar[0]

    # logger.error(f"Levels: {nodes}")

    parent_of_child = treevar[1]

    # rebuild tree.

    for node in nodes.keys():
        if parent_of_child[node] is None:
            tree.insert("", tk.END, node, **nodes[node])
        else:
            tree.insert(parent_of_child[node], tk.END, node, **nodes[node])


def ex_tree_rebuild(tree, cmdr: str, query: str) -> None:  # noqa: CCR001
    """Rebuild the treeview for the explorer window."""
    global data
    global full_ex_tree

    tree.delete(*tree.get_children())
    # tree.insert("", tk.END, text="System", iid=0, open=True)
    iid = 0
    query_found = False

    new_data_exists = ((os.path.getmtime(soldbiodata_file)
                        > soldbiodata_file_mtime) or
                       (os.path.getmtime(notsoldbiodata_file)
                        > notsoldbiodata_file_mtime))

    if full_ex_tree is not None and query == "" and not new_data_exists:
        logger.info("Loading tree from saved state ...")
        load_treeview_state(full_ex_tree, tree)
        logger.info("Tree loaded from saved state.")
        return

    try:
        for item in data[cmdr]:
            # logger.warning(f"Checking {item}")
            for value in item:
                if query == "":
                    query_found = True
                    break
                elif query.lower() in str(value).lower():
                    query_found = True
                    break
                else:
                    query_found = False
            if not query_found:
                continue
            child = 0
            while True:
                # check until we find the right child. As it might exist already.
                try:
                    if str(item[0]) == tree.item(child)['text']:
                        try:
                            subchild = 0
                            while True:
                                if str(item[1]) == tree.item(subchild)['text']:
                                    body_iid = subchild
                                    tree.insert(body_iid, tk.END, text=str(item[2:]), iid=iid, open=False)
                                    tree.move(iid, body_iid, "end")
                                    # logger.debug(f"created signal {item[2:]} for body {item[1]} in system {item[0]}
                                    #  with iid {iid} and moved it to {body_iid}")
                                    iid += 1
                                    break
                                subchild += 1
                            break
                        except Exception:
                            # logger.warning(f"parent: {tree.item(child)}")
                            parent_iid = child
                            tree.insert(child, tk.END, text=str(item[1]), iid=iid, open=False)
                            tree.move(iid, parent_iid, "end")
                            # logger.debug(f"created body {item[1]} in system {item[0]}
                            #  with iid {iid} and moved it to {parent_iid}")
                            body_iid = iid
                            iid += 1
                            tree.insert(body_iid, tk.END, text=str(item[2:]), iid=iid, open=False)
                            tree.move(iid, body_iid, "end")
                            # logger.debug(f"created signal {item[2:]} for body {item[1]} in system {item[0]}
                            #  with iid {iid} and moved it to {body_iid}")
                            iid += 1
                            # logger.warning(f"Added {item} to {item[0]}")
                            break
                except Exception:  # as e:
                    tree.insert("", tk.END, text=str(item[0]), iid=iid, open=False)
                    # logger.debug(f"created system {item[0]} with iid {iid}")
                    parent_iid = iid
                    iid += 1
                    tree.insert(child, tk.END, text=str(item[1]), iid=iid, open=False)
                    tree.move(iid, parent_iid, "end")
                    # logger.debug(f"created body {item[1]} in system {item[0]}
                    #  with iid {iid} and moved it to {parent_iid}")
                    body_iid = iid
                    iid += 1
                    tree.insert(body_iid, tk.END, text=str(item[2:]), iid=iid, open=False)
                    tree.move(iid, body_iid, "end")
                    # logger.debug(f"created signal {item[2:]} for body {item[1]} in system {item[0]}
                    #  with iid {iid} and moved it to {body_iid}")
                    iid += 1
                    # logger.warning(f"Added {item} to {item[0]} and created parent {item[0]} in same step, Error {e}")
                    break
                child += 1

    except KeyError as e:
        logger.error(f"KeyError: {e}")
        pass

    if query == "" and full_ex_tree is None:
        full_ex_tree = save_treeview_state(tree)


def tree_search(tree, search_entry, cmdr: str) -> None:  # noqa: CCR001
    """Search items in the table."""
    logger.warning("Searching ...")
    query = search_entry.get()
    logger.warning(f"Query: {query}")
    selections = []
    tree_rebuild(tree, cmdr)
    children = tree.get_children()
    if search_entry.get() == "":
        tree.selection_set([])
        return
    # logger.info(f"Children: {children}")
    for child in children:
        # logger.info(f"Child: {child}")
        # logger.info(f"Values: {tree.item(child)['values']}")
        for value in tree.item(child)['values']:
            if query.lower() in str(value).lower():
                # logger.info(f"Found: {tree.item(child)['values']}")
                selections.append(child)
                break
            elif str(value).lower() == "no" or str(value).lower() == "yes":
                tree.delete(child)
                break
    # logger.info(f"Selections: {selections}")
    logger.info("Search complete")
    tree.selection_set(selections)


def tree_search_ex(tree, search_entry, cmdr: str) -> None:  # noqa: CCR001
    """Search the tree."""
    logger.warning("Searching ...")
    query = search_entry.get()
    logger.warning(f"Query: {query}")
    selections = []
    ex_tree_rebuild(tree, cmdr, query)
    children = tree.get_children()
    if search_entry.get() == "":
        tree.selection_set([])
        return
    logger.warning(f"Children: {children}")
    for child in children:
        logger.warning(f"Child: {child}")
        logger.warning(f"Values: {tree.item(child)['values']}")
        for value in tree.item(child)['values']:
            if query.lower() in str(value).lower():
                logger.warning(f"Found: {tree.item(child)['values']}")
                selections.append(child)
                break
            elif str(value).lower() == "no" or str(value).lower() == "yes":
                tree.delete(child)
                break
    logger.warning(f"Selections: {selections}")
    logger.warning("Search complete")
    tree.selection_set(selections)


def tree_search_worker(plugin, tree, search_entry, cmdr: str) -> None:
    """Start a thread to search the tree."""
    plugin.searchthread = threading.Thread(target=tree_search(tree, search_entry, cmdr))
    plugin.searchthread.start()


def tree_search_worker_ex(plugin, tree, search_entry, cmdr: str) -> None:
    """Start a thread to search the tree."""
    plugin.searchthread = threading.Thread(target=tree_search_ex(tree, search_entry, cmdr))
    plugin.searchthread.start()


def show_codex_window(plugin, cmdr: str) -> None:  # noqa: CCR001
    """Show the AST Codex window."""
    global data
    global data_initialised
    global tk_to_ttk_migration

    logger.info("Opening AST Codex ...")

    new_data_exists = ((os.path.getmtime(soldbiodata_file)
                       > soldbiodata_file_mtime) or
                       (os.path.getmtime(notsoldbiodata_file)
                       > notsoldbiodata_file_mtime))

    # while True:
    if plugin.AST_debug.get():
        logger.debug("Checking if data is initialised ...")
        logger.debug(data_initialised)

        logger.debug(soldbiodata_file_mtime)
        logger.debug(notsoldbiodata_file_mtime)

        logger.debug(os.path.getmtime(soldbiodata_file))
        logger.debug(os.path.getmtime(notsoldbiodata_file))

    if new_data_exists:
        data_initialised = False

    if data_initialised:
        # check if file was changed since last initialisation
        try:
            plugin.init_thread.join()
            plugin.init_thread = None
        except Exception as e:
            logger.error(f"Error: {e}")

        if not new_data_exists:
            # data is still initialised. The old data is still the same
            pass
        else:
            data_initialised = False
            if plugin.AST_debug.get():
                logger.debug("Starting new initialisation thread ...")

            plugin.init_thread = threading.Thread(target=init_data)
            plugin.init_thread.start()
            plugin.init_thread.join()
            data_initialised = True
            plugin.init_thread = None
    else:
        if plugin.init_thread is not None:
            return

        if plugin.AST_debug.get():
            logger.debug("Starting new initialisation thread ...")

        plugin.init_thread = threading.Thread(target=init_data)
        plugin.init_thread.start()
        plugin.init_thread.join()
        data_initialised = True
        plugin.init_thread = None

    if plugin.AST_debug.get():
        logger.debug("After Init thread concluded")

    if plugin.newwindowrequested:
        if plugin.AST_debug.get():
            logger.debug("New window is requested")
        return

    if plugin.AST_debug.get():
        logger.debug("Creating Window")

    plugin.AST_Codex_window = tk.Tk()
    plugin.AST_Codex_window.title("AST Codex")

    logger.info(f"{theme}")

    if tk_to_ttk_migration:
        # Initialize theme Object for AST Codex
        themething = ASTTheme(plugin.AST_Codex_window)

    titlegap = tk.ttk.Label(plugin.AST_Codex_window, text=" ")
    titlegap.grid(row=0, column=0, sticky="nsew", pady=(0, 0))

    tab_control = tk.ttk.Notebook(plugin.AST_Codex_window)

    tab1 = tk.ttk.Frame(tab_control)
    tab2 = tk.ttk.Frame(tab_control)

    # tk.Grid.rowconfigure(plugin.AST_Codex_window, 0, weight=0)
    tk.Grid.rowconfigure(plugin.AST_Codex_window, 1, weight=10)
    tk.Grid.columnconfigure(plugin.AST_Codex_window, 0, weight=10)

    tab1.grid(row=0, column=0, sticky="nsew")
    tab2.grid(row=0, column=0, sticky="nsew")

    tab_control.add(tab1, text="Table View")
    tab_control.add(tab2, text="Tree View")
    tab_control.grid(row=1, column=0, sticky='nsew')

    columns = ["System", "Body", "Species", "Value", "Sold"]

    tree = tk.ttk.Treeview(tab1, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col:
                     tree_sort_column(tree, _col, False))

    for col in columns:
        tree.column(col, width=75, stretch=True)

    if plugin.AST_debug.get():
        logger.debug("Rebuild Tree")

    tree_rebuild(tree, cmdr)

    tree.grid(row=1, column=0, sticky="nsew")

    search_label = tk.ttk.Label(tab1, text="Search:")
    search_label.grid(row=0, column=0, sticky=tk.W)

    search_entry = tk.ttk.Entry(tab1, width=30)
    search_entry.grid(row=0, column=0, padx=(55, 0), sticky=tk.W)

    search_button = tk.ttk.Button(tab1,
                                  text="🔍",
                                  command=lambda _search_entry=search_entry:
                                  tree_search_worker(plugin, tree, _search_entry, cmdr),
                                  width=0)
    search_button.grid(row=0, column=0, sticky=tk.W, padx=(250, 0))

    scrollbar = tk.ttk.Scrollbar(tab1,
                                 orient="vertical",
                                 command=tree.yview,
                                 style="AST.Vertical.TScrollbar")
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=1, sticky="nsew")

    ex_tree = tk.ttk.Treeview(tab2)

    ex_tree.heading("#0", text="System", command=lambda: ex_tree_sort_column(ex_tree, "#0", False))

    ex_tree_rebuild(ex_tree, cmdr, "")

    if plugin.AST_debug.get():
        logger.debug("Rebuild Ex Tree")

    ex_tree.grid(row=1, column=0, sticky="nsew")

    search_label2 = tk.ttk.Label(tab2, text="Search:")
    search_label2.grid(row=0, column=0, sticky=tk.W)

    search_entry2 = tk.ttk.Entry(tab2, width=30)
    search_entry2.grid(row=0, column=0, padx=(55, 0), sticky=tk.W)

    search_button2 = tk.ttk.Button(tab2,
                                   text="🔍",
                                   command=lambda _search_entry2=search_entry2:
                                   tree_search_worker_ex(plugin, ex_tree, _search_entry2, cmdr),
                                   width=0)
    search_button2.grid(row=0, column=0, sticky=tk.W, padx=(250, 0))

    scrollbar2 = tk.ttk.Scrollbar(tab2,
                                  orient="vertical",
                                  command=ex_tree.yview,
                                  style="AST.Vertical.TScrollbar")
    ex_tree.configure(yscrollcommand=scrollbar2.set)
    scrollbar2.grid(row=1, column=1, sticky="nsew")

    tab1.columnconfigure((1, 0), weight=10)
    tab1.columnconfigure((1, 1), weight=0)
    tab1.rowconfigure((1, 1), weight=10)

    tab2.columnconfigure((1, 0), weight=10)
    tab2.columnconfigure((1, 1), weight=0)
    tab2.rowconfigure((1, 1), weight=10)

    if plugin.AST_debug.get():
        logger.debug("Going in main loop")

    if tk_to_ttk_migration:
        themething.apply()

        applied_theme = themething.active
        transparent = themething.active_transparent

    # plugin.AST_Codex_window.mainloop()
    while True:
        try:
            plugin.AST_Codex_window.grab_status()
            if tk_to_ttk_migration:
                if (applied_theme != theme.active) or (transparent != theme.active_transparent):
                    applied_theme, transparent = themething.apply()
                    # break
            if plugin.newwindowrequested:
                logger.debug("New window is requested")
                try:
                    plugin.AST_Codex_window.destroy()
                except Exception as e:
                    logger.error(f"Error: {e}")
                break
            plugin.AST_Codex_window.update_idletasks()
            plugin.AST_Codex_window.update()

            if not testmode and not tk_to_ttk_migration:
                theme.update(plugin.AST_Codex_window)
        except Exception as e:
            logger.error(f"Error: {e}")
            break

    logger.info("Closing AST Codex ...")

    plugin.AST_Codex_window = None
    plugin.newwindowrequested = False

    gc.collect()

# endregion

# region AST Main UI


def clear_ui(frame) -> None:
    """Remove all labels from this plugin."""
    # remove all labels from the frame
    for label in frame.winfo_children():
        label.destroy()


def rebuild_ui(plugin, cmdr: str) -> None:  # noqa: CCR001
    """Rebuild the UI in case of preferences change."""
    global tk_to_ttk_migration
    if plugin.AST_debug.get():
        logger.debug("Rebuilding UI ...")

    clear_ui(plugin.frame)

    # recreate UI
    current_row = 0

    if tk_to_ttk_migration:
        style = tk.ttk.Style()
        style.configure("AST.green.TLabel", foreground="green")
        style.configure("AST.red.TLabel", foreground="red")

    if plugin.updateavailable:
        latest = f"https://github.com/{plugin.AST_REPO}/releases/latest"
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
                # Copy to Clipboard button
                if tk_to_ttk_migration:
                    clippy_button = tk.ttk.Button(plugin.frame, text="📋", command=plugin.clipboard, width=0)
                else:
                    clippy_button = tk.Button(plugin.frame, text="📋", command=plugin.clipboard)
                clippy_button.grid(row=current_row, column=2, sticky=tk.E)
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

    if plugin.AST_hide_CODEX_button.get() != 1:
        if tk_to_ttk_migration:
            codex_button = button(plugin.frame,
                                  " Open AST Codex ",
                                  plugin.show_codex_window_worker,
                                  current_row,
                                  0,
                                  tk.W)
        else:
            codex_button = tk.Button(plugin.frame, text=" Open AST Codex ", command=plugin.show_codex_window_worker)
            codex_button.grid(row=current_row, column=0, sticky=tk.W)
        current_row += 1

    # Tracked sold bio scans as the last thing to add to the UI
    if plugin.AST_hide_sold_bio.get() != 1:
        build_sold_bio_ui(plugin, cmdr, current_row)

    if not testmode and not tk_to_ttk_migration:
        # Apply theme colours to the frame and its children, including the new widgets
        theme.update(plugin.frame)


def build_sold_bio_ui(plugin, cmdr: str, current_row) -> None:  # noqa: CCR001
    """Build the UI for the sold/scanned exobiology scans in current system."""
    global tk_to_ttk_migration
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

    if tk_to_ttk_migration:
        style = tk.ttk.Style()
        style.configure("AST.green.TLabel", foreground="green")
        style.configure("AST.red.TLabel", foreground="red")

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
        if tk_to_ttk_migration:
            down_button = tk.ttk.Button(plugin.frame, text=" ▼ ", command=plugin.switchhidesoldexobio, width=0)
            down_button.grid(row=current_row, column=2, sticky=tk.W)
        else:
            down_button = tk.Button(plugin.frame, text=" ▼ ", command=plugin.switchhidesoldexobio)
            down_button.grid(row=current_row, column=2, sticky=tk.W)
    else:
        if tk_to_ttk_migration:
            up_button = tk.ttk.Button(plugin.frame, text=" ▲ ", command=plugin.switchhidesoldexobio, width=0)
            up_button.grid(row=current_row, column=2, sticky=tk.W)
        else:
            up_button = tk.Button(plugin.frame, text=" ▲ ", command=plugin.switchhidesoldexobio)
            up_button.grid(row=current_row, column=2, sticky=tk.W)

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

            if currentbody in bodylist:
                colour = "green"

            colourlabel(plugin.frame, species, current_row, 0, colour, tk.W)
            label(plugin.frame, bodies, current_row, 1, tk.W)

# endregion
