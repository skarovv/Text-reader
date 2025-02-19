import tkinter as tk
from tkinter import filedialog, ttk
from gtts import gTTS
import tempfile
import pygame
import threading
import PyPDF2

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Reader")
        self.root.geometry("600x400")
        
        self.languages = {
            'English': 'en',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Japanese': 'ja',
            'Italian': 'it',
            'Chinese': 'zh-CN'
        }
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.is_playing = False
        self.current_temp_file = None
        
        #gui setup
        self.create_widgets()

    def create_widgets(self):
        self.text_area = tk.Text(self.root, wrap=tk.WORD, height=10)
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        
        #file open button
        self.open_btn = ttk.Button(control_frame, text="Open File", command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        #play and stop buttons
        self.play_btn = ttk.Button(control_frame, text="Read Aloud", command=self.toggle_playback)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        #language selection
        self.lang_var = tk.StringVar(value='English')
        self.lang_dropdown = ttk.Combobox(
            control_frame, 
            textvariable=self.lang_var,
            values=list(self.languages.keys()),
            state='readonly'
        )
        self.lang_dropdown.pack(side=tk.LEFT, padx=5)
        
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Text/PDF files", "*.txt *.pdf"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                if file_path.lower().endswith('.pdf'):
                    text = self.extract_text_from_pdf(file_path)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, text)
                self.update_status(f"Loaded: {file_path}")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")

    def extract_text_from_pdf(self, file_path):
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"PDF read error: {str(e)}")

    def toggle_playback(self):
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            self.update_status("No text to read!")
            return
        
        self.is_playing = True
        self.play_btn.config(text="Stop Reading")
        self.update_status("Preparing audio...")
        
        threading.Thread(target=self.play_audio, args=(text,), daemon=True).start()

    def stop_playback(self):
        self.is_playing = False
        pygame.mixer.music.stop()
        self.play_btn.config(text="Read Aloud")
        self.update_status("Stopped")

    def play_audio(self, text):
        try:
            lang_code = self.languages[self.lang_var.get()]
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                tts = gTTS(text=text, lang=lang_code)
                tts.save(fp.name)
                self.current_temp_file = fp.name
            
            self.update_status("Playing...")
            pygame.mixer.music.load(self.current_temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy() and self.is_playing:
                pygame.time.Clock().tick(10)
                self.root.update_idletasks()
            
            #cleanup
            if self.is_playing:
                self.update_status("Finished")
            self.is_playing = False
            self.play_btn.config(text="Read Aloud")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.is_playing = False
            self.play_btn.config(text="Read Aloud")

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()