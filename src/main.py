import tkinter as tk
from tkinter import ttk, scrolledtext
from controllers.speed_controller import SpeedController
from utils.text_processor import TextProcessor
from utils.scrape import scrape_headway_book  # We'll create this function
import threading

class SpeedReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Reader")
        self.root.state('zoomed')
        
        # Configure modern style
        self.style = ttk.Style()
        # Modern flat design for buttons
        self.style.configure('Controls.TButton', 
            font=('Segoe UI', 11, 'bold'),
            padding=(25, 12),
            background='#ffffff',  # Modern blue
            foreground='white',
            borderwidth=0,
            relief='flat'
        )
        self.style.map('Controls.TButton',
            background=[('active', '#ffffff'), ('disabled', '#90a4ae')],
            foreground=[('disabled', '#eceff1')],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')]
        )
        
        self.style.configure('Reader.TLabel', font=('Segoe UI', 48, 'bold'))
        self.style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'))
        self.style.configure('Speed.TFrame', padding=20)
        
        # Create centered container
        container = ttk.Frame(root)
        container.place(rely=0.5, relx=0.5, anchor='center')
        
        # Title
        self.title_label = ttk.Label(container, text="Speed Reader", style='Title.TLabel')
        self.title_label.pack(pady=(0, 40))
        
        # Text input container
        self.text_container = ttk.Frame(container)
        self.text_input = scrolledtext.ScrolledText(
            self.text_container, 
            height=8, 
            width=60,
            font=('Segoe UI', 12),
            borderwidth=1,
            relief='solid'
        )
        self.text_input.pack(pady=20)
        self.text_container.pack()
        
        # Display area
        display_frame = ttk.Frame(container, style='Speed.TFrame')
        display_frame.pack(fill='both', expand=True)
        
        self.display_label = ttk.Label(display_frame, text="Ready to start", style='Reader.TLabel')
        self.display_label.pack(pady=40)
        
        # Bottom control panel
        self.bottom_panel = ttk.Frame(root)  # Make it instance variable
        self.bottom_panel.pack(side='bottom', fill='x', pady=20)
        
        # Left side - Speed controls
        self.speed_frame = ttk.Frame(self.bottom_panel)  # Make it instance variable
        self.speed_frame.pack(side='left', padx=20)
        
        ttk.Label(self.speed_frame, text="WPM:", font=('Helvetica', 12)).pack(side='left', padx=5)
        self.speed_var = tk.StringVar(value="400")
        speed_entry = ttk.Entry(self.speed_frame, textvariable=self.speed_var, width=6, 
                              font=('Helvetica', 12))
        speed_entry.pack(side='left', padx=5)
        
        # Center - Control buttons
        self.button_frame = ttk.Frame(self.bottom_panel)  # Make it instance variable
        self.button_frame.pack(side='left', padx=20)
        
        self.start_stop_button = ttk.Button(self.button_frame, text="Start", 
                                          style='Start.TButton',
                                          command=self.toggle_reading)
        self.start_stop_button.pack(side='left', padx=10)
        
        ttk.Button(self.button_frame, text="Toggle Text", 
                  style='Controls.TButton',
                  command=self.toggle_text).pack(side='left', padx=10)
        
        ttk.Button(self.button_frame, text="Headway", 
                  style='Controls.TButton',
                  command=self.show_headway_inputs).pack(side='left', padx=10)
        
        ttk.Button(self.button_frame, text="Toggle Theme", 
                  style='Controls.TButton',
                  command=self.toggle_theme).pack(side='left', padx=10)

        # Right side - Toggle Controls button
        toggle_controls_frame = ttk.Frame(self.bottom_panel)
        toggle_controls_frame.pack(side='right', padx=20)
        
        self.toggle_controls_button = ttk.Button(toggle_controls_frame, 
                                               text="Hide Controls", 
                                               style='Controls.TButton',
                                               command=self.toggle_controls)
        self.toggle_controls_button.pack()
        
        # Initialize components
        self.text_processor = TextProcessor()
        self.speed_controller = SpeedController(self.text_processor, self.update_display)
        self.dark_mode = False
        self.theme_mode = 0  # 0: light, 1: dark, 2: custom
        self.paused = False
        
        # Set initial theme
        self.apply_theme()
        
        # Add key bindings
        self.root.bind('<s>', lambda e: self.toggle_reading())  # Space to toggle reading
        self.root.bind('<h>', lambda e: self.toggle_controls())     # 'h' key to hide/show controls
        self.root.bind('<t>', lambda e: self.toggle_theme())         # 't' key to toggle text
        self.root.bind('<a>', lambda e: self.toggle_text())  # 'c' key to toggle controls
    def apply_theme(self):
        if self.theme_mode == 0:  # Light theme
            bg_color = '#ffffff'
            fg_color_input = '#2d2d2d'
            fg_color = '#2d2d2d'
            accent_color = '#b3d0ff'
            secondary_bg = '#f5f5f5'
            button_bg = '#e0e0e0'
            button_fg = '#2d2d2d'
            start_btn_color = '#e0e0e0'
            stop_btn_color = '#e0e0e0'
        elif self.theme_mode == 1:  # Dark theme
            bg_color = '#1a1a1a'
            fg_color_input = '#ffffff'
            fg_color = '#ffffff'
            accent_color = '#b3d0ff'
            secondary_bg = '#2d2d2d'
            button_bg = '#3d3d3d'
            button_fg = '#3d3d3d'
            start_btn_color = '#ffffff'
            stop_btn_color = '#ffffff'
        else:  # Custom theme (beige/brown)
            bg_color = '#f0dec6'
            fg_color_input = '#9a866d'
            fg_color = '#9a866d'
            accent_color = '#ffffff'
            secondary_bg = '#f0dec6'
            button_bg = '#9a866d'
            button_fg = '#9a866d'
            start_btn_color = '#9a866d'
            stop_btn_color = '#9a866d'

        # Set background and text colors
        self.root.configure(bg=bg_color)
        self.style.configure('Reader.TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('Title.TLabel', background=bg_color, foreground=accent_color)
        self.style.configure('TFrame', background=bg_color)

        # Configure button styles
        self.style.configure('Controls.TButton',
            font=('Segoe UI', 11, 'bold'),
            padding=(15, 10),
            background=button_bg,
            foreground=button_fg,
            borderwidth=0,
            relief='flat'
        )
        self.style.configure('Start.TButton',
            font=('Segoe UI', 11, 'bold'),
            padding=(15, 10),
            background=start_btn_color,
            foreground=button_fg,
            borderwidth=0,
            relief='flat'
        )
        self.style.configure('Stop.TButton',
            font=('Segoe UI', 11, 'bold'),
            padding=(15, 10),
            background=stop_btn_color,
            foreground=button_fg,
            borderwidth=0,
            relief='flat'
        )

        # Configure button hover effects
        hover_bg = accent_color if self.theme_mode != 2 else '#b3a18a'  # Lighter brown for custom theme
        self.style.map('Controls.TButton',
            background=[('active', hover_bg), ('disabled', button_bg)],
            foreground=[('disabled', '#aaaaaa')]
        )
        self.style.map('Start.TButton',
            background=[('active', hover_bg), ('disabled', '#90a4ae')],
            foreground=[('disabled', '#aaaaaa')]
        )
        self.style.map('Stop.TButton',
            background=[('active', hover_bg), ('disabled', '#90a4ae')],
            foreground=[('disabled', '#aaaaaa')]
        )

        # Configure text input
        self.text_input.configure(
            bg=secondary_bg,
            fg=fg_color_input,
            insertbackground=fg_color,
            selectbackground=accent_color,
            selectforeground=button_fg
        )

    def update_display(self, word):
        self.display_label.config(text=word)
        self.root.update()
        
    def toggle_reading(self):
        if self.start_stop_button['text'] == 'Start':
            # Start reading
            text = self.text_input.get("1.0", tk.END)
            self.text_processor.set_text(text)
            
            try:
                speed_wpm = int(self.speed_var.get())
                speed_ms = int(60000 / speed_wpm)
                self.speed_controller.set_speed(speed_ms)
                self.speed_controller.start_reading()
                self.start_stop_button.configure(text='Stop', style='Stop.TButton')
            except ValueError:
                self.display_label.config(text="Please enter a valid speed")
        else:
            # Stop reading
            self.speed_controller.stop_reading()
            self.start_stop_button.configure(text='Start', style='Start.TButton')
        
    def toggle_text(self):
        if hasattr(self.text_container, '_is_hidden') and not self.text_container._is_hidden:
            self.text_container.pack_forget()
            self.text_container._is_hidden = True
        else:
            self.text_container.pack(after=self.title_label)
            self.text_container._is_hidden = False
            
    def toggle_theme(self):
        self.theme_mode = (self.theme_mode + 1) % 3  # Cycle through 3 themes
        self.apply_theme()
        
    def show_headway_inputs(self):
        if not hasattr(self, 'headway_frame'):
            # Create headway input frame
            self.headway_frame = ttk.Frame(self.root)
            
            # Email input with pre-filled value
            ttk.Label(self.headway_frame, text="Email:").pack(pady=5)
            self.email_var = tk.StringVar(value="hhh.honzula@gmail.com")  # Pre-fill email
            ttk.Entry(self.headway_frame, textvariable=self.email_var, width=40).pack()
            
            # Password input with pre-filled value
            ttk.Label(self.headway_frame, text="Password:").pack(pady=5)
            self.password_var = tk.StringVar(value="pw.")  # Pre-fill password
            password_entry = ttk.Entry(self.headway_frame, textvariable=self.password_var, show="*", width=40)
            password_entry.pack()
            
            # Book URL input (left empty for pasting)
            ttk.Label(self.headway_frame, text="Book URL:").pack(pady=5)
            self.book_url_var = tk.StringVar()
            ttk.Entry(self.headway_frame, textvariable=self.book_url_var, width=40).pack()
            
            # Send button
            ttk.Button(self.headway_frame, text="Send", 
                      command=self.scrape_and_load_book, 
                      style='Controls.TButton').pack(pady=20)
            
        if hasattr(self.headway_frame, '_is_hidden') and not self.headway_frame._is_hidden:
            self.headway_frame.pack_forget()
            self.headway_frame._is_hidden = True
        else:
            self.headway_frame.pack(after=self.title_label, pady=20)
            self.headway_frame._is_hidden = False

    def scrape_and_load_book(self):
        # Disable inputs while scraping
        for child in self.headway_frame.winfo_children():
            if isinstance(child, ttk.Entry) or isinstance(child, ttk.Button):
                child['state'] = 'disabled'
        
        # Show loading message
        self.display_label.config(text="Scraping book...")
        
        # Start scraping in a separate thread
        def scrape_thread():
            try:
                # Get the scraped text
                scraped_text = scrape_headway_book(
                    self.email_var.get(),
                    self.password_var.get(),
                    self.book_url_var.get()
                )
                
                # Update the text input with scraped content
                self.text_input.delete('1.0', tk.END)
                self.text_input.insert('1.0', scraped_text)
                
                # Hide the headway frame
                self.headway_frame.pack_forget()
                self.headway_frame._is_hidden = True
                
                # Show success message
                self.display_label.config(text="Book loaded successfully!")
                
            except Exception as e:
                self.display_label.config(text=f"Error: {str(e)}")
                
            finally:
                # Re-enable inputs
                for child in self.headway_frame.winfo_children():
                    if isinstance(child, ttk.Entry) or isinstance(child, ttk.Button):
                        child['state'] = 'normal'
        
        threading.Thread(target=scrape_thread, daemon=True).start()

    def toggle_controls(self):
        if hasattr(self.speed_frame, '_is_hidden') and not self.speed_frame._is_hidden:
            # Hide controls
            self.speed_frame.pack_forget()
            self.button_frame.pack_forget()
            self.speed_frame._is_hidden = True
            self.button_frame._is_hidden = True
            self.toggle_controls_button.configure(text="Show Controls")
        else:
            # Show controls
            self.speed_frame.pack(side='left', padx=20)
            self.button_frame.pack(side='left', padx=20)
            self.speed_frame._is_hidden = False
            self.button_frame._is_hidden = False
            self.toggle_controls_button.configure(text="Hide Controls")

def main():
    root = tk.Tk()
    app = SpeedReaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()