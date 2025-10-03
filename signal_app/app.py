from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
        NavigationToolbar2Tk,
    )
    from matplotlib.figure import Figure
    _MATPLOTLIB_IMPORT_ERROR: Exception | None = None
except ImportError as _exc:  # noqa: N816 - keep name consistent for clarity
    FigureCanvasTkAgg = None  # type: ignore[assignment]
    NavigationToolbar2Tk = None  # type: ignore[assignment]
    Figure = None  # type: ignore[assignment]
    _MATPLOTLIB_IMPORT_ERROR = _exc

from signal_app.signals import Signal


class SignalApp(tk.Tk):
    """Main Tkinter window for the DSP Signal Tool."""
    def __init__(self) -> None:
        super().__init__()
        self.title("DSP Signal Tool")
        self.geometry("1000x650")

        self.signals: list[Signal] = []
        self.selected_indices: set[int] = set()

        if _MATPLOTLIB_IMPORT_ERROR is not None:
            raise RuntimeError(
                "Matplotlib is required for plotting. Please install it with 'pip install matplotlib'."
            ) from _MATPLOTLIB_IMPORT_ERROR

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the menu, left controls, and right plotting canvas."""
        self._build_menu()

        root_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        root_pane.pack(fill=tk.BOTH, expand=True)

        # Left: signal list and operations
        left_frame = ttk.Frame(root_pane)
        root_pane.add(left_frame, weight=1)

        right_frame = ttk.Frame(root_pane)
        root_pane.add(right_frame, weight=3)

        # Left: Header row with label and Load button
        header_row = ttk.Frame(left_frame)
        header_row.pack(fill=tk.X, padx=8, pady=(8, 0))
        ttk.Label(header_row, text="Signals").pack(side=tk.LEFT)
        ttk.Button(header_row, text="Load TXT...", command=self._load_signal).pack(
            side=tk.RIGHT
        )

        self.signal_list = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.signal_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.signal_list.bind("<<ListboxSelect>>", self._on_select)

        # Left: Operations frame
        ops = ttk.LabelFrame(left_frame, text="Operations")
        ops.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Multiply
        mult_row = ttk.Frame(ops)
        mult_row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(mult_row, text="Multiply by").pack(side=tk.LEFT)
        self.multiply_var = tk.StringVar(value="1.0")
        mult_entry = ttk.Entry(mult_row, width=8, textvariable=self.multiply_var)
        mult_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(mult_row, text="Apply", command=self._on_multiply).pack(side=tk.LEFT)

        # Add / Subtract
        add_row = ttk.Frame(ops)
        add_row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(add_row, text="Add selected", command=self._on_add).pack(side=tk.LEFT)
        ttk.Button(add_row, text="Subtract sel (1st - rest)", command=self._on_subtract).pack(side=tk.LEFT, padx=6)

        # Shift and Fold
        shift_row = ttk.Frame(ops)
        shift_row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(shift_row, text="Shift k").pack(side=tk.LEFT)
        self.shift_var = tk.StringVar(value="0")
        ttk.Entry(shift_row, width=6, textvariable=self.shift_var).pack(side=tk.LEFT, padx=4)
        ttk.Button(shift_row, text="Apply", command=self._on_shift).pack(side=tk.LEFT)
        ttk.Button(shift_row, text="Fold x(-n)", command=self._on_fold).pack(side=tk.LEFT, padx=6)

        # Right: Matplotlib Figure
        fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Signal Plot")
        self.ax.set_xlabel("n")
        self.ax.set_ylabel("x[n]")
        self.ax.grid(True, linestyle=":", alpha=0.6)

        self.canvas = FigureCanvasTkAgg(fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, right_frame)
        toolbar.update()

    def _build_menu(self) -> None:
        """Create the application menu bar."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(
            label="Load Signal from TXT...",
            command=self._load_signal,
            accelerator="Ctrl+O",
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menubar)
        # Keyboard shortcut
        self.bind_all("<Control-o>", lambda _e: self._load_signal())

    def _on_select(self, _event=None) -> None:
        """Handle list selection changes and update plot."""
        self.selected_indices = set(self.signal_list.curselection())
        self._plot_selected()

    def _add_signal(self, sig: Signal) -> None:
        """Append a new signal to the list and display name in the UI."""
        self.signals.append(sig)
        display_name = sig.name or f"Signal {len(self.signals)}"
        self.signal_list.insert(tk.END, display_name)

    def _parse_float(self, s: str, default: float | None = None) -> float:
        """Parse string to float; return default if provided on failure."""
        try:
            return float(s)
        except ValueError:
            if default is not None:
                return default
            raise

    def _parse_int(self, s: str, default: int | None = None) -> int:
        """Parse string to int (via float to accept "3.0"); fallback to default."""
        try:
            return int(float(s))
        except ValueError:
            if default is not None:
                return default
            raise

    # Menu actions
    def _load_signal(self) -> None:
        """Open a file dialog, parse a TXT signal, and add it to the list."""
        path = filedialog.askopenfilename(
            title="Select Signal TXT",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            sig = Signal.from_txt_file(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Load Error", str(exc))
            return
        self._add_signal(sig)

    # Operations
    def _on_multiply(self) -> None:
        """Multiply each selected signal by the provided scalar and add results."""
        if not self.selected_indices:
            messagebox.showinfo("Multiply", "Select at least one signal.")
            return
        scalar = self._parse_float(self.multiply_var.get(), default=1.0)
        for i in sorted(self.selected_indices):
            base = self.signals[i]
            res = base.multiply(scalar, name=f"({base.name or 'sig'})*{scalar}")
            self._add_signal(res)

    def _on_add(self) -> None:
        """Add all selected signals together and append the sum signal."""
        idxs = sorted(self.selected_indices)
        if len(idxs) < 2:
            messagebox.showinfo("Add", "Select two or more signals to add.")
            return
        acc = self.signals[idxs[0]].clone(name="sum")
        for j in idxs[1:]:
            acc = acc.add(self.signals[j])
        acc.name = " + ".join((self.signal_list.get(i) for i in idxs))
        self._add_signal(acc)

    def _on_subtract(self) -> None:
        """Subtract the rest of selected signals from the first one."""
        idxs = sorted(self.selected_indices)
        if len(idxs) < 2:
            messagebox.showinfo(
                "Subtract",
                "Select two or more signals: first minus rest.",
            )
            return
        acc = self.signals[idxs[0]].clone(name="diff")
        for j in idxs[1:]:
            acc = acc.subtract(self.signals[j])
        acc.name = " - ".join((self.signal_list.get(i) for i in idxs))
        self._add_signal(acc)

    def _on_shift(self) -> None:
        """Shift each selected signal by k steps (delay if k>0, advance if k<0)."""
        if not self.selected_indices:
            messagebox.showinfo("Shift", "Select at least one signal.")
            return
        k = self._parse_int(self.shift_var.get(), default=0)
        for i in sorted(self.selected_indices):
            base = self.signals[i]
            res = base.shift(k, name=f"{base.name or 'sig'} shifted {k}")
            self._add_signal(res)

    def _on_fold(self) -> None:
        """Fold (time-reverse) each selected signal: x(-n)."""
        if not self.selected_indices:
            messagebox.showinfo("Fold", "Select at least one signal.")
            return
        for i in sorted(self.selected_indices):
            base = self.signals[i]
            res = base.fold(name=f"fold({base.name or 'sig'})")
            self._add_signal(res)

    def _plot_selected(self) -> None:
        """Render selected signals to the Matplotlib axes."""
        self.ax.clear()
        self.ax.set_title("Signal Plot")
        self.ax.set_xlabel("n")
        self.ax.set_ylabel("x[n]")
        self.ax.grid(True, linestyle=":", alpha=0.6)

        for idx in sorted(self.selected_indices) or []:
            sig = self.signals[idx]
            xs, ys = sig.to_sorted_series()
            if xs:
                self.ax.stem(xs, ys, label=self.signal_list.get(idx))
        if self.selected_indices:
            self.ax.legend(loc="best")
        self.canvas.draw_idle()


def main() -> None:
    """Entrypoint to launch the Tkinter application."""
    app = SignalApp()
    app.mainloop()


if __name__ == "__main__":
    main()