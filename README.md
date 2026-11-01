# Theremin Game

### 🎮 Download Latest Windows EXE:
**[⬇️ CLICK HERE TO DOWNLOAD noteStudy33.exe](https://github.com/flyCouch/theremin2/releases/latest/download/theremin2.exe)**

No Python needed - just download and double-click!

---

#Theremin3 - 7-Octave Microtonal Theremin Workbench

Hardware-feel theremin for Linux Mint with joystick + mouse, scale quantization, and historical temperaments.

- **Joy Y: bottom=0 vol OFF, top=full** - LOG volume `pow(2.2)`
- **Joy X: LOG pitch** `pow(0.65)` - quantized to selected scale notes shown on keyboard
- **Center: drones** (does not cut off)
- **Mouse: also follows scale** - drag on black bar

### Features Kept

- **Root Key:** C, C#, D... B transpose
- **Scales:** Chromatic, Major (Ionian), Natural Minor, Pentatonic Major, Whole Tone, Blues, Pelog/Slendro (Gamelan approx), Hirajoshi, Raga Bhairav, OFF (Gliss)
- **Temperaments:** Equal Temperament 12-TET, Just Intonation, Pythagorean, Quarter-Comma Meantone, Werckmeister III, 19TET approx, OFF
- **Ref Pitch:** 415, 432, 435, 440, 442, 528 Hz
- **7-Octave Visual Keyboard:** white = active scale notes, grey = out of scale
- **Breakdown Table:** Note, MIDI, Freq, Cents, Status - fixed height 18 rows, uncramped

### Audio

- `sounddevice` OutputStream on device 20 (pulse) - 48000Hz, 2048 block, latency high
- True drone callback with smooth freq/vol interpolation - no clicks
- LOG vol for natural loudness.
