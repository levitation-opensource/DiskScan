# -*- coding: utf-8 -*-

#
# Author: Roland Pihlakas, 2017 - 2023
#
# roland@simplify.ee
#
# Version 1.0.5
# 
# Roland Pihlakas licenses this file to you under the GNU Lesser General Public License, ver 2.1.
# See the LICENSE file for more information.
#

import os
import sys
import time
from random import randint
import struct


# first argument is the python script name
if len(sys.argv) >= 2:

  print("")
  print("Starting...")

  # NB! for finding out drive order numbers used in the physical disk name, do NOT rely on AIDA64, instead use the drive order from Windows Disk Management 
  disk_name = sys.argv[1]

else:   #/ if len(sys.argv) >= 2:

  print('')
  print('')
  print('Description:')
  print('')
  print('Some RAID controllers to not provide full SMART functionality. Therefore they may report about SMART errors, but not be able to enable automatic background disk surface scans by SMART itself. In these cases it might be helpful to run these disk surface scans by using a manual tool.')
  print('')
  print('The current tool reads the whole surface of a given physical disk and then repeats indefinitely. The theory behind the motivation is that when the disk encounters a weak sector during the read operation, its firmware will hopefully relocate the data in this sector into a good spare sector. This will definitely happen when the weak sector is written to, but maybe reading the weak sector first helps the disk firmware to become aware sooner that the data in the weak sector needs to be relocated.')
  print('')
  print('Weak sector is a sector which is not yet bad, but is more difficult to read for the disk and might later go bad. Each disk has a set of spare sectors with the purpose of relocating data from weak sectors into the spares. After relocating the data the disk firmware will map the address of the weak sector to point to the spare sector.')
  print('')
  print('Some RAID controllers have this surface scan functionality built in and have various names like "patrol read" and "disk scrubbing" (in other contexts the latter phrase can confusingly also mean safe disk data deletion software, but this is unrelated to surface scanning). Also, SMART itself has this surface scan functionality as well, called "automatic offline testing", but it needs to be enabled first by a manual command. But some RAID controllers do not have this automatic disk scan functionality. Considering that some RAID controllers also do not pass on all SMART commands to the disk firmware, the automatic SMART surface scanning can not be enabled and a custom solution might be helpful.')
  print('')
  print('While running under Windows, the current software is able to detect whether the computer is in use and slow down the disk scan rate while the user is active.')
  print('')
  print('Note: Relying solely on this tool to detect and address disk issues may not be sufficient, and it is recommended to use a combination of tools and techniques for disk maintenance and monitoring.')
  print('')
  print('')
  print('Usage:')
  print('')
  print('Under Windows:')
  print(r'python diskscan.py "\\.\PhysicalDrive0"')
  print('or')
  print('Under Linux:')
  print(r'python diskscan.py "/dev/ploop12345"')
  print('')
  print('')
  print('A Python 2 or 3 installation is required. There are package dependencies:')
  print(' - psutil')
  print(' - pywin32 (under Windows OS only)')
  print(' - wmi (under Windows OS only, needed if pywin32 is not installed)')
  print('')
  print('')
  print('Version 1.0.5')
  print('Copyright: Roland Pihlakas, 2017 - 2023, roland@simplify.ee')
  print('Licence: LGPL 2.1')
  print('You can obtain a copy of this free software from https://github.com/levitation-opensource/DiskScan/')
  print('')
  print('')

  sys.exit()

#/ if len(sys.argv) >= 2:



if os.name == "nt":
  try:
    import win32api
  except Exception as msg:
    print(str(msg))
    print("run pip install pywin32")
    pass
    
    
def get_idle_time():
  try:
    return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000
  except:
    return sys.maxsize
    

try:
  import psutil

  if hasattr(psutil, "Process"):
    pid = os.getpid()

    p = psutil.Process(pid)
    
    # set to lowest  priority, this is windows only,  on Unix  use  ps.nice(19)
    # On UNIX this is a number which usually goes from -20 to 20. The higher the nice value, the lower the priority of the process.
    # https://psutil.readthedocs.io/en/latest/#psutil.Process.nice
    # p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 10)  # TODO: config
    p.nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 20)  # TODO: config
    # p.nice(psutil.IDLE_PRIORITY_CLASS)

    # On Windows only *ioclass* is used and it can be set to 2
    # (normal), 1 (low) or 0 (very low).
    p.ionice(0 if os.name == "nt" else psutil.IOPRIO_CLASS_IDLE)
    # p.ionice(2 if os.name == "nt" else psutil.IOPRIO_CLASS_BE)  # BE = best effort = normal
    
    print("Priorities set...")
    
  #/ if psutil.Process:
except Exception as msg:
  print(str(msg))
  print("run pip install psutil")
  pass


if os.name == "nt":
  try:  # psutil fails to set IO priority under Windows for some reason
    import win32process
  
    # NB! Sometimes SetPiorityClass is not enough to set IO priority
    # NB! SetThreadPriority must be called before SetPriorityClass else SetThreadPriority will throw
  
    # 0x00010000: THREAD_MODE_BACKGROUND_BEGIN
    # Begin background processing mode. The system lowers the resource scheduling priorities of the thread so that it can perform background work without significantly affecting activity in the foreground.
    # This value can be specified only if hThread is a handle to the current thread. The function fails if the thread is already in background processing mode.
    # Windows Server 2003:  This value is not supported
    # win32process.SetThreadPriority(-2, 0x00010000)  # NB! -2: win32api.GetCurrentThread()
   
    # 0x00100000: PROCESS_MODE_BACKGROUND_BEGIN
    # Begin background processing mode. The system lowers the resource scheduling priorities of the process (and its threads) so that it can perform background work without significantly affecting activity in the foreground.
    # This value can be specified only if hProcess is a handle to the current process. The function fails if the process is already in background processing mode.
    # Windows Server 2003 and Windows XP:  This value is not supported.
    # https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass
    win32process.SetPriorityClass(-1, 0x00100000)   # NB! -1: win32api.GetCurrentProcess()
 
  except Exception as msg:
    print(str(msg))
    print("run pip install pywin32")
    pass


if os.name == "nt":

  try:
    import win32file
    import winioctlcon
  
    # https://stackoverflow.com/questions/9901792/wmi-win32-diskdrive-to-get-total-sector-on-the-physical-disk-drive
    f = win32file.CreateFile(disk_name, win32file.GENERIC_READ, win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, 0)
    size = win32file.DeviceIoControl(f, winioctlcon.IOCTL_DISK_GET_LENGTH_INFO, None, 512, None)  #returns bytes
    precise_capacity = struct.unpack('q', size)[0]  #convert 64 bit int from bytes to int -> first element of returned tuple
    f.close()
 
  except Exception as msg:
    print(str(msg))
    print("run pip install pywin32")
  
    try:
      # NB! WMI result is a bit smaller than actual disk size
      import wmi
      c = wmi.WMI()
      disk_info = c.query("SELECT * FROM Win32_DiskDrive WHERE Name = '" + disk_name + "'")[0]
      precise_capacity = disk_info.BytesPerSector * disk_info.TotalSectors
    except Exception as msg:
      print(str(msg))
      print("run pip install wmi")  
    
      # use AIDA64 to get precise capacity: 
      # Storage -> ATA -> select Disk -> LBA Sectors * Physical / Logical Sector Size (assume 512 if missing)
      # NB! do not use this since it is rounded: Storage -> ATA -> select Disk -> Unformatted Capacity
      # NB! similarly, do not use Windows provided capacity
      # NB! for finding out drive order numbers used in the physical disk name, do NOT rely on AIDA64, instead use the drive order from Windows Disk Management 
      precise_capacity = 976703805 * 512  # 500072348160  
      pass

else:   #/ if os.name == "nt":

  # alternative would be to call "lsblk -b -d -o NAME,SIZE" command

  with open(disk_name, 'rb', buffering=0) as f:
    # f.seek(offset=0, whence=0)
    # Many Python built-in functions accept no keyword arguments
    f.seek(0, 2)   # whence=2 means seek to end
    precise_capacity = f.tell()

#/ #/ if os.name == "nt":
      

# https://superuser.com/questions/839502/windows-equivalent-for-dd
with open(disk_name, 'rb', buffering=0) as f:

  print("precise_capacity: " + str(precise_capacity))
  capacity = precise_capacity 

  # divide by 4M and then find next power of two
  step = precise_capacity / (16 * 1024 * 1024)
  step = max(4096, 1 << int(step - 1).bit_length())   # https://stackoverflow.com/questions/14267555/find-the-smallest-power-of-2-greater-than-or-equal-to-n-in-python
  # step = int((step + 4095) / 4096) * 4096
  # step = 128 * 1024
  # step = 1024 * 1024
  
  idle_step = 16 * step  
  idle_time = 60  # seconds


  print("step: " + str(step))

  if os.name == "nt":
    print("idle_step: " + str(idle_step))
    print("idle_time: " + str(idle_time))


  mb = 1024 * 1024

  start_offset = randint(0, int(precise_capacity / step)) * step
  # f.seek(offset=start_offset, whence=0)   # skip the bad sector   # whence=0 means absolute file positioning
  # Many Python built-in functions accept no keyword arguments
  f.seek(start_offset, 0)   # whence=0 means absolute file positioning

  i = 0
  prev_i = 0
  total_bytes_read = 0
  while True:

    if abs(i - prev_i) >= mb:   # NB! handle cases when offset was changed in 512 byte increments
      print('{} MB scanned, offset {}'.format(int(total_bytes_read / mb), (start_offset + i) % capacity))
      prev_i = i
      
    try:
      while psutil.sensors_battery() and not psutil.sensors_battery().power_plugged:   # NB! psutil.sensors_battery() may be None if there is no battery
        time.sleep(1)
    except Exception:
      pass


    try:

      if start_offset + i >= capacity:
        start_offset = 0
        i = 0
        # f.seek(offset=0, whence=0)
        # Many Python built-in functions accept no keyword arguments
        f.seek(0, 0)   # whence=0 means absolute file positioning
        

      current_step = idle_step if get_idle_time() >= idle_time else step

      next_rounded_offset = int((start_offset + i + current_step) / step) * step
      current_step = next_rounded_offset - (start_offset + i)   # NB! after stepping bad sectors try to adjust offset so that it again aligns with the step
      
      len_until_disk_end = capacity - (start_offset + i)
      current_step = min(current_step, len_until_disk_end)  # NB! do not try to read past disk end

      # print(str(current_step))

      a = f.read(current_step)      
      i += current_step
      total_bytes_read += current_step

    except Exception as msg:

      if start_offset + i < precise_capacity:
        print("Error reading disk at offset " + str((start_offset + i) % capacity) + " : " + str(msg))

      
      # NB! step by one sector increments until no more errors are encountered in order to detect any further bad sectors immediately after the first one
      
      i += 512
      total_bytes_read += 512
      # f.seek(offset=512, whence=1)   # skip the bad sector   # whence=1 means seek relative to the current position
      # Many Python built-in functions accept no keyword arguments
      f.seek(512, 1)   # skip the bad sector   # whence=1 means seek relative to the current position


    if total_bytes_read >= capacity:
      break

    time.sleep(1)

  #/ while True:
#/ with open(disk_name,'rb') as f:

print("")
print("Done.")
print("")
