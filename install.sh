#!/bin/bash

#  Installation.sh

#  Copyright (C) 2014 Stroz Friedberg, LLC
#    
#  This program is free open source software and licensed under the terms of the GNU Lesser General Public License version 2.1.  
#  A copy of the GNU Lesser General Public License version 2.1 is available at <http://www.gnu.org/licenses/lgpl-2.1.txt>.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You can contact Stroz Friedberg by electronic and paper mail as follows:
#    
#  Stroz Friedberg, LLC
#  32 Avenue of the Americas, 4th Floor
#  New York, NY, 10013
#  info@strozfriedberg.com
#    
#  Disclaimer:
#  This software has not been authorized, sponsored, or otherwise approved by Apple, Inc.
#    
#  Please see README.md for usage and disclaimer.
#

check_ret()
{
        if [ $? -ne 0 ] ; then
                echo "Failed! Leaving"
                read -p "Press Return to Close..."
                exit
        fi
}

echo "Only run this setup program in its own folder along with the components of unTRUST."
read -p "Press Return to Continue..."

echo "You must install Xcode command line tools first..."
xcode-select --version
check_ret
echo "All set."

echo "Installing homebrew"
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
echo "Done."


echo "Installing libimobiledevice dependencies"
brew install openssl python git pkgconfig cmake automake autoconf libtool libusb libgcrypt libplist libzip usbmuxd
check_ret
echo "Done."

echo "Installing Cython"
sudo pip install cython
check_ret
echo "Done"

echo "Installing biplist"
sudo easy_install biplist
check_ret
echo "Done"

echo "Installing libplist"
rm -rf ./libplist
check_ret
git clone https://github.com/libimobiledevice/libplist.git
check_ret
cd ./libplist
autoreconf -i
./autogen.sh
check_ret
make
check_ret
sudo make install
check_ret
echo "Done."

echo "Moving things into place..."
sudo mkdir /usr/local/include/plist/cython
sudo cp /usr/local/lib/python2.7/site-packages/plist.* /usr/local/include/plist/cython
check_ret
sudo cp ./cython/plist.pxd /usr/local/include/plist/cython
check_ret
cd ..
rm -rf ./libplist
echo "Done."

echo "Installing custom libimobiledevice"
cd ./libimobiledevice-stroz
autoreconf -f -i
./autogen.sh
check_ret
make
make #often fails the first time
check_ret
sudo make install
check_ret
echo "Done."

echo "Moving everything into place..."
sudo cp /usr/local/lib/python2.7/site-packages/imobiledevice.* /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7
check_ret
sudo cp /usr/local/lib/python2.7/site-packages/plist.* /System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7
check_ret
echo "Done!"

