import tkinter as tk
from tkinter import ttk, messagebox
from benchmark_module import install_benchmark

# ---------------- Simulation ----------------
def simulate(pages, frames):
    fifo, lru = [], []
    fifo_faults = lru_faults = 0
    rows = []

    for i, p in enumerate(pages, start=1):
        # FIFO
        fifo_hit = p in fifo
        if not fifo_hit:
            fifo_faults += 1
            if len(fifo) == frames:
                fifo.pop(0)
            fifo.append(p)

        # LRU
        lru_hit = p in lru
        if lru_hit:
            lru.remove(p)
        else:
            lru_faults += 1
            if len(lru) == frames:
                lru.pop(0)
        lru.append(p)

        rows.append({
            "step": i,
            "req": p,
            "fifo_status": "HIT" if fifo_hit else "FAULT",
            "fifo_frames": fifo.copy(),
            "lru_status": "HIT" if lru_hit else "FAULT",
            "lru_frames": lru.copy(),
        })

    return rows, fifo_faults, lru_faults


def parse_pages(raw: str):
    raw = raw.replace(",", " ").strip()
    return [x for x in raw.split() if x]

# ---------------- UI Helpers ----------------
def clear_table():
    for item in tree.get_children():
        tree.delete(item)

def set_status_label(lbl, status):
    if status == "HIT":
        lbl.config(text="HIT", fg="#0b6b2a")
    else:
        lbl.config(text="FAULT", fg="#b00020")

def build_frame_boxes(frames):
    # clear old boxes
    for w in fifo_boxes_frame.winfo_children():
        w.destroy()
    for w in lru_boxes_frame.winfo_children():
        w.destroy()

    fifo_box_labels.clear()
    lru_box_labels.clear()

    for _ in range(frames):
        lab = tk.Label(
            fifo_boxes_frame, text="—", width=14, height=2,
            font=("Consolas", 12, "bold"),
            relief="solid", bd=1, bg="white"
        )
        lab.pack(pady=4, fill="x")
        fifo_box_labels.append(lab)

    for _ in range(frames):
        lab = tk.Label(
            lru_boxes_frame, text="—", width=14, height=2,
            font=("Consolas", 12, "bold"),
            relief="solid", bd=1, bg="white"
        )
        lab.pack(pady=4, fill="x")
        lru_box_labels.append(lab)

def update_boxes(box_labels, frames_list):
    # show from top to bottom: frame 1..N
    for i, lab in enumerate(box_labels):
        if i < len(frames_list):
            lab.config(text=str(frames_list[i]))
        else:
            lab.config(text="—")

def on_row_select(_event=None):
    sel = tree.selection()
    if not sel:
        return

    item = tree.item(sel[0])
    vals = item["values"]
    # values order: Step, Requested, FIFO, FIFO Frames, LRU, LRU Frames
    step = vals[0]
    req = vals[1]
    fifo_status = vals[2]
    fifo_frames_str = vals[3]
    lru_status = vals[4]
    lru_frames_str = vals[5]

    # parse frames strings back into lists
    fifo_list = [] if fifo_frames_str.strip() == "" else fifo_frames_str.split(" | ")
    lru_list = [] if lru_frames_str.strip() == "" else lru_frames_str.split(" | ")

    req_var.set(str(req))
    step_var.set(str(step))

    set_status_label(fifo_status_lbl, fifo_status)
    set_status_label(lru_status_lbl, lru_status)

    update_boxes(fifo_box_labels, fifo_list)
    update_boxes(lru_box_labels, lru_list)

def on_run():
    pages = parse_pages(pages_var.get())

    try:
        frames = int(frames_var.get())
        if frames <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Frames", "Frames must be a positive integer.")
        return

    if not pages:
        messagebox.showerror("Invalid Input", "Enter at least 1 page (string).")
        return

    build_frame_boxes(frames)
    clear_table()

    rows, fifo_faults, lru_faults = simulate(pages, frames)

    for r in rows:
        fifo_frames_str = " | ".join(r["fifo_frames"])
        lru_frames_str = " | ".join(r["lru_frames"])

        #Extra line to add tags
        tag = "fault_row" if (r["fifo_status"] == "FAULT" or r["lru_status"] == "FAULT") else "hit_row"

        tree.insert(
            "",
            "end",
            values=(r["step"], r["req"], r["fifo_status"], fifo_frames_str, r["lru_status"], lru_frames_str), tags= (tag,)
        )

    fifo_faults_var.set(str(fifo_faults))
    lru_faults_var.set(str(lru_faults))

    if lru_faults < fifo_faults:
        verdict_var.set("LRU wins (fewer page faults).")
    elif lru_faults > fifo_faults:
        verdict_var.set("FIFO wins (fewer page faults).")
    else:
        verdict_var.set("Tie (same number of page faults).")

    # auto-select last row so boxes show something immediately
    children = tree.get_children()
    if children:
        tree.selection_set(children[-1])
        tree.see(children[-1])
        on_row_select()

def on_clear():
    pages_var.set("")
    frames_var.set("3")
    fifo_faults_var.set("0")
    lru_faults_var.set("0")
    verdict_var.set("")
    req_var.set("—")
    step_var.set("—")
    clear_table()
    build_frame_boxes(int(frames_var.get()))

def on_demo():
    pages_var.set("Chrome Gmail YouTube Chrome Gmail Docs Chrome Gmail YouTube")
    frames_var.set("3")


# ---------------- Main Window ----------------
root = tk.Tk()
root.title("Page Replacement Simulator (FIFO vs LRU)")
root.geometry("1200x650")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
style.configure("Treeview", font=("Consolas", 10), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# Root layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

container = ttk.Frame(root, padding=14)
container.grid(row=0, column=0, sticky="nsew")
container.grid_rowconfigure(1, weight=1)
container.grid_columnconfigure(0, weight=1)

# Top controls
top = ttk.Frame(container)
top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
top.grid_columnconfigure(1, weight=1)

ttk.Label(top, text="FIFO vs LRU Page Replacement", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12))

pages_var = tk.StringVar()
frames_var = tk.StringVar(value="3")
fifo_faults_var = tk.StringVar(value="0")
lru_faults_var = tk.StringVar(value="0")
verdict_var = tk.StringVar(value="")

ttk.Label(top, text="Reference string:").grid(row=1, column=0, sticky="w", pady=(8, 0))
ttk.Entry(top, textvariable=pages_var, width=60).grid(row=1, column=1, sticky="ew", pady=(8, 0), padx=(8, 8))

ttk.Label(top, text="Frames:").grid(row=1, column=2, sticky="w", pady=(8, 0))
ttk.Spinbox(top, from_=1, to=20, textvariable=frames_var, width=6).grid(row=1, column=3, sticky="w", pady=(8, 0), padx=(8, 0))

btns = ttk.Frame(top)
btns.grid(row=2, column=1, sticky="w", pady=(10, 0))
ttk.Button(btns, text="Run", command=on_run).grid(row=0, column=0, padx=(0, 8))
ttk.Button(btns, text="Clear", command=on_clear).grid(row=0, column=1, padx=(0, 8))
ttk.Button(btns, text="Load Demo", command=on_demo).grid(row=0, column=2)

#Line of code to benchmark
install_benchmark(
    root=root,
    top_frame=top,
    btns_frame=btns,
    pages_var=pages_var,
    simulate_fn=simulate,
    parse_pages_fn=parse_pages
)


# Middle split: Left visual, Right table
mid = ttk.Frame(container)
mid.grid(row=1, column=0, sticky="nsew")
mid.grid_rowconfigure(0, weight=1)
mid.grid_columnconfigure(1, weight=1)

# -------- Left panel: Memory slots --------
left = ttk.Frame(mid, padding=12)
left.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
left.grid_columnconfigure(0, weight=1)

req_var = tk.StringVar(value="—")
step_var = tk.StringVar(value="—")

ttk.Label(left, text="Selected Step", style="Header.TLabel").grid(row=0, column=0, sticky="w")
ttk.Label(left, text="Step:").grid(row=1, column=0, sticky="w", pady=(8, 0))
ttk.Label(left, textvariable=step_var, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w")
ttk.Label(left, text="Requested:").grid(row=3, column=0, sticky="w", pady=(10, 0))
ttk.Label(left, textvariable=req_var, font=("Consolas", 12, "bold")).grid(row=4, column=0, sticky="w")

ttk.Separator(left).grid(row=5, column=0, sticky="ew", pady=12)

# FIFO visual
ttk.Label(left, text="FIFO Frames", style="Header.TLabel").grid(row=6, column=0, sticky="w")
fifo_status_row = ttk.Frame(left)
fifo_status_row.grid(row=7, column=0, sticky="w", pady=(6, 6))
ttk.Label(fifo_status_row, text="Status:").pack(side="left")
fifo_status_lbl = tk.Label(fifo_status_row, text="—", font=("Segoe UI", 10, "bold"))
fifo_status_lbl.pack(side="left", padx=8)

fifo_boxes_frame = ttk.Frame(left)
fifo_boxes_frame.grid(row=8, column=0, sticky="ew")

ttk.Separator(left).grid(row=9, column=0, sticky="ew", pady=12)

# LRU visual
ttk.Label(left, text="LRU Frames", style="Header.TLabel").grid(row=10, column=0, sticky="w")
lru_status_row = ttk.Frame(left)
lru_status_row.grid(row=11, column=0, sticky="w", pady=(6, 6))
ttk.Label(lru_status_row, text="Status:").pack(side="left")
lru_status_lbl = tk.Label(lru_status_row, text="—", font=("Segoe UI", 10, "bold"))
lru_status_lbl.pack(side="left", padx=8)

lru_boxes_frame = ttk.Frame(left)
lru_boxes_frame.grid(row=12, column=0, sticky="ew")

fifo_box_labels = []
lru_box_labels = []

# -------- Right panel: Table --------
right = ttk.Frame(mid)
right.grid(row=0, column=1, sticky="nsew")
right.grid_rowconfigure(0, weight=1)
right.grid_columnconfigure(0, weight=1)

columns = ("Step", "Requested", "FIFO", "FIFO Frames", "LRU", "LRU Frames")
tree = ttk.Treeview(right, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)

#New line to change colour
# ---- Row coloring (FAULT = red, HIT = white) ----
tree.tag_configure("fault_row", background="#ffd6d6")  # light red
tree.tag_configure("hit_row", background="white")


tree.column("Step", width=60, anchor="center")
tree.column("Requested", width=160, anchor="w")
tree.column("FIFO", width=80, anchor="center")
tree.column("FIFO Frames", width=360, anchor="w")
tree.column("LRU", width=80, anchor="center")
tree.column("LRU Frames", width=360, anchor="w")

vsb = ttk.Scrollbar(right, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)

tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

tree.bind("<<TreeviewSelect>>", on_row_select)

# Bottom summary
bottom = ttk.Frame(container, padding=(0, 10, 0, 0))
bottom.grid(row=2, column=0, sticky="ew")

ttk.Label(bottom, text="FIFO faults:").grid(row=0, column=0, sticky="w")
ttk.Label(bottom, textvariable=fifo_faults_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(6, 18))

ttk.Label(bottom, text="LRU faults:").grid(row=0, column=2, sticky="w")
ttk.Label(bottom, textvariable=lru_faults_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=3, sticky="w", padx=(6, 18))

ttk.Label(bottom, textvariable=verdict_var, font=("Segoe UI", 10, "bold")).grid(row=0, column=4, sticky="w")

# Start with default boxes
build_frame_boxes(int(frames_var.get()))
set_status_label(fifo_status_lbl, "FAULT")  # just to color it nicely at start
set_status_label(lru_status_lbl, "FAULT")
req_var.set("—")
step_var.set("—")

root.mainloop()
