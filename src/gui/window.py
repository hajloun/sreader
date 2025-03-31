import tkinter as tk
from tkinter import ttk, scrolledtext
from controllers.speed_controller import SpeedController
from utils.text_processor import TextProcessor

class SpeedReaderWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Reader")
        self.root.geometry("600x400")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text input area
        self.text_input = scrolledtext.ScrolledText(main_frame, height=10)
        self.text_input.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Speed control
        ttk.Label(main_frame, text="Speed (words per minute):").grid(row=1, column=0)
        self.speed_var = tk.StringVar(value="200")
        speed_entry = ttk.Entry(main_frame, textvariable=self.speed_var)
        speed_entry.grid(row=1, column=1)
        
        # Display area
        self.display_label = ttk.Label(main_frame, text="Word display", font=("Arial", 24))
        self.display_label.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Control buttons
        self.start_button = ttk.Button(main_frame, text="Start", command=self.start_reading)
        self.start_button.grid(row=3, column=0)
        
        self.stop_button = ttk.Button(main_frame, text="Stop", command=self.stop_reading)
        self.stop_button.grid(row=3, column=1)
        
        # Initialize components
        self.text_processor = TextProcessor()
        self.speed_controller = SpeedController(self.text_processor, self.update_display)
        
    def update_display(self, word):
        self.display_label.config(text=word)
        self.root.update()
        
    def start_reading(self):
        text = self.text_input.get("1.0", tk.END)
        self.text_processor.set_text(text)
        speed_wpm = int(self.speed_var.get())
        speed_ms = int(60000 / speed_wpm)  # Convert WPM to milliseconds
        self.speed_controller.set_speed(speed_ms)
        self.speed_controller.start_reading()
        
    def stop_reading(self):
        self.speed_controller.stop_reading()