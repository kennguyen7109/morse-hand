# 🖐️Morse Hand is a real-time webcam application that recognizes hand gestures to enter Morse code and convert it into text.
---
# 🖐️Gesture Control Guide

Touch your thumb to the corresponding fingertip to perform a command:

- **Index finger**: Enter a dot (`.`) 
- **Middle finger**: Enter a dash (`-`)
- **Ring finger**: Commit the character (if a Morse code is available) / Add a space ( ) (if the buffer is empty)
- **Pinky**: Delete one character (Backspace)
---

#🛠️**System Requirements & Installation**
 **Requirements**
- **Python:** `3.11` (recommended)
- **Webcam:** Connected to your computer / WSL2
---

# Installation
1. **Cloning Repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<TEN_TAI_KHOAN>/morse_hand.git
   cd morse_hand
2. **Create and activate a virtual environment (venv):**
   ```bash
   python3.11 -m venv .venv311
   source .venv311/bin/activate
   Or .venv311\Scripts\activate in Windows PowerShell
4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   
