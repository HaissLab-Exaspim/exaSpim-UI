## UI for the Exaspim microscope
Developped at AllenBrainInstitute by Adam Glaser and Micah Woodard. THis is a simple Fork for pasteur's implementation following their open source published material.
Their original archrive publication is available here : https://www.biorxiv.org/content/10.1101/2023.06.08.544277v3

## List of fixes to adapt the original Exaspim codebase
These small fixes were necessary to adapt our specific motor config, and make the acquisitions possible.

- Adapting the axes movements to arbitrary axes configuration with the Pose classes : (removing away hardcoded axes names)
  - https://github.com/HaissLab-Exaspim/spim-core/issues/1
  - https://github.com/HaissLab-Exaspim/exa-spim-control/issues/3

- Fixing small isue with axes movements frozen in ``wait=True`` mode  
  - https://github.com/HaissLab-Exaspim/TigerASI/issues/2

- ASI serial device codes had outdated values depending on firmware installed  
  - https://github.com/HaissLab-Exaspim/TigerASI/issues/1
 
- Adapting the waveforms configuration to ensure -10V free signals in AO outputs 
  - https://github.com/HaissLab-Exaspim/exa-spim-control/issues/1
