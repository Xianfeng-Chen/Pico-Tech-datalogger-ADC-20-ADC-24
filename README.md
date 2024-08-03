PicoScope ADC-20/ADC-24
1. Use the picosdk-python-wrappers from the official PicoTech github website
(1) Install the PicoSDK
https://www.picotech.com/downloads 
(2) Install git, change the path
https://git-scm.com/downloads 
https://stackoverflow.com/questions/4492979/error-git-is-not-recognized-as-an-internal-or-external-command
(3) Clone the picosdk-python-wrappers using git in a chosen folder
Anaconda Prompt-> cd [a chosen folder] ->
->git clone https://github.com/picotech/picosdk-python-wrappers.git
(4) In the command prompt, cd the chosen folder and follow the github instructions
https://github.com/picotech/picosdk-python-wrappers#unsupported-models 
->pip install .
Important notes:
voltage_range = ctypes.c_int16(0)  # Voltage range index (0 corresponds to 2500mV), only choose 0 or 1 for ADC20
