# R6 Tactical Overlay

A Windows desktop companion for Tom Clancy's Rainbow Six Siege. It includes a visual reference launcher and an always-on-top in-game overlay with optional screen and audio analysis.

## Features

- **Launcher:** a scrollable home page with News, Agents, and Maps sections.
- **Operator reference:** attacker and defender cards, operator details, gadget descriptions, and tactical tips.
- **Map reference:** map artwork, floor information, and camera references where available.
- **In-game HUD:** press **F1** to show or hide the tactical HUD. It displays your detected operator's information and enemy operators recognized by the program, alongside teammate information and match details.
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
| F1 | Show or hide the tactical HUD with your detected operator and recognized enemies |

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

- The launcher and in-game HUD are separate entry points: `iniciar.bat` opens the launcher, while `main.py` starts the in-game overlay process. F1 is the only registered global hotkey.
- Some visual recognition depends on game HUD layout and screen resolution; OCR and audio features may be unavailable when their external tools or supported devices are missing.
- This is a community companion project and is not affiliated with or endorsed by Ubisoft.
