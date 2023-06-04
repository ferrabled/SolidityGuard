import tkinter as tk
from tkinter import filedialog

file_path = None  # Declare file_path as a global variable

def main():
    def select_file():
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("Solidity Files", "*.sol")])
        if file_path:
            analyze_button.config(state=tk.NORMAL)
        return file_path

    def analyze_file():
        global file_path
        if not file_path:
            print("Please select a .sol file first.")
            return
        print("File path:", file_path)
        #print("Use chatbot:", use_chatbot_var.get())
        window.destroy()
        return file_path

    def destroy_window():
        global file_path
        file_path = None
        window.destroy()


    # Create the main window
    window = tk.Tk()
    window.title("SafetyGuard")
    window.geometry("300x200")

    # Create a label for the checkbox
    checkbox_label = tk.Label(window, text="Use chatbot for recommendations")
    checkbox_label.pack(pady=10)

    # Create the checkbox
    use_chatbot_var = tk.BooleanVar()
    use_chatbot_checkbox = tk.Checkbutton(window, variable=use_chatbot_var)
    use_chatbot_checkbox.pack()

    # Create a button to select a .sol file
    select_file_button = tk.Button(window, text="Select .sol file", command=select_file)
    select_file_button.pack(pady=10)

    # Create the analyze button (initially disabled)
    analyze_button = tk.Button(window, text="Analyze", command=analyze_file, state=tk.DISABLED)
    analyze_button.pack()

    # Start the Tkinter event loop
    window.protocol("WM_DELETE_WINDOW", destroy_window)
    window.mainloop()

    return file_path, use_chatbot_var.get()