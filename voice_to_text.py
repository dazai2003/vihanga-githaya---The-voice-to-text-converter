import pyaudio
import json
from vosk import Model, KaldiRecognizer
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import time
import customtkinter as ctk
import os
from datetime import datetime
import sys

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(application_path, 'model')

class VoiceToTextApp:
    def __init__(self):
        # Set theme and color scheme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create the main window with adjusted size
        self.root = ctk.CTk()
        self.root.title("VIhanga Githaya")
        self.root.geometry("1000x700")  # Smaller initial size
        self.root.minsize(800, 600)     # Smaller minimum size
        
        # Set window background to dark night sky color
        self.root.configure(fg_color=("#050A1A", "#050A1A"))  # Darker blue for more depth
        
        # Configure grid weight
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Update main frame for enhanced misty night effect
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=20,
            fg_color=("#0A1128", "#0A1128"),  # Darker background
            border_width=2,
            border_color="#1f538d"
        )
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")  # Reduced padding
        
        # Configure grid weights for resizing
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)  # Make text area expand
        
        # Create menu frame
        self.menu_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.menu_frame.grid(row=0, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        # Create menu buttons with larger width
        self.file_menu = ctk.CTkOptionMenu(
            self.menu_frame,
            values=["New", "Open", "Save", "Save As", "Exit"],
            command=self.handle_file_menu,
            width=100,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.file_menu.grid(row=0, column=0, padx=10)  # Increased padding
        self.file_menu.set("File")
        
        self.options_menu = ctk.CTkOptionMenu(
            self.menu_frame,
            values=["Light Mode", "Dark Mode", "System Mode", "About", "Help"],
            command=self.handle_options_menu,
            width=100,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.options_menu.grid(row=0, column=1, padx=10)  # Increased padding
        self.options_menu.set("Options")
        
        # Title and subtitle with adjusted spacing
        title_text = "🎤 VIhanga Githaya"
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=title_text,
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#4DA6FF"
        )
        self.title_label.grid(row=1, column=0, columnspan=2, pady=(30, 5))  # Adjusted padding
        
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Transform your voice into text with precision",
            font=ctk.CTkFont(family="Segoe UI", size=14, slant="italic"),
            text_color="#8BB8FF"
        )
        self.subtitle_label.grid(row=2, column=0, columnspan=2, pady=(0, 30))
        
        # Update text area size and spacing
        self.text_area = ctk.CTkTextbox(
            self.main_frame,
            corner_radius=15,
            border_width=2,
            border_color="#1f538d",
            fg_color=("#0D1B3B", "#0D1B3B"),
            text_color="#E6EBF8",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=320,    # Reduced height to prevent overlap
            width=800
        )
        self.text_area.grid(row=3, column=0, columnspan=2, padx=30, pady=(10, 15), sticky="nsew")
        
        # Configure text widget properties
        self.text_area._textbox.configure(
            insertbackground="#4da6ff",     # Cursor color
            selectbackground="#1f538d",     # Selection color
            selectforeground="#ffffff"      # Selected text color
        )
        
        # Create control panel frame
        self.control_panel = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.control_panel.grid(row=4, column=0, columnspan=2, pady=(0, 5))
        
        # Control buttons with adjusted size
        button_configs = {
            "width": 160,      # Slightly smaller width
            "height": 40,      # Slightly smaller height
            "corner_radius": 12,
            "border_width": 2,
            "border_color": "#1f538d",
            "fg_color": ("#1f538d", "#1f538d"),
            "hover_color": ("#2B86FF", "#2B86FF"),
            "font": ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            "text_color": "#E6EBF8"
        }
        
        self.record_button = ctk.CTkButton(
            self.control_panel,
            text="Start Recording",
            command=self.toggle_recording,
            **button_configs
        )
        self.record_button.grid(row=0, column=0, padx=15)  # Increased padding
        
        self.clear_button = ctk.CTkButton(
            self.control_panel,
            text="Clear Text",
            command=self.clear_text,
            **button_configs
        )
        self.clear_button.grid(row=0, column=1, padx=15)
        
        self.copy_button = ctk.CTkButton(
            self.control_panel,
            text="Copy Text",
            command=self.copy_text,
            **button_configs
        )
        self.copy_button.grid(row=0, column=2, padx=15)
        
        # Update status frame spacing and size
        self.status_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=("#0A1128", "#0A1128"),
            border_width=2,
            border_color="#1f538d"
        )
        self.status_frame.grid(row=5, column=0, columnspan=2, pady=(5, 5))
        
        # Make status labels more compact
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8BB8FF",
            width=200,  # Increased width
            height=25   # Increased height
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=5)
        
        self.word_count_label = ctk.CTkLabel(
            self.status_frame,
            text="Words: 0",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8BB8FF",
            width=100
        )
        self.word_count_label.grid(row=0, column=1, padx=15, pady=5)
        
        # Update footer frame to be more compact
        self.footer_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=("#0A1128", "#0A1128"),
            border_width=2,
            border_color="#1f538d",
            height=30  # Set fixed height
        )
        self.footer_frame.grid(row=6, column=0, columnspan=2, pady=(5, 10), sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1)
        
        # Make copyright more compact
        copyright_text = "© 2024 VIhanga Githaya"  # Shortened text
        self.copyright_label = ctk.CTkLabel(
            self.footer_frame,
            text=copyright_text,
            font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"),
            text_color="#4DA6FF",
            height=20
        )
        self.copyright_label.grid(row=0, column=0, pady=5)
        
        # Update version label
        self.version_label = ctk.CTkLabel(
            self.footer_frame,
            text="v1.0.0",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#4DA6FF",
            height=20
        )
        self.version_label.grid(row=0, column=1, padx=15, pady=5)
        
        # Initialize variables
        self.is_recording = False
        self.recording_thread = None
        self.current_file = None
        self.auto_save = False
        self.recorded_text = []
        self.word_count = 0
        
        # Bind text changes to word count update
        self.text_area.bind('<KeyRelease>', self.update_word_count)
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Update model loading with better error handling
        try:
            if hasattr(sys, '_MEIPASS'):
                model_path = os.path.join(sys._MEIPASS, 'model')
            else:
                model_path = "model"
            
            if not os.path.exists(model_path):
                raise Exception(f"Model not found at {model_path}")
            
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
        except Exception as e:
            self.text_area.insert("0.0", f"Error loading model: {str(e)}\n")
            self.record_button.configure(state="disabled")
        
        # Add hover effects to buttons
        def on_enter(e, button):
            button.configure(border_color="#4da6ff")
        
        def on_leave(e, button):
            button.configure(border_color="#1f538d")
        
        # Apply hover effects to buttons
        for button in [self.record_button, self.clear_button, self.copy_button]:
            button.bind("<Enter>", lambda e, b=button: on_enter(e, b))
            button.bind("<Leave>", lambda e, b=button: on_leave(e, b))
        
        # Remove mode switching animation since we removed transparency
        def handle_mode_switch(mode):
            ctk.set_appearance_mode(mode)
        
        self.speech_mode = "continuous"  # or "line-by-line"
        
        # Add mode selection buttons to control panel
        self.mode_frame = ctk.CTkFrame(
            self.control_panel,
            fg_color="transparent"
        )
        self.mode_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        self.mode_label = ctk.CTkLabel(
            self.mode_frame,
            text="Recording Mode:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8BB8FF"
        )
        self.mode_label.grid(row=0, column=0, padx=5)
        
        self.mode_switch = ctk.CTkSegmentedButton(
            self.mode_frame,
            values=["Continuous", "Line by Line"],
            command=self.change_mode,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            selected_color="#1f538d",
            selected_hover_color="#2B86FF"
        )
        self.mode_switch.grid(row=0, column=1, padx=5)
        self.mode_switch.set("Continuous")
    
    def handle_file_menu(self, choice):
        if choice == "New":
            self.new_file()
        elif choice == "Open":
            self.open_file()
        elif choice == "Save":
            self.save_file()
        elif choice == "Save As":
            self.save_file_as()
        elif choice == "Exit":
            self.on_closing()
        self.file_menu.set("File")
    
    def handle_options_menu(self, choice):
        if choice == "Light Mode":
            ctk.set_appearance_mode("light")
        elif choice == "Dark Mode":
            ctk.set_appearance_mode("dark")
        elif choice == "System Mode":
            ctk.set_appearance_mode("system")
        elif choice == "About":
            self.show_about()
        elif choice == "Help":
            self.show_help()
        self.options_menu.set("Options")
    
    def new_file(self):
        self.current_file = None
        self.clear_text()
        self.status_label.configure(text="New file created")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.delete("0.0", "end")
                    self.text_area.insert("0.0", file.read())
                self.current_file = file_path
                self.status_label.configure(text=f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_label.configure(text=f"Error opening file: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
    
    def save_to_file(self, file_path):
        try:
            text = self.text_area.get("0.0", "end")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            self.status_label.configure(text=f"Saved: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_label.configure(text=f"Error saving file: {str(e)}")
    
    def copy_text(self):
        text = self.text_area.get("0.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_label.configure(text="Text copied to clipboard")
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.record_button.configure(text="Stop Recording", fg_color="#c42b2b", hover_color="#a62424")
        self.status_label.configure(text="Recording... (Text will be saved when stopped)")
        self.recorded_text = []
        
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
    
    def stop_recording(self):
        self.is_recording = False
        self.record_button.configure(text="Start Recording", fg_color="#1f538d", hover_color="#164070")
        
        # Create save dialog
        if self.recorded_text:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Save Recording")
            dialog.geometry("400x150")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f'+{x}+{y}')
            
            label = ctk.CTkLabel(
                dialog,
                text="Would you like to save this recording?",
                font=ctk.CTkFont(family="Segoe UI", size=14)
            )
            label.pack(pady=20)
            
            button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            button_frame.pack(pady=10)
            
            def save():
                if not self.current_file:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    self.current_file = f"recording_{timestamp}.txt"
                
                try:
                    with open(self.current_file, 'a', encoding='utf-8') as f:
                        f.write("\n".join(self.recorded_text) + "\n")
                    self.status_label.configure(text=f"Saved to: {os.path.basename(self.current_file)}")
                except Exception as e:
                    self.status_label.configure(text=f"Error saving: {str(e)}")
                
                dialog.destroy()
            
            def discard():
                self.recorded_text = []
                self.status_label.configure(text="Recording discarded")
                dialog.destroy()
            
            save_btn = ctk.CTkButton(
                button_frame,
                text="Save",
                command=save,
                width=100,
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            save_btn.pack(side="left", padx=10)
            
            discard_btn = ctk.CTkButton(
                button_frame,
                text="Discard",
                command=discard,
                width=100,
                fg_color="#c42b2b",
                hover_color="#a62424",
                font=ctk.CTkFont(family="Segoe UI", size=12)
            )
            discard_btn.pack(side="left", padx=10)
    
    def record_audio(self):
        stream = self.p.open(format=pyaudio.paInt16,
                           channels=1,
                           rate=16000,
                           input=True,
                           frames_per_buffer=4000)
        
        stream.start_stream()
        
        try:
            while self.is_recording:
                data = stream.read(2000, exception_on_overflow=False)
                if len(data) == 0:
                    break
                    
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self.recorded_text.append(text)
                        if self.speech_mode == "line-by-line":
                            self.update_text(f"{text}\n")
                            # Pause recording briefly to separate lines
                            time.sleep(1.5)
                        else:
                            self.update_text(f"{text} ")
        finally:
            stream.stop_stream()
            stream.close()
    
    def update_word_count(self, event=None):
        """Update the word count display"""
        text = self.text_area.get("0.0", "end-1c")
        # Count only non-empty words
        words = len([word for word in text.split() if word.strip()])
        self.word_count = words
        self.word_count_label.configure(text=f"Words: {words}")
    
    def update_text(self, text):
        """Update text area and word count"""
        self.text_area.insert("end", text)
        self.text_area.see("end")
        self.update_word_count()
    
    def clear_text(self):
        """Clear text and reset word count"""
        self.text_area.delete("0.0", "end")
        self.word_count = 0
        self.word_count_label.configure(text="Words: 0")
        self.status_label.configure(text="Text cleared")
    
    def on_closing(self):
        if self.is_recording:
            self.stop_recording()
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
        self.p.terminate()
        self.root.destroy()
    
    def show_about(self):
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("About VoiceScribe Pro")
        about_window.geometry("500x400")  # Larger size
        about_window.resizable(False, False)  # Fixed size
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'{width}x{height}+{x}+{y}')
        
        about_text = """
        🎤 VIhanga Githaya
        Version 1.0.0
        
        Created by VIhanga Githaya
        
        A professional voice-to-text converter
        with real-time transcription capabilities.
        
        © 2024 All Rights Reserved.
        """
        
        label = ctk.CTkLabel(
            about_window,
            text=about_text,
            font=ctk.CTkFont(size=16),  # Larger font
            justify="center"
        )
        label.pack(pady=40, padx=30)
    
    def show_help(self):
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("Help")
        help_window.geometry("500x400")  # Larger size
        help_window.resizable(False, False)  # Fixed size
        
        # Center the window
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f'{width}x{height}+{x}+{y}')
        
        help_text = """
        Quick Guide:
        
        1. Click 'Start Recording' to begin
        2. Speak clearly into your microphone
        3. Click 'Stop Recording' when finished
        4. Use File menu to save your text
        5. Copy button copies text to clipboard
        
        Tips:
        - Speak clearly and at a normal pace
        - Use in a quiet environment
        - Text is auto-saved when recording stops
        - Use keyboard shortcuts for common actions
        """
        
        label = ctk.CTkLabel(
            help_window,
            text=help_text,
            font=ctk.CTkFont(size=16),  # Larger font
            justify="left"
        )
        label.pack(pady=40, padx=30)
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def change_mode(self, mode):
        self.speech_mode = "continuous" if mode == "Continuous" else "line-by-line"

if __name__ == "__main__":
    app = VoiceToTextApp()
    app.run() 