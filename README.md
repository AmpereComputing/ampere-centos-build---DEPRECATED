Ampere CentOS kernel RPM build script

This is Ampere CentOS kernel RPM build script to support Ampere eMag
SoC's. These scripts are used to create RPM files for Ampere CentOS
kernel.

How to build Ampere CentOS RPM:
1. Clone ampere-centos-kernel
 # mkdir ampere-centos
 # cd ampere-centos
 # git clone https://github.com/AmpereComputing/ampere-centos-kernel
 # git clone https://github.com/AmpereComputing/ampere-centos-build
2. Build Ampere CentOS RPM files
 # cd ampere-centos-build
 # ./ampere-centos-build.sh

When the above steps are completed, the Ampere CentOS RPM files are
located at:
 ./amp_sw_centos_7.4-yymmdd.tar.xz
 ./amp_sw_centos_7.4-yymmdd.ilp32.tar.xz

Where yy is the last two digits of the year,
      mm is the digit of the month, and
      dd is the digit of the day.
The amp_sw_centos_7.4-yymmdd.tar.xz is the non-optimized version of
the Ampere CentOS kernel.
The amp_sw_centos_7.4-yymmdd.ilp32.tar.xz is the optimized version of
the Ampere CentOS kernel.
