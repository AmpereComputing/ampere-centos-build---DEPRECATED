DEPRECATED
This repository is deprecated and set to archive status. It will eventually be deleted.

Ampere CentOS 8.0 Build
===============

System Requirements
------------

- Ampere Altra system
- CentOS 8 
- Ampere Toolchain 8.3.0


Installing CentOS 8.0 via Installation Media 
------------

Preparing CentOS Installation Media
1. Prepare one USB storage device (8GB) and one SATA drive.
2. On a Linux machine, download the latest CentOS ISO file and dd to a USB storage device (>= 8GB)
```
# wget http://linux.mirrors.es.net/centos/8.0.1905/isos/aarch64/CentOS-8-aarch64-1905-dvd1.iso
# dd if= CentOS-8-aarch64-1905-dvd1.iso of=/dev/sdX
```
3. Plug the USB device and SATA disk into the board. 
4. Step by step install CentOS 8.0

Setting up Native CentOS Development Environment
------------

First, install the necessary development packages (if not done already).
```
# yum groupinstall "Development Tools"
# yum install ncurses-devel
# yum install hmaccalc zlib-devel binutils-devel elfutils-devel libelf-devel newt-devel python-devel
# yum install audit-libs-devel numactl-devel pciutils-devel openssl-devel
# yum install bc bison perl-ExtUtils-Embed.noarch xmlto asciidoc
```

Installing Ampere Computing Toolchain
------------

Install the toolchain on the board. Get Ampere 8.3.0 toolchain from Ampere support team.
```
# mkdir -p /opt/amp
# tar -xf ampere-8.3.0-20191025-dynamic-nosysroot-nativetools.tar.xz -C /opt/amp
```
Set PATH to point to the Ampere Toolchain
```
# export PATH=/opt/amp/ampere-8.3.0-20191025-dynamic-nosysroot/bin:$PATH;
# which gcc
# /opt/amp/ampere-8.3.0-20191025-dynamic-nosysroot/bin/gcc
```

Building Ampere CentOS
------------

Clone ampere-centos kernel and ampere-centos-build source
```
# git clone https://github.com/AmpereComputing/ampere-centos-kernel
# cd ampere-centos-kernel ; git checkout amp-centos-8.0-kernel ; cd ..
# git clone https://github.com/AmpereComputing/ampere-centos-build
# cd ampere-centos-build ; git checkout amp-centos-8.0-build ; cd ..
```
Package ampere-centos kernel source, you can find rpmversion, pkgrelease in SPECS/kernel-emag.spec
Currently,  rpmversion=4.18.0, pkgrelease=80.11.2.el8_0
```
# cd ampere-centos-build
# cp -r ../ampere-centos-kernel linux-4.18.0-80.11.2.el8_0
# cd linux-4.18.0-80.11.2.el8_0
# make distclean
# rm -fr .git
# cd -
# tar -cJf SOURCES/linux-4.18.0-80.11.2.el8_0.tar.xz linux-4.18.0-80.11.2.el8_0
# rm -fr linux-4.18.0-80.11.2.el8_0 
```
Build CentOS Kernel
```
rpmbuild --target aarch64 --define '%_topdir `pwd`' --define 'buildid .yymmdd+amp' --without debug --without debuginfo --without tools --without perf -ba SPECS/kernel-emag.spec
```
Build Optimized CentOS Kernel
```
rpmbuild --target aarch64 --define '%_topdir `pwd`' --define 'buildid .yymmdd+amp' --without debug --without debuginfo --without tools --without perf -ba SPECS/kernel-emag-optimized.spec
```

Building Ampere CentOS by script
------------

```
# git clone https://github.com/AmpereComputing/ampere-centos-kernel
# cd ampere-centos-kernel ; git checkout amp-centos-8.0-kernel ; cd ..
# git clone https://github.com/AmpereComputing/ampere-centos-build
# cd ampere-centos-build ; git checkout amp-centos-8.0-build ; cd ..
# cd ampere-centos-build ; 
# git checkout amp-centos-8.0-build
# ./amp-centos-build.sh
```
After build done, you will see these tarball files
```
amp_sw_centos_8.0-ddmmyy.opt-src.tar.xz
amp_sw_centos_8.0-ddmmyy.opt.tar.xz
amp_sw_centos_8.0-ddmmyy.src.tar.xz
amp_sw_centos_8.0-ddmmyy.tar.xz
```

Install Ampere CentOS Kernel
------------

Build CentOS Kernel
```
# cd RPMS/aarch64
# yum -y localinstall kernel*
```

Or extract amp_sw_centos_8.0-ddmmyy.tar.xz
```
# tar xf amp_sw_centos_8.0-ddmmyy.tar.xz
# cd aarch64
# yum -y localinstall kernel*
```

Install Ampere Optimized CentOS Kernel with Optimization Support
------------

Build Optimized CentOS Kernel
```
# cd RPMS/aarch64
# yum -y localinstall kernel*
```

Or extract amp_sw_centos_8.0-ddmmyy.opt.tar.xz
```
# tar xf amp_sw_centos_8.0-ddmmyy.opt.tar.xz
# cd aarch64
# yum -y localinstall kernel*
```

DEPRECATED  
