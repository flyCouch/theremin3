Windows Peeps, look to the right to see releases.

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



Now it's a waiting game for the Mac test. The Mac one will be the fussy one, so give your friend's friend a heads-up - it will NOT just double-click and run like Windows.
Forward them this:
Mac test steps:
Download the noteStudy43-macOS.zip from the Release, not the .exe
Unzip it - you'll get noteStudy43.app
Don't double-click it first time. Right-click > Open
macOS will say "unverified developer" - click Open again in that popup
If it asks for Microphone access, click Allow - it needs that for sounddevice
If it opens and runs like the Windows version, we're golden.
What to ask them to report back:
Did it open at all, or did it bounce and quit?
Did the audio / sound part work?
Any popup about "damaged" or "can't be opened"? That one means Gatekeeper blocked it and we need to add a signing step.

## Linux - Ubuntu / Mint

### Install

1. Go to **Releases** on the right side of this page
2. Download the newest file that ends in `-linux.tar.gz`
   - Example: `noteStudy43-linux.tar.gz`
3. Find the downloaded file in your Downloads folder
4. Right-click it > **Extract Here**
   - You will get a file with no extension, e.g. `noteStudy43`

### Run

**Option 1 - Double-click (easiest):**
Double-click the extracted `noteStudy43` file.
If it asks "Do you want to run this?", click **Run**.

**Option 2 - Terminal (shows errors if it fails):**
1. Right-click in the folder where you extracted it > **Open in Terminal**
2. Type:
```bash
./noteStudy43
Press Enter.
If it won't run
1. "Execute as program" is off:
Right-click the file > Properties > Permissions > tick Allow executing file as program.
Or in terminal:
bash
chmod +x noteStudy43
2. It does nothing when you double-click:
Run it from terminal with Option 2 above to see the error. Double-click hides errors.
3. GLIBC_2.38 not found error:
You have an old download. Delete it and download the newest Linux release. The current build is made for Ubuntu 22.04 / Mint 21 and newer.
4. No sound / mic not working:
Make sure your mic is not muted in Sound Settings, and close any other app using the mic (Zoom, browser, etc.), then start the app again.
Uninstall
Just delete the noteStudy43 file and the .tar.gz file. Nothing else is installed on your system.
