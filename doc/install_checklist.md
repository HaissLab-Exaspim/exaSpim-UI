## Driver/software downloads and installs. 

- [x] Pycharm or whatever python interpreter to write code. **Used VScode**
- [ ] Tiger ASI driver for the USB serial adapter
- [ ] Tiger Control Panel
- [x] Gitbash- IMPORTANT when prompted let git be added to PATH. Makes things easier downstream. Computer will need to be restarted. **I used plain git instead. With pdm, no need for gitbash.**
- [x] Anaconda or another python console interpreter. I like anaconda to make environments and stuff in prompt. IMPORTANT add anaconda to PATH when prompted it will save headache in the future. **I used pdm for a more lightweighted and reproducible approach**
- [x] Ni-DAQ Driver. **Florent did it**
- [x] Camera driver e.g. egrabber for coaxlink and gigelink.After downloading and installing eGrabber, you will need to install the eGrabber python package (stored as a wheel file). To install, open conda, navigatre to egrabber subfolder and write: **Florent did it**
	To install [egrabber python](https://documentation.euresys.com/Products/COAXLINK/COAXLINK/en-us/Content/04_eGrabber/programmers-guide/Python.htm) bindings, you have to go to the egrabber installation folder (found in python folder of the install folder). Of course, [egrabber must be installed](https://www.euresys.com/en/Support/Download-area) first.
    Go to your environment to use it's package manager (pip, pdm etc) and run :  
    
```shell
pip install C:\Program Files\Euresys\eGrabber\python\egrabber-23.08.0.17-py2.py3-none-any.whl
```  

## Adding all the necessary repos to pdm
- [x] exaSpim-UI (forked into HaissLab-Exaspim)
	it installs (via requirements :)
	- [x] exa-spim-control (forked into HaissLab-Exaspim)
    - [x] Spim-core (forked into HaissLab-Exaspim)
    - [x] TigerASI (HaissLab-Exaspim - comes with Spim core HaissLab-Exaspim as a requirement)
	- [x] Aind-data-schema (forked into HaissLab-Exaspim)

- [ ] SPIM-UI-Launch ( this repo doesn't exist ?)

- Laser repos (oxxius_laser, vortran_laser, obis-laser)
    Florent installed the coherent laser control UI

## Running things

- Once everything is installed correctly then go to the device manager and update the com ports in the config.toml file for the correct devices.

    Run exaspim_main.py in exaspim_UI repo and hopefully napari will pop up no problem

        If you have trouble connecting to lasers, switch lasers on and off and turn interlock on and back off

        If napari won’t pop up, check the console and see if you’re missing a pip installable package

    Install fio

    If using spim-core, need to install fios. I found it hard, but I’m sure it’ll be a piece of cake for you!

    Clone the repo into projects folder

    The fio repo has a pretty detailed install but just incase I’ll reiterate what worked for me

    Download the latest fio msi windows installer

    Download cygwin. IMPORTANT: when installing Cygwin, it will ask you what packages you want installed. Specify make and then any packages starting with mingw64-x86_64

    Open cyqwin terminal and navigate to the drive your working from. For example, mine was the c drive so type:

          cd /cygdrive/c 

Navigate to the projects folder where you cloned the fio repo

    cd   /cygdrive/c/users/micah.woodard/projects/fio 

Then run

./configure 

make 

make install 

    IMPORTANT: I had to delete the block comments found in the configure file before this would run and it still complained a little about $’\r’ not being found but it did work.

    Make sure to close any pycharm or command prompt instances before trying to use command fio

TROUBLESHOOTING HARDWARE :

Stage:

    Problem- Responses from stage have strange characters intermixed within reply.

    Cause- The Tiger Controller cards are physically addressed and hardcoded in the field to a certain card number. This is listed on the top of the front panel of the card. The physical order (left to right) in the controller does not matter, but there cannot be duplicates of the same card number at the same time. In the in the event that there are duplicates, there can be strange behavior. For example, both duplicated cards may not appear properly to the controller, other cards could be impacted, and the overall communication in/out of the controller may be corrupted.

    Solution- Remove one of the duplicated cards. If both need to be connected at the same time, the card must be physically shipped back to ASI for a reflash of new firmware. WARNING: never remove a card from the controller when it is powered ON. This can 'brick' and destroy the entire controller and/or card(s).

    Problem- The two twin vertical stages (usually Z/F axes) are corrupt and blink red repeatedly after being moved.

    Cause- The two vertical stages are usually coupled together, where the F is 'slave' to the Z axis. If the two axes get off from one another too much in their position, the controller will lock them out and flash red indicating an error. You can visually inspect the two risers to roughly check if they are at the same position or not or check the Tiger UI positions tab.

    Solution- If one axis is very far off from the other, you can explicitly tell the F axis to move to a certain position using the MOVEREL or MOVE commands. Be very careful here, and ideally detached anything like a XY stage that is attached to both vertical stages. Because if things go awry, this could mechanically damage and torque the XY stage. Alternatively, you could connect the cables from the ZF stages to a different card, like the XY card. In this case you could use the joystick to independently move both risers to the same location. Same caution here, detach anything attached to both vertical stages.


## IMPORTANT :
- [ ] tigerasi  : COM ports to None for simulated mode, otherwise, was COM3 before (but anyway we will have a trinamic thing on watever port we will see at that point)
    in file : exa-spim-control\exaspim\exaspim.py

- etf electronic tunable focus (something like that)


Documentation of how to tune the TigerASI stages  
- https://asiimaging.com/docs/stage_accuracy_settling_time_for_asi_stage#tuning_stages_to_minimize_move_time

Documentation of how to use TigerASI commands
- https://asiimaging.com/docs/products/tiger

Documentation of the Custom Commands 
(example : for switching the z axis to linear / rotary encoders )
- https://asiimaging.com/docs/products/serial_commands#commandcustoma_cca

Documentation of the settling time and accuracy for axes movements (dependant on PID tuning and other settings)
- https://asiimaging.com/docs/stage_accuracy_settling_time_for_asi_stage
