# noteStudy52.py - ver51 + labels fixed: Single Voice, KB ALWAYS FREE, Chord Only = Gliss + Joystick only
# Default = Fast Notes, Mouse Default, Joystick Auto, Windows + Linux
# No PC keyboard. KB: Hold mouse, drag across keys, release to stop. Y = volume, LOG.
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"
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
except:
    HAS_SD=False

SCALE_MAP = {"Chromatic (Full 12)": list(range(12)), "Major (Ionian)": [0,2,4,5,7,9,11], "Natural Minor": [0,2,3,5,7,8,10], "Pentatonic Major": [0,2,4,7,9], "Whole Tone": [0,2,4,6,8,10], "Blues": [0,3,5,6,7,10], "Pelog (Gamelan approx)": [0,1,5,7,10], "Slendro (Gamelan approx)": [0,2,5,7,9], "Hirajoshi (Japanese)": [0,2,3,7,8], "Raga Bhairav": [0,1,4,5,7,8,11], "OFF (Gliss)": list(range(12))}
TEMP_MAP = {"Equal Temperament (12-TET)": [0]*12, "Just Intonation (Ptolemaic)": [0, -29, 4, -6, -14, -2, -20, 2, -12, 16, -18, -10], "Pythagorean Tuning": [0, 4, 8, -8, 12, -4, 16, 2, 6, 10, -12, 14], "Quarter-Comma Meantone": [0, -24, -7, 10, -6, -27, -3, 14, -13, 4, -20, -10], "Werckmeister III": [0, -6, 2, -4, 4, -2, 6, -2, 2, 4, -4, 2], "19TET approx": [0,3,6,9,13,16,19,22,25,28,31,34], "OFF": [0]*12}
NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
BLACK_KEYS = {1,3,6,8,10}

def log_vol(raw):
    # raw 0.0 to 1.0, linear from mouse / joystick position
    # returns log-feeling volume, 0.0 to 1.0
    # Human ears hear log, not linear. 1.6 makes middle feel like middle.
    raw = max(0.0, min(1.0, raw))
    return pow(raw, 1.6)

CHORD_TYPES = {
    "Major": ([0,4,7], "Major - happy, home"),
    "Minor": ([0,3,7], "Minor - sad, soft"),
    "Major 7": ([0,4,7,11], "Major 7 - jazzy, dreamy"),
    "Minor 7": ([0,3,7,10], "Minor 7 - mellow"),
    "Dominant 7": ([0,4,7,10], "Dominant 7 - bluesy, wants to resolve"),
    "Diminished": ([0,3,6], "Diminished - tense"),
    "Augmented": ([0,4,8], "Augmented - floating"),
    "Sus2": ([0,2,7], "Sus2 - open, no 3rd, airy"),
    "Sus4": ([0,5,7], "Sus4 - hanging, wants to fall back to major"),
    "Major 6": ([0,4,7,9], "Major 6 - sweet"),
    "Minor 6": ([0,3,7,9], "Minor 6 - old movie"),
    "Power (5)": ([0,7], "Power chord - just root + 5th"),
}
DIATONIC = [("I", 0, "Major"), ("ii", 2, "Minor"), ("iii", 4, "Minor"), ("IV", 5, "Major"), ("V", 7, "Major"), ("vi", 9, "Minor"), ("vii", 11, "Diminished")]
QUICK_COMMENTS = {
    "I": "Home. Start here, end here. Safe.",
    "IV": "The lift. Goes up, feels open.",
    "V": "The pull. Wants to go back home to I.",
    "vi": "The sad one. Soft, the other home. Am in C.",
    "Sus2": "Open sound. No major, no minor, just airy.",
    "Sus4": "Hanging sound. Wants to fall back to I. Play Sus4 then I.",
}

class TrueDrone:
    def __init__(self):
        self.target_freq=440.0; self.current_freq=440.0; self.target_vol=0.0; self.current_vol=0.0; self.phase=0.0; self.sr=48000; self.stream=None
        if HAS_SD:
            def callback(outdata, frames, time_info, status):
                freq_start = self.current_freq
                freq_end = freq_start + (self.target_freq - freq_start) * 0.08
                vol_start = self.current_vol
                vol_end = vol_start + (self.target_vol - vol_start) * 0.18
                freqs = np.linspace(freq_start, freq_end, frames, dtype=np.float32)
                vols = np.linspace(vol_start, vol_end, frames, dtype=np.float32)
                self.current_freq = float(freq_end); self.current_vol = float(vol_end)
                phase_inc = 2 * np.pi * freqs / self.sr
                phases = np.cumsum(phase_inc, dtype=np.float32) + self.phase
                self.phase = float(phases[-1] % (2*np.pi*100))
                out = np.sin(phases).astype(np.float32) * vols * 0.45
                out = np.clip(out, -0.9, 0.9)
                outdata[:,0] = out
            try:
                # Works on Windows + Linux - sounddevice picks driver, no ALSA-only code
                self.stream=sd.OutputStream(samplerate=self.sr, channels=1, callback=callback, blocksize=1024, latency='high')
                self.stream.start()
            except Exception as e:
                print("sounddevice fail", e)
    def set(self,freq,vol=0.6):
        vol=max(0,min(1,vol)); self.target_vol=math.pow(vol,2.2); self.target_freq=float(freq)
    def stop(self):
        self.target_vol=0.0

drone=TrueDrone()
def play_sustained(freq,vol=0.6): drone.set(freq,vol)
def stop_sustained(): drone.stop()

class SevenOctaveMintWorkbench:
    def __init__(self,root):
        self.root=root; self.root.title("noteStudy52 - Single Voice, KB Free, Fast Notes"); self.root.geometry("1450x980"); self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.style=ttk.Style(); self.style.theme_use("clam"); self.style.configure(".", font=("Arial",12)); self.style.configure("Treeview", font=("Consolas",11), rowheight=26); self.style.configure("Treeview.Heading", font=("Arial",11,"bold"))

        ctrl_frame=ttk.LabelFrame(root, text=" MOUSE is default - JOYSTICK auto if plugged in - FAST NOTES always on - SINGLE VOICE, last mover wins ", padding=10); ctrl_frame.pack(fill="x", padx=12, pady=6)
        ttk.Label(ctrl_frame, text="Root:").grid(row=0,column=0,padx=4, sticky="e")
        self.root_var=tk.StringVar(value="C")
        self.root_combo=ttk.Combobox(ctrl_frame, textvariable=self.root_var, values=NOTE_NAMES, state="readonly", width=6, font=("Arial",12)); self.root_combo.grid(row=0,column=1,padx=4, sticky="w"); self.root_combo.bind("<<ComboboxSelected>>", lambda e: self.on_root_change())
        ttk.Label(ctrl_frame, text="Scale:").grid(row=0,column=2,padx=(12,4), sticky="e")
        self.scale_var=tk.StringVar(value="Major (Ionian)")
        self.scale_combo=ttk.Combobox(ctrl_frame, textvariable=self.scale_var, values=list(SCALE_MAP.keys()), state="readonly", width=22, font=("Arial",12)); self.scale_combo.grid(row=0,column=3,padx=4, sticky="w"); self.scale_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        ttk.Label(ctrl_frame, text="Temp:").grid(row=0,column=4,padx=(12,4), sticky="e")
        self.temp_var=tk.StringVar(value="Equal Temperament (12-TET)")
        self.temp_combo=ttk.Combobox(ctrl_frame, textvariable=self.temp_var, values=list(TEMP_MAP.keys()), state="readonly", width=24, font=("Arial",12)); self.temp_combo.grid(row=0,column=5,padx=4, sticky="w"); self.temp_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        ttk.Label(ctrl_frame, text="Ref:").grid(row=1,column=0,padx=4, pady=(6,0), sticky="e")
        self.ref_var=tk.StringVar(value="440 Hz")
        self.ref_combo=ttk.Combobox(ctrl_frame, textvariable=self.ref_var, values=["415 Hz","432 Hz","435 Hz","440 Hz","442 Hz","528 Hz"], state="readonly", width=8, font=("Arial",12)); self.ref_combo.grid(row=1,column=1,padx=4, pady=(6,0), sticky="w"); self.ref_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        self.joy_status=tk.StringVar(value="Mouse Ready - No Joystick")
        self.joy_label=ttk.Label(ctrl_frame, textvariable=self.joy_status, font=("Arial",12,"bold"), foreground="#555555"); self.joy_label.grid(row=1,column=2, columnspan=2, padx=12, pady=(6,0), sticky="w")
        self.chord_only_var=tk.BooleanVar(value=False)
        # VER52 LABEL: Chord Only = Gliss + Joystick only, KB stays FREE
        self.chord_only_check=ttk.Checkbutton(ctrl_frame, text="Chord Only - Gliss + Joystick only, KB stays FREE to play any note", variable=self.chord_only_var, command=self.refresh_ui); self.chord_only_check.grid(row=1,column=4, columnspan=2, padx=12, pady=(6,0), sticky="w")
        ttk.Label(ctrl_frame, text="Fast Notes: ON - KB: Hold mouse, drag across keys, Y = volume (top loud) - Release to stop - Single Voice", font=("Arial",10,"bold"), foreground="#007700").grid(row=2,column=0, columnspan=6, padx=4, pady=(6,0), sticky="w")

        chord_frame=ttk.LabelFrame(root, text=" Chord Chart - Pick from dropdown, or use Quick Chords ", padding=10); chord_frame.pack(fill="x", padx=12, pady=4)
        left_chord=ttk.Frame(chord_frame); left_chord.pack(side="left", fill="y", padx=4)
        ttk.Label(left_chord, text="Chord:").grid(row=0,column=0, sticky="w", padx=2)
        self.chord_var=tk.StringVar(value="No Chord")
        self.chord_combo=ttk.Combobox(left_chord, textvariable=self.chord_var, state="readonly", width=28, font=("Arial",12,"bold")); self.chord_combo.grid(row=0,column=1, columnspan=3, padx=4, sticky="w"); self.chord_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_ui())
        ttk.Label(left_chord, text="Quick:").grid(row=1,column=0, sticky="w", padx=2, pady=(6,0))
        self.quick_btns={}
        for col, roman in enumerate(["I","IV","V"]):
            b=ttk.Button(left_chord, text=roman, width=7, command=lambda r=roman: self.set_quick_chord(r)); b.grid(row=1,column=1+col, padx=2, pady=(6,0), sticky="ew"); self.quick_btns[roman]=b
        ttk.Label(left_chord, text="Colour:").grid(row=2,column=0, sticky="w", padx=2, pady=(4,0))
        for col, roman in enumerate(["vi","Sus2","Sus4"]):
            b=ttk.Button(left_chord, text=roman, width=7, command=lambda r=roman: self.set_quick_chord(r)); b.grid(row=2,column=1+col, padx=2, pady=(4,0), sticky="ew"); self.quick_btns[roman]=b
        self.chord_notes_var=tk.StringVar(value="No Chord - full scale")
        notes_box=ttk.LabelFrame(chord_frame, text=" Notes in this chord + comment ", padding=6)
        notes_box.pack(side="left", padx=12, fill="x", expand=True)
        self.chord_notes_label=ttk.Label(notes_box, textvariable=self.chord_notes_var, font=("Consolas",14,"bold"), foreground="#1a1a1a"); self.chord_notes_label.pack(anchor="w")
        self.chord_desc_var=tk.StringVar(value="")
        self.chord_desc_label=ttk.Label(notes_box, textvariable=self.chord_desc_var, font=("Arial",10), foreground="#555555"); self.chord_desc_label.pack(anchor="w")
        self.chord_comment_var=tk.StringVar(value="Pick a chord to see its notes")
        self.chord_comment_label=ttk.Label(notes_box, textvariable=self.chord_comment_var, font=("Arial",11,"italic"), foreground="#007700"); self.chord_comment_label.pack(anchor="w", pady=(2,0))

        self.pitch_curve=0.65; self.last_mouse_time=0
        self.mouse_x=0.5; self.joy_x=0.0; self.joy_y=0.0
        self.kb_playing=False; self.last_kb_note=None
        # VER52 LABEL: KB ALWAYS FREE
        kb_frame=ttk.LabelFrame(root, text=" 7-Octave KB - ALWAYS FREE - Play any note, even if not in chord - FAST: Hold mouse, drag, Y = volume - BLUE = Tonic, YELLOW = Chord tones ", padding=8); kb_frame.pack(fill="x", padx=12, pady=4)
        self.kb_canvas=tk.Canvas(kb_frame, height=180, bg="#1a1a1a", highlightthickness=0); self.kb_canvas.pack(fill="x", expand=True)
        self.kb_canvas.bind("<Button-1>", self.on_kb_press)
        self.kb_canvas.bind("<B1-Motion>", self.on_kb_drag)
        self.kb_canvas.bind("<ButtonRelease-1>", self.on_kb_release)
        gliss_frame=ttk.LabelFrame(root, text=" MOUSE GREEN + JOY RED - SINGLE VOICE, last mover makes sound ", padding=8); gliss_frame.pack(fill="x", padx=12, pady=4)
        self.gliss_canvas=tk.Canvas(gliss_frame, height=95, bg="#0f0f1a", highlightthickness=0); self.gliss_canvas.pack(fill="x", expand=True)
        self.gliss_canvas.bind("<B1-Motion>", self.on_gliss_drag); self.gliss_canvas.bind("<Button-1>", self.on_gliss_drag); self.gliss_canvas.bind("<ButtonRelease-1>", lambda e: stop_sustained())
        self.readout_label=ttk.Label(gliss_frame, text="Drag: left-right pitch, up-down volume | Joystick works too", font=("Consolas",11,"bold")); self.readout_label.pack(pady=2)
        data_frame=ttk.LabelFrame(root, text=" Breakdown - Expanded ", padding=8); data_frame.pack(fill="both", expand=True, padx=12, pady=6)
        cols=("Note","MIDI","Freq","Cents","Status"); self.tree=ttk.Treeview(data_frame, columns=cols, show="headings", height=14)
        widths={"Note":120,"MIDI":80,"Freq":150,"Cents":100,"Status":110}
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=widths[c], minwidth=widths[c], anchor="center", stretch=True)
        scroll=ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        self.key_rects={}; self.kb_canvas.bind("<Configure>", lambda e: self.refresh_ui())
        self.build_chord_list()
        self.refresh_ui()
        self.joy_thread_running=True
        if HAS_PYGAME: threading.Thread(target=self.joystick_loop, daemon=True).start()

    def build_chord_list(self):
        ro=self.get_root_offset() if hasattr(self,'root_var') else 0
        items=["No Chord"]
        self.chord_lookup={}
        for roman, offset, ctype in DIATONIC:
            chord_pc=(ro+offset)%12
            if ctype=="Diminished": letter=NOTE_NAMES[chord_pc]+"dim"
            elif ctype=="Minor": letter=NOTE_NAMES[chord_pc]+"m"
            else: letter=NOTE_NAMES[chord_pc]
            display=f"{letter}  ({roman} - {ctype})"
            items.append(display)
            intervals, desc = CHORD_TYPES[ctype]
            self.chord_lookup[display]=(chord_pc, intervals, f"{ctype} - {desc}")
        for ctype in ["Major 7","Minor 7","Dominant 7","Sus2","Sus4","Major 6","Power (5)"]:
            chord_pc=ro
            suffix = {"Major 7":"maj7","Minor 7":"m7","Dominant 7":"7","Sus2":"sus2","Sus4":"sus4","Major 6":"6","Power (5)":"5"}.get(ctype,"")
            letter=NOTE_NAMES[chord_pc]+suffix
            display=f"{letter}  ({ctype} on tonic)"
            items.append(display)
            intervals, desc = CHORD_TYPES[ctype]
            self.chord_lookup[display]=(chord_pc, intervals, f"{ctype} - {desc}")
        self.chord_combo.configure(values=items)
        if self.chord_var.get() not in items:
            self.chord_var.set("No Chord")
    def set_quick_chord(self, key):
        for display in self.chord_combo.cget("values"):
            if key in ["Sus2","Sus4"]:
                if f"({key} on tonic)" in display:
                    self.chord_var.set(display); self.refresh_ui(); return
            else:
                if f"({key} -" in display:
                    self.chord_var.set(display); self.refresh_ui(); return
    def set_chord_by_roman(self, roman):
        self.set_quick_chord(roman)
    def on_root_change(self):
        old=self.chord_var.get()
        old_roman=None
        if "(" in old:
            try: old_roman=old.split("(")[1].split(" ")[0]
            except: pass
        self.build_chord_list()
        if old_roman:
            if "Sus" in old:
                if "Sus2" in old: self.set_quick_chord("Sus2")
                elif "Sus4" in old: self.set_quick_chord("Sus4")
            else:
                self.set_quick_chord(old_roman)
        self.refresh_ui()
    def get_current_chord(self):
        sel=self.chord_var.get()
        if sel=="No Chord" or sel not in self.chord_lookup:
            return None
        pc, intervals, desc = self.chord_lookup[sel]
        return (pc, intervals, sel, desc)
    def get_chord_pcs(self):
        cur=self.get_current_chord()
        if not cur: return None
        pc, intervals, sel, desc = cur
        return set((pc+t)%12 for t in intervals)
    def on_close(self):
        self.joy_thread_running=False; stop_sustained()
        try: drone.stream.stop(); drone.stream.close()
        except: pass
        self.root.destroy()
    def get_reference_pitch(self): return float(self.ref_var.get().split(" ")[0])
    def get_root_offset(self): return NOTE_NAMES.index(self.root_var.get())
    def calculate_note_freq(self, note_idx_7oct):
        ro=self.get_root_offset(); abs_s=note_idx_7oct+ro; semi=abs_s%12; ref=self.get_reference_pitch(); midi=24+abs_s; cents=TEMP_MAP[self.temp_var.get()][semi]; base=ref*(2**((midi-69)/12.0)); actual=base*(2**(cents/1200.0)); return actual,cents,midi,abs_s
    def freq_from_norm(self, norm):
        norm=max(0,min(1,norm)); curved=math.pow(norm, self.pitch_curve); ro=self.get_root_offset(); ref=self.get_reference_pitch()
        if self.scale_var.get()=="OFF (Gliss)" and self.temp_var.get()=="OFF":
            base_midi=24+ro+curved*84.0; freq=ref*(2**((base_midi-69)/12.0)); return freq, base_midi, False
        scale=SCALE_MAP[self.scale_var.get()]; allowed=[]
        chord_pcs=self.get_chord_pcs()
        for i in range(84):
            abs_s=i+ro; degree=(abs_s - ro) % 12
            if degree not in scale: continue
            if self.chord_only_var.get() and chord_pcs is not None:
                if (abs_s % 12) not in chord_pcs: continue
            allowed.append(i)
        if not allowed: allowed=list(range(84))
        idx=int(curved*(len(allowed)-1)); idx=max(0,min(len(allowed)-1, idx)); note_idx=allowed[idx]
        freq,cents,midi,abs_s=self.calculate_note_freq(note_idx); return freq,midi,True
    def joystick_loop(self):
        import pygame
        pygame.joystick.init()
        stick=None
        while self.joy_thread_running:
            if stick is None:
                if pygame.joystick.get_count()>0:
                    try:
                        stick=pygame.joystick.Joystick(0); stick.init()
                        self.root.after(0, lambda: [self.joy_status.set("Joystick Ready - Red Cursor"), self.joy_label.config(foreground="#007700")])
                    except: stick=None
                else:
                    self.root.after(0, lambda: [self.joy_status.set("Mouse Ready - No Joystick"), self.joy_label.config(foreground="#555555")]); time.sleep(0.3); continue
            if stick:
                pygame.event.pump()
                try:
                    # SINGLE VOICE: mouse wins for 1.5s, then joystick resumes
                    if time.time() - self.last_mouse_time < 1.5: time.sleep(0.02); continue
                    rx=stick.get_axis(0); ry=stick.get_axis(1); self.joy_x=(rx+1)/2; self.joy_y=(ry+1)/2
                    freq,midi,is_step=self.freq_from_norm(self.joy_x)
                    # JOYSTICK Y = VOL, LOG - stick up = loud, down = quiet, same curve as mouse
                    raw_vol = 1.0 - self.joy_y
                    vol = log_vol(raw_vol)
                    if vol<0.02: stop_sustained()
                    else: play_sustained(freq, vol=vol)
                    def upd(f=freq,m=midi,v=vol, qs=is_step):
                        w=self.gliss_canvas.winfo_width() or 1300; x=self.joy_x*w; mx=self.mouse_x*w
                        self.gliss_canvas.delete("all")
                        self.gliss_canvas.create_line(20,55,w-20,55, fill="#00adb5", width=4)
                        self.gliss_canvas.create_line(mx,15,mx,90, fill="#00ff88", width=3)
                        self.gliss_canvas.create_line(x,15,x,90, fill="#ff2e63", width=5)
                        note_name = f"{NOTE_NAMES[int(m)%12]}{int(m)//12-1}" if qs else f"{f:.1f}Hz"
                        self.gliss_canvas.create_text(x, 10, text=note_name, fill="#ffffff", font=("Consolas",12,"bold"))
                        self.readout_label.config(text=f"JOY {f:.1f}Hz {note_name} vol {v:.2f}  |  Mouse green, Joy red")
                    self.root.after(0, upd)
                except:
                    stick=None; stop_sustained()
                    self.root.after(0, lambda: [self.joy_status.set("Mouse Ready - No Joystick"), self.joy_label.config(foreground="#555555")])
                time.sleep(0.02)
    def refresh_ui(self):
        cur=self.get_current_chord()
        ro=self.get_root_offset() if hasattr(self,'root_var') else 0
        quick_map={}
        for roman, offset, ctype in DIATONIC:
            pc=(ro+offset)%12
            if ctype=="Diminished": letter=NOTE_NAMES[pc]+"dim"
            elif ctype=="Minor": letter=NOTE_NAMES[pc]+"m"
            else: letter=NOTE_NAMES[pc]
            quick_map[roman]=letter
        quick_map["Sus2"]=NOTE_NAMES[ro]+"sus2"
        quick_map["Sus4"]=NOTE_NAMES[ro]+"sus4"
        for key, btn in self.quick_btns.items():
            letter=quick_map.get(key, key)
            btn.configure(text=f"{letter} ({key})")
        if not cur:
            self.chord_notes_var.set("No Chord - full scale")
            self.chord_desc_var.set("Pick a chord to see its notes")
            self.chord_comment_var.set("Pick a chord to see its notes")
        else:
            pc, intervals, sel, desc = cur
            names=[NOTE_NAMES[(pc+t)%12] for t in intervals]
            self.chord_notes_var.set(f"{sel.split('  ')[0]}  =  {' - '.join(names)}")
            self.chord_desc_var.set(desc)
            comment=""
            if "(I -" in sel: comment=QUICK_COMMENTS["I"]
            elif "(IV -" in sel: comment=QUICK_COMMENTS["IV"]
            elif "(V -" in sel: comment=QUICK_COMMENTS["V"]
            elif "(vi -" in sel: comment=QUICK_COMMENTS["vi"]
            elif "Sus2" in sel: comment=QUICK_COMMENTS["Sus2"]
            elif "Sus4" in sel: comment=QUICK_COMMENTS["Sus4"]
            else: comment="Try it with Chord Only on - you can only land on these notes."
            self.chord_comment_var.set(comment)
        self.draw_keyboard(); self.draw_gliss_pad(); self.update_table()
    def draw_keyboard(self):
        self.kb_canvas.delete("all"); self.key_rects.clear(); scale=SCALE_MAP[self.scale_var.get()]; ro=self.get_root_offset(); chord_pcs=self.get_chord_pcs(); cw=self.kb_canvas.winfo_width() or 1400; whites=[i for i in range(84) if (i+ro)%12 not in BLACK_KEYS]; ww=max(16.0, (cw-30)/float(len(whites))); xp=15.0
        for ki in whites:
            _,_,midi,abs_s=self.calculate_note_freq(ki); rel=(abs_s - ro)%12; act=rel in scale; is_chord = chord_pcs is not None and (abs_s%12) in chord_pcs; is_tonic = (abs_s%12)==ro
            if is_tonic: col="#4a90e2"
            elif is_chord: col="#ffd700"
            elif act: col="#ffffff"
            else: col="#444444"
            rect=self.kb_canvas.create_rectangle(xp,15,xp+ww,165, fill=col, outline="#000000", width=2.0 if (is_chord or is_tonic) else 1.0)
            txt=self.kb_canvas.create_text(xp+ww/2,130, text=f"{NOTE_NAMES[abs_s%12]}{midi//12-1}", fill="#ffffff" if is_tonic else "#000000", font=("Arial",7,"bold"))
            self.key_rects[rect]=ki; self.key_rects[txt]=ki; xp+=ww
        cur=15.0
        for i in range(84):
            _,_,midi,abs_s=self.calculate_note_freq(i); sem=abs_s%12
            if sem not in BLACK_KEYS: cur+=ww
            else:
                rel=(abs_s - ro)%12; act=rel in scale; is_chord = chord_pcs is not None and (abs_s%12) in chord_pcs; is_tonic = (abs_s%12)==ro
                if is_tonic: col="#2a5a9a"
                elif is_chord: col="#b8860b"
                elif act: col="#111111"
                else: col="#2c2c2c"
                bx=cur-(ww*0.35)
                rect=self.kb_canvas.create_rectangle(bx,15,bx+(ww*0.7),95, fill=col, outline="#4a90e2" if is_tonic else ("#ffd700" if is_chord else ("#00ff00" if act else "#777777")), width=2.5 if (is_chord or is_tonic) else 1.0)
                txt_color = "#ffffff" if is_tonic else ("#ffd700" if is_chord else ("#00ff88" if act else "#666666"))
                txt=self.kb_canvas.create_text(bx+(ww*0.35),50, text=f"{NOTE_NAMES[sem]}{midi//12-1}", fill=txt_color, font=("Arial",8,"bold"))
                self.key_rects[rect]=i; self.key_rects[txt]=i
    def draw_gliss_pad(self):
        self.gliss_canvas.delete("all"); w=self.gliss_canvas.winfo_width() or 1300; self.gliss_canvas.create_line(20,55,w-20,55, fill="#00adb5", width=4)
    def update_table(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        scale=SCALE_MAP[self.scale_var.get()]; ro=self.get_root_offset(); chord_pcs=self.get_chord_pcs()
        for i in range(84):
            freq,cents,midi,abs_s=self.calculate_note_freq(i); rel=(abs_s - ro)%12
            if (abs_s%12)==ro: status="TONIC"
            elif chord_pcs is not None and (abs_s%12) in chord_pcs: status="CHORD"
            elif rel in scale: status="ACTIVE"
            else: status="GREYED"
            self.tree.insert("", "end", values=(f"{NOTE_NAMES[abs_s%12]}{midi//12-1}",midi,f"{freq:.2f}",f"{cents:+}",status))
    # --- FAST NOTES KB - mouse only, no PC keyboard, Y = VOL LOG, KB ALWAYS FREE ---
    def _kb_note_at(self, event):
        items=self.kb_canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        for it in reversed(items):
            if it in self.key_rects:
                return self.key_rects[it]
        cur=self.kb_canvas.find_withtag("current")
        if cur and cur[0] in self.key_rects:
            return self.key_rects[cur[0]]
        return None
    def _play_kb_note(self, ki, event=None):
        if ki is None: return
        if ki==self.last_kb_note and self.kb_playing: return
        self.last_kb_note=ki; self.kb_playing=True; self.last_mouse_time=time.time()
        freq,_,midi,_=self.calculate_note_freq(ki)
        # MOUSE Y = VOL, LOG - top of KB loud, bottom quiet
        # KB is ALWAYS FREE - plays any note, even if not in chord, even if Chord Only is on
        if event is not None:
            raw_vol = 1.0 - (event.y / 180.0)
            vol = log_vol(raw_vol)
        else:
            vol = log_vol(0.7)
        play_sustained(freq, vol)
    def on_kb_press(self, event):
        self.kb_playing=True; self.last_kb_note=None
        ki=self._kb_note_at(event)
        self._play_kb_note(ki, event)
    def on_kb_drag(self, event):
        if not self.kb_playing: return
        ki=self._kb_note_at(event)
        if ki is not None and ki != self.last_kb_note:
            self._play_kb_note(ki, event)
        elif ki is not None and ki == self.last_kb_note:
            raw_vol = 1.0 - (event.y / 180.0)
            vol = log_vol(raw_vol)
            freq,_,_,_=self.calculate_note_freq(ki)
            play_sustained(freq, vol)
    def on_kb_release(self, event):
        self.kb_playing=False; self.last_kb_note=None
        stop_sustained()
    def on_gliss_drag(self, event):
        self.last_mouse_time=time.time(); w=self.gliss_canvas.winfo_width() or 1300; h=self.gliss_canvas.winfo_height() or 95
        norm=max(0,min(1,event.x/float(w))); self.mouse_x=norm
        # MOUSE Y = VOL, LOG - top loud, bottom quiet
        raw_vol = 1.0 - (event.y / float(h))
        vol = log_vol(raw_vol)
        freq,midi,qs=self.freq_from_norm(norm); self.gliss_canvas.delete("all"); w2=self.gliss_canvas.winfo_width() or 1300
        self.gliss_canvas.create_line(20,55,w2-20,55, fill="#00adb5", width=4)
        jx=self.joy_x*w2
        self.gliss_canvas.create_line(jx,15,jx,90, fill="#ff2e63", width=3)
        self.gliss_canvas.create_line(event.x,15,event.x,90, fill="#00ff88", width=5, tags="cursor")
        note_name = f"{NOTE_NAMES[int(midi)%12]}{int(midi)//12-1}" if qs else f"{freq:.1f}Hz"
        self.gliss_canvas.create_text(event.x, 10, text=note_name, fill="#ffffff", font=("Consolas",12,"bold"), tags="cursor")
        self.readout_label.config(text=f"MOUSE {freq:.1f}Hz {note_name} vol {vol:.2f}  |  Mouse green, Joy red")
        if vol < 0.02: stop_sustained()
        else: play_sustained(freq, vol)

if __name__=="__main__":
    root=tk.Tk(); app=SevenOctaveMintWorkbench(root); root.mainloop()
