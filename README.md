### Disk surface background scan tool

Some RAID controllers to not provide full SMART functionality. Therefore they may report about SMART errors, but not be able to enable automatic background disk surface scans by SMART itself. In these cases it might be helpful to run these disk surface scans by using a manual tool.

The current tool slowly reads the whole surface of a given physical disk and then repeats indefinitely. The theory behind the motivation is that when the disk encounters a weak sector during the read operation, its firmware will hopefully relocate the data in this sector into a good spare sector. This will definitely happen when the weak sector is written to, but maybe reading the weak sector first helps the disk firmware to notice sooner that the data in the weak sector needs to be relocated.

Weak sector is a sector which is not yet bad, but is more difficult to read for the disk and might later go bad. Each disk has a set of spare sectors with the purpose of relocating data from weak sectors into the spares. After relocating the data the disk firmware will map the address of the weak sector to point to the spare sector.

Some RAID controllers have this surface scan functionality built in and have various names like "patrol read" and "disk scrubbing" (in other contexts the latter phrase can confusingly also mean safe disk data deletion software, but this is unrelated to surface scanning). Also, SMART itself has this surface scan functionality as well, called "automatic offline testing", but it needs to be enabled first by a manual command. But some RAID controllers do not have this automatic disk scan functionality. Considering that some RAID controllers also do not pass on all SMART commands to the disk firmware, the automatic SMART surface scanning can not be enabled and a custom solution might be helpful.

The scanning starts at random offset in order to avoid the bias towards scanning the beginning of the disk more often after the computer boots. While running under Windows, the current software is able to detect whether the computer is in use and slow down the disk scan rate while the user is active.

Note: Relying solely on this tool to detect and address disk issues may not be sufficient, and it is recommended to use a combination of tools and techniques for disk maintenance and monitoring.


### Usage

Under Windows:
<br>python diskscan.py "\\\\.\\PhysicalDrive0"
<br>or
<br>Under Linux:
<br>python diskscan.py "/dev/ploop12345"


A Python 2 or 3 installation is required. There are package dependencies:
<br> - psutil
<br> - pywin32 (under Windows OS only)
<br> - wmi (under Windows OS only, needed if pywin32 is not installed)


### Licence
Version 1.0.5
<br>Copyright: Roland Pihlakas, 2022, roland@simplify.ee
<br>Licence: LGPL 2.1
<br>You can obtain a copy of this free software from https://github.com/levitation-opensource/DiskScan/


### State
Ready to use. Maintained and in active use.


<br>
<br>
<br>
<br>

[![Analytics](https://ga-beacon.appspot.com/UA-351728-28/DiskScan/README.md?pixel)](https://github.com/igrigorik/ga-beacon)    
