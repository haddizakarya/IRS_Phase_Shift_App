import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

last_phases = None

def compute_phase_shift():
    global last_phases
    try:
        N = int(entry_N.get())
        theta_i = float(entry_theta_i.get())
        theta_r = float(entry_theta_r.get())

        theta_i_rad = np.radians(theta_i)
        theta_r_rad = np.radians(theta_r)
        delta = np.sin(theta_r_rad) - np.sin(theta_i_rad)

        n = np.arange(N)
        phases = -2 * np.pi * delta * n
        last_phases = phases

        text_output.delete("1.0", tk.END)
        for i in range(N):
            text_output.insert(tk.END, f"Element {i}: Phase = {phases[i]:.3f} rad\n")

        plt.figure()
        plt.plot(phases, marker='o')
        plt.xlabel("Element Index")
        plt.ylabel("Phase (rad)")
        plt.title("IRS Phase Shift Distribution")
        plt.grid(True)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_plot_png():
    try:
        if last_phases is None:
            messagebox.showerror("Error", "Compute phase shift first.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Image", "*.png")])
        if file:
            plt.figure()
            plt.plot(last_phases, marker='o')
            plt.xlabel("Element Index")
            plt.ylabel("Phase (rad)")
            plt.title("IRS Phase Shift Distribution")
            plt.grid(True)
            plt.savefig(file, dpi=300)
            plt.close()
            messagebox.showinfo("Success", "Plot saved as PNG!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_csv():
    try:
        if last_phases is None:
            messagebox.showerror("Error", "Compute phase shift first.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV File", "*.csv")])
        if file:
            df = pd.DataFrame({"Element Index": np.arange(len(last_phases)),
                               "Phase (rad)": last_phases})
            df.to_csv(file, index=False)
            messagebox.showinfo("Success", "Phase data saved as CSV!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("IRS Phase Shift Visualizer")
root.geometry("450x520")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Number of Elements (N):").pack()
entry_N = ttk.Entry(frame)
entry_N.pack()

ttk.Label(frame, text="Incident Angle θᵢ (deg):").pack()
entry_theta_i = ttk.Entry(frame)
entry_theta_i.pack()

ttk.Label(frame, text="Reflection Angle θᵣ (deg):").pack()
entry_theta_r = ttk.Entry(frame)
entry_theta_r.pack()

ttk.Button(frame, text="Compute Phase Shifts", command=compute_phase_shift).pack(pady=10)
ttk.Button(frame, text="Save Plot as PNG", command=save_plot_png).pack(pady=5)
ttk.Button(frame, text="Save Phases as CSV", command=save_csv).pack(pady=5)

text_output = tk.Text(frame, height=12, width=55)
text_output.pack()

root.mainloop()
