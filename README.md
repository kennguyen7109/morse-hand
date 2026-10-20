# 🖐️Morse Hand is a real-time webcam application that recognizes hand gestures to enter Morse code and convert it into text.

# 🖐️Gesture Control Guide

Touch your thumb to the corresponding fingertip to perform a command:

- **Index finger**: Enter a dot (`.`) 
- **Middle finger**: Enter a dash (`-`)
- **Ring finger**: Commit the character (if a Morse code is available) / Add a space ( ) (if the buffer is empty)
- **Pinky**: Delete one character (Backspace)

#🛠️**System Requirements & Installation**

**Requirements**
- **Python:** `3.11` (recommended)
- **Webcam:** Connected to your computer / WSL2

**Installation**
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

# 📹 Webcam connection
- **Method 1**: Run directly on Windows (the simplest option)
  + If you’re running the code in Windows PowerShell or Command Prompt, OpenCV will detect the webcam automatically without any additional configuration.
- **Method 2**: If you’re running the application in an Ubuntu environment on WSL, follow these steps to forward the webcam from Windows to WSL
- Step 1: Open PowerShell on Windows as an administrator
  1. List the connected USB devices:
     ```
     usbipd list
  2. Attach the webcam to WSL2 (replace <BUSID> with the camera’s ID)
     ```
     usbipd attach --wsl --busid <BUSID>
   + Tip: Automatically connect on future runs
     ```
     usbipd attach --wsl --busid <BUSID> --auto-attach
- Step 2: Check and grant permissions in the WSL terminal.
  + Check whether WSL has detected the camera (usually /dev/video0)
    ```
    ls /dev/video*
  + Grant Python permission to access the camera device
    ```
    sudo chmod 666 /dev/video0
# 🚀 Run the application
```
python main.py
