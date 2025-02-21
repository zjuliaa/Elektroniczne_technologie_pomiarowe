import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
import threading
import serial

serialInst = serial.Serial()

def open_port_command():
    try:
        port = port_var.get()
        baudrate= int(baudrate_var.get())
        timeout = float(timeout_var.get())
        stopbits = int(stopbits_var.get())
        databits = int(databits_var.get())
        parity = parity_var.get()
        xonxoff = xonxoff_var.get()
        rtscts = rtscts_var.get()
        serialInst.port = port
        serialInst.baudrate = baudrate
        serialInst.timeout = timeout
        serialInst.stopbits = stopbits
        serialInst.bytesize= databits
        serialInst.parity = parity
        if xonxoff == "On":
            serialInst.xonxoff = True
        else:
            serialInst.xonxoff = False
        if rtscts == "On":
            serialInst.rtscts = True
        else:
            serialInst.rtscts = False
        serialInst.open()
        port_status_var.set(f"Port {port} is open")
        start_read_thread()
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error opening port: {e}")

def close_port_command():
    try:
        if serialInst.is_open:
            serialInst.close()
            port_status_var.set("Port is closed")
            stop_read_thread()
        else:
            port_status_var.set("Port is already closed")
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error closing port: {e}")

def start_read_thread():
    global read_thread_running
    read_thread_running = True
    read_thread.start()

def stop_read_thread():
    global read_thread_running
    read_thread_running = False
    read_thread.join()

def read_data():
    try:
        if read_thread_running and serialInst.in_waiting > 0:
            data = serialInst.read(1000)
            if data:
                output_text.insert(tk.END, data.decode())
                output_text.yview(tk.END)
        root.after(1, read_data)
    except Exception as e:
        tk.messagebox.showerror("Błąd", f"Błąd odczytu danych: {e}")

def save_data_command():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(output_text.get(1.0, tk.END))
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error saving file: {e}")

root = tk.Tk()
root.title("Serial Port Reader")
port_var = tk.StringVar(value="COM4")
baudrate_var = tk.StringVar(value="9600")
timeout_var = tk.StringVar(value="1")
stopbits_var = tk.StringVar(value="1")
databits_var = tk.StringVar(value="8")
parity_var = tk.StringVar(value='N')
xonxoff_var = tk.StringVar(value="Off")
rtscts_var = tk.StringVar(value="Off")
line_var = tk.StringVar(value="")
port_status_var = tk.StringVar(value="Port is closed")

labels = ["Port COM", "Baud rate", "Czas oczekiwania", "Bity stopu", "Bity danych", "Parzystosc", "Xon/Xoff", "Rts/Cts"]
combobox_vars = [port_var, baudrate_var, timeout_var, stopbits_var, databits_var, parity_var, xonxoff_var, rtscts_var]
combobox_options = [
    ["COM1", "COM2", "COM3", "COM4", "COM5"], 
    ["9600", "19200", "38400", "57600", "115200"], 
    ["1", "0"], 
    ["1", "1.5", "2"], 
    ["5", "6", "7", "8"], 
    ['N', 'E', 'O', 'M','S'], 
    ["Off", "On"], 
    ["Off", "On"],
]

for label, combobox_var, options in zip(labels, combobox_vars, combobox_options):
    ttk.Label(root, text=label).grid(column=0, row=labels.index(label))
    ttk.Combobox(root, textvariable=combobox_var, values=options).grid(column=1, row=labels.index(label))

ttk.Button(root, text="Otworz port", command=open_port_command).grid(column=0, row=len(labels), columnspan=2, pady=10)
ttk.Button(root, text="Zamknij port", command=close_port_command).grid(column=0, row=len(labels)+1, columnspan=2, pady=5)
ttk.Button(root, text="Zapisz dane", command=save_data_command).grid(column=0, row=len(labels)+2, columnspan=2, pady=5)

output_text = scrolledtext.ScrolledText(root, width=40, height=10)
output_text.grid(column=2, row=0, rowspan=len(labels)+4, padx=10, pady=10)

ttk.Label(root, textvariable=port_status_var).grid(column=0, row=len(labels)+3, columnspan=2)

read_thread = threading.Thread(target=read_data, daemon=True)
read_thread_running = False

root.mainloop()

