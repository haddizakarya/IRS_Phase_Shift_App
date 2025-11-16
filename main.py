import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
matplotlib.use('Agg')  # use non-interactive backend for saving when needed
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd


class IRSPhaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IRS Phase Shift Visualizer")
        self.root.geometry("760x620")
        self.root.resizable(False, False)

        self.last_phases = None

        self.setup_style()
        self.build_ui()

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 11))

    def build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        input_frame = ttk.LabelFrame(container, text="Inputs", padding=8)
        input_frame.grid(row=0, column=0, sticky="nw", padx=6, pady=6)

        ttk.Label(input_frame, text="Number of Elements (N):").grid(row=0, column=0, sticky="w")
        self.entry_N = ttk.Entry(input_frame, width=12)
        self.entry_N.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(input_frame, text="Incident Angle θᵢ (deg):").grid(row=1, column=0, sticky="w")
        self.entry_theta_i = ttk.Entry(input_frame, width=12)
        self.entry_theta_i.grid(row=1, column=1, padx=6, pady=4)

        ttk.Label(input_frame, text="Reflection Angle θᵣ (deg):").grid(row=2, column=0, sticky="w")
        self.entry_theta_r = ttk.Entry(input_frame, width=12)
        self.entry_theta_r.grid(row=2, column=1, padx=6, pady=4)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=8, sticky="w")

        ttk.Button(btn_frame, text="Compute", command=self.compute).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Save PNG", command=self.save_png).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Save CSV", command=self.save_csv).grid(row=0, column=2, padx=4)
        ttk.Button(btn_frame, text="Reset", command=self.reset).grid(row=0, column=3, padx=4)

        output_frame = ttk.LabelFrame(container, text="Results", padding=8)
        output_frame.grid(row=0, column=1, sticky="ne", padx=6, pady=6, rowspan=2)

        self.text_output = tk.Text(output_frame, height=18, width=48, wrap="none", font=("Consolas", 10))
        self.text_output.pack(side="left", fill="both", expand=False)

        scroll_y = ttk.Scrollbar(output_frame, orient="vertical", command=self.text_output.yview)
        scroll_y.pack(side="left", fill="y")
        self.text_output.configure(yscrollcommand=scroll_y.set)

        plot_frame = ttk.LabelFrame(container, text="Plot", padding=8)
        plot_frame.grid(row=1, column=0, sticky="sw", padx=6, pady=6)

        self.fig = plt.Figure(figsize=(7.2, 3.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Element Index")
        self.ax.set_ylabel("Phase (rad)")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        # small help text
        help_txt = ttk.Label(container, text="Enter N (integer), angles in degrees. Click Compute to see phases.")
        help_txt.grid(row=2, column=0, columnspan=2, pady=6, sticky="w")

    def compute(self):
        try:
            N_raw = self.entry_N.get().strip()
            ti_raw = self.entry_theta_i.get().strip()
            tr_raw = self.entry_theta_r.get().strip()

            if not N_raw or not ti_raw or not tr_raw:
                raise ValueError("Fill all input fields.")

            N = int(N_raw)
            if N <= 0 or N > 10000:
                raise ValueError("N must be between 1 and 10000.")

            theta_i = float(ti_raw)
            theta_r = float(tr_raw)

            theta_i_rad = np.radians(theta_i)
            theta_r_rad = np.radians(theta_r)
            delta = np.sin(theta_r_rad) - np.sin(theta_i_rad)

            n = np.arange(N)
            phases = -2 * np.pi * delta * n
            self.last_phases = phases

            self.text_output.delete("1.0", tk.END)
            for i, ph in enumerate(phases):
                self.text_output.insert(tk.END, f"{i:04d} | Phase = {ph: .6f} rad\n")

            # update plot
            self.ax.clear()
            self.ax.plot(phases, marker='o', linestyle='-', markersize=4)
            self.ax.set_title("IRS Phase Shift Distribution")
            self.ax.set_xlabel("Element Index")
            self.ax.set_ylabel("Phase (rad)")
            self.ax.grid(True)
            self.canvas.draw()

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_png(self):
        if self.last_phases is None:
            messagebox.showerror("Error", "Compute phase shifts first.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Image", "*.png")],
                                            title="Save plot as PNG")
        if file:
            try:
                # save a fresh figure (to ensure proper size)
                fig = plt.Figure(figsize=(8, 3.5), dpi=200)
                ax = fig.add_subplot(111)
                ax.plot(self.last_phases, marker='o', linestyle='-')
                ax.set_title("IRS Phase Shift Distribution")
                ax.set_xlabel("Element Index")
                ax.set_ylabel("Phase (rad)")
                ax.grid(True)
                fig.tight_layout()
                fig.savefig(file, dpi=300)
                plt.close(fig)
                messagebox.showinfo("Saved", f"Plot saved to:\n{file}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def save_csv(self):
        if self.last_phases is None:
            messagebox.showerror("Error", "Compute phase shifts first.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV File", "*.csv")],
                                            title="Save phase data as CSV")
        if file:
            try:
                df = pd.DataFrame({
                    "Element Index": np.arange(len(self.last_phases)),
                    "Phase (rad)": self.last_phases
                })
                df.to_csv(file, index=False)
                messagebox.showinfo("Saved", f"CSV saved to:\n{file}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def reset(self):
        self.text_output.delete("1.0", tk.END)
        self.entry_N.delete(0, tk.END)
        self.entry_theta_i.delete(0, tk.END)
        self.entry_theta_r.delete(0, tk.END)
        self.ax.clear()
        self.ax.set_xlabel("Element Index")
        self.ax.set_ylabel("Phase (rad)")
        self.ax.grid(True)
        self.canvas.draw()
        self.last_phases = None


def main():
    root = tk.Tk()
    app = IRSPhaseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
