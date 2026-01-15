# benchmark_module.py
import tkinter as tk
from tkinter import ttk, messagebox


def _benchmark(pages, max_frames, simulate_fn):
    results = []
    for f in range(1, max_frames + 1):
        _, fifo_faults, lru_faults = simulate_fn(pages, f)

        if lru_faults < fifo_faults:
            winner = "LRU"
        elif fifo_faults < lru_faults:
            winner = "FIFO"
        else:
            winner = "TIE"

        results.append((f, fifo_faults, lru_faults, winner, abs(fifo_faults - lru_faults)))
    return results


def install_benchmark(root, top_frame, btns_frame, pages_var, simulate_fn, parse_pages_fn):
    """
    Adds:
      - Benchmark up to: [Spinbox]
      - Benchmark button
    Uses your existing simulate() + parse_pages().
    """

    bench_var = tk.StringVar(value="10")

    # Put "Benchmark up to" controls on the TOP row (same row as Frames)
    ttk.Label(top_frame, text="Benchmark up to:").grid(
        row=1, column=4, sticky="w", pady=(8, 0), padx=(12, 0)
    )
    ttk.Spinbox(top_frame, from_=1, to=50, textvariable=bench_var, width=6).grid(
        row=1, column=5, sticky="w", pady=(8, 0), padx=(8, 0)
    )

    def on_benchmark():
        pages = parse_pages_fn(pages_var.get())
        if not pages:
            messagebox.showerror("Invalid Input", "Enter at least 1 page (string).")
            return

        try:
            max_f = int(bench_var.get())
            if max_f <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Benchmark Frames", "Benchmark max frames must be a positive integer.")
            return

        data = _benchmark(pages, max_f, simulate_fn)

        win = tk.Toplevel(root)
        win.title("Benchmark: FIFO vs LRU")
        win.geometry("720x520")

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)

        cols = ("Frames", "FIFO Faults", "LRU Faults", "Winner", "Difference")
        t = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for c in cols:
            t.heading(c, text=c)
            t.column(c, anchor="center")

        t.tag_configure("lru_win", background="#eaffea")
        t.tag_configure("fifo_win", background="#e6f0ff")
        t.tag_configure("tie", background="white")

        vs = ttk.Scrollbar(frame, orient="vertical", command=t.yview)
        t.configure(yscrollcommand=vs.set)

        t.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        lru_wins = fifo_wins = ties = 0
        fifo_sum = lru_sum = 0

        for f, fifo_faults, lru_faults, winner, diff in data:
            fifo_sum += fifo_faults
            lru_sum += lru_faults

            if winner == "LRU":
                tag = "lru_win"
                lru_wins += 1
            elif winner == "FIFO":
                tag = "fifo_win"
                fifo_wins += 1
            else:
                tag = "tie"
                ties += 1

            t.insert("", "end", values=(f, fifo_faults, lru_faults, winner, diff), tags=(tag,))

        avg_fifo = fifo_sum / len(data)
        avg_lru = lru_sum / len(data)

        ttk.Label(
            frame,
            text=f"LRU wins: {lru_wins} | FIFO wins: {fifo_wins} | Ties: {ties}   "
                 f"(Avg faults → FIFO: {avg_fifo:.2f}, LRU: {avg_lru:.2f})",
            font=("Segoe UI", 10, "bold")
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

    # Add the Benchmark button next to Run/Clear/Load Demo
    ttk.Button(btns_frame, text="Benchmark", command=on_benchmark).grid(
        row=0, column=3, padx=(8, 0)
    )
