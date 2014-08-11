#!/usr/bin/python
'''
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
    
Disclaimer:
This software has not been authorized, sponsored, or otherwise approved by Apple, Inc.
    
Please see README.md for usage and disclaimer.

Version: 1.0
'''

import glob
import sys
import os
import fnmatch

import shutil
import time
import biplist
import imobiledevice

class RemovePairRecords():
    def __init__(self):
        self.logfilename =  './removePairRecords_' + str(int(time.time())) + '.log'
        print '[-] Setting up logfile: %s' % self.logfilename
        self.logfile = open(self.logfilename, 'a')
        self.logr('unTRUST version 1.0 Copyright (C) 2014 Stroz Friedberg, LLC', 0)
        self.logr('unTRUST is designed to remove the pairing records from iOS devices.\n', 0)
        self.logr('This script utilizes libimobiledevice which is a beta library. If you encounter a Segmentation Fault:11 please run the script again. This is a known bug\n', 0)
    
        # Use libimobiledevice Cython wrapper to connect to device
        self.logr('Please connect your iOS device, hit Trust on the phone if necessary, and wait a few seconds, then press enter to continue...', 1)
        raw_input()
        self.logr('Connecting to device...', 0)
        try:
            self.device = imobiledevice.iDevice()
            self.client = imobiledevice.LockdownClient(self.device, handshake=True)
            self.logr('Device connected succesfully.', 0)
        except:
            self.logr('Failed to connect to device.', 0)
            print '\nCould not connect to device. Please ensure device is connected and try again'
            sys.exit()

    def strip_formatting(self, entry):
        return entry.replace('\n','').replace('\t','')


    def parse_plist_file(self, filename):
        plist_dict = None
        self.logr('Parsing .plist file: %s' % filename, 0)

        try:
            plist_dict = biplist.readPlist(filename)
        except:
            self.logr('Error parsing .plist file %s' % filename, 1)

        # Apple base64 encodes the Certificates in the binary plists
        # If any of these keys do not exist, give them blank string value
        if 'HostCertificate' in plist_dict.keys():
            plist_dict['HostCertificate'] = self.strip_formatting(plist_dict['HostCertificate'].encode("base64").strip())
        else:
            plist_dict['HostCertificate'] = ' '

        if 'RootCertificate' in plist_dict.keys():
            plist_dict['RootCertificate'] = self.strip_formatting(plist_dict['RootCertificate'].encode("base64").strip())
        else:
            plist_dict['HostCertificate'] = ' '

        if 'DeviceCertificate' in plist_dict.keys():
            plist_dict['DeviceCertificate'] = self.strip_formatting(plist_dict['DeviceCertificate'].encode("base64").strip())
        else:
            plist_dict['HostCertificate'] = ' '

        if 'HostID' not in plist_dict.keys():
            plist_dict['HostID'] = ' '

        if 'SystemBUID' not in plist_dict.keys():
            plist_dict['SystemBUID'] = ' '
        
        plist_dict['mtime'] = time.ctime(os.path.getmtime(filename))

        return plist_dict
    
    
    def clean_folders(self):
        if os.path.exists('./tmp'):
            shutil.rmtree('./tmp')
        if os.path.exists('./output'):
            shutil.rmtree('./output')

        os.mkdir('./tmp')
        os.mkdir('./output')


    def dump_pair_records(self):
        try:
            fr_service = self.client.start_service(imobiledevice.FileRelayClient)
            frc = imobiledevice.FileRelayClient(self.device, fr_service)

            dev_conn = frc.request_sources(['Lockdown'])
            data = dev_conn.receive(4096)
            
            filepath = './tmp/Lockdown.cpio.gz'
            f = open(filepath, 'wb')
            self.logr('Receiving %s' % filepath, 0)
            while data:
                print '.',
                f.write(data)
                data = dev_conn.receive(4096)
            
            print ''
            self.logr('Extracting...', 0)
            f.close()
            
            os.system('tar -xzf %s -C ./output' % filepath)
            
            self.logr('Shredding tmp files', 0)
            self.shred_files(['./tmp/Lockdown.cpio.gz'])
            shutil.rmtree('./tmp')
        except:
            self.logr('Could not connect to device!', 2)
            sys.exit()
            
        self.logr('Dumped pair records, press enter to continue...', 1)
        raw_input()


    def get_pair_records(self, root, plist_files):
        # Glob .plist pair records
        self.logr('The pairing records from the iOS device are temporarily stored here: %s' % root, 0)
        
        records = list()
        for filename in plist_files:
            # Parse the plist
            pr_dict = self.parse_plist_file(filename)
            records.append(pr_dict)
            
        return records
            
    
    def remove_pair_records(self, records):
        active_pr_dict = self.client.current_pair_record()
        if not active_pr_dict['SystemBUID']:
            active_pr_dict['SystemBUID'] = ''
        
        for pr_dict in records:
            if not pr_dict['SystemBUID']:
                pr_dict['SystemBUID'] = ''
            
            if not pr_dict:
                self.logr('Could not parse plist, skipping: %s' % filename, 1)
                continue
            
            if active_pr_dict['DeviceCertificate'] == pr_dict['DeviceCertificate'] and active_pr_dict['HostCertificate'] == pr_dict['HostCertificate'] and active_pr_dict['RootCertificate'] == pr_dict['RootCertificate'] and active_pr_dict['HostID'] == pr_dict['HostID']:
                self.logr('Skipping active pair record', 0)
                continue
            
            pair_record = imobiledevice.LockdownPairRecord(pr_dict['DeviceCertificate'], pr_dict['HostCertificate'], pr_dict['RootCertificate'], pr_dict['HostID'], pr_dict['SystemBUID'])
            self.client.unpair(pair_record)
            self.logr('Removed pair record created on %s with Host ID: %s' % (pr_dict['mtime'],pr_dict['HostID']), 0)

        if active_pr_dict:
            self.logr('Would you like to delete the active pair record with hostID: %s?' % active_pr_dict['HostID'], 1)
            to_del = raw_input('Type YES to delete the active pair record or NO to skip: ')
            if to_del.lower() == 'yes':
                # Passing no pair record removes the active pair record
                self.client.unpair()
                self.logr('Removed active pair record with Host ID: %s' % active_pr_dict['HostID'], 0)
            else:
                self.logr('Skipping record', 0)

    
    def start(self):
        self.logr('Starting program...',0)

        self.logr('Current working directory: %s' % os.getcwd(), 0)
        
        self.clean_folders()
        self.dump_pair_records()

        records_root = os.path.expanduser('./output/var/root/Library/Lockdown/pair_records')
        plist_files = (glob.glob(os.path.join(records_root, '*.plist')))

        records = self.get_pair_records(records_root, plist_files)
        
        self.remove_pair_records(records)

        self.logr('Process complete!', 0)
        self.logr('Would you like to shred the temporary copies of the pairing records and output files extracted from your phone and stored here: %s' % records_root, 1)

        # Show which files we're deleting
        to_del = raw_input('Type YES to shred the files, or press enter to close the program: ')

        if to_del.lower() == 'yes':
            self.logr('Shredding all output files...', 0)
            files = self.r_glob('./output')
            self.shred_files(files)
            shutil.rmtree('./output')
        else:
            self.logr('Not shredding plist files.', 0)

        self.logr('Goodbye.', 0)
        self.logfile.close()
		# A bandaid to get around the memory issues in libimobiledevice Cython wrappers
        self.client.quit(0)


    def r_glob(self, path):
        results = []
        for base, dirs, files in os.walk(path):
            matches = fnmatch.filter(files, '*')
            results.extend(os.path.join(base, file) for file in matches)
        return results


    def shred_files(self, filelist):
        for f in filelist:
            self.logr('Shredding and deleting %s' % f, 0)
            size = os.path.getsize(f)
            try:
                file = open(f, 'wb')
                for i in range(0,size):
                    file.write(''.join([chr(0x00)]))

                file.close()
                os.unlink(f)
                self.logr('Successfully shredded and deleted %s' % f, 0)
            except:
                self.logr('Error shredding %s' % f, 2)


    def logr(self, msg, sev):
        lvl = { 0: '[-] ', 1: '[*] ', 2: '[!] ' }
        lt = time.asctime( time.localtime(time.time()))
        level = lvl[sev]
        print level + msg
        self.logfile.write(level + lt + '\t' + msg + '\n')


if __name__ == "__main__":
    p = RemovePairRecords()
    p.start()