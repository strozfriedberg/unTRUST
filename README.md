Copyright (C) 2014 Stroz Friedberg, LLC

This program is free open source software and licensed under the terms of the GNU Lesser General Public License version 2.1.  
A copy of the GNU Lesser General Public License version 2.1 is available at <http://www.gnu.org/licenses/lgpl-2.1.txt>.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You can contact Stroz Friedberg by electronic and paper mail as follows:  
  
Stroz Friedberg, LLC
32 Avenue of the Americas, 4th Floor
New York, NY, 10013
info@strozfriedberg.com

Version: 1.0

Disclaimer:
This software has not been authorized, sponsored, or otherwise approved by Apple, Inc.

About:
    unTRUST is designed to remove the pairing records from iOS devices, thus requiring the user to choose to Trust subsequent connections 
    with computers in order to allow the computer to access certain functions and features of iOS, including those that transfer user data. 

Install:
    Run bash install.sh in Terminal on any Mac with Mac OS X 10.9+ 

Requirements:
  1. OS: Mac OS X 10.9.x
  2. Python: version 2.7, subprocess, glob, sys, os, biplist, six
  3. C: libimobiledevice-stroz, libusb, libgcrypt, libplist, libzip, usbmuxd
  4. OS utilities: gcc, git, pkgconfigm, cmake, automake, autoconf, libtool, Xcode 5.x, tar

Notes:
  1. This will create files in the curret working directory.
  2. This will offer to completely shred temp files it creates.

Usage:
  1. Run install.sh in this directory which will install all dependencies. Optionally, you may follow the steps outlined in install.sh manually.
  2. Connect your iOS device to this computer.
  3. Run unTRUST.py: python unTRUST.py and follow prompts
    
    
libimobiledevice modifications:
  1. Added method to lockdown.c called: lockdownd_pair_record_t pair_record_get_current(lockdownd_client_t client) which gives direct access to the current pair record for the connection and corresponding Cython method in lockdown.pxi called: cpdef dict current_pair_record(self)
  2. Added method to imobiledevice.pyx called: cpdef bytes receive(self, uint32_t size) which allows for receiving data through file_relay in Cython
  3. Added __cinit__ and __dealloc__ method in lockdown.pxi in LockdownPairRecord object for creation and release of custom pair record
    
