# noteStudy33.py - FIXED mouse + any sound device
import math, threading, time
import tkinter as tk
from tkinter import ttk
try:
    import pygame
    HAS_PYGAME=True
except:
    HAS_PYGAME=False
try:
    import sounddevice as sd
    import numpy as np
    HAS_SD=True
    # REMOVED hardcoded device=20 - use default device
except:
    HAS_SD=False

SCALE_MAP = {"Chromatic (Full 12)": list(range(12)), "Major (Ionian)": [0,2,4,5,7,9,11], "Natural Minor": [0,2,3,5,7,8,10], "Pentatonic Major": [0,2,4,7,9], "Whole Tone": [0,2,4,6,8,10], "Blues": [0,3,5,6,7,10], "Pelog (Gamelan approx)": [0,1,5,7,10], "Slendro (Gamelan approx)": [0,2,5,7,9], "Hirajoshi (Japanese)": [0,2,3,7,8], "Raga Bhairav": [0,1,4,5,7,8,11], "OFF (Gliss)": list(range(12))}
TEMP_MAP = {"Equal Temperament (12-TET)": [0]*12, "Just Intonation (Ptolemaic)": [0, -29, 4, -6, -14, -2, -20, 2, -12, 16, -18, -10], "Pythagorean Tuning": [0, 4, 8, -8, 12, -4, 16, 2, 6, 10, -12, 14], "Quarter-Comma Meantone": [0, -24, -7, 10, -6, -27, -3, 14, -13, 4, -20, -10], "Werckmeister III": [0, -6, 2, -4, 4, -2, 6, -2, 2, 4, -4, 2], "19TET approx": [0,3,6,9,13,16,19,22,25,28,31,34], "OFF": [0]*12}
NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
BLACK_KEYS = {1,3,6,8,10}

class TrueDrone:
    def __init__(self):
        self.target_freq=440.0; self.current_freq=440.0; self.target_vol=0.0; self.current_vol=0.0; self.phase=0.0; self.sr=48000; self.stream=None
        if HAS_SD:
            def callback(outdata, frames, time_info, status):
                self.current_freq += (self.target_freq - self.current_freq)*0.15
                self.current_vol += (self.target_vol - self.current_vol)*0.20
                t=np.arange(frames, dtype=np.float32); phase_inc=2*np.pi*self.current_freq/self.sr; phases=self.phase+t*phase_inc
                out=np.sin(phases, dtype=np.float32)*self.current_vol*0.4; outdata[:,0]=out; self.phase=(self.phase+frames*phase_inc)%(2*np.pi*100)
            try:
                # FIXED: no device number - use Windows default
                self.stream=sd.OutputStream(samplerate=self.sr, channels=1, callback=callback, blocksize=2048, latency='high')
                self.stream.start(); print("Drone OK")
            except Exception as e: print("sounddevice fail", e)
    def set(self,freq,vol=0.6):
        vol=max(0,min(1,vol)); self.target_vol=math.pow(vol,2.2); self.target_freq=float(freq)
    def stop(self): self.target_vol=0.0

drone=TrueDrone()
def play_sustained(freq,vol=0.6): drone.set(freq,vol)
def stop_sustained(): drone.stop()

class SevenOctaveMintWorkbench:
    def __init__(self,root):
        self.root=root; self.root.title("noteStudy33 - joystick OR mouse"); self.root.geometry("1950x1300"); self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.style=ttk.Style(); self.style.theme_use("clam"); self.style.configure(".", font=("Arial",14))
        self.style.configure("Treeview", font=("Consolas",11), rowheight=22); self.style.configure("Treeview.Heading", font=("Arial",11,"bold"))
        ctrl_frame=ttk.LabelFrame(root, text=" BOTTOM=0 joy follows KB - MOUSE WORKS IF NO JOYSTICK ", padding=15); ctrl_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(ctrl_frame, text="Root Key:").grid(row=0,column=0,padx=5); self.root_var=tk.StringVar(value="C")
        self.root_combo=ttk.Combobox(ctrl_frame, textvariable=self.root_var, values=NOTE_NAMES, state="readonly", width=8, font=("Arial",14)); self.root_combo.grid(row=0,column=1,padx=5); self.root_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        ttk.Label(ctrl_frame, text="Scale:").grid(row=0,column=2,padx=15); self.scale_var=tk.StringVar(value="Major (Ionian)")
        self.scale_combo=ttk.Combobox(ctrl_frame, textvariable=self.scale_var, values=list(SCALE_MAP.keys()), state="readonly", width=24, font=("Arial",14)); self.scale_combo.grid(row=0,column=3,padx=5); self.scale_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        ttk.Label(ctrl_frame, text="Temp:").grid(row=0,column=4,padx=15); self.temp_var=tk.StringVar(value="Equal Temperament (12-TET)")
        self.temp_combo=ttk.Combobox(ctrl_frame, textvariable=self.temp_var, values=list(TEMP_MAP.keys()), state="readonly", width=28, font=("Arial",14)); self.temp_combo.grid(row=0,column=5,padx=5); self.temp_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        ttk.Label(ctrl_frame, text="Ref:").grid(row=0,column=6,padx=15); self.ref_var=tk.StringVar(value="440 Hz")
        self.ref_combo=ttk.Combobox(ctrl_frame, textvariable=self.ref_var, values=["415 Hz","432 Hz","435 Hz","440 Hz","442 Hz","528 Hz"], state="readonly", width=10, font=("Arial",14)); self.ref_combo.grid(row=0,column=7,padx=5); self.ref_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        self.joy_status=tk.StringVar(value="Audio: default device - Use MOUSE on red bar"); ttk.Label(ctrl_frame, textvariable=self.joy_status, font=("Consolas",11,"bold")).grid(row=0,column=8,padx=20)
        self.quantize_var=tk.BooleanVar(value=True); ttk.Checkbutton(ctrl_frame, text="Quantize", variable=self.quantize_var).grid(row=0,column=9,padx=15)
        self.pitch_curve=0.65
        kb_frame=ttk.LabelFrame(root, text=" 7-Octave - green = black keys active ", padding=10); kb_frame.pack(fill="x", padx=20, pady=5)
        self.kb_canvas=tk.Canvas(kb_frame, height=210, bg="#1a1a1a", highlightthickness=0); self.kb_canvas.pack(fill="x", expand=True); self.kb_canvas.bind("<Button-1>", self.on_keyboard_click)
        gliss_frame=ttk.LabelFrame(root, text=" Red bar = note - DRAG MOUSE HERE - WHITE note floats above ", padding=10); gliss_frame.pack(fill="x", padx=20, pady=10)
        self.gliss_canvas=tk.Canvas(gliss_frame, height=110, bg="#0f0f1a", highlightthickness=0); self.gliss_canvas.pack(fill="x", expand=True)
        self.gliss_canvas.bind("<B1-Motion>", self.on_gliss_drag); self.gliss_canvas.bind("<Button-1>", self.on_gliss_drag); self.gliss_canvas.bind("<ButtonRelease-1>", lambda e: stop_sustained())
        self.readout_label=ttk.Label(gliss_frame, text="Mouse drag on red bar = sound! Joystick also works if plugged in", font=("Consolas",12,"bold")); self.readout_label.pack(pady=4)
        data_frame=ttk.LabelFrame(root, text=" Breakdown ", padding=10); data_frame.pack(fill="both", expand=True, padx=20, pady=10)
        cols=("Note","MIDI","Freq","Cents","Status"); self.tree=ttk.Treeview(data_frame, columns=cols, show="headings", height=18)
        widths={"Note":120,"MIDI":80,"Freq":160,"Cents":120,"Status":120}
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=widths[c], minwidth=widths[c], anchor="center", stretch=True)
        scroll=ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        self.key_rects={}; self.kb_canvas.bind("<Configure>", lambda e: self.refresh_ui()); self.refresh_ui()
        self.joy_x=0.0; self.joy_y=0.0; self.joy_thread_running=True
        if HAS_PYGAME: threading.Thread(target=self.joystick_loop, daemon=True).start()
    def on_close(self):
        self.joy_thread_running=False; stop_sustained()
        try: drone.stream.stop(); drone.stream.close()
        except: pass
        self.root.destroy()
    def get_reference_pitch(self): return float(self.ref_var.get().split(" ")[0])
    def get_root_offset(self): return NOTE_NAMES.index(self.root_var.get())
    def calculate_note_freq(self, note_idx_7oct):
        ro=self.get_root_offset(); abs_s=note_idx_7oct+ro; semi=abs_s%12; ref=self.get_reference_pitch(); midi=24+abs_s; cents=TEMP_MAP[self.temp_var.get()][semi]; base=ref*(2**((midi-69)/12.0)); actual=base*(2**(cents/1200.0)); return actual,cents,midi,abs_s
    def freq_from_norm(self, norm, force_quantize=False):
        norm=max(0,min(1,norm)); curved=math.pow(norm, self.pitch_curve); ro=self.get_root_offset(); ref=self.get_reference_pitch()
        quant=self.quantize_var.get() or force_quantize
        if not quant or self.scale_var.get()=="OFF (Gliss)" or self.temp_var.get()=="OFF":
            base_midi=24+ro+curved*84.0; freq=ref*(2**((base_midi-69)/12.0)); return freq, base_midi, False
        else:
            scale=SCALE_MAP[self.scale_var.get()]; mids=[]
            for i in range(84):
                abs_s=i+ro; rel=(abs_s%12 - ro)%12
                if rel in scale: mids.append(i)
            if not mids: mids=list(range(84))
            idx=int(curved*len(mids)); idx=max(0,min(len(mids)-1, idx)); note_idx=mids[idx]
            freq,cents,midi,abs_s=self.calculate_note_freq(note_idx); return freq,midi,True
    def joystick_loop(self):
        import pygame; pygame.display.init(); pygame.joystick.init()
        try: pygame.mixer.quit()
        except: pass
        stick=None; no_joy_reported=False
        while self.joy_thread_running:
            if stick is None:
                if pygame.joystick.get_count()>0:
                    try: stick=pygame.joystick.Joystick(0); stick.init(); self.root.after(0, lambda: self.joy_status.set(f"Joystick: {stick.get_name()} - + MOUSE"))
                    except: stick=None
                else:
                    if not no_joy_reported:
                        self.root.after(0, lambda: self.joy_status.set("No joystick found - MOUSE MODE active - drag red bar"))
                        no_joy_reported=True
                    time.sleep(0.2); continue
            if stick:
                pygame.event.pump()
                try:
                    rx=stick.get_axis(0); ry=stick.get_axis(1); self.joy_x=(rx+1)/2; self.joy_y=(ry+1)/2
                    freq,midi,is_step=self.freq_from_norm(self.joy_x, force_quantize=True); vol=1.0-self.joy_y; vol=max(0.0,min(1.0,vol))
                    if vol<0.02: stop_sustained()
                    else: play_sustained(freq, vol=vol)
                    def upd(f=freq,m=midi,v=vol, qs=is_step):
                        w=self.gliss_canvas.winfo_width() or 1800; x=self.joy_x*w
                        self.gliss_canvas.delete("all")
                        self.gliss_canvas.create_line(20,55,w-20,55, fill="#00adb5", width=4)
                        self.gliss_canvas.create_line(x,15,x,90, fill="#ff2e63", width=4, tags="cursor")
                        note_name = f"{NOTE_NAMES[int(m)%12]}{int(m)//12-1}" if qs else f"{f:.1f}Hz"
                        self.gliss_canvas.create_text(x, 10, text=note_name, fill="#ffffff", font=("Consolas",12,"bold"), tags="cursor")
                        self.readout_label.config(text=f"JOY {f:.1f}Hz {note_name} MIDI {int(m)} vol {v:.2f}")
                    self.root.after(0, upd)
                except Exception as e:
                    if self.joy_thread_running: print(f"joy err {e}"); stick=None; stop_sustained(); no_joy_reported=False
                time.sleep(0.02)
    def refresh_ui(self): self.draw_keyboard(); self.draw_gliss_pad(); self.update_table()
    def draw_keyboard(self):
        self.kb_canvas.delete("all"); self.key_rects.clear(); scale=SCALE_MAP[self.scale_var.get()]; ro=self.get_root_offset(); cw=self.kb_canvas.winfo_width() or 1850; whites=[i for i in range(84) if (i+ro)%12 not in BLACK_KEYS]; ww=max(16.0, (cw-30)/float(len(whites))); xp=15.0
        for ki in whites:
            _,_,midi,abs_s=self.calculate_note_freq(ki); rel=(abs_s%12 - ro)%12; act=rel in scale; col="#ffffff" if act else "#444444"
            rect=self.kb_canvas.create_rectangle(xp,15,xp+ww,195, fill=col, outline="#000000", width=1.0)
            txt=self.kb_canvas.create_text(xp+ww/2,145, text=f"{NOTE_NAMES[abs_s%12]}{midi//12-1}", fill="#000000" if act else "#999999", font=("Arial",7,"bold"))
            self.key_rects[rect]=ki; self.key_rects[txt]=ki; xp+=ww
        cur=15.0
        for i in range(84):
            _,_,midi,abs_s=self.calculate_note_freq(i); sem=abs_s%12
            if sem not in BLACK_KEYS: cur+=ww
            else:
                rel=(sem - ro)%12; act=rel in scale; col="#111111" if act else "#2c2c2c"; bx=cur-(ww*0.35)
                rect=self.kb_canvas.create_rectangle(bx,15,bx+(ww*0.7),110, fill=col, outline="#777777" if not act else "#00ff00", width=1.5 if act else 1.0)
                txt_color = "#00ff88" if act else "#666666"
                txt=self.kb_canvas.create_text(bx+(ww*0.35),55, text=f"{NOTE_NAMES[sem]}{midi//12-1}", fill=txt_color, font=("Arial",8,"bold"))
                self.key_rects[rect]=i; self.key_rects[txt]=i
    def draw_gliss_pad(self): self.gliss_canvas.delete("all"); w=self.gliss_canvas.winfo_width() or 1800; self.gliss_canvas.create_line(20,55,w-20,55, fill="#00adb5", width=4)
    def update_table(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        scale=SCALE_MAP[self.scale_var.get()]; ro=self.get_root_offset()
        for i in range(84):
            freq,cents,midi,abs_s=self.calculate_note_freq(i); rel=(abs_s%12 - ro)%12; status="ACTIVE" if rel in scale else "GREYED"
            self.tree.insert("", "end", values=(f"{NOTE_NAMES[abs_s%12]}{midi//12-1}",midi,f"{freq:.2f}",f"{cents:+}",status))
    def on_keyboard_click(self, event):
        item=self.kb_canvas.find_withtag("current")
        if item and item[0] in self.key_rects: ki=self.key_rects[item[0]]; freq,_,midi,_=self.calculate_note_freq(ki); play_sustained(freq, 0.7); self.root.after(500, stop_sustained)
    def on_gliss_drag(self, event):
        w=self.gliss_canvas.winfo_width() or 1800; norm=max(0,min(1,event.x/float(w))); freq,midi,qs=self.freq_from_norm(norm, force_quantize=True)
        self.gliss_canvas.delete("all"); w2=self.gliss_canvas.winfo_width() or 1800
        self.gliss_canvas.create_line(20,55,w2-20,55, fill="#00adb5", width=4)
        self.gliss_canvas.create_line(event.x,15,event.x,90, fill="#ff2e63", width=4, tags="cursor")
        note_name = f"{NOTE_NAMES[int(midi)%12]}{int(midi)//12-1}" if qs else f"{freq:.1f}Hz"
        self.gliss_canvas.create_text(event.x, 10, text=note_name, fill="#ffffff", font=("Consolas",12,"bold"), tags="cursor")
        play_sustained(freq, 0.6)

if __name__=="__main__": root=tk.Tk(); app=SevenOctaveMintWorkbench(root); root.mainloop()
