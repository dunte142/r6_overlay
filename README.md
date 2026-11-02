# R6 Tactical Overlay

A Windows desktop companion for Tom Clancy's Rainbow Six Siege. It includes a visual reference launcher and an always-on-top in-game overlay with optional screen and audio analysis.

## Features

- **Launcher:** a scrollable home page with News, Agents, and Maps sections.
- **Operator reference:** attacker and defender cards, operator details, gadget descriptions, and tactical tips.
- **Map reference:** map artwork, floor information, and camera references where available.
- **Two in-game overlay layers:** a lightweight sound layer stays available over the game, while **F1** or **Insert** shows or hides the tactical layer. The sound direction ring sits around the in-game compass. The tactical layer shows your operator, detected teammates, and revealed enemies.
- **Operator cards:** in-game team cards use the supplied attacker and defender mini-data artwork, including operator names, gadget images, and descriptions.
- **Vision worker:** screen capture and visual recognition for maps, floors, sides, operators, enemies, and minimap data. OCR uses Tesseract when it is installed.
- **Audio worker:** optional WASAPI loopback audio analysis through PyAudioWPatch.
- **Fault isolation:** the Qt interface, vision worker, and audio worker run separately so failures in native vision or audio dependencies are less likely to close the interface.

The application reads visual and audio output for its companion HUD; it does not need to read or modify game memory.

## Requirements

- Windows 10 or 11, 64-bit.
- Python 3.12 (64-bit) is recommended. The launcher script also accepts Python 3.10 or 3.11 (64-bit) as a fallback.
- Tesseract OCR for text-based recognition. Install it separately; the vision worker checks the Windows default install locations and the system `PATH`.
- A loopback-capable Windows audio device for audio direction features. Audio analysis is optional.

Python packages and pinned versions are listed in [`requirements.txt`](requirements.txt).

## Run

Double-click `iniciar.bat`. It selects a supported 64-bit Python installation, installs the required packages, and starts `launcher.py`.

To open the visual overlay demo without starting the full launcher, run `probar_demo.bat`.

## In-game hotkeys

| Key | Action |
| --- | --- |
| F1 or Insert | Show or hide the tactical information layer; the sound layer remains available |

## Project layout

```text
launcher.py          Desktop launcher and reference screens
main.py              In-game overlay entry point and worker coordination
ui/                  Qt overlay, assets, and Windows hotkeys
vision/              Screen capture, OCR, minimap, and visual recognition
audio/               Isolated WASAPI loopback worker
data/                Operator, gadget, camera, and map reference data
assets/              UI artwork, operator cards, and map resources
tools/               Development and maintenance utilities
```

## Notes

- The launcher and in-game HUD are separate entry points: `iniciar.bat` opens the launcher, while `main.py` starts the in-game overlay process. F1 and Insert are registered as global hotkeys so the tactical layer can be toggled during a round without giving it focus.
- Some visual recognition depends on game HUD layout and screen resolution; OCR and audio features may be unavailable when their external tools or supported devices are missing.
- This is a community companion project and is not affiliated with or endorsed by Ubisoft.
