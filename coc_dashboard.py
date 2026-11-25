"""
Clash of Clans Upgrade Dashboard
--------------------------------
Paste your village JSON export (or open a .json file) and see every running
upgrade with a live countdown. Standard library only, nothing to install.
"""
import json
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Your last export is saved here, so the dashboard is filled in when you reopen it.
SAVE_FILE = Path(__file__).with_name("last_export.json")

# ---------------------------------------------------------------- game data
# Which part of the export each list is, and who does the work.
# (village, worker, label used when a name is unknown)
SECTIONS = {
    "buildings":      ("Home Village", "Builder",    "Building"),
    "traps":          ("Home Village", "Builder",    "Trap"),
    "heroes":         ("Home Village", "Builder",    "Hero"),
    "units":          ("Home Village", "Lab",        "Troop"),
    "spells":         ("Home Village", "Lab",        "Spell"),
    "siege_machines": ("Home Village", "Lab",        "Siege"),
    "pets":           ("Home Village", "Pet House",  "Pet"),
    "equipment":      ("Home Village", "Blacksmith", "Equipment"),
    "buildings2":     ("Builder Base", "Builder",    "Building"),
    "traps2":         ("Builder Base", "Builder",    "Trap"),
    "heroes2":        ("Builder Base", "Builder",    "Hero"),
    "units2":         ("Builder Base", "Star Lab",   "Troop"),
}

# The export only has numeric IDs. Troop, spell, hero, pet and siege names come from
# the game's data tables (export ID = category prefix + table index). Building names
# beyond ~1000070 are less certain. Anything missing shows up as e.g.
# "Building #1000106": add it here.
NAMES = {
    # Home village buildings
    1000000: "Army Camp", 1000001: "Town Hall", 1000002: "Elixir Collector",
    1000003: "Elixir Storage", 1000004: "Gold Mine", 1000005: "Gold Storage",
    1000006: "Barracks", 1000007: "Laboratory", 1000008: "Cannon", 1000009: "Archer Tower",
    1000010: "Wall", 1000011: "Wizard Tower", 1000012: "Air Defense", 1000013: "Mortar",
    1000014: "Clan Castle", 1000015: "Builder's Hut", 1000019: "Hidden Tesla",
    1000020: "Spell Factory", 1000021: "X-Bow", 1000022: "Barbarian King Altar",
    1000023: "Dark Elixir Drill", 1000024: "Dark Elixir Storage",
    1000025: "Archer Queen Altar", 1000026: "Dark Barracks", 1000027: "Inferno Tower",
    1000028: "Air Sweeper", 1000029: "Dark Spell Factory", 1000030: "Grand Warden Altar",
    1000031: "Eagle Artillery", 1000032: "Bomb Tower", 1000059: "Workshop",
    1000066: "Royal Champion Altar", 1000067: "Scattershot", 1000068: "Pet House",
    1000070: "Blacksmith", 1000071: "Hero Hall", 1000072: "Spell Tower",
    1000077: "Monolith",
    # Builder base buildings
    1000033: "Wall (BB)", 1000034: "Builder Hall", 1000035: "Elixir Collector (BB)",
    1000036: "Elixir Storage (BB)", 1000037: "Gold Mine (BB)", 1000038: "Gold Storage (BB)",
    1000039: "Clock Tower", 1000040: "Barracks (BB)", 1000041: "Double Cannon",
    1000042: "Army Camp (BB)", 1000043: "Hidden Tesla (BB)", 1000044: "Cannon (BB)",
    1000045: "Multi Mortar", 1000046: "Star Laboratory", 1000048: "Archer Tower (BB)",
    1000050: "Air Bombs", 1000051: "Guard Post", 1000052: "Mega Tesla",
    1000053: "Battle Machine Altar", 1000055: "Crusher", 1000057: "Giant Cannon",
    1000058: "Gem Mine", 1000063: "Lava Launcher", 1000080: "Battle Copter Altar",
    # Heroes (home + builder base)
    28000000: "Barbarian King", 28000001: "Archer Queen", 28000002: "Grand Warden",
    28000003: "Battle Machine", 28000004: "Royal Champion", 28000005: "Battle Copter",
    28000006: "Minion Prince", 28000007: "Dragon Duke",
    # Home troops
    4000000: "Barbarian", 4000001: "Archer", 4000002: "Goblin", 4000003: "Giant",
    4000004: "Wall Breaker", 4000005: "Balloon", 4000006: "Wizard", 4000007: "Healer",
    4000008: "Dragon", 4000009: "P.E.K.K.A", 4000010: "Minion", 4000011: "Hog Rider",
    4000012: "Valkyrie", 4000013: "Golem", 4000015: "Witch", 4000017: "Lava Hound",
    4000022: "Bowler", 4000023: "Baby Dragon", 4000024: "Miner", 4000026: "Super Barbarian",
    4000027: "Super Archer", 4000028: "Super Wall Breaker", 4000029: "Super Giant",
    4000053: "Yeti", 4000055: "Sneaky Goblin", 4000056: "Super Miner",
    4000057: "Rocket Balloon", 4000058: "Ice Golem", 4000059: "Electro Dragon",
    4000063: "Inferno Dragon", 4000064: "Super Valkyrie", 4000065: "Dragon Rider",
    4000066: "Super Witch", 4000076: "Ice Hound", 4000080: "Super Bowler",
    4000081: "Super Dragon", 4000082: "Headhunter", 4000083: "Super Wizard",
    4000084: "Super Minion", 4000095: "Electro Titan", 4000097: "Apprentice Warden",
    4000098: "Super Hog Rider", 4000110: "Root Rider", 4000123: "Druid", 4000132: "Thrower",
    4000147: "Super Yeti", 4000150: "Furnace", 4000177: "Meteor Golem",
    # Siege machines
    4000051: "Wall Wrecker", 4000052: "Battle Blimp", 4000062: "Stone Slammer",
    4000075: "Siege Barracks", 4000087: "Log Launcher", 4000091: "Flame Flinger",
    4000092: "Battle Drill", 4000135: "Troop Launcher", 4000188: "Sky Wagon",
    # Builder base troops
    4000031: "Raged Barbarian", 4000032: "Sneaky Archer", 4000033: "Beta Minion",
    4000034: "Boxer Giant", 4000035: "Bomber", 4000036: "Power P.E.K.K.A",
    4000037: "Cannon Cart", 4000038: "Drop Ship", 4000041: "Baby Dragon",
    4000042: "Night Witch", 4000070: "Hog Glider", 4000106: "Electrofire Wizard",
    # Spells
    26000000: "Lightning Spell", 26000001: "Healing Spell", 26000002: "Rage Spell",
    26000003: "Jump Spell", 26000005: "Freeze Spell", 26000009: "Poison Spell",
    26000010: "Earthquake Spell", 26000011: "Haste Spell", 26000016: "Clone Spell",
    26000017: "Skeleton Spell", 26000028: "Bat Spell", 26000035: "Invisibility Spell",
    26000053: "Recall Spell", 26000070: "Overgrowth Spell", 26000098: "Revive Spell",
    26000109: "Ice Block Spell", 26000120: "Totem Spell",
    # Pets
    73000000: "L.A.S.S.I", 73000001: "Mighty Yak", 73000002: "Electro Owl",
    73000003: "Unicorn", 73000004: "Phoenix", 73000007: "Poison Lizard", 73000008: "Diggy",
    73000009: "Frosty", 73000010: "Spirit Fox", 73000011: "Angry Jelly", 73000016: "Sneezy",
    73000017: "Greedy Raven",
}

HELPERS = {
    93000000: "Builder's Apprentice", 93000001: "Lab Assistant",
    93000002: "Alchemist", 93000003: "Prospector",
}

# ------------------------------------------------------------------- colours
BG, PANEL, CARD = "#14141f", "#1e1e2e", "#2a2a3d"
FG, MUTED = "#f5f5f5", "#9a9ab0"
GOLD, GREEN, ORANGE = "#f5c542", "#5fd38d", "#ff9f43"
FONT = "Segoe UI"


# ------------------------------------------------------------------- helpers
def fmt(seconds):
    """1d 3h 12m / 3h 12m 5s / 12m 5s"""
    seconds = max(0, int(seconds))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if d:
        return f"{d}d {h}h {m}m"
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def fmt_clock(ts):
    """Local date/time, e.g. 'Mon Nov 23, 3:12 PM'."""
    return time.strftime("%a %b %d, %I:%M %p", time.localtime(ts)).replace(" 0", " ")


def extract(data):
    """Pull running upgrades, helper cooldowns and the Clock Tower boost out of an export.

    Every 'timer' in the export is seconds left *at the moment of export*
    (data['timestamp']), so finish time = timestamp + timer.
    """
    base = data.get("timestamp") or time.time()

    upgrades = []
    for key, items in data.items():
        if not isinstance(items, list):
            continue
        village, worker, kind = SECTIONS.get(key, (
            "Builder Base" if key.endswith("2") else "Home Village",
            "Other", key.replace("_", " ").title()))
        for item in items:
            if not isinstance(item, dict) or not item.get("timer"):
                continue
            ident = item.get("data")
            lvl = item.get("lvl", 0)
            upgrades.append({
                "village": village,
                "worker": worker,
                "name": NAMES.get(ident, f"{kind} #{ident}"),
                "level": f"{lvl} → {lvl + 1}" if lvl else "New → 1",
                "finish": base + item["timer"],
            })
    upgrades.sort(key=lambda u: u["finish"])

    helpers = []
    for h in data.get("helpers", []):
        if isinstance(h, dict):
            name = HELPERS.get(h.get("data"), f"Helper #{h.get('data')}")
            helpers.append((name, base + h.get("helper_cooldown", 0)))

    boosts = data.get("boosts")
    clock = None
    if isinstance(boosts, dict) and boosts.get("clocktower_cooldown") is not None:
        clock = ("Clock Tower boost", base + boosts["clocktower_cooldown"])

    return upgrades, helpers, clock


# ----------------------------------------------------------------------- app
class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clash of Clans Upgrade Dashboard")
        self.geometry("1000x680")
        self.minsize(860, 560)
        self.configure(bg=BG)

        self.upgrades, self.timers, self.export_ts = [], [], None
        self.timer_labels = []
        self.source = ""
        self.notified = set()
        self.last_text = ""
        self.view = tk.StringVar(value="All")
        self.auto = tk.BooleanVar(value=True)

        self.setup_style()
        self.build()
        self.bind("<FocusIn>", self.on_focus)
        self.restore()
        self.tick()

    # ---- look
    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=FG, rowheight=30, borderwidth=0,
                        font=(FONT, 10))
        style.configure("Treeview.Heading", background=PANEL, foreground=GOLD,
                        font=(FONT, 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#44446a")])
        style.configure("Vertical.TScrollbar", background=PANEL,
                        troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)

    def card(self, parent, title):
        frame = tk.Frame(parent, bg=CARD, padx=14, pady=8)
        tk.Label(frame, text=title.upper(), bg=CARD, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        value = tk.Label(frame, text="–", bg=CARD, fg=FG, font=(FONT, 16, "bold"))
        value.pack(anchor="w")
        sub = tk.Label(frame, text="", bg=CARD, fg=MUTED, font=(FONT, 9))
        sub.pack(anchor="w")
        return frame, value, sub

    def build(self):
        # header
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=18, pady=(14, 0))
        tk.Label(head, text="⚔  Upgrade Dashboard", bg=BG, fg=GOLD,
                 font=(FONT, 22, "bold")).pack(side="left")
        self.tag = tk.Label(head, text="", bg=BG, fg=MUTED, font=(FONT, 11))
        self.tag.pack(side="right")
        self.status = tk.Label(self, text="Export your village in the game, then paste it here",
                               bg=BG, fg=MUTED, font=(FONT, 10), anchor="w")
        self.status.pack(fill="x", padx=18, pady=(0, 8))

        # toolbar
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=18)
        for text, cmd in [("📋 Paste from clipboard", self.from_clipboard),
                          ("📂 Open JSON file", self.from_file)]:
            tk.Button(bar, text=text, command=cmd, bg=GOLD, fg="#222", relief="flat",
                      font=(FONT, 10, "bold"), padx=12, pady=4,
                      cursor="hand2").pack(side="left", padx=(0, 8))
        tk.Checkbutton(bar, text="Auto-load when I switch back", variable=self.auto,
                       bg=BG, fg=MUTED, selectcolor=BG, activebackground=BG,
                       activeforeground=FG, font=(FONT, 9)).pack(side="left", padx=8)
        for label in ("Builder Base", "Home Village", "All"):
            tk.Radiobutton(bar, text=label, value=label, variable=self.view,
                           command=self.refresh_table, indicatoron=0, bg=PANEL, fg=FG,
                           selectcolor=GOLD, activebackground=CARD, relief="flat",
                           font=(FONT, 9, "bold"), padx=10, pady=4, bd=0,
                           cursor="hand2").pack(side="right", padx=2)

        # summary cards
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=18, pady=12)
        self.cards = []
        for i, title in enumerate(["In progress", "Next to finish", "Everything done in"]):
            frame, value, sub = self.card(cards, title)
            frame.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            cards.columnconfigure(i, weight=1, uniform="c")
            self.cards.append((value, sub))

        # helpers / boosts
        self.timer_row = tk.Frame(self, bg=BG)
        self.timer_row.pack(fill="x", padx=18, pady=(0, 10))

        # table
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        cols = [("village", "Village", 105), ("worker", "Worker", 90),
                ("name", "Name", 210), ("level", "Level", 90),
                ("left", "Time left", 130), ("finish", "Finishes", 170)]
        self.tree = ttk.Treeview(wrap, columns=[c[0] for c in cols], show="headings")
        for key, title, width in cols:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="w" if key == "name" else "center")
        self.tree.tag_configure("done", foreground=GREEN)
        self.tree.tag_configure("soon", foreground=ORANGE)
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # ---- loading data
    def from_clipboard(self):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            messagebox.showerror("Error", "The clipboard is empty.")
            return
        self.load_text(text, "clipboard")

    def from_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as e:
            messagebox.showerror("Error", f"Couldn't read the file:\n{e}")
            return
        self.load_text(text, Path(path).name)

    def on_focus(self, event):
        """When you come back from the game/browser, pick up a fresh export from the clipboard."""
        if event.widget is not self or not self.auto.get():
            return
        try:
            text = self.clipboard_get()
        except tk.TclError:
            return
        if text != self.last_text and text.lstrip().startswith("{") and '"timestamp"' in text:
            self.load_text(text, "clipboard", quiet=True)

    def restore(self):
        if SAVE_FILE.exists():
            try:
                self.load_text(SAVE_FILE.read_text(encoding="utf-8"), "saved copy",
                               quiet=True, save=False)
            except OSError:
                pass

    def load_text(self, text, source, quiet=False, save=True):
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError
        except ValueError:
            if not quiet:
                messagebox.showerror("Error", "That isn't valid village JSON.")
            return False

        self.last_text = text
        self.source = source
        self.export_ts = data.get("timestamp") or time.time()
        upgrades, helpers, clock = extract(data)
        self.upgrades = upgrades
        self.timers = helpers + ([clock] if clock else [])
        self.tag.config(text=data.get("tag", ""))

        now = time.time()
        # don't beep for things that were already finished when loaded
        self.notified = {i for i, u in enumerate(self.upgrades) if u["finish"] <= now}

        self.build_timer_row()
        self.refresh_table()

        if save:
            try:
                SAVE_FILE.write_text(text, encoding="utf-8")
            except OSError:
                pass
        return True

    # ---- showing data
    def build_timer_row(self):
        for child in self.timer_row.winfo_children():
            child.destroy()
        self.timer_labels = []
        for i, (name, _finish) in enumerate(self.timers):
            frame, value, _sub = self.card(self.timer_row, name)
            frame.pack(side="left", padx=(0 if i == 0 else 8, 0), fill="y")
            value.config(font=(FONT, 12, "bold"))
            self.timer_labels.append(value)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        view = self.view.get()
        for i, u in enumerate(self.upgrades):
            if view != "All" and u["village"] != view:
                continue
            self.tree.insert("", "end", iid=str(i),
                             values=(u["village"], u["worker"], u["name"], u["level"],
                                     "", fmt_clock(u["finish"])))
        self.update_live()

    def update_live(self):
        now = time.time()

        running = []
        for i, u in enumerate(self.upgrades):
            left = u["finish"] - now
            if left > 0:
                running.append((left, u))
            elif i not in self.notified:
                self.notified.add(i)
                self.bell()  # an upgrade just finished

        for iid in self.tree.get_children():
            left = self.upgrades[int(iid)]["finish"] - now
            if left <= 0:
                text, tag = "✅ Done!", "done"
            else:
                text, tag = fmt(left), ("soon" if left < 3600 else "normal")
            self.tree.set(iid, "left", text)
            self.tree.item(iid, tags=(tag,))

        # cards
        count, nxt, last = self.cards
        if running:
            soonest = min(running, key=lambda r: r[0])
            latest = max(running, key=lambda r: r[0])
            count[0].config(text=str(len(running)))
            count[1].config(text=f"of {len(self.upgrades)} in this export")
            nxt[0].config(text=fmt(soonest[0]))
            nxt[1].config(text=soonest[1]["name"])
            last[0].config(text=fmt(latest[0]))
            last[1].config(text=latest[1]["name"])
        else:
            for value, sub in self.cards:
                value.config(text="–")
                sub.config(text="")
            count[1].config(text="Nothing running" if self.export_ts else "")

        # helpers + clock tower
        for label, (_name, finish) in zip(self.timer_labels, self.timers):
            left = finish - now
            label.config(text="Ready ✅" if left <= 0 else fmt(left),
                         fg=GREEN if left <= 0 else FG)

        # status line
        if self.export_ts:
            ago = fmt(now - self.export_ts)
            msg = f"Exported {fmt_clock(self.export_ts)} ({ago} ago) · from {self.source}"
            if self.upgrades and not running:
                msg += " · everything has finished, export again to refresh"
            self.status.config(text=msg)

    def tick(self):
        self.update_live()
        self.after(1000, self.tick)


if __name__ == "__main__":
    Dashboard().mainloop()