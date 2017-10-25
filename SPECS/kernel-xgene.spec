# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

%global src_pkg_name kernel-alt
%global bin_pkg_name kernel
%global bin_suffix_name %{nil}

Summary: The Linux kernel

# % define buildid .local

# For a kernel released for public testing, released_kernel should be 1.
# For internal testing builds during development, it should be 0.
%global released_kernel 0

%global distro_build 22

%define rpmversion 4.11.0
%define pkgrelease 22.el7a

# allow pkg_release to have configurable %{?dist} tag
%define specrelease 22%{?dist}

%define pkg_release %{specrelease}%{?buildid}

# The kernel tarball/base version
%define rheltarball %{rpmversion}-%{pkgrelease}

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# kernel
%define with_default   %{?_without_default:   0} %{?!_without_default:   1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-kdump (only for s390x)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     0}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 0}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_with_kernel_abi_whitelists: 0} %{?!_with_kernel_abi_whitelists: 1}

# In RHEL, we always want the doc build failing to build to be a failure,
# which means settings this to false.
%define doc_build_fail false

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}

# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}

# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'. RHEL only ever does 1.
%define debugbuildsenabled 1

%define with_gcov %{?_with_gcov: 1} %{?!_with_gcov: 0}

# turn off debug kernel and kabichk for gcov builds
%if %{with_gcov}
%define with_debug 0
%define with_kabichk 0
%endif

%define make_target bzImage

# Kernel Version Release + Arch -> KVRA
%define KVRA %{version}-%{release}.%{_target_cpu}
%define hdrarch %{_target_cpu}
%define asmarch %{_target_cpu}
%define cross_target %{_target_cpu}

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_debug 0
%define with_kdump 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_default 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%endif

# These arches install vdso/ directories.
%define vdso_arches aarch64 ppc64le s390x x86_64

# Overrides for generic default options

# only build debug kernel on architectures below
%ifnarch aarch64 ppc64le s390x x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_kernel_abi_whitelists 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_default 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs %{src_pkg_name}-%{version}-*.config
%endif

# sparse blows up on ppc*
%ifarch ppc64 ppc64le ppc
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch aarch64
%define asmarch arm64
%define hdrarch arm64
%define all_arch_configs %{src_pkg_name}-%{version}-xgene.config %{src_pkg_name}-%{version}-xgene-debug.config
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%define image_install_path boot
%endif

%ifarch i686
%define asmarch x86
%define hdrarch i386
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs %{src_pkg_name}-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%endif

%ifarch ppc64 ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs %{src_pkg_name}-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_bootwrapper 1
%define cross_target powerpc64
%define kcflags -O3
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs %{src_pkg_name}-%{version}-s390x*.config
%define image_install_path boot
%define kernel_image arch/s390/boot/bzImage
%define with_tools 0
%define with_kdump 1
%endif

#cross compile make
%if %{with_cross}
%define cross_opts CROSS_COMPILE=%{cross_target}-linux-gnu-
%define with_perf 0
%define with_tools 0
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%define listnewconfig_fail 1

# We only build kernel headers package on the following, for being able to do
# builds with a different bit length (eg. 32-bit build on a 64-bit environment).
# Do not remove them from ExclusiveArch tag below
%define nobuildarches i686 ppc s390

%ifarch %nobuildarches
%define with_bootwrapper 0
%define with_default 0
%define with_debug 0
%define with_debuginfo 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs aarch64 ppc64le x86_64

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3, xfsprogs < 4.3.0, kmod < 20-9

# We moved the drm include files into kernel headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
%define initrd_prereq  dracut >= 033-283

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVRA}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20160615-46\
Requires(post): %{_sbindir}/new-kernel-pkg\
Requires(post): system-release\
Requires(preun): %{_sbindir}/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: %{src_pkg_name}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# Some architectures need a different headers version for user space builds with
# a different bit length environment (eg. 32-bit user space build on 64-bit).
# For architectures we support, where we must provide a compatible kernel-headers
# package, don't exclude them in ExclusiveArch below, but add them to
# %%nobuildarches (above) instead. Example: if we support x86_64, we must build
# the i686 (32-bit) headers and provide a package with them
ExclusiveArch: aarch64 i686 noarch ppc ppc64le s390 s390x x86_64
ExclusiveOS: Linux

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config >= 9.1.0-55
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl openssl-devel
BuildRequires: hmaccalc
BuildRequires: python-devel, newt-devel, perl(ExtUtils::Embed)
BuildRequires: git
%ifarch x86_64
BuildRequires: pesign >= 0.109-4
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel bison
BuildRequires: audit-libs-devel
%ifnarch s390 s390x
BuildRequires: numactl-devel
%endif
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
%if %{with_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8/RHEL 6.
# The -r flag to find-debuginfo.sh invokes eu-strip --reloc-debug-sections
# which reduces the number of relocations in kernel module .ko.debug files and
# was introduced with rpm 4.9 and elfutils 0.153.
BuildRequires: rpm-build >= 4.9.0-1, elfutils >= 0.153-1
%define debuginfo_args --strict-build-id -r
%endif
%ifarch s390x
# required for zfcpdump
BuildRequires: glibc-static
%endif

Source0: linux-%{rpmversion}-%{pkgrelease}.tar.xz

Source1: Makefile.common

Source10: sign-modules
%define modsign_cmd %{SOURCE10}
Source11: x509.genkey
Source12: extra_certificates
%if %{?released_kernel}
Source13: securebootca.cer
Source14: secureboot.cer
%define pesign_name redhatsecureboot301
%else
Source13: securebootca.cer
Source14: secureboot.cer
%define pesign_name redhatsecureboot003
%endif
Source15: centos-ldup.x509
Source16: centos-kpatch.x509

Source18: check-kabi

Source20: Module.kabi_x86_64
Source21: Module.kabi_ppc64le
Source22: Module.kabi_aarch64
Source23: Module.kabi_s390x

Source25: kernel-abi-whitelists-%{distro_build}.tar.bz2

Source50: %{src_pkg_name}-%{version}-x86_64.config
Source51: %{src_pkg_name}-%{version}-x86_64-debug.config

# Source60: %{src_pkg_name}-%{version}-ppc64.config
# Source61: %{src_pkg_name}-%{version}-ppc64-debug.config
Source62: %{src_pkg_name}-%{version}-ppc64le.config
Source63: %{src_pkg_name}-%{version}-ppc64le-debug.config

Source70: %{src_pkg_name}-%{version}-s390x.config
Source71: %{src_pkg_name}-%{version}-s390x-debug.config
Source72: %{src_pkg_name}-%{version}-s390x-kdump.config

Source80: %{src_pkg_name}-%{version}-aarch64.config
Source81: %{src_pkg_name}-%{version}-aarch64-debug.config

Source90: %{src_pkg_name}-%{version}-xgene.config
Source91: %{src_pkg_name}-%{version}-xgene-debug.config
Source92: %{src_pkg_name}-%{version}-xgene-optimized.config
Source93: %{src_pkg_name}-%{version}-xgene-optimized-debug.config

# Sources for kernel tools
Source2000: cpupower.service
Source2001: cpupower.config

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

BuildRoot: %{_tmppath}/%{src_pkg_name}-%{KVRA}-root

%description
The %{src_pkg_name} package contains the Linux kernel sources. The Linux kernel
is the core of any Linux operating system.  The kernel handles the basic
functions of the operating system: memory allocation, process allocation, device
input and output, etc.


%package -n %{bin_pkg_name}
Summary: The Linux kernel
Group: System Environment/Kernel
%kernel_reqprovconf

%description -n %{bin_pkg_name}
The %{bin_pkg_name} package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions of the operating
system: memory allocation, process allocation, device input and output, etc.


%package -n %{bin_pkg_name}-doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
AutoReqProv: no
%description -n %{bin_pkg_name}-doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package -n %{bin_pkg_name}-headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description -n %{bin_pkg_name}-headers
%{bin_pkg_name}-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package -n %{bin_pkg_name}-bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description -n %{bin_pkg_name}-bootwrapper
%{bin_pkg_name}-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{bin_pkg_name}-debuginfo packages
Group: Development/Debug
%description -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
This package is required by %{bin_pkg_name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf%{?bin_suffix:-%{bin_suffix}}
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf%{?bin_suffix:-%{bin_suffix}}
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}

%package -n python-perf%{?bin_suffix:-%{bin_suffix}}
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf%{?bin_suffix:-%{bin_suffix}}
The python-perf%{?bin_suffix:-%{bin_suffix}} package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}

%package -n %{bin_pkg_name}-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:2.0
Requires: %{bin_pkg_name}-tools-libs = %{version}-%{release}
%description -n %{bin_pkg_name}-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n %{bin_pkg_name}-tools-libs
Summary: Libraries for the %{bin_pkg_name}-tools
Group: Development/System
License: GPLv2
%description -n %{bin_pkg_name}-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n %{bin_pkg_name}-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: %{bin_pkg_name}-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: %{bin_pkg_name}-tools-libs = %{version}-%{release}
%description -n %{bin_pkg_name}-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n %{bin_pkg_name}-tools-debuginfo
Summary: Debug information for package %{bin_pkg_name}-tools
Group: Development/Debug
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n %{bin_pkg_name}-tools-debuginfo
This package provides debug information for package %{bin_pkg_name}-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|XXX' -o tools-debuginfo.list}

%endif # with_tools

%if %{with_gcov}
%package -n %{bin_pkg_name}-gcov
Summary: gcov graph and source files for coverage data collection.
Group: Development/System
%description -n %{bin_pkg_name}-gcov
kernel-gcov includes the gcov graph and source files for gcov coverage collection.
%endif

%package -n %{bin_pkg_name}-abi-whitelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol whitelists
Group: System Environment/Kernel
AutoReqProv: no
%description -n %{bin_pkg_name}-abi-whitelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package -n %{bin_pkg_name}-%{?1:%{1}-}debuginfo\
Summary: Debug information for package %{bin_pkg_name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{bin_pkg_name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{bin_pkg_name}-%{?1:%{1}-}debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{bin_pkg_name}-%{?1:%{1}-}debuginfo\
This package provides debug information for package %{bin_pkg_name}%{?1:-%{1}}.\
This is required to use SystemTap with %{bin_pkg_name}%{?1:-%{1}}-%{KVRA}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVRA}%{?1:\.%{1}}/.*|/.*%%{KVRA}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package -n %{bin_pkg_name}-%{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: %{bin_pkg_name}-%{?1:%{1}-}devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVRA}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n %{bin_pkg_name}-%{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package -n %{bin_pkg_name}-%1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description -n %{bin_pkg_name}-debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description -n %{bin_pkg_name}-kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_default}
echo "Cannot build --with baseonly, default kernel build is disabled"
exit 1
%endif
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

%setup -q -n %{src_pkg_name}-%{rheltarball} -c
mv linux-%{rheltarball} linux-%{KVRA}
cd linux-%{KVRA}

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/%{src_pkg_name}-%{version}-*.config .

ApplyOptionalPatch linux-kernel-test.patch


if [ ! -d .git ]; then
  git init
  git config user.email "noreply@centos.org"
  git config user.name "AltArch Kernel"
  git config gc.auto 0
  git add .
  git commit -a -q -m "baseline"
fi


# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
	mkdir configs
fi

# Remove configs not for the buildarch
for cfg in %{src_pkg_name}-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f %{src_pkg_name}-%{version}-*debug.config
%endif

# enable GCOV kernel config options if gcov is on
%if %{with_gcov}
for i in *.config
do
  sed -i 's/# CONFIG_GCOV_KERNEL is not set/CONFIG_GCOV_KERNEL=y\nCONFIG_GCOV_PROFILE_ALL=y\n/' $i
done
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make %{?cross_opts} ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make %{?cross_opts} ARCH=$Arch oldnoconfig
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK='sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug -i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=%{src_pkg_name}-%{version}-xgene${Flavour:+-${Flavour}}.config
    # Config=%{src_pkg_name}-%{version}-xgene.config
    DevelDir=/usr/src/kernels/%{KVRA}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{KVRA}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # and now to start the build process

    make %{?cross_opts} -s mrproper

    cp %{SOURCE11} ./certs	# x509.genkey
    cp %{SOURCE12} ./certs	# extra_certificates
    cp %{SOURCE15} ./certs	# rheldup3.x509
    cp %{SOURCE16} ./certs	# rhelkpatch1.x509

    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

%ifarch s390x
    if [ "$Flavour" == "kdump" ]; then
        pushd arch/s390/boot
        gcc -static -o zfcpdump zfcpdump.c
        popd
    fi
%endif

    make -s %{?cross_opts} ARCH=$Arch oldnoconfig >/dev/null
    make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" $MakeTarget %{?sparse_mflags}

    if [ "$Flavour" != "kdump" ]; then
        make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} KCFLAGS="%{?kcflags}" WITH_GCOV="%{?with_gcov}" modules %{?sparse_mflags} || exit 1
    fi

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
# EFI SecureBoot signing, x86_64-only
%ifarch x86_64
    %pesign -s -i $KernelImage -o $KernelImage.signed -a certs/%{SOURCE13} -c certs/%{SOURCE14} -n %{pesign_name}
    mv $KernelImage.signed $KernelImage
%endif
    $CopyKernel $KernelImage $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/kernel
    if [ "$Flavour" != "kdump" ]; then
        # Override $(mod-fw) because we don't want it to install any firmware
        # we'll get it from the linux-firmware package and we don't want conflicts
        make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
%if %{with_gcov}
	# install gcov-needed files to $BUILDROOT/$BUILD/...:
	#   gcov_info->filename is absolute path
	#   gcno references to sources can use absolute paths (e.g. in out-of-tree builds)
	#   sysfs symlink targets (set up at compile time) use absolute paths to BUILD dir
	find . \( -name '*.gcno' -o -name '*.[chS]' \) -exec install -D '{}' "$RPM_BUILD_ROOT/$(pwd)/{}" \;
%endif
    fi
%ifarch %{vdso_arches}
    make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{bin_pkg_name}-$KernelVer.conf
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi

    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz

%if %{with_kabichk}
    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/$Arch || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc64 ppc64le
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # some arch/arm64 header files refer to arch/arm, so include them too
    cp -a --parents arch/arm/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # include/trace/events/wbt.h uses blk-{wbt,stat}.h private kernel headers,
    # and systemtap uses wbt.h when we run a script which uses wbt:* trace points
    cp block/blk-{wbt,stat}.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/block/

    # copy objtool for kernel-devel (needed for building external modules)
    if grep -q CONFIG_STACK_VALIDATION=y .config; then
      mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool
    fi

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
    collect_modules_list block 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm 'drm_open|drm_init'
    collect_modules_list modesetting 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    rm -f modinfo modnames

    # Save off the .tmp_versions/ directory.  We'll use it in the
    # __debug_install_post macro below to sign the right things
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp certs/signing_key.pem signing_key.pem.sign${Flavour:+.${Flavour}}
    cp certs/signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap softdep devname
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVRA}

%if %{with_default}
BuildKernel %make_target %kernel_image
%endif

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_kdump}
BuildKernel %make_target %kernel_image kdump
%endif

%global perf_make make %{?_smp_mflags} -C tools/perf -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 prefix=%{_prefix} lib=%{_lib}
%if %{with_perf}
# perf
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?cross_opts} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   make
   popd
   pushd tools/power/x86/turbostat
   make
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools
make tmon
popd
%endif

%if %{with_doc}
# Make the HTML and man pages.
make htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke 'make modules_sign' and the mod-extra-sign.sh
# commands to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Finally, pick a module at random and check that it's signed and fail the build
# if it isn't.

%define __modsign_install_post \
  if [ "%{with_debug}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-xgene-debug.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign.debug .tmp_versions \
    mv signing_key.pem.sign.debug signing_key.pem \
    mv signing_key.x509.sign.debug signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA}.debug || exit 1 \
  fi \
    if [ "%{with_default}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-xgene.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign .tmp_versions \
    mv signing_key.pem.sign signing_key.pem \
    mv signing_key.x509.sign signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA} || exit 1 \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list -n %{bin_pkg_name}-debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif

%endif

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVRA}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir/man/man9
make INSTALL_MAN_PATH=$man9dir installmandocs
ls $man9dir/man/man9 | grep -q '' || > $man9dir/man/man9/BROKEN
%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \( -name .install -o -name .check -o -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/
mkdir -p $INSTALL_KABI_PATH

# install kabi releases directories
tar xjvf %{SOURCE25} -C $INSTALL_KABI_PATH
%endif  # with_kernel_abi_whitelists

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install
# remove the 'trace' symlink.
rm -f $RPM_BUILD_ROOT/%{_bindir}/trace

# perf-python extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT try-install-man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
make INSTALL_ROOT=%{buildroot} install
popd
%endif

%endif

%if %{with_bootwrapper}
make %{?cross_opts} ARCH=%{hdrarch} DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif

%if %{with_doc}
# Red Hat UEFI Secure Boot CA cert, which can be used to authenticate the kernel
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}
install -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}/kernel-signing-ca.cer
%endif

###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n %{bin_pkg_name}-tools
/sbin/ldconfig

%postun -n %{bin_pkg_name}-tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post -n %{bin_pkg_name}-%{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVRA}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.%{?dist}.*/$f $f\
     done)\
fi\
%{nil}


# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans -n %{bin_pkg_name}%{?1:-%{1}}}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVRA}%{?-v:.%{-v*}} || exit $?\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?1:-%{1}} --rpmposttrans %{KVRA}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post -n %{bin_pkg_name}%{?-v:-%{-v*}}}\
%{-r:\
if [ `uname -i` == "x86_64" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
%{_sbindir}/new-kernel-pkg --package %{bin_pkg_name}%{?-v:-%{-v*}} --install %{KVRA}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun -n %{bin_pkg_name}%{?1:-%{1}}}\
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVRA}%{?1:.%{1}} || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVRA}%{?1:.%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post 

%kernel_variant_preun debug
%kernel_variant_post -v debug

%ifarch s390x
%postun -n %{bin_pkg_name}-kdump
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVRA}.kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*.kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi

%post -n %{bin_pkg_name}-kdump
    ln -sf /boot/vmlinuz-%{KVRA}.kdump /boot/zfcpdump
%endif # s390x

###
### file lists
###

%if %{with_headers}
%files -n %{bin_pkg_name}-headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files -n %{bin_pkg_name}-bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files -n %{bin_pkg_name}-doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}/kernel-signing-ca.cer
%dir %{_datadir}/doc/kernel-keys/%{rpmversion}-%{pkgrelease}
%dir %{_datadir}/doc/kernel-keys
%endif

%if %{with_kernel_abi_whitelists}
%files -n %{bin_pkg_name}-abi-whitelists
%defattr(-,root,root,-)
/lib/modules/kabi-*
%endif

%if %{with_perf}
%files -n perf%{?bin_suffix:-%{bin_suffix}}
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_libdir}/traceevent
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%{_datadir}/perf-core/strace/groups
%{_datadir}/doc/perf-tip/tips.txt

%files -n python-perf%{?bin_suffix:-%{bin_suffix}}
%defattr(-,root,root)
%{python_sitearch}

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
%defattr(-,root,root)

%files -f python-perf-debuginfo.list -n python-perf%{?bin_suffix:-%{bin_suffix}}-debuginfo
%defattr(-,root,root)
%endif
%endif

%if %{with_tools}
%files -n %{bin_pkg_name}-tools -f cpupower.lang
%defattr(-,root,root)
%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%endif
%{_bindir}/tmon
%if %{with_debuginfo}
%files -f tools-debuginfo.list -n %{bin_pkg_name}-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n %{bin_pkg_name}-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n %{bin_pkg_name}-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif

%endif # with_tools

%if %{with_gcov}
%ifarch x86_64 s390x ppc64 ppc64le
%files -n %{bin_pkg_name}-gcov
%defattr(-,root,root)
%{_builddir}
%endif
%endif

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files -n %{bin_pkg_name}%{?2:-%{2}}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVRA}%{?2:.%{2}}\
/%{image_install_path}/.vmlinuz-%{KVRA}%{?2:.%{2}}.hmac \
%attr(600,root,root) /boot/System.map-%{KVRA}%{?2:.%{2}}\
/boot/symvers-%{KVRA}%{?2:.%{2}}.gz\
/boot/config-%{KVRA}%{?2:.%{2}}\
%dir /lib/modules/%{KVRA}%{?2:.%{2}}\
/lib/modules/%{KVRA}%{?2:.%{2}}/kernel\
/lib/modules/%{KVRA}%{?2:.%{2}}/build\
/lib/modules/%{KVRA}%{?2:.%{2}}/source\
/lib/modules/%{KVRA}%{?2:.%{2}}/extra\
/lib/modules/%{KVRA}%{?2:.%{2}}/updates\
/lib/modules/%{KVRA}%{?2:.%{2}}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVRA}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/%{bin_pkg_name}-%{KVRA}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVRA}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVRA}%{?2:.%{2}}.img\
%{expand:%%files -n %{bin_pkg_name}-%{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVRA}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list -n %{bin_pkg_name}-%{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_default}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_kdump} kdump

%changelog
* Sun Sep 03 2017 Jim Perrin <jperrin@centos.org> [4.11.0-22.el7a]
- debranding of certs, add git framework

* Fri Aug 04 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-22.el7a]
- [fs] xfs: drop iolock from reclaim context to appease lockdep (Brian Foster) [1450297]
- [fs] xfs: handle array index overrun in xfs_dir2_leaf_readbuf() (Eric Sandeen) [1475852]
- [net] netfilter: nf_ct_helper: permit cthelpers with different names via nfnetlink (Matteo Croce) [1472057]
- [net] sit: use __GFP_NOWARN for user controlled allocation (Matteo Croce) [1472614]
- [crypto] authencesn: Fix digest_null crash (Herbert Xu) [1425049]
- [powerpc] perf: Add thread IMC PMU support (Jiri Olsa) [1379294]
- [powerpc] perf: Add core IMC PMU support (Jiri Olsa) [1379294]
- [powerpc] perf: Add nest IMC PMU support (Jiri Olsa) [1379294]
- [powerpc] powernv: Detect and create IMC device (Jiri Olsa) [1379294]
- [powerpc] powernv: Add IMC OPAL APIs (Jiri Olsa) [1379294]
- [iommu] arm-smmu, ACPI: Enable Cavium SMMU-v3 (Robert Richter) [1431610]
- [iommu] arm-smmu-v3: Add workaround for Cavium ThunderX2 erratum #126 (Robert Richter) [1431610]
- [iommu] arm-smmu-v3: Add workaround for Cavium ThunderX2 erratum #74 (Robert Richter) [1431610]
- [acpi] ACPI/IORT: Fixup SMMUv3 resource size for Cavium ThunderX2 SMMUv3 model (Robert Richter) [1431610]
- [acpi] iommu/arm-smmu-v3, acpi: Add temporary Cavium SMMU-V3 IORT model number definitions (Robert Richter) [1431610]
- [iommu] arm-smmu: Plumb in new ACPI identifiers (Robert Richter) [1431610]
- [i2c] xgene-slimpro: Add ACPI support by using PCC mailbox (Iyappan Subramanian) [1437693]
- [i2c] xgene-slimpro: Use a single function to send command message (Iyappan Subramanian) [1437693]
- [i2c] xgene: Set ACPI_COMPANION_I2C (Iyappan Subramanian) [1437693]
- [i2c] mailbox: pcc: Fix crash when request PCC channel 0 (Iyappan Subramanian) [1474962]

* Thu Aug 03 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-21.el7a]
- [netdrv] tap: convert a mutex to a spinlock (Steve Best) [1477345]
- [net] rtnetlink: allocate more memory for dev_set_mac_address() (Stefano Brivio) [1477127]
- [irqchip] gic-v3: Fix out-of-bound access in gic_set_affinity (Auger Eric) [1477112]
- [irqchip] gic-v3-its: Don't assume GICv3 hardware supports 16bit INTID (Auger Eric) [1477112]
- [irqchip] gic-v3-its: Fix MSI alias accounting (Auger Eric) [1477112]
- [block] disable runtime-pm for blk-mq (Ming Lei) [1476998]
- [tools] power turbostat: decode MSR_IA32_MISC_ENABLE only on Intel (Jiri Olsa) [1456386]
- [mm] hmm: various fixes for powerpc and HMM (Jerome Glisse) [1459703]
- [powerpc] mm: Wire up hpte_removebolted for powernv (Jerome Glisse) [1459703]
- [scsi] qla2xxx: Deprecate unsupported ISP (Himanshu Madhani) [1452822]

* Wed Aug 02 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-20.el7a]
- [net] netfilter: nf_ct_dccp/sctp: fix memory leak after netns cleanup (Davide Caratti) [1472535]
- [net] netfilter: udplite: Remove duplicated udplite4/6 declaration (Davide Caratti) [1472535]
- [net] ipv4: fib: Fix NULL pointer deref during fib_sync_down_dev() (Stefano Brivio) [1476681]
- [redhat] configs: Disable CONFIG_IP_DCCP (Stefano Brivio) [1432597]
- [redhat] configs: enable CONFIG_NET_ACT_TUNNEL_KEY (Davide Caratti) [1470564]
- [net] account for current skb length when deciding about UFO (Sabrina Dubroca) [1476185]
- [net] ping: do not abuse udp_poll() (Sabrina Dubroca) [1476185]
- [net] sched: Fix one possible panic when no destroy callback (Stefano Brivio) [1475862]
- [net] fix compile error in skb_orphan_partial() (Stefano Brivio) [1475856]
- [net] netem: fix skb_orphan_partial() (Stefano Brivio) [1475856]
- [net] netfilter: nft_set_rbtree: handle element re-addition after deletion (Stefano Brivio) [1475849]
- [net] netfilter: synproxy: fix conntrackd interaction (Stefano Brivio) [1475849]
- [wireless] mac80211: don't send SMPS action frame in AP mode when not needed (Stefano Brivio) [1475840]
- [wireless] mac80211: don't look at the PM bit of BAR frames (Stefano Brivio) [1475840]
- [wireless] mac80211: free netdev on dev_alloc_name() error (Stefano Brivio) [1475840]
- [wireless] mac80211: fix dropped counter in multiqueue RX (Stefano Brivio) [1475840]
- [wireless] mac80211: strictly check mesh address extension mode (Stefano Brivio) [1475840]
- [wireless] mac80211: fix IBSS presp allocation size (Stefano Brivio) [1475840]
- [netdrv] brcmfmac: fix double free upon register_netdevice() failure (Stefano Brivio) [1475527]
- [net] 8021q: Fix one possible panic caused by BUG_ON in free_netdev (Stefano Brivio) [1475527]
- [s390] net: s390: fix up for "Fix inconsistent teardown and release of private netdev state" (Stefano Brivio) [1475527]
- [net] Fix inconsistent teardown and release of private netdev state (Stefano Brivio) [1475527]
- [net] Fix an intermittent pr_emerg warning about lo becoming free (Stefano Brivio) [1475414]
- [net] net/packet: fix missing net_device reference release (Stefano Brivio) [1475414]
- [net] bpf: add bpf_clone_redirect to bpf_helper_changes_pkt_data (Stefano Brivio) [1475385]
- [net] Bluetooth: Fix user channel for 32bit userspace on 64bit kernel (Stefano Brivio) [1475376]
- [net] af_unix: Add sockaddr length checks before accessing sa_family in bind and connect handlers (Stefano Brivio) [1475324]
- [net] sock: reset sk_err when the error queue is empty (Sabrina Dubroca) [1475709]
- [net] rtnetlink: NUL-terminate IFLA_PHYS_PORT_NAME string (Sabrina Dubroca) [1475709]
- [net] rtnetlink: add IFLA_GROUP to ifla_policy (Sabrina Dubroca) [1475709]
- [net] Zero ifla_vf_info in rtnl_fill_vfinfo() (Sabrina Dubroca) [1475709]
- [net] Improve handling of failures on link and route dumps (Sabrina Dubroca) [1475709]
- [net] handle NAPI_GRO_FREE_STOLEN_HEAD case also in napi_frags_finish() (Sabrina Dubroca) [1475709]
- [net] don't call strlen on non-terminated string in dev_set_alias() (Sabrina Dubroca) [1475709]
- [net] core: Fix slab-out-of-bounds in netdev_stats_to_stats64 (Sabrina Dubroca) [1475709]
- [net] iov_iter: don't revert iov buffer if csum error (Sabrina Dubroca) [1475709]
- [net] ppp: Fix false xmit recursion detect with two ppp devices (Matteo Croce) [1473902]
- [net] ip6_tunnel: Correct tos value in collect_md mode (Hangbin Liu) [1474767]
- [net] ipv6: fix calling in6_ifa_hold incorrectly for dad work (Hangbin Liu) [1474767]
- [net] ipv6: Compare lwstate in detecting duplicate nexthops (Hangbin Liu) [1474767]
- [net] ipv6: Do not leak throw route references (Hangbin Liu) [1474767]
- [net] ipv6: Release route when device is unregistering (Hangbin Liu) [1474767]
- [net] ipv6: Fix CALIPSO causing GPF with datagram support (Hangbin Liu) [1474767]
- [net] ip6_tunnel: fix traffic class routing for tunnels (Hangbin Liu) [1474767]
- [net] ip6_tunnel, ip6_gre: fix setting of DSCP on encapsulated packets (Hangbin Liu) [1474767]
- [net] ipv4, ipv6: ensure raw socket message is big enough to hold an IP header (Hangbin Liu) [1474767]
- [net] ipv6: Do not duplicate DAD on link up (Hangbin Liu) [1474767]
- [scsi] hisi_sas: optimise DMA slot memory (Jun Ma) [1474164]
- [scsi] hisi_sas: create hisi_sas_get_fw_info() (Jun Ma) [1474164]
- [scsi] hisi_sas: add pci_dev in hisi_hba struct (Jun Ma) [1474164]
- [scsi] hisi_sas: relocate get_ncq_tag_v2_hw() (Jun Ma) [1474164]
- [scsi] hisi_sas: relocate sata_done_v2_hw() (Jun Ma) [1474164]
- [scsi] hisi_sas: relocate get_ata_protocol() (Jun Ma) [1474164]
- [scsi] hisi_sas: optimise the usage of hisi_hba.lock (Jun Ma) [1474164]
- [scsi] hisi_sas: define hisi_sas_device.device_id as int (Jun Ma) [1474164]
- [scsi] hisi_sas: fix timeout check in hisi_sas_internal_task_abort() (Jun Ma) [1474164]

* Tue Aug 01 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-19.el7a]
- [powerpc] pseries: Fix of_node_put() underflow during reconfig remove (Laurent Vivier) [1471745]
- [powerpc] mm: Fix pmd/pte_devmap() on non-leaf entries (David Gibson) [1475118]
- [powerpc] powernv: Enable PCI peer-to-peer (Steve Best) [1437849]
- [scsi] ses: do not add a device to an enclosure if enclosure_add_links() fails (Maurizio Lombardi) [1427426]
- [net] bridge: mdb: fix leak on complete_info ptr on fail path (Stefano Brivio) [1475402]
- [net] bridge: fix a null pointer dereference in br_afspec (Stefano Brivio) [1475402]
- [net] bridge: netlink: check vlan_default_pvid range (Stefano Brivio) [1475402]
- [redhat] spec: don't ship build-id links installed by vdso_install target ("Herton R. Krzesinski") [1464263]
- [redhat] configs: disable CHACHA20POLY1305 on ppc64le and SHA3 on ppc64le/arm64 ("Herton R. Krzesinski") [1475646]
- [net] sctp: fix an array overflow when all ext chunks are set (Xin Long) [1474759]
- [net] sctp: ensure ep is not destroyed before doing the dump (Xin Long) [1474759]
- [net] sctp: return next obj by passing pos + 1 into sctp_transport_get_idx (Xin Long) [1474759]
- [net] sctp: disable BH in sctp_for_each_endpoint (Xin Long) [1474759]
- [net] sctp: set new_asoc temp when processing dupcookie (Xin Long) [1474759]
- [net] sctp: fix stream update when processing dupcookie (Xin Long) [1474759]
- [net] sctp: fix ICMP processing if skb is non-linear (Xin Long) [1474759]
- [net] sctp: fix src address selection if using secondary addresses for ipv6 (Xin Long) [1474759]
- [net] ipvs: explicitly forbid ipv6 service/dest creation if ipv6 mod is disabled (Matteo Croce) [1470957]

* Mon Jul 31 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-18.el7a]
- [powerpc] KVM: PPC: Book3S HV: Enable TM before accessing TM registers (David Gibson) [1456910]
- [powerpc] KVM: PPC: Book3S HV: Save/restore host values of debug registers (David Gibson) [1456910]
- [powerpc] KVM: PPC: Book3S HV: Preserve userspace HTM state properly (David Gibson) [1456910]
- [powerpc] KVM: PPC: Book3S HV: Restore critical SPRs to host values on guest exit (David Gibson) [1456910]
- [powerpc] KVM: PPC: Book3S HV: Context-switch EBB registers properly (David Gibson) [1456910]
- [netdrv] virtio-net: fix module unloading (Andrew Jones) [1472694]
- [net] xfrm6: Fix IPv6 payload_len in xfrm6_transport_finish (Hangbin Liu) [1474815]
- [net] xfrm: NULL dereference on allocation failure (Hangbin Liu) [1474815]
- [net] xfrm: Oops on error in pfkey_msg2xfrm_state() (Hangbin Liu) [1474815]
- [net] xfrm: fix stack access out of bounds with CONFIG_XFRM_SUB_POLICY (Hangbin Liu) [1474815]
- [net] tcp: reset sk_rx_dst in tcp_disconnect() (Florian Westphal) [1474881]
- [net] tcp: fix wraparound issue in tcp_lp (Florian Westphal) [1474881]
- [net] tcp: fix access to sk->sk_state in tcp_poll() (Florian Westphal) [1474881]
- [net] tcp: avoid fragmenting peculiar skbs in SACK (Florian Westphal) [1474881]
- [net] tcp: eliminate negative reordering in tcp_clean_rtx_queue (Florian Westphal) [1474881]
- [net] tcp: avoid fastopen API to be used on AF_UNSPEC (Florian Westphal) [1474881]
- [net] ipv4: add reference counting to metrics (Florian Westphal) [1474881]
- [net] tcp: disallow cwnd undo when switching congestion control (Florian Westphal) [1474881]
- [net] igmp: acquire pmc lock for ip_mc_clear_src() (Florian Westphal) [1474881]
- [net] igmp: add a missing spin_lock_init() (Florian Westphal) [1474881]
- [powerpc] hotplug-mem: Fix missing endian conversion of aa_index (Laurent Vivier) [1473203]
- [netdrv] net/mlx5e: Fix TX carrier errors report in get stats ndo (Slava Shwartsman) [1473362]
- [mmc] core: Use device_property_read instead of of_property_read (Slava Shwartsman) [1466917]
- [mmc] dw_mmc: Use device_property_read instead of of_property_read (Slava Shwartsman) [1466917]
- [base] device property: Make dev_fwnode() public (Slava Shwartsman) [1466917]

* Fri Jul 28 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-17.el7a]
- [char] ipmi:ssif: Add missing unlock in error branch (Tony Camuso) [1473422]
- [char] ipmi: constify bmc_dev_attr_group and bmc_device_type (Tony Camuso) [1473422]
- [char] ipmi:ssif: Check dev before setting drvdata (Tony Camuso) [1473422]
- [char] ipmi: get rid of field-by-field __get_user() (Tony Camuso) [1473422]
- [char] ipmi: get COMPAT_IPMICTL_RECEIVE_MSG in sync with the native one (Tony Camuso) [1473422]
- [char] ipmi: Convert DMI handling over to a platform device (Tony Camuso) [1473422]
- [char] ipmi: Create a platform device for a DMI-specified IPMI interface (Tony Camuso) [1473422]
- [char] ipmi: use rcu lock around call to intf->handlers->sender() (Tony Camuso) [1473422]
- [char] ipmi:ssif: Use i2c_adapter_id instead of adapter->nr (Tony Camuso) [1473422]
- [char] ipmi: Use the proper default value for register size in ACPI (Tony Camuso) [1473422]
- [char] ipmi_ssif: remove redundant null check on array client->adapter->name (Tony Camuso) [1473422]
- [char] ipmi/watchdog: fix watchdog timeout set on reboot (Tony Camuso) [1473422]
- [char] ipmi_ssif: unlock on allocation failure (Tony Camuso) [1473422]
- [char] ipmi/watchdog: fix wdog hang on panic waiting for ipmi response (Tony Camuso) [1473422]
- [char] Annotate hardware config module parameters in drivers/char/ipmi/ (Tony Camuso) [1473422]
- [kernel] Annotate module params that specify hardware parameters (eg. ioport) (Tony Camuso) [1473422]
- [char] ipmi: bt-bmc: Add ast2500 compatible string (Tony Camuso) [1473422]
- [char] ipmi_ssif: use setup_timer (Tony Camuso) [1473422]
- [char] ipmi: Fix kernel panic at ipmi_ssif_thread() (Tony Camuso) [1473422]
- [powerpc] KVM: PPC: Book3S HV: Don't sleep if XIVE interrupt pending on POWER9 (Mauricio Oliveira) [1474963]
- [powerpc] KVM: PPC: Book3S HV: Don't let VCPU sleep if it has a doorbell pending (Mauricio Oliveira) [1474963]
- [mm] mmap: expand_downwards: don't require the gap if !vm_prev (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [mm] fix overflow check in expand_upwards() (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [mm] mmap: do not blow on PROT_NONE MAP_FIXED holes in the stack (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [mm] fs/proc/task_mmu.c: remove obsolete comment in show_map_vma() (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [mm] fix new crash in unmapped_area_topdown() (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [mm] Allow stack to grow up to address space limit (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [mm] larger stack guard gap, between vmas (Rafael Aquini) [1461915] {CVE-2017-1000364}
- [net] netfilter: ipt_CLUSTERIP: fix use-after-free of proc entry (Stefano Brivio) [1472835]
- [redhat] configs: enable CHECKPOINT_RESTORE on aarch64 (Adrian Reber) [1464595]
- [net] ipv6: avoid unregistering inet6_dev for loopback (Hangbin Liu) [1470935]
- [net] ipv6: only call ip6_route_dev_notify() once for NETDEV_UNREGISTER (Hangbin Liu) [1470935]
- [net] ipv6: reorder ip6_route_dev_notifier after ipv6_dev_notf (Hangbin Liu) [1470935]
- [net] ipv6: initialize route null entry in addrconf_init() (Hangbin Liu) [1470935]
- [netdrv] net/mlx5e: Initialize CEE's getpermhwaddr address buffer to 0xff (Slava Shwartsman) [1472946]
- [powerpc] powernv/npu-dma: Add explicit flush when sending an ATSD (Mauricio Oliveira) [1464978]
- [powerpc] Only do ERAT invalidate on radix context switch on P9 DD1 (Mauricio Oliveira) [1471172]
- [powerpc] Fix /proc/cpuinfo revision for POWER9 DD2 (Mauricio Oliveira) [1465951]
- [powerpc] 64s: Invalidate ERAT on powersave wakeup for POWER9 (Mauricio Oliveira) [1465875]
- [powerpc] 64s/idle: Branch to handler with virtual mode offset (Mauricio Oliveira) [1465875]
- [powerpc] xive: Fix offset for store EOI MMIOs (Mauricio Oliveira) [1471163]
- [fs] userfaultfd: shmem: handle coredumping in handle_userfault() (Andrea Arcangeli) [1466806]

* Mon Jul 24 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-16.el7a]
- [net] netfilter: xt_socket: Fix broken IPv6 handling (Hangbin Liu) [1471001]
- [scsi] csiostor: update module version (Sai Vemuri) [1458005]
- [scsi] csiostor: add check for supported fw version (Sai Vemuri) [1458005]
- [scsi] csiostor: Avoid content leaks and casts (Sai Vemuri) [1458005]
- [scsi] csiostor: add support for Chelsio T6 adapters (Sai Vemuri) [1458005]
- [scsi] csiostor: fix use after free in csio_hw_use_fwconfig() (Sai Vemuri) [1458005]
- [scsi] csiostor: switch to pci_alloc_irq_vectors (Sai Vemuri) [1458005]
- [net] netfilter: ipt_CLUSTERIP: do not hold dev (Xin Long) [1449013]
- [tools] perf vendor events: Add POWER9 PVRs to mapfile (Jiri Olsa) [1416317]
- [tools] perf vendor events: Add POWER9 PMU events (Jiri Olsa) [1416317]
- [net] netfilter: xtables: fix build failure from COMPAT_XT_ALIGN outside CONFIG_COMPAT (Florian Westphal) [1470745]
- [net] netfilter: xtables: zero padding in data_to_user (Florian Westphal) [1470745]
- [block] Fix __blkdev_issue_zeroout loop (Ming Lei) [1470923]
- [block] blk-mq-sched: fix performance regression of mq-deadline (Ming Lei) [1470923]
- [block] provide bio_uninit() free freeing integrity/task associations (Ming Lei) [1470923]
- [block] blk-mq: fix performance regression with shared tags (Ming Lei) [1470923]
- [block] Fix a blk_exit_rl() regression (Ming Lei) [1470923]
- [block] Avoid that blk_exit_rl() triggers a use-after-free (Ming Lei) [1470923]
- [block] cfq-iosched: fix the delay of cfq_group's vdisktime under iops mode (Ming Lei) [1470923]
- [block] blk-mq: Take tagset lock when updating hw queues (Ming Lei) [1470923]
- [block] partitions/msdos: FreeBSD UFS2 file systems are not recognized (Ming Lei) [1470923]
- [block] blk-mq: NVMe 512B/4K+T10 DIF/DIX format returns I/O error on dd with split op (Ming Lei) [1470923]
- [block] mq: fix potential deadlock during cpu hotplug (Ming Lei) [1470923]
- [block] mq: Cure cpu hotplug lock inversion (Ming Lei) [1470923]
- [block] cfq: Disable writeback throttling by default (Ming Lei) [1470923]
- [block] fix inheriting request priority from bio (Ming Lei) [1470923]
- [block] blkcg: allocate struct blkcg_gq outside request queue spinlock (Ming Lei) [1470923]
- [block] block new I/O just after queue is set as dying (Ming Lei) [1470923]
- [block] rename blk_mq_freeze_queue_start() (Ming Lei) [1470923]
- [block] add a read barrier in blk_queue_enter() (Ming Lei) [1470923]
- [block] blk-mq: comment on races related with timeout handler (Ming Lei) [1470923]
- [block] Fix oops scsi_disk_get() (Ming Lei) [1470923]
- [lib] kobject: Export kobject_get_unless_zero() (Ming Lei) [1470923]

* Mon Jul 24 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-15.el7a]
- [kernel] sched/deadline: Use the revised wakeup rule for suspending constrained dl tasks (Xunlei Pang) [1471599]
- [kernel] sched/deadline: Fix dl_bw comment (Xunlei Pang) [1471599]
- [kernel] sched/deadline: Zero out positive runtime after throttling constrained tasks (Xunlei Pang) [1471599]
- [virt] KVM: trigger uevents when creating or destroying a VM (BZ#1394223) (Paolo Bonzini) [1394223]
- [redhat] config: x86_64/powerpc64le: enable DEVICE_PUBLIC & DEVICE_PUBLIC (Jerome Glisse) [1459704]
- [mm] memcontrol: support MEMORY_DEVICE_PRIVATE and MEMORY_DEVICE_PUBLIC v3 (Jerome Glisse) [1459704]
- [mm] memcontrol: allow to uncharge page without using page->lru field (Jerome Glisse) [1459704]
- [mm] hmm: add new helper to hotplug CDM memory region v3 (Jerome Glisse) [1459704]
- [mm] device-public-memory: device memory cache coherent with CPU v4 (Jerome Glisse) [1459704]
- [mm] zone-device: rename DEVICE_PUBLIC to DEVICE_HOST (Jerome Glisse) [1459704]
- [mm] hmm: fix handling of pmd inside HMM CPU page table snapshot helper (Jerome Glisse) [1459704]
- [mm] hmm: update pegas HMM to lastest HMM v24 (Jerome Glisse) [1459704]
- [powerpc] hugetlbfs: Export HPAGE_SHIFT (Jerome Glisse) [1459703]
- [mm] huge_memory.c: deposit a pgtable for DAX PMD faults when required (Jerome Glisse) [1459703]
- [mm] huge_memory.c: use zap_deposited_table() more (Jerome Glisse) [1459703]
- [powerpc] mm: Enable ZONE_DEVICE on powerpc (Jerome Glisse) [1459703]
- [mm] x86: Add ARCH_HAS_ZONE_DEVICE to Kconfig (Jerome Glisse) [1459703]
- [powerpc] mm: Add devmap support for ppc64 (Jerome Glisse) [1459703]
- [powerpc] vmemmap: Add altmap support (Jerome Glisse) [1459703]
- [powerpc] vmemmap: Reshuffle vmemmap_free() (Jerome Glisse) [1459703]
- [redhat] configs: Enable CONFIG_MPROFILE_KERNEL for powerpc64le related fixes (Jiri Olsa) [1368733]
- [redhat] configs: Enable CONFIG_KPROBES_ON_FTRACE for powerpc64le (Jiri Olsa) [1368733]
- [redhat] configs: Enable function tracer for powerpc64le (Jiri Olsa) [1368733]
- [powerpc] ftrace: Move stack setup and teardown code into ftrace_graph_caller() (Jiri Olsa) [1368733]
- [powerpc] kprobes: Remove duplicate saving of MSR (Jiri Olsa) [1368733]
- [tools] perf powerpc: Choose local entry point with kretprobes (Jiri Olsa) [1368733]
- [tools] perf kretprobes: Offset from reloc_sym if kernel supports it (Jiri Olsa) [1368733]
- [tools] perf probe: Factor out the ftrace README scanning (Jiri Olsa) [1368733]
- [tools] perf probe: Generalize probe event file open routine (Jiri Olsa) [1368733]
- [powerpc] kprobes: Fix handling of instruction emulation on probe re-entry (Jiri Olsa) [1368733]
- [tools] perf sdt: Add scanning of sdt probes arguments (Jiri Olsa) [1368733]
- [powerpc] kprobes: Prefer ftrace when probing function entry (Jiri Olsa) [1368733]
- [powerpc] Introduce a new helper to obtain function entry points (Jiri Olsa) [1368733]
- [powerpc] kprobes: Add support for KPROBES_ON_FTRACE (Jiri Olsa) [1368733]
- [powerpc] ftrace: Restore LR from pt_regs (Jiri Olsa) [1368733]
- [powerpc] kprobes: Convert __kprobes to NOKPROBE_SYMBOL() (Jiri Olsa) [1368733]
- [powerpc] kprobes: Emulate instructions on kprobe handler re-entry (Jiri Olsa) [1368733]
- [powerpc] kprobes: Factor out code to emulate instruction into a helper (Jiri Olsa) [1368733]
- [powerpc] kretprobes: Override default function entry offset (Jiri Olsa) [1368733]
- [kernel] powerpc/kprobes: Fix handling of function offsets on ABIv2 (Jiri Olsa) [1368733]
- [kernel] kprobes: Convert kprobe_lookup_name() to a function (Jiri Olsa) [1368733]
- [kernel] kprobes: Skip preparing optprobe if the probe is ftrace-based (Jiri Olsa) [1368733]
- [tools] perf sdt powerpc: Add argument support (Jiri Olsa) [1368733]
- [tools] perf/sdt/x86: Move OP parser to tools/perf/arch/x86/ (Jiri Olsa) [1368733]
- [tools] perf/sdt/x86: Add renaming logic for (missing) 8 bit registers (Jiri Olsa) [1368733]
- [tools] perf sdt x86: Add renaming logic for rNN and other registers (Jiri Olsa) [1368733]
- [tools] perf probe: Add sdt probes arguments into the uprobe cmd string (Jiri Olsa) [1368733]
- [kernel] trace/kprobes: Fix check for kretprobe offset within function entry (Jiri Olsa) [1368733]
- [kernel] trace/kprobes: Add back warning about offset in return probes (Jiri Olsa) [1368733]
- [kernel] trace/kprobes: Allow return probes with offsets and absolute addresses (Jiri Olsa) [1368733]
- [kernel] kretprobes: Ensure probe location is at function entry (Jiri Olsa) [1368733]

* Sat Jul 22 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-14.el7a]
- [netdrv] cxgb4: Update register ranges of T4/T5/T6 adapters (Arjun Vynipadath) [1473388]
- [redhat] aarch64: configs: Enable X-Gene PMU (Iyappan Subramanian) [1469302]
- [perf] xgene: Add support for SoC PMU version 3 (Iyappan Subramanian) [1469302]
- [perf] xgene: Move PMU leaf functions into function pointer structure (Iyappan Subramanian) [1469302]
- [perf] xgene: Parse PMU subnode from the match table (Iyappan Subramanian) [1469302]
- [scsi] Add STARGET_CREATED_REMOVE state to scsi_target_state (Ewan Milne) [1472412]
- [kernel] sched/fair: Spare idle load balancing on nohz_full CPUs (Lauro Ramos Venancio) [1470850]
- [kernel] nohz: Move idle balancer registration to the idle path (Lauro Ramos Venancio) [1470850]
- [kernel] sched/loadavg: Generalize "_idle" naming to "_nohz" (Lauro Ramos Venancio) [1470850]
- [kernel] nohz: Fix spurious warning when hrtimer and clockevent get out of sync (Lauro Ramos Venancio) [1470850]
- [kernel] nohz: Fix buggy tick delay on IRQ storms (Lauro Ramos Venancio) [1470850]
- [kernel] nohz: Reset next_tick cache even when the timer has no regs (Lauro Ramos Venancio) [1470850]
- [kernel] nohz: Fix collision between tick and other hrtimers, again (Lauro Ramos Venancio) [1470850]
- [kernel] nohz: Add hrtimer sanity check (Lauro Ramos Venancio) [1470850]

* Thu Jul 20 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-13.el7a]
- [kernel] sched/core: Implement new approach to scale select_idle_cpu() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Rename sched_group_cpus() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Rename sched_group_mask() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Simplify sched_group_mask() usage (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Rewrite get_group() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Add a few comments (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Fix overlapping sched_group_capacity (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Add sched_group_capacity debugging (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Small cleanup (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Fix overlapping sched_group_mask (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Remove FORCE_SD_OVERLAP (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Move comment about asymmetric node setups (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Optimize build_group_mask() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Verify the first group matches the child domain (Lauro Ramos Venancio) [1470779]
- [kernel] sched/debug: Print the scheduler topology group mask (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Simplify build_overlap_sched_groups() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Fix building of overlapping sched-groups (Lauro Ramos Venancio) [1470779]
- [kernel] sched/fair, cpumask: Export for_each_cpu_wrap() (Lauro Ramos Venancio) [1470779]
- [kernel] sched/topology: Refactor function build_overlap_sched_groups() (Lauro Ramos Venancio) [1470779]
- [powerpc] powernv: Fix boot on Power8 bare metal due to opal_configure_cores() (Steve Best) [1472358]
- [powerpc] powernv: Tell OPAL about our MMU mode on POWER9 (Steve Best) [1471127]
- [net] xfrm: move xfrm_garbage_collect out of xfrm_policy_flush (Hangbin Liu) [1468116]
- [kernel] tracing: Rename update the enum_map file (Jeremy Linton) [1375669]
- [kernel] tracing: Add TRACE_DEFINE_SIZEOF macros (Jeremy Linton) [1375669]
- [kernel] tracing: define TRACE_DEFINE_SIZEOF macro to map sizeofs to their values (Jeremy Linton) [1375669]
- [kernel] tracing: Rename enum_replace to eval_replace (Jeremy Linton) [1375669]
- [kernel] trace: rename enum_map functions (Jeremy Linton) [1375669]
- [kernel] trace: rename trace.c enum functions (Jeremy Linton) [1375669]
- [kernel] trace: rename trace_enum_mutex to trace_eval_mutex (Jeremy Linton) [1375669]
- [kernel] trace: rename trace enum data structures in trace.c (Jeremy Linton) [1375669]
- [kernel] trace: rename struct module entry for trace enums (Jeremy Linton) [1375669]
- [kernel] trace: rename trace_enum_map to trace_eval_map (Jeremy Linton) [1375669]
- [kernel] trace: rename kernel enum section to eval (Jeremy Linton) [1375669]
- [arm64] arm_arch_timer: Fix read and iounmap of incorrect variable (Jun Ma) [1467188]

* Wed Jul 19 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-12.el7a]
- [redhat] rh-dist-git: fix update of dist-git sources file for linux tarball (again) ("Herton R. Krzesinski")
- [netdrv] vxlan: eliminate cached dst leak (Lance Richardson) [1471068]
- [arm64] fix downstream CPU capability naming scheme (Wei Huang) [1470937]
- [cpuidle] cpuidle-powernv: Allow Deep stop states that don't stop time (Steve Best) [1471075]
- [powerpc] powernv/idle: Use Requested Level for restoring state on P9 DD1 (Steve Best) [1471075]
- [powerpc] powernv/idle: Restore SPRs for deep idle states via stop API (Steve Best) [1471075]
- [powerpc] powernv/idle: Restore LPCR on wakeup from deep-stop (Steve Best) [1471075]
- [powerpc] powernv/idle: Decouple Timebase restore & Per-core SPRs restore (Steve Best) [1471075]
- [powerpc] powernv/idle: Correctly initialize core_idle_state_ptr (Steve Best) [1471075]
- [powerpc] powernv: Set NAPSTATELOST after recovering paca on P9 DD1 (Steve Best) [1471075]
- [powerpc] powernv: Fix CPU_HOTPLUG=n idle.c compile error (Steve Best) [1471075]
- [scsi] virtio_scsi: always read VPD pages for multiqueue too (Paolo Bonzini) [1466861]
- [scsi] virtio_scsi: let host do exception handling (Paolo Bonzini) [1466861]
- [scsi] virtio_scsi: Always try to read VPD pages (Paolo Bonzini) [1466861]
- [powerpc] mm/hugetlb: add support for 1G huge pages (Desnes Augusto Nunes do Rosario) [1467812]
- [powerpc] mm/hugetlb: Filter out hugepage size not supported by page table layout (Desnes Augusto Nunes do Rosario) [1467812]
- [mm] hugetlb: clean up ARCH_HAS_GIGANTIC_PAGE (Desnes Augusto Nunes do Rosario) [1467812]
- [powerpc] KVM: PPC: Book3S: Fix typo in XICS-on-XIVE state saving code (Laurent Vivier) [1469362]
- [scsi] qla2xxx: Fix NVMe entry_type for iocb packet on BE system (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: avoid unused-function warning (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: fix a bunch of typos and spelling mistakes (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Protect access to qpair members with qpair->qp_lock (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Update Driver version to 10.00.00.00-k (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Use FC-NVMe FC4 type for FDMI registration (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Send FC4 type NVMe to the management server (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add FC-NVMe F/W initialization and transport registration (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add FC-NVMe command handling (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add FC-NVMe port discovery and PRLI handling (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Update driver version to 9.01.00.00-k (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Include Exchange offload/Extended Login into FW dump (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Move target stat counters from vha to qpair (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Remove datasegs_per_cmd and datasegs_per_cont field (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Remove unused tgt_enable_64bit_addr flag (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add debug logging routine for qpair (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add function call to qpair for door bell (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: use shadow register for ISP27XX (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: move fields from qla_hw_data to qla_qpair (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add fw_started flags to qpair (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add debug knob for user control workload (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix mailbox failure while deleting Queue pairs (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Enable Target Multi Queue (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Preparation for Target MQ (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Combine Active command arrays (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: don't include generated/utsrelease.h (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix compile warning (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: remove redundant null check on tgt (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: remove writeq/readq function definitions (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Remove extra register read (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Remove unused irq_cmd_count field (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Accelerate SCSI BUSY status generation in target mode (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Remove redundant wait when target is stopped (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Add ql2xiniexchg parameter (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Turn on FW option for exchange check (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Cleanup debug message IDs (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix name server relogin (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Convert 32-bit LUN usage to 64-bit (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Use flag PFLG_DISCONNECTED (Himanshu Madhani) [1402999]
- [scsi] tcm_qla2xxx: Do not allow aborted cmd to advance (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix path recovery (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Retain loop test for fwdump length exceeding buffer length (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Replace usage of spin_lock with spin_lock_irqsave (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Allow ABTS, PURX, RIDA on ATIOQ for ISP83XX/27XX (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Remove an unused structure member (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix extraneous ref on sp's after adapter break (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix crash due to NULL pointer dereference of ctx (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix mailbox pointer error in fwdump capture (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Set bit 15 for DIAG_ECHO_TEST MBC (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Modify T262 FW dump template to specify same start/end to debug customer issues (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix crash due to mismatch mumber of Q-pair creation for Multi queue (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix NULL pointer access due to redundant fc_host_port_name call (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix recursive loop during target mode configuration for ISP25XX leaving system unresponsive (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: don't disable a not previously enabled PCI device (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: remove some redundant pointer assignments (Himanshu Madhani) [1402999]
- [scsi] qla2xxx: Fix typo in driver (Himanshu Madhani) [1402999]
- [block] blk-mq: map sequentially all HWQ to CPUs also in hyperthreaded systems (Desnes Augusto Nunes do Rosario) [1468262]
- [powerpc] Change message for IBM Power 8 unsupported (Steve Best) [1470052]
- [powerpc] 64s: Handle data breakpoints in Radix mode (Steve Best) [1469537]
- [powerpc] sysfs: Fix reference leak of cpu device_nodes present at boot (Steve Best) [1469256]
- [powerpc] pseries: Fix of_node_put() underflow during DLPAR remove (Steve Best) [1469256]
- [redhat] kconfig: Enable cxl library for power 9 (Steve Best) [1459621]
- [misc] cxl: Export library to support IBM XSL (Steve Best) [1459621]
- [misc] cxl: Fixes for Coherent Accelerator Interface Architecture 2.0 (Steve Best) [1459621]
- [misc] cxl: Fix error path on bad ioctl (Steve Best) [1459621]
- [misc] cxl: Avoid double free_irq() for psl, slice interrupts (Steve Best) [1459621]
- [misc] cxl: Mask slice error interrupts after first occurrence (Steve Best) [1459621]
- [misc] cxl: Route eeh events to all drivers in cxl_pci_error_detected() (Steve Best) [1459621]
- [misc] cxl: Force context lock during EEH flow (Steve Best) [1459621]
- [ppc64] powerpc/64s: Support new device tree binding for discovering CPU features (Steve Best) [1459621]
- [s390] dasd: suppress command reject error for query host access command (Hendrik Brueckner) [1455250]
- [s390] dasd: check if query host access feature is supported (Hendrik Brueckner) [1455250]

* Mon Jul 17 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-11.el7a]
- [arm64] PCI: Set root bus NUMA node on ACPI systems (Robert Richter) [1451736]
- [powerpc] npu-dma: Remove spurious WARN_ON when a PCI device has no of_node (Steve Best) [1468079]
- [nvme] nvmet-rdma: occasionally flush ongoing controller teardown (Slava Shwartsman) [1428832]
- [fs] disable unsupported new disk formats (Eric Sandeen) [1426688]
- [redhat] Ignore localversion and configs directory (Don Zickus)
- [powerpc] perf: Fix Power9 test_adder fields (Desnes Augusto Nunes do Rosario) [1456346]
- [redhat] configs: remove old and unneeded drivers from kernel (Jonathan Toppins) [1445880]
- [scsi] Fix driver unload/reload operation (Maurizio Lombardi) [1448109]
- [arm64] kvm: vgic: use SYS_DESC() (Auger Eric) [1450127]
- [arm64] kvm: sysreg: fix typo'd SYS_ICC_IGRPEN*_EL1 (Auger Eric) [1450127]
- [virt] KVM: arm64: Log an error if trapping a write-to-read-only GICv3 access (Auger Eric) [1450127]
- [virt] KVM: arm64: Log an error if trapping a read-from-write-only GICv3 access (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Log which GICv3 system registers are trapped (Auger Eric) [1450127]
- [virt] KVM: arm64: Enable GICv3 common sysreg trapping via command-line (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_PMR_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_CTLR_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_RPR_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_DIR_EL1 handler (Auger Eric) [1450127]
- [arm64] Add workaround for Cavium Thunder erratum 30115 (Auger Eric) [1450127]
- [arm64] Add MIDR values for Cavium cn83XX SoCs (Auger Eric) [1450127]
- [virt] KVM: arm64: Enable GICv3 Group-0 sysreg trapping via command-line (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Enable trapping of Group-0 system registers (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add misc Group-0 handlers (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_IGNREN0_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_BPR0_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: Enable GICv3 Group-1 sysreg trapping via command-line (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Enable trapping of Group-1 system registers (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_HPPIR1_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_AP1Rn_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_EOIR1_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_IAR1_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_IGRPEN1_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add ICV_BPR1_EL1 handler (Auger Eric) [1450127]
- [virt] KVM: arm64: vgic-v3: Add hook to handle guest GICv3 sysreg accesses at EL2 (Auger Eric) [1450127]
- [virt] KVM: arm64: Make kvm_condition_valid32() accessible from EL2 (Auger Eric) [1450127]
- [virt] KVM: arm/arm64: vgic-v3: Add accessors for the ICH_APxRn_EL2 registers (Auger Eric) [1450127]
- [arm64] Add a facility to turn an ESR syndrome into a sysreg encoding (Auger Eric) [1450127]
- [arm64] Add CNTFRQ_EL0 trap handler (Auger Eric) [1450127]
- [redhat] Makefile.cross: cleaned up inconsistent use of s390/s390x (Al Stone) [1460827]
- [redhat] makefile: avoid unconditional execution of brew command (Al Stone) [1460827]
- [redhat] Fix some cross-compilation issues (Al Stone) [1460827]
- [powerpc] powerpc/powernv/pci: Add support for PHB4 diagnostics (Steve Best) [1467959]
- [powerpc] powerpc/powernv/pci: Dynamically allocate PHB diag data (Steve Best) [1467959]
- [powerpc] powerpc/powernv/pci: Reduce spam when dumping PEST (Steve Best) [1467959]
- [arm64] kernel: restrict /dev/mem read() calls to linear region (Robert Richter) [1460329]
- [scsi] aacraid: Update driver version to 50834 (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Remove reference to Series-9 (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Add reset debugging statements (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Enable ctrl reset for both hba and arc (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Make sure ioctl returns on controller reset (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Use correct function to get ctrl health (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Rework aac_src_restart (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Rework SOFT reset code (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Add periodic checks to see IOP reset status (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Rework IOP reset (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Using single reset mask for IOP reset (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Print ctrl status before eh reset (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Log count info of scsi cmds before reset (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Change wait time for fib completion (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Remove reset support from check_health (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Set correct Queue Depth for HBA1000 RAW disks (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Added 32 and 64 queue depth for arc natives (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Fix DMAR issues with iommu=pt (Raghava Aditya Renukunta) [1368685]
- [scsi] aacraid: Remove __GFP_DMA for raw srb memory (Raghava Aditya Renukunta) [1368685]
- [scsi] scsi: aacraid: pci_alloc_consistent failures on ARM64 (Raghava Aditya Renukunta) [1368685]
- [mm] hwpoison, memcg: forcibly uncharge LRU pages (Desnes Augusto Nunes do Rosario) [1465114]
- [mm] skip HWPoisoned pages when onlining pages (Desnes Augusto Nunes do Rosario) [1465114]
- [virtio] virtio-net: serialize tx routine during reset (Andrew Jones) [1467071]
- [virtio] virtio_balloon: disable VIOMMU support (Andrew Jones) [1467071]
- [virtio] fix spelling of virtblk_scsi_request_done (Andrew Jones) [1467071]
- [virt] drm/virtio: don't leak bo on drm_gem_object_init failure (Andrew Jones) [1467071]
- [virt] drm/virtio: call drm_plane_cleanup() at destroy phase (Andrew Jones) [1467071]
- [net] sctp: do not inherit ipv6_mc_list, ipv6_ac_list, ipv6_fl_list from parent (Florian Westphal) [1455614] {CVE-2017-8890 CVE-2017-9075 CVE-2017-9076 CVE-2017-9077}
- [net] ipv6/dccp: do not inherit ipv6_mc_list from parent (Florian Westphal) [1455614] {CVE-2017-8890 CVE-2017-9075 CVE-2017-9076 CVE-2017-9077}
- [net] dccp/tcp: do not inherit mc_list from parent (Florian Westphal) [1455614] {CVE-2017-8890 CVE-2017-9075 CVE-2017-9076 CVE-2017-9077}
- [net] tcp: do not inherit fastopen_req from parent (Florian Westphal) [1455614] {CVE-2017-8890 CVE-2017-9075 CVE-2017-9076 CVE-2017-9077}
- [redhat] qedr: Enable module by default (Harish Patil) [1444511]
- [infiniband] rdma/qedr: Add 64KB PAGE_SIZE support to user-space queues (Harish Patil) [1444511]
- [infiniband] ib: Replace ib_umem page_size by page_shift (Harish Patil) [1444511]
- [infiniband] rdma/qedr: Initialize byte_len in WC of READ and SEND commands (Harish Patil) [1444511]
- [infiniband] qed: Correct doorbell configuration for !4Kb pages (Harish Patil) [1444511]

* Wed Jun 21 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-10.el7a]
- [redhat] change DIST tag to el7a ("Herton R. Krzesinski")
- [mm] ksm: optimize refile of stable_node_dup at the head of the chain (Andrea Arcangeli) [1395384]
- [mm] ksm: swap the two output parameters of chain/chain_prune (Andrea Arcangeli) [1395384]
- [mm] ksm: cleanup stable_node chain collapse case (Andrea Arcangeli) [1395384]
- [mm] ksm: prevent crash after write_protect_page fails (Andrea Arcangeli) [1395384]
- [mm] ksm: fix use after free with merge_across_nodes = 0 (Andrea Arcangeli) [1395384]
- [mm] ksm: validate STABLE_NODE_DUP_HEAD conditional to gcc version (Andrea Arcangeli) [1395384]
- [mm] ksm: add reschedule points to unmerge_and_remove_all_rmap_items (Andrea Arcangeli) [1395384]
- [mm] ksm: introduce ksm_max_page_sharing per page deduplication limit (Andrea Arcangeli) [1395384]
- [vfio] type1: Reduce repetitive calls in vfio_pin_pages_remote() (Auger Eric) [1462706]
- [vfio] type1: Prune vfio_pin_page_external() (Auger Eric) [1462706]
- [vfio] type1: Remove locked page accounting workqueue (Auger Eric) [1462706]
- [powerpc] powernv/npu-dma.c: Fix opal_npu_destroy_context() call (Gustavo Duarte) [1452875]
- [mm] vmstat: Remove spurious WARN() during zoneinfo print (Gustavo Duarte) [1452875]
- [powerpc] powernv: Fix TCE kill on NVLink2 (Gustavo Duarte) [1320912]
- [powerpc] powernv: Require MMU_NOTIFIER to fix NPU build (Gustavo Duarte) [1320912]
- [powerpc] powernv: Introduce address translation services for Nvlink2 (Gustavo Duarte) [1320912]
- [powerpc] powernv: Add sanity checks to pnv_pci_get_gpu_dev/pnv_pci_get_npu_dev (Gustavo Duarte) [1320912]
- [of] drivers/of/base.c: Add of_property_read_u64_index (Gustavo Duarte) [1320912]

* Fri Jun 16 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-9.el7]
- [redhat] config: aarch64: re-enable /dev/mem for debug kernels (Al Stone) [1456956]
- [powerpc] powernv/idle: Don't override default/deepest directly in kernel (Desnes Augusto Nunes do Rosario) [1448166]
- [powerpc] powernv/smp: Add busy-wait loop as fall back for CPU-Hotplug (Desnes Augusto Nunes do Rosario) [1448166]
- [powerpc] powernv: Move CPU-Offline idle state invocation from smp.c to idle.c (Desnes Augusto Nunes do Rosario) [1448166]
- [powerpc] KVM: PPC: Book3S HV: Ignore timebase offset on POWER9 DD1 (David Gibson) [1451884]
- [kernel] sched: disable autogroups by default (Lauro Ramos Venancio) [1458378]
- [net] bridge: start hello timer only if device is up (Xin Long) [1422334]
- [net] bridge: fix hello and hold timers starting/stopping (Xin Long) [1422334]
- [net] bridge: start hello_timer when enabling KERNEL_STP in br_stp_start (Xin Long) [1422334]
- [arm64] KVM: Allow unaligned accesses at EL2 (Wei Huang) [1459864]
- [arm64] KVM: Preserve RES1 bits in SCTLR_EL2 (Wei Huang) [1459864]
- [virt] KVM: arm/arm64: Handle possible NULL stage2 pud when ageing pages (Wei Huang) [1459864]
- [virt] KVM: arm/arm64: vgic-v3: Fix nr_pre_bits bitfield extraction (Wei Huang) [1459864]
- [virt] KVM: arm/arm64: Fix isues with GICv2 on GICv3 migration (Wei Huang) [1459864]
- [virt] kvm: arm/arm64: Fix use after free of stage2 page table (Wei Huang) [1459864]
- [virt] kvm: arm/arm64: Force reading uncached stage2 PGD (Wei Huang) [1459864]
- [virt] kvm: arm/arm64: Fix race in resetting stage2 PGD (Wei Huang) [1459864]
- [virt] KVM: arm/arm64: vgic-v3: Use PREbits to infer the number of ICH_APxRn_EL2 registers (Wei Huang) [1459864]
- [virt] KVM: arm/arm64: vgic-v3: Do not use Active+Pending state for a HW interrupt (Wei Huang) [1459864]
- [virt] KVM: arm/arm64: vgic-v2: Do not use Active+Pending state for a HW interrupt (Wei Huang) [1459864]
- [arm64] KVM: Do not use stack-protector to compile EL2 code (Wei Huang) [1459864]
- [redhat] config: aarch64: enable CRYPTO_CRC32_ARM64_CE (Jeffrey Bastian) [1370247]
- [virt] KVM: arm/arm64: Hold slots_lock when unregistering kvm io bus devices (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Fix bug when registering redist iodevs (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: vgic-its: Cleanup after failed ITT restore (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Don't call map_resources when restoring ITS tables (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Register ITS iodev when setting base address (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Get rid of its->initialized field (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Register iodevs when setting redist base and creating VCPUs (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Slightly rework kvm_vgic_addr (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Make vgic_v3_check_base more broadly usable (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: Refactor vgic_register_redist_iodevs (Auger Eric) [1411488]
- [virt] KVM: Add kvm_vcpu_get_idx to get vcpu index in kvm->vcpus (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: vgic: Rename kvm_vgic_vcpu_init to kvm_vgic_vcpu_enable (Auger Eric) [1411488]
- [documentation] KVM: arm/arm64: Clarification and relaxation to ITS save/restore ABI (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-v3: KVM_DEV_ARM_VGIC_SAVE_PENDING_TABLES (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Fix pending table sync (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: ITT save and restore (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Device table save/restore (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: vgic_its_check_id returns the entry's GPA (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Collection table save/restore (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Add infrastructure for table lookup (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: vgic_its_alloc_ite/device (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: KVM_DEV_ARM_ITS_SAVE/RESTORE_TABLES (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Read config and pending bit in add_lpi() (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-v3: vgic_v3_lpi_sync_pending_status (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Check the device id matches TYPER DEVBITS range (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Interpret MAPD ITT_addr field (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Interpret MAPD Size field and check related errors (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Implement vgic_mmio_uaccess_write_its_iidr (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Introduce migration ABI infrastructure (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Implement vgic_mmio_uaccess_write_its_creadr (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: Implement vgic_its_has_attr_regs and attr_regs_access (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: vgic: expose (un)lock_all_vcpus (Auger Eric) [1411488]
- [virt] KVM: arm64: vgic-its: KVM_DEV_ARM_VGIC_GRP_ITS_REGS group (Auger Eric) [1411488]
- [virt] arm/arm64: vgic: turn vgic_find_mmio_region into public (Auger Eric) [1411488]
- [virt] KVM: arm/arm64: vgic-its: rename itte into ite (Auger Eric) [1411488]
- [documentation] KVM: arm/arm64: Add GICV3 pending table save API documentation (Auger Eric) [1411488]
- [documentation] KVM: arm/arm64: Add ITS save/restore API documentation (Auger Eric) [1411488]
- [tty] pl011: use "qdf2400_e44" as the earlycon name for QDF2400 E44 (Steve Ulrich) [1455336]
- [iommu] arm-smmu-v3: Increase CMDQ drain timeout value (Robert Richter) [1447562]
- [scsi] scsi_sysfs: make unpriv_sgio queue attribute accessible for non-block devices (Ewan Milne) [1392079]

* Tue Jun 13 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-8.el7]
- [net] ipv6: Fix leak in ipv6_gso_segment() (Eric Garver) [1459953] {CVE-2017-9074}
- [net] ipv6: xfrm: Handle errors reported by xfrm6_find_1stfragopt() (Eric Garver) [1459953] {CVE-2017-9074}
- [net] ipv6: Check ip6_find_1stfragopt() return value properly (Eric Garver) [1459953] {CVE-2017-9074}
- [net] ipv6: Prevent overrun when parsing v6 header options (Eric Garver) [1459953] {CVE-2017-9074}
- [nvme] nvme-rdma: Support ctrl_loss_tmo (David Milburn) [1443936]
- [nvme] nvme-fabrics: Allow ctrl loss timeout configuration (David Milburn) [1443936]
- [nvme] nvme-rdma: get rid of local reconnect_delay (David Milburn) [1443936]
- [powerpc] 64s: Idle POWER8 avoid full state loss recovery where possible (Steve Best) [1368734]
- [powerpc] 64s: Idle do not hold reservation longer than required (Steve Best) [1368734]
- [powerpc] 64s: Expand core idle state bits (Steve Best) [1368734]
- [powerpc] 64s: Fix POWER9 machine check handler from stop state (Steve Best) [1368734]
- [powerpc] 64s: Use alternative feature patching (Steve Best) [1368734]
- [powerpc] 64s: Stop using bit in HSPRG0 to test winkle (Steve Best) [1368734]
- [powerpc] 64s: Move remaining system reset idle code into idle_book3s.S (Steve Best) [1368734]
- [powerpc] 64s: Remove unnecessary relocation branch from idle handler (Steve Best) [1368734]
- [powerpc] powernv: Recover correct PACA on wakeup from a stop on P9 DD1 (Steve Best) [1368734]
- [powerpc] 64s: POWER8 add missing machine check definitions (Steve Best) [1368734]
- [powerpc] 64s: Data driven machine check handling (Steve Best) [1368734]
- [powerpc] 64s: Data driven machine check evaluation (Steve Best) [1368734]
- [powerpc] 64s: Move POWER machine check defines into mce_power.c (Steve Best) [1368734]
- [powerpc] 64s: Clean up machine check recovery flushing (Steve Best) [1368734]
- [powerpc] 64s: Machine check print NIP (Steve Best) [1368734]
- [pci] MSI: pci-xgene-msi: Enable MSI support in ACPI boot for X-Gene v1 (Jonathan Toppins) [1445092]
- [redhat] kconfig: Enable to assign a node which has only movable memory for power 9 (Steve Best) [1368719]
- [redhat] config: aarch64: re-disable /dev/mem (Al Stone) [1456956]
- [redhat] config: aarch64: re-disable /dev/port (Al Stone) [1456956]

* Thu Jun 08 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-7.el7]
- [net] ipv6: fix out of bound writes in __ip6_append_data() (Hangbin Liu) [1459239] {CVE-2017-9242}
- [rtc] interface: Validate alarm-time before handling rollover (Steve Best) [1440117]
- [rtc] opal: Handle disabled TPO in opal_get_tpo_time() (Steve Best) [1440117]
- [virt] KVM: API: Use the upstream version of KVM_CAP ABI definition (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: Move shared files to virt/kvm/arm (Wei Huang) [1448160]
- [virt] Revert "KVM: Support vCPU-based gfn->hva cache" (Wei Huang) [1448160]
- [arm64] kvm: Fix decoding of Rt/Rt2 when trapping AArch32 CP accesses (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic-v3: Fix off-by-one LR access (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic-v3: De-optimize VMCR save/restore when emulating a GICv2 (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: Report PMU overflow interrupts to userspace irqchip (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: Support arch timers with a userspace gic (Wei Huang) [1448160]
- [arm64] kvm: arm/arm64: Add ARM user space interrupt signaling ABI (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: Cleanup the arch timer code's irqchip checking (Wei Huang) [1448160]
- [documentation] arm/arm64: Add hyp-stub API documentation (Wei Huang) [1448160]
- [arm64] hyp-stub: Zero x0 on successful stub handling (Wei Huang) [1448160]
- [arm64] hyp-stub/kvm: Kill __hyp_get_vectors (Wei Huang) [1448160]
- [arm64] kvm: Implement HVC_SOFT_RESTART in the init code (Wei Huang) [1448160]
- [arm64] kvm: Convert __cpu_reset_hyp_mode to using __hyp_reset_vectors (Wei Huang) [1448160]
- [arm64] kvm: Allow the main HYP code to use the init hyp stub implementation (Wei Huang) [1448160]
- [arm64] kvm: Implement HVC_GET_VECTORS in the init code (Wei Huang) [1448160]
- [arm64] kvm: Implement HVC_RESET_VECTORS stub hypercall in the init code (Wei Huang) [1448160]
- [arm64] hyp-stub: Implement HVC_RESET_VECTORS stub hypercall (Wei Huang) [1448160]
- [arm64] hyp-stub: Update documentation in asm/virt.h (Wei Huang) [1448160]
- [arm64] hyp-stub: Define a return value for failed stub calls (Wei Huang) [1448160]
- [arm64] hyp-stub: Don't save lr in the EL1 code (Wei Huang) [1448160]
- [arm64] kvm: Move lr save/restore to do_el2_call (Wei Huang) [1448160]
- [arm64] hyp-stub: Stop pointlessly clobbering lr (Wei Huang) [1448160]
- [arm64] kvm: Do not corrupt registers on failed 64bit CP read (Wei Huang) [1448160]
- [arm64] kvm: Treat sysreg accessors returning false as successful (Wei Huang) [1448160]
- [arm64] kvm: pmu: Inject UNDEF on read access to PMSWINC_EL0 (Wei Huang) [1448160]
- [arm64] kvm: Make unexpected reads from WO registers inject an undef (Wei Huang) [1448160]
- [arm64] kvm: pmu: Inject UNDEF on non-privileged accesses (Wei Huang) [1448160]
- [arm64] kvm: pmu: Inject UNDEF exception on illegal register access (Wei Huang) [1448160]
- [arm64] kvm: pmu: Refactor pmu_*_el0_disabled (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Improve sync_hwstate performance (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Don't check vgic_initialized in sync/flush (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Implement early VGIC init functionality (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Get rid of MISR and EISR fields (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Get rid of unnecessary save_maint_int_state (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Get rid of unnecessary process_maintenance operation (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Only set underflow when actually out of LRs (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Get rid of live_lrs (Wei Huang) [1448160]
- [virt] kvm: arm/arm64: vgic: Avoid flushing vgic state when there's no pending IRQ (Wei Huang) [1448160]
- [arm64] cpufeature: Make ID reg accessor naming less counterintuitive (Wei Huang) [1448160]
- [arm64] kvm: arm64: Use common Set/Way sys definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: Use common sysreg definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: use common invariant sysreg definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: Use common physical timer sysreg definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: Use common GICv3 sysreg definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: Use common performance monitor sysreg definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: Use common debug sysreg definitions (Wei Huang) [1448160]
- [arm64] kvm: arm64: add SYS_DESC() (Wei Huang) [1448160]
- [arm64] sysreg: add Set/Way sys encodings (Wei Huang) [1448160]
- [arm64] sysreg: add register encodings used by KVM (Wei Huang) [1448160]
- [arm64] sysreg: add physical timer registers (Wei Huang) [1448160]
- [arm64] sysreg: subsume GICv3 sysreg definitions (Wei Huang) [1448160]
- [arm64] sysreg: add performance monitor registers (Wei Huang) [1448160]
- [arm64] sysreg: add debug system registers (Wei Huang) [1448160]
- [arm64] sysreg: sort by encoding (Wei Huang) [1448160]
- [arm64] kvm: Add support for VPIPT I-caches (Wei Huang) [1448160]
- [arm64] cache: Identify VPIPT I-caches (Wei Huang) [1448160]
- [arm64] cache: Merge cachetype.h into cache.h (Wei Huang) [1448160]
- [arm64] cache: Remove support for ASID-tagged VIVT I-caches (Wei Huang) [1448160]
- [arm64] cacheinfo: Remove CCSIDR-based cache information probing (Wei Huang) [1448160]
- [arm64] cpuinfo: remove I-cache VIPT aliasing detection (Wei Huang) [1448160]
- [mm] migrate: allow migrate_vma() to alloc new page on empty entry v2 (Jerome Glisse) [1433282 1422592]
- [mm] migrate: support un-addressable ZONE_DEVICE page in migration v2 (Jerome Glisse) [1433282 1422592]
- [mm] migrate: migrate_vma() unmap page from vma while collecting pages (Jerome Glisse) [1433282 1422592]
- [mm] migrate: new memory migration helper for use with device memory v4 (Jerome Glisse) [1433282 1422592]
- [mm] migrate: new migrate mode MIGRATE_SYNC_NO_COPY (Jerome Glisse) [1433282 1422592]
- [mm] hmm/devmem: dummy HMM device for ZONE_DEVICE memory v3 (Jerome Glisse) [1433282 1422592]
- [mm] hmm/devmem: device memory hotplug using ZONE_DEVICE v5 (Jerome Glisse) [1433282 1422592]
- [mm] ZONE_DEVICE: special case put_zone_device_page() for private pages (Jerome Glisse) [1433282 1422592]
- [mm] ZONE_DEVICE: new type of ZONE_DEVICE for unaddressable memory v3 (Jerome Glisse) [1433282 1422592]
- [mm] memory_hotplug: introduce add_pages (Jerome Glisse) [1433282 1422592]
- [mm] hmm/mirror: device page fault handler (Jerome Glisse) [1433282 1422592]
- [mm] hmm/mirror: helper to snapshot CPU page table v3 (Jerome Glisse) [1433282 1422592]
- [mm] hmm/mirror: mirror process address space on device with HMM helpers v3 (Jerome Glisse) [1433282 1422592]
- [mm] hmm: heterogeneous memory management (HMM for short) v4 (Jerome Glisse) [1433282 1422592]
- [documentation] hmm: heterogeneous memory management documentation (Jerome Glisse) [1433282 1422592]
- [netdrv] drivers: net: xgene: Fix redundant prefetch buffer cleanup (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Workaround for HW errata 10GE_10/ENET_15 (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Add frame recovered statistics counter for errata 10GE_8/ENET_11 (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Workaround for HW errata 10GE_4 (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Add rx_overrun/tx_underrun statistics (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Extend ethtool statistics (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Remove unused macros (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Refactor statistics error parsing code (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Remove redundant local stats (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Use rgmii mdio mac access (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: phy: xgene: Add lock to protect mac access (Iyappan Subramanian) [1455037]
- [netdrv] drivers: net: xgene: Protect indirect MAC access (Iyappan Subramanian) [1455037]
- [irqchip] mbigen: Fix the clear register offset calculation (Jun Ma) [1455055]
- [irqchip] mbigen: Fix potential NULL dereferencing (Jun Ma) [1455055]
- [irqchip] mbigen: Fix memory mapping code (Jun Ma) [1455055]
- [irqchip] mbigen: Fix return value check in mbigen_device_probe() (Jun Ma) [1455055]
- [powerpc] pstore: Fix flags to enable dumps on powerpc (Steve Best) [1455303]
- [arm64] pmuv3: disable PMUv3 in VM when vPMU=off (Wei Huang) [1452803]
- [perf] drivers/perf: arm_pmu_acpi: avoid perf IRQ init when guest PMU is off (Wei Huang) [1452803]
- [arm64] pmuv3: use arm_pmu ACPI framework (Jeremy Linton) [1420476]
- [arm64] pmuv3: handle !PMUv3 when probing (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: add ACPI framework (Jeremy Linton) [1420476]
- [arm64] add function to get a cpu's MADT GICC table (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: split out platform device probe logic (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: move irq request/free into probe (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: split cpu-local irq request/free (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: rename irq request/free functions (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: handle no platform_device (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: simplify cpu_pmu_request_irqs() (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: factor out pmu registration (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: fold init into alloc (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: define armpmu_init_fn (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: remove pointless PMU disabling (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: split irq request from enable (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: manage interrupts per-cpu (Jeremy Linton) [1420476]
- [drivers] perf: arm_pmu: rework per-cpu allocation (Jeremy Linton) [1420476]

* Tue Jun 06 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-6.el7]
- [redhat] rename kernel-pegas to kernel-alt ("Herton R. Krzesinski")

* Fri May 26 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-5.el7]
- [powerpc] Mark IBM Power 8 unsupported (Steve Best) [1451378]
- [powerpc] kvm: ppc: book3s hv: Add radix checks in real-mode hypercall handlers (David Gibson) [1449039]
- [powerpc] kvm: ppc: Pass kvm* to kvmppc_find_table() (David Gibson) [1449039]
- [scsi] cxlflash: Select IRQ_POLL (Steve Best) [1455362]
- [scsi] cxlflash: Introduce hardware queue steering (Steve Best) [1452604]
- [scsi] cxlflash: Add hardware queues attribute (Steve Best) [1452604]
- [scsi] cxlflash: Support multiple hardware queues (Steve Best) [1452604]
- [scsi] cxlflash: Improve asynchronous interrupt processing (Steve Best) [1452604]
- [scsi] cxlflash: Fix warnings/errors (Steve Best) [1452604]
- [scsi] cxlflash: Fix power-of-two validations (Steve Best) [1452604]
- [scsi] cxlflash: Remove unnecessary DMA mapping (Steve Best) [1452604]
- [scsi] cxlflash: Fence EEH during probe (Steve Best) [1452604]
- [scsi] cxlflash: Support up to 4 ports (Steve Best) [1452604]
- [scsi] cxlflash: SISlite updates to support 4 ports (Steve Best) [1452604]
- [scsi] cxlflash: Hide FC internals behind common access routine (Steve Best) [1452604]
- [scsi] cxlflash: Remove port configuration assumptions (Steve Best) [1452604]
- [scsi] cxlflash: Support dynamic number of FC ports (Steve Best) [1452604]
- [scsi] cxlflash: Update sysfs helper routines to pass config structure (Steve Best) [1452604]
- [scsi] cxlflash: Implement IRQ polling for RRQ processing (Steve Best) [1452604]
- [scsi] cxlflash: Serialize RRQ access and support offlevel processing (Steve Best) [1452604]
- [scsi] cxlflash: Separate RRQ processing from the RRQ interrupt handler (Steve Best) [1452604]
- [kernel] rh_taint: introduce mark_hardware_deprecated() (Scott Wood) [1451092]
- [pci] add pci_hw_vendor_status() (Scott Wood) [1451092]
- [kernel] rh_taint: Remove taint and update unsupported hardware message (Scott Wood) [1451092]
- [kernel] rh_taint: Forward-port RH specific TAINT flags (Scott Wood) [1451092]
- [irqchip] arm64: gic: Do not allow bypass FIQ signals to reach to processor (Mark Salter) [1408317]

* Mon May 22 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-4.el7]
- [misc] cxl: Enable PCI device IDs for future IBM CXL adapters (Steve Best) [1452796]
- [redhat] kconfig: PowerNV platform RTC driver for power 9 (Steve Best) [1452588]
- [powerpc] KVM: PPC: Book3S HV: Native usage of the XIVE interrupt controller (David Gibson) [1396118]
- [pci] Apply Cavium ACS quirk only to CN81xx/CN83xx/CN88xx devices (Robert Richter) [1451727]
- [redhat] kconfig: Enable this driver to get read/write support I2C EEPROMs for power 9 (Steve Best) [1451680]
- [tools] perf trace: Handle unpaired raw_syscalls:sys_exit event (Jiri Olsa) [1441286]
- [redhat] Enable Qualcomm IPMI and EMAC drivers (Steve Ulrich) [1443724]
- [scsi] hisi_sas: controller reset for multi-bits ECC and AXI fatal errors (Zhou Wang) [1266303]
- [scsi] hisi_sas: fix NULL deference when TMF timeouts (Zhou Wang) [1266303]
- [scsi] hisi_sas: add v2 hw internal abort timeout workaround (Zhou Wang) [1266303]
- [scsi] hisi_sas: workaround SoC about abort timeout bug (Zhou Wang) [1266303]
- [scsi] hisi_sas: workaround a SoC SATA IO processing bug (Zhou Wang) [1266303]
- [scsi] hisi_sas: workaround STP link SoC bug (Zhou Wang) [1266303]
- [scsi] hisi_sas: fix SATA dependency (Zhou Wang) [1266303]
- [scsi] hisi_sas: add missing break in switch statement (Zhou Wang) [1266303]
- [scsi] hisi_sas: add is_sata_phy_v2_hw() (Zhou Wang) [1266303]
- [scsi] hisi_sas: use dev_is_sata to identify SATA or SAS disk (Zhou Wang) [1266303]
- [scsi] hisi_sas: check hisi_sas_lu_reset() error message (Zhou Wang) [1266303]
- [scsi] hisi_sas: release SMP slot in lldd_abort_task (Zhou Wang) [1266303]
- [scsi] hisi_sas: add hisi_sas_clear_nexus_ha() (Zhou Wang) [1266303]
- [scsi] hisi_sas: rename hisi_sas_link_timeout_enable/disable_link (Zhou Wang) [1266303]
- [scsi] hisi_sas: handle PHY UP+DOWN simultaneous irq (Zhou Wang) [1266303]
- [scsi] hisi_sas: some modifications to v2 hw reg init (Zhou Wang) [1266303]
- [scsi] hisi_sas: process error codes according to their priority (Zhou Wang) [1266303]
- [scsi] hisi_sas: remove task free'ing for timeouts (Zhou Wang) [1266303]
- [scsi] hisi_sas: fix some sas_task.task_state_lock locking (Zhou Wang) [1266303]
- [scsi] hisi_sas: free slots after hardreset (Zhou Wang) [1266303]
- [scsi] hisi_sas: check for SAS_TASK_STATE_ABORTED in slot complete (Zhou Wang) [1266303]
- [scsi] hisi_sas: hardreset for SATA disk in LU reset (Zhou Wang) [1266303]
- [scsi] hisi_sas: modify hisi_sas_abort_task() for SSP (Zhou Wang) [1266303]
- [scsi] hisi_sas: modify error handling for v2 hw (Zhou Wang) [1266303]
- [scsi] hisi_sas: only reset link for PHY_FUNC_LINK_RESET (Zhou Wang) [1266303]
- [scsi] hisi_sas: error hisi_sas_task_prep() when port down (Zhou Wang) [1266303]
- [scsi] hisi_sas: remove hisi_sas_port_deformed() (Zhou Wang) [1266303]
- [scsi] hisi_sas: add softreset function for SATA disk (Zhou Wang) [1266303]
- [scsi] hisi_sas: move PHY init to hisi_sas_scan_start() (Zhou Wang) [1266303]
- [scsi] hisi_sas: add controller reset (Zhou Wang) [1266303]
- [scsi] hisi_sas: add to_hisi_sas_port() (Zhou Wang) [1266303]
- [redhat] aarch64: configs: Enable HiSilicon SAS controller (Zhou Wang) [1266303]
- [netdrv] hns: fix ethtool_get_strings overflow in hns driver (Zhou Wang) [1266302]
- [netdrv] hns: support deferred probe when no mdio (Zhou Wang) [1266302]
- [netdrv] hns: support deferred probe when can not obtain irq (Zhou Wang) [1266302]
- [netdrv] hns: Some checkpatch.pl script & warning fixes (Zhou Wang) [1266302]
- [netdrv] hns: Avoid Hip06 chip TX packet line bug (Zhou Wang) [1266302]
- [netdrv] hns: Adjust the SBM module buffer threshold (Zhou Wang) [1266302]
- [netdrv] hns: Simplify the exception sequence in hns_ppe_init() (Zhou Wang) [1266302]
- [netdrv] hns: Optimise the code in hns_mdio_wait_ready() (Zhou Wang) [1266302]
- [netdrv] hns: Clean redundant code from hns_mdio.c file (Zhou Wang) [1266302]
- [netdrv] hns: Remove redundant mac table operations (Zhou Wang) [1266302]
- [netdrv] hns: Remove redundant mac_get_id() (Zhou Wang) [1266302]
- [netdrv] hns: Remove the redundant adding and deleting mac function (Zhou Wang) [1266302]
- [netdrv] hns: Correct HNS RSS key set function (Zhou Wang) [1266302]
- [netdrv] hns: Replace netif_tx_lock to ring spin lock (Zhou Wang) [1266302]
- [netdrv] hns: Fix to adjust buf_size of ring according to mtu (Zhou Wang) [1266302]
- [netdrv] hns: Optimize hns_nic_common_poll for better performance (Zhou Wang) [1266302]
- [netdrv] hns: bug fix of ethtool show the speed (Zhou Wang) [1266302]
- [netdrv] hns: Remove redundant memset during buffer release (Zhou Wang) [1266302]
- [netdrv] hns: Optimize the code for GMAC pad and crc Config (Zhou Wang) [1266302]
- [netdrv] hns: Modify GMAC init TX threshold value (Zhou Wang) [1266302]
- [netdrv] hns: Fix the implementation of irq affinity function (Zhou Wang) [1266302]
- [redhat] aarch64: configs: Enable HiSilicon HNS networking modules (Zhou Wang) [1266302]
- [iommu] aarch64: Set bypass mode per default (Robert Richter) [1437372]
- [iommu] arm-smmu: Return IOVA in iova_to_phys when SMMU is bypassed (Robert Richter) [1437372]
- [iommu] Print a message with the default domain type created (Robert Richter) [1437372]
- [iommu] Allow default domain type to be set on the kernel command line (Robert Richter) [1437372]
- [iommu] arm-smmu-v3: Install bypass STEs for IOMMU_DOMAIN_IDENTITY domains (Robert Richter) [1437372]
- [iommu] arm-smmu-v3: Make arm_smmu_install_ste_for_dev return void (Robert Richter) [1437372]
- [iommu] arm-smmu: Install bypass S2CRs for IOMMU_DOMAIN_IDENTITY domains (Robert Richter) [1437372]
- [iommu] arm-smmu: Restrict domain attributes to UNMANAGED domains (Robert Richter) [1437372]
- [edac] thunderx: Remove unused code (Robert Richter) [1243040]
- [edac] thunderx: Change LMC index calculation (Robert Richter) [1243040]
- [edac] thunderx: Fix L2C MCI interrupt disable (Robert Richter) [1243040]

* Mon May 15 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-3.el7]
- [arm64] redhat: crashkernel auto reservation code for ARM64 (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [firmware] efi/libstub/arm*: Set default address and size cells values for an empty dtb (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] dt: chosen properties for arm64 kdump (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] kdump: describe arm64 port (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: enable kdump in defconfig (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: provide /proc/vmcore file (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: add VMCOREINFO's for user-space tools (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: implement machine_crash_shutdown() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] hibernate: preserve kdump image around hibernation (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: protect crash dump kernel memory (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mm: add set_memory_valid() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] kdump: reserve memory for crash dump kernel (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] limit memory regions based on DT property, usable-memory-range (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] memblock: add memblock_cap_memory_range() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] memblock: add memblock_clear_nomap() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mm: set the contiguous bit for kernel mappings where appropriate (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mm: remove pointless map/unmap sequences when creating page tables (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: replace 'page_mappings_only' parameter with flags argument (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: add contiguous bit to sanity bug check (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: ignore debug_pagealloc for kernel segments (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: align alloc_init_pte prototype with pmd/pud versions (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: apply strict permissions to .init.text and .init.data (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: map .text as read-only from the outset (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] alternatives: apply boot time fixups via the linear mapping (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] mmu: move TLB maintenance from callers to create_mapping_late() (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [virt] arm: kvm: move kvm_vgic_global_state out of .text section (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] Revert "memblock: add memblock_clear_nomap()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [mm] Revert "memblock: add memblock_cap_memory_range()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: limit memory regions based on DT property, usable-memory-range" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: reserve memory for crash dump kernel" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: mm: add set_memory_valid()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: protect crash dump kernel memory" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: hibernate: preserve kdump image around hibernation" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: implement machine_crash_shutdown()" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: add VMCOREINFO's for user-space tools" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: provide /proc/vmcore file" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "arm64: kdump: enable kdump in defconfig" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] Revert "Documentation: kdump: describe arm64 port" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [documentation] Revert "Documentation: dt: chosen properties for arm64 kdump" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [firmware] Revert "efi/libstub/arm*: Set default address and size cells values for an empty dtb" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [arm64] Revert "redhat: crashkernel auto reservation code for ARM64" (Pratyush Anand) [1390457 1342670 1433230 1388289]
- [redhat] use installmandocs target to install kernel API man pages ("Herton R. Krzesinski") [1451051]
- [documentation] allow installing man pages to a user defined directory ("Herton R. Krzesinski") [1451051]
- [powerpc] perf: Add Power8 mem_access event to sysfs (Steve Best) [1368735]
- [powerpc] perf: Support to export SIERs bit in Power9 (Steve Best) [1368735]
- [powerpc] perf: Support to export SIERs bit in Power8 (Steve Best) [1368735]
- [powerpc] perf: Support to export MMCRA(TEC*) field to userspace (Steve Best) [1368735]
- [powerpc] perf: Export memory hierarchy info to user space (Steve Best) [1368735]
- [netdrv] i40e: only register client on iWarp-capable devices (Stefan Assmann) [1441817]
- [netdrv] i40e: close client on remove and shutdown (Stefan Assmann) [1441817]
- [netdrv] i40e: register existing client on probe (Stefan Assmann) [1441817]
- [netdrv] i40e: remove client instance on driver unload (Stefan Assmann) [1441817]
- [netdrv] i40e: fix RSS queues only operating on PF0 (Stefan Assmann) [1441817]
- [netdrv] i40e: initialize params before notifying of l2_param_changes (Stefan Assmann) [1441817]
- [netdrv] i40e: KISS the client interface (Stefan Assmann) [1441817]
- [netdrv] i40e: fix up recent proxy and wol bits for X722_SUPPORT (Stefan Assmann) [1441817]
- [netdrv] i40e: Acquire NVM lock before reads on all devices (Stefan Assmann) [1441817]
- [netdrv] drivers: net: xgene: Add workaround for errata 10GE_8/ENET_11 (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Add workaround for errata 10GE_1 (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Fix Rx checksum validation logic (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Fix wrong logical operation (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: xgene: Fix hardware checksum setting (Iyappan Subramanian) [1441795]
- [netdrv] drivers: net: phy: xgene: Fix mdio write (Iyappan Subramanian) [1441795]
- [block] sg_io: introduce unpriv_sgio queue flag (Paolo Bonzini) [1394238]
- [block] sg_io: pass request_queue to blk_verify_command (Paolo Bonzini) [1394238]
- [redhat] aarch64: configs: Enable X-Gene Ethernet v2 (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Fix error return code in xge_mdio_config() (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Extend ethtool statistics (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: misc fixes (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Fix port reset (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add ethtool support (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add MDIO support (Iyappan Subramanian) [1383485]
- [netdrv] maintainers: Add entry for APM X-Gene SoC Ethernet (v2) driver (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add transmit and receive (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add base driver (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add ethernet hardware configuration (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add mac configuration (Iyappan Subramanian) [1383485]
- [netdrv] drivers: net: xgene-v2: Add DMA descriptor (Iyappan Subramanian) [1383485]
- [redhat] kconfig: Enable XIVE and XIVE_NATIVE for Power 9 (Steve Best) [1320898]
- [powerpc] 64s: Revert setting of LPCR(LPES) on POWER9 (Steve Best) [1320898]
- [powerpc] powernv: Add XIVE related definitions to opal-api.h (Steve Best) [1320898]
- [powerpc] Fixup LPCR:PECE and HEIC setting on POWER9 (Steve Best) [1320898]
- [powerpc] Consolidate variants of real-mode MMIOs (Steve Best) [1320898]
- [powerpc] kvm: Remove obsolete kvm_vm_ioctl_xics_irq declaration (Steve Best) [1320898]
- [powerpc] kvm: Make kvmppc_xics_create_icp static (Steve Best) [1320898]
- [powerpc] kvm: Massage order of #include (Steve Best) [1320898]
- [powerpc] xive: Native exploitation of the XIVE interrupt controller (Steve Best) [1320898]
- [powerpc] smp: Remove migrate_irq() custom implementation (Steve Best) [1320898]
- [powerpc] Add optional smp_ops->prepare_cpu SMP callback (Steve Best) [1320898]
- [powerpc] Add more PPC bit conversion macros (Steve Best) [1320898]
- [redhat] aarch64: configs: Enable DesignWare GPIO (Iyappan Subramanian) [1429651]
- [gpio] dwapb: Add support for next generation of X-Gene SoC (Iyappan Subramanian) [1429651]
- [arm64] DO NOT UPSTREAM - Enable workaround for accessing ICC_SRE_EL2 (Wei Huang) [1442825]
- [arm64] qcom: Add defines for ARMv8 implementer (MIDR) (Wei Huang) [1442825]
- [acpi] iort: Fix CONFIG_IOMMU_API dependency (Jun Ma) [1266462]
- [acpi] iort: Remove linker section for IORT entries probing (Jun Ma) [1266462]
- [iommu] arm-smmu: Clean up early-probing workarounds (Jun Ma) [1266462]
- [arm64] dma-mapping: Remove the notifier trick to handle early setting of dma_ops (Jun Ma) [1266462]
- [acpi] drivers: acpi: Handle IOMMU lookup failure with deferred probing or error (Jun Ma) [1266462]
- [iommu] of: Handle IOMMU lookup failure with deferred probing or error (Jun Ma) [1266462]
- [of] acpi: Configure dma operations at probe time for platform/amba/pci bus devices (Jun Ma) [1266462]
- [of] device: Fix overflow of coherent_dma_mask (Jun Ma) [1266462]
- [acpi] iort: Add function to check SMMUs drivers presence (Jun Ma) [1266462]
- [of] dma: Make of_dma_deconfigure() public (Jun Ma) [1266462]
- [iommu] of: Prepare for deferred IOMMU configuration (Jun Ma) [1266462]
- [iommu] of: Refactor of_iommu_configure() for error handling (Jun Ma) [1266462]
- [misc] cxl: Add psl9 specific code (Steve Best) [1320907]
- [misc] cxl: Isolate few psl8 specific calls (Steve Best) [1320907]
- [misc] cxl: Rename some psl8 specific functions (Steve Best) [1320907]
- [misc] cxl: Update implementation service layer (Steve Best) [1320907]
- [misc] cxl: Keep track of mm struct associated with a context (Steve Best) [1320907]
- [misc] cxl: Remove unused values in bare-metal environment (Steve Best) [1320907]
- [misc] cxl: Read vsec perst load image (Steve Best) [1320907]
- [arm64] vdso: Remove ISB from gettimeofday (Robert Richter) [1445440]
- [arm64] vdso: Rewrite gettimeofday into C (Robert Richter) [1445440]
- [redhat] configs: enable CONFIG_NF_SOCKET_IPV4 and CONFIG_NF_SOCKET_IPV6 (Davide Caratti) [1436771]
- [redhat] config: enable CHECKPOINT_RESTORE only on x86_64 and powerpc64 (Aristeu Rozanski) [1391536]
- Revert "[redhat] aarch64: configs: Enable Qlogic networking support" ("Herton R. Krzesinski")

* Tue May 09 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-2.el7]
- [ethernet] bnx2x: Align RX buffers (Scott Wood) [1438582]
- [acpi] Continue to ignore interrupt producer/consumer flag (Jeremy Linton) [1448077]
- [i2c] thunderx: Enable HWMON class probing (Robert Richter) [1448181]
- [acpi] apd: Add clock frequency for Hisilicon Hip07/08 I2C controller (Jun Ma) [1403804]
- [i2c] designware: Add ACPI HID for Hisilicon Hip07/08 I2C controller (Jun Ma) [1403804]
- [redhat] aarch64:configs: Enable desingware I2C controller (Jun Ma) [1403804]
- [redhat] aarch64: configs: Enable Qlogic networking support (Zhou Wang) [1266393]
- [redhat] aarch64: configs: Enable HiSilicon VGA (Zhou Wang) [1266321]
- [fs] iomap_dio_rw: Prevent reading file data beyond iomap_dio->i_size (Gustavo Duarte) [1444708]
- [acpi] arm64: Add SBSA Generic Watchdog support in GTDT driver (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: add GTDT support for memory-mapped timer (Jun Ma) [1403765]
- [acpi] arm64: Add memory-mapped timer support in GTDT driver (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: simplify ACPI support code (Jun Ma) [1403765]
- [acpi] arm64: Add GTDT table parse driver (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: split MMIO timer probing (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: add structs to describe MMIO timer (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: move arch_timer_needs_of_probing into DT init call (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: refactor arch_timer_needs_probing (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: split dt-only rate handling (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: rework PPI selection (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: add a new enum for spi type (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: move enums and defines to header file (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: rename the PPI enum (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: rename type macros (Jun Ma) [1403765]
- [clocksource] arm_arch_timer: clean up printk usage (Jun Ma) [1403765]
- [arm64] arch_timer: Add HISILICON_ERRATUM_161010101 ACPI matching data (Jun Ma) [1439440]
- [arm64] arch_timer: Allow erratum matching with ACPI OEM information (Jun Ma) [1439440]
- [arm64] arch_timer: Workaround for Cortex-A73 erratum 858921 (Jun Ma) [1439440]
- [arm64] arch_timer: Enable CNTVCT_EL0 trap if workaround is enabled (Jun Ma) [1439440]
- [arm64] arch_timer: Save cntkctl_el1 as a per-cpu variable (Jun Ma) [1439440]
- [arm64] arch_timer: Move clocksource_counter and co around (Jun Ma) [1439440]
- [arm64] arch_timer: Allows a CPU-specific erratum to only affect a subset of CPUs (Jun Ma) [1439440]
- [arm64] arch_timer: Make workaround methods optional (Jun Ma) [1439440]
- [arm64] arch_timer: Rework the set_next_event workarounds (Jun Ma) [1439440]
- [arm64] arch_timer: Get rid of erratum_workaround_set_sne (Jun Ma) [1439440]
- [arm64] arch_timer: Move arch_timer_reg_read/write around (Jun Ma) [1439440]
- [arm64] arch_timer: Add erratum handler for CPU-specific capability (Jun Ma) [1439440]
- [arm64] arch_timer: Add infrastructure for multiple erratum detection methods (Jun Ma) [1439440]
- [arm64] cpu_errata: Add capability to advertise Cortex-A73 erratum 858921 (Jun Ma) [1439440]
- [arm64] cpu_errata: Allow an erratum to be match for all revisions of a core (Jun Ma) [1439440]
- [arm64] Define Cortex-A73 MIDR (Jun Ma) [1439440]
- [arm64] Add CNTVCT_EL0 trap handler (Jun Ma) [1439440]
- [arm64] Allow checking of a CPU-local erratum (Jun Ma) [1439440]
- [irqchip] gic-v3-its: Add IORT hook for platform MSI support (Jun Ma) [1266314]
- [irqchip] mbigen: Add ACPI support (Jun Ma) [1266314]
- [irqchip] mbigen: Introduce mbigen_of_create_domain() (Jun Ma) [1266314]
- [irqchip] mbigen: Drop module owner (Jun Ma) [1266314]
- [base] platform-msi: Make platform_msi_create_device_domain() ACPI aware (Jun Ma) [1266314]
- [acpi] platform: setup MSI domain for ACPI based platform device (Jun Ma) [1266314]
- [acpi] platform-msi: retrieve devid from IORT (Jun Ma) [1266314]
- [acpi] iort: Introduce iort_node_map_platform_id() to retrieve dev id (Jun Ma) [1266314]
- [acpi] iort: Rename iort_node_map_rid() to make it generic (Jun Ma) [1266314]
- [irqchip] gicv3-its: platform-msi: Scan MADT to create platform msi domain (Jun Ma) [1266314]
- [irqchip] gicv3-its: platform-msi: Refactor its_pmsi_init() to prepare for ACPI (Jun Ma) [1266314]
- [irqchip] gicv3-its: platform-msi: Refactor its_pmsi_prepare() (Jun Ma) [1266314]
- [irqchip] gic-v3-its: Keep the include header files in alphabetic order (Jun Ma) [1266314]
- [acpi] iort: Rework iort_match_node_callback() return value handling (Jun Ma) [1266314]
- [acpi] iort: Add missing comment for iort_dev_find_its_id() (Jun Ma) [1266314]
- [acpi] iort: Fix the indentation in iort_scan_node() (Jun Ma) [1266314]
- [redhat] Modify CONFIG_UPROBE_EVENT and CONFIG_KPROBE_EVENT (Pratyush Anand) [1448376]

* Wed May 03 2017 Herton R. Krzesinski <herton@redhat.com> [4.11.0-1.el7]
- [acpi] pci: Add MCFG quirk for 2nd node of Cavium ThunderX pass2.x host controller (Robert Richter) [1430388]
- [redhat] copy blk-wbt.h and blk-stat.h headers in kernel-devel package ("Herton R. Krzesinski") [1440236]
- [ata] ahci: thunderx2: Fix for errata that affects stop engine (Robert Richter) [1430391]
- [redhat] aarch64: configs: Enable ARCH_THUNDER2 (Robert Richter) [1414532]
- [gpio] xlp: Update for ARCH_THUNDER2 (Robert Richter) [1414532]
- [spi] xlp: update for ARCH_VULCAN2 (Robert Richter) [1414532]
- [iommu] arm-smmu, acpi: Enable Cavium SMMU-v2 (Robert Richter) [1427523]
- [iommu] arm-smmu: Print message when Cavium erratum 27704 was detected (Robert Richter) [1427523]
- [iommu] arm-smmu: Fix 16bit ASID configuration (Robert Richter) [1427523]
- [redhat] aarch64: configs: Enable edac support for Cavium CN88xx (Robert Richter) [1243040]
- [edac] thunderx: Add Cavium ThunderX EDAC driver (Robert Richter) [1243040]
- [redhat] aarch64: Enable CONFIG_CRASH_DUMP (Pratyush Anand) [1388289]
- [char] ipmi_si: use smi_num for init_name (Tony Camuso) [1435727]
- [i2c] thunderx: ACPI support for clock settings (Robert Richter) [1268499]
- [i2c] xlp9xx: update for ARCH_THUNDER2 (Robert Richter) [1268499]
- [arm64] redhat: crashkernel auto reservation code for ARM64 (Pratyush Anand) [1388289 1342670 1390457]
- [firmware] efi/libstub/arm*: Set default address and size cells values for an empty dtb (Pratyush Anand) [1388289 1342670 1390457]
- [documentation] dt: chosen properties for arm64 kdump (Pratyush Anand) [1388289 1342670 1390457]
- [documentation] kdump: describe arm64 port (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: enable kdump in defconfig (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: provide /proc/vmcore file (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: add VMCOREINFO's for user-space tools (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: implement machine_crash_shutdown() (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] hibernate: preserve kdump image around hibernation (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: protect crash dump kernel memory (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] mm: add set_memory_valid() (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] kdump: reserve memory for crash dump kernel (Pratyush Anand) [1388289 1342670 1390457]
- [arm64] limit memory regions based on DT property, usable-memory-range (Pratyush Anand) [1388289 1342670 1390457]
- [mm] memblock: add memblock_cap_memory_range() (Pratyush Anand) [1388289 1342670 1390457]
- [mm] memblock: add memblock_clear_nomap() (Pratyush Anand) [1388289 1342670 1390457]
- [redhat] aarch64: configs: Enable crypto support for Cavium CN88xx (Robert Richter) [1404503]
- [redhat] configs: Enable CRYPTO_CRC32C_ARM64 (Herbert Xu) [1370247]
- [base] cacheinfo: let arm64 provide cache info without using DT or ACPI (Al Stone) [1382130 1340200]
- [tty] Fix ldisc crash on reopened tty (Steve Best) [1434165]
- [redhat] docs: require machine parseable upstream commit ids (Jiri Benc)
- [redhat] configs: Enable CONFIG_X86_AMD_PLATFORM_DEVICE (Scott Wood) [1430011]
- [redhat] kconfig: Disable Software IOTLB support for powerpc (Steve Best) [1428506]
- [pci] vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Robert Richter) [1430377]
- [arm64] topology: Adjust sysfs topology (Jonathan Toppins) [1392076]
- [redhat] configs: ppc64: Remove unselectable symbols for unsupported hardware (Scott Wood) [1420897]
- [pci] Workaround for Broadcom Vulcan DMA alias calculation (Robert Richter) [1430372]
- [redhat] aarch64: configs: CN99xx: Add support for Vulcan i2c controller (Robert Richter) [1344226]
- [redhat] kconfig: remove obsolete symbols for ARM64 (Mark Langsdorf) [1425525]
- [redhat] configs: CONFIG_NF_CT_PROTO_* options should be y not m (Prarit Bhargava) [1430505]
- [x86] kdump: crashkernel=X try to reserve below 896M first, then try below 4G, then MAXMEM (Xunlei Pang) [1375960]
- [powerpc] kdump: Adjust crashkernel reservation for 2GB-4GB systems (Xunlei Pang) [1375960]
- [powerpc] kdump: Support crashkernel auto memory reservation on a system with 2GB or more (Xunlei Pang) [1375960]
- [powerpc] kdump: Set crashkernel 'auto' memory reservation threshold to 2GB (Xunlei Pang) [1375960]
- [s390x] kdump: Increase crashkernel=auto base reservation from 128M to 160M (Xunlei Pang) [1375960]
- [kernel] kdump: Increase x86 crashkernel=auto base reservation from 128M to 160M (Xunlei Pang) [1375960]
- [kernel] kdump: Improve logging when crashkernel=auto can't be satisfied (Xunlei Pang) [1375960]
- [s390x] kdump: Use 4 GiB for KEXEC_AUTO_THRESHOLD (Xunlei Pang) [1375960]
- [kdump] crashkernel=auto fixes and cleanup (Xunlei Pang) [1375960]
- [kdump] Add crashkernel=auto support (Xunlei Pang) [1375960]
- [fs] revert "libxfs: pack the agfl header structure so XFS_AGFL_SIZE is correct" (Eric Sandeen) [1411637]
- [redhat] kconfig: Disable HIBERNATION for powerpc (Steve Best) [1422587]
- [redhat] aarch64: configs: Disable X-Gene PktDMA driver (Jeffrey Bastian) [1408300]
- [redhat] aarch64: configs: Enable Cavium HW RNG module (David Daney) [1385929]
- [redhat] configs: enable CONFIG_VFIO_NOIOMMU for aarch64 (William Townsend) [1418087]
- [redhat] configs: disable CONFIG_SERIAL_8250 on s390x ("Herton R. Krzesinski") [1418787]
- [redhat] enable s390x build again for testing ("Herton R. Krzesinski") [1410579]
- [s390x] add zfcpdump user space tools from RHEL 7 ("Herton R. Krzesinski") [1410579]
- [redhat] rhmaintainers: update files list and maintainer for infiniband (Jonathan Toppins)
- [redhat] rhmaintainers: update tg3 and bna maintainer fields with jtoppins (Jonathan Toppins)
- [redhat] rhmaintainers: update bnxt_en maintainer info (Jonathan Toppins)
- [redhat] aarch64: configs: enable _en bits of mlx5 driver (Jonathan Toppins) [1404081]
- [redhat] add support for aarch64 in rh-cross-* make targets (Al Stone) [1415855]
- [redhat] build-configs.sh: simplify config building (Jonathan Toppins)
- [makefile] arm64, powerpc, x86: Add -Werror to kernel build ("Herton R. Krzesinski") [1404449]
- [makefile] Revert "Fix gcc-4.9.0 miscompilation of load_balance() in scheduler" ("Herton R. Krzesinski") [1387899]
- [redhat] rhmaintainers: add Amazon Ethernet Drivers entry (Vitaly Kuznetsov)
- [redhat] configs: enable LIO iSCSI target mode for cxgb4 (Jonathan Toppins) [1405565]
- [redhat] configs: Enable IMA and INTEGRITY by default ("Herton R. Krzesinski") [1326888]
- [tty] 8250_dw: quirk lack of spcr driver's ability to report mmio32 (Jonathan Toppins) [1406924]
- [char] crash: add crash driver (Dave Anderson) [1398016]
- [arm64] acpi: prefer booting with ACPI over DTS (Jonathan Toppins) [1405174]
- [redhat] config: re-enable RDMAVT and HFI1 due to defaults change (Jonathan Toppins) [1409890]
- [redhat] add missing .gitattributes directives from RHEL 7 setup ("Herton R. Krzesinski")
- [redhat] configs: enable Amazon Elastic Network Adapter ("Herton R. Krzesinski")
- [redhat] configs: enable CONFIG_CRYPTO_DEV_CHELSIO=m ("Herton R. Krzesinski")
- [redhat] RHMAINTAINERS: update Kernel Maintainer entry ("Herton R. Krzesinski")
- [redhat] genspec.sh: do not hide arm64 changelog entries ("Herton R. Krzesinski")
- [redhat] configs: disable CONFIG_USELIB on all architectures ("Herton R. Krzesinski") [1388940]
- [redhat] configs: enable driver for X-Gene hardware sensors (Jeffrey Bastian) [1400331]
- [arch] arm64: Workaround for QDF2432 ID_AA64 SR accesses (Mark Langsdorf) [1389083]
- [kernel] kbuild: AFTER_LINK (Roland McGrath)
- [redhat] scripts/new_release.sh: do not increment PREBUILD line ("Herton R. Krzesinski")
- [redhat] determine proper tag on initial release ("Herton R. Krzesinski")
- [redhat] rh-dist-git: fix update of dist-git sources file for linux tarball ("Herton R. Krzesinski")
- [redhat] scripts/rh-dist-git.sh: fix the upload of the kabi tarball ("Herton R. Krzesinski")
- [redhat] update git/files and .gitignore after latest kabi changes ("Herton R. Krzesinski")
- [redhat] kabi: enable kernel-abi-whitelists package and kabi-check (Petr Oros)
- [redhat] kabi: show-kabi: allow empty whitelist (Petr Oros)
- [redhat] kabi: add support for aarch64 (Petr Oros)
- [redhat] kabi: remove support for s390x (Petr Oros)
- [redhat] kabi: remove support for ppc64 (Petr Oros)
- [redhat] kabi: clean all symbols in x86_64 (Petr Oros)
- [redhat] kabi: clean all symbols in ppc64le (Petr Oros)
- [redhat] Remove dup scripts from kernel tree (Petr Oros)
- [redhat] configs: set to y accelerated implementations of CONFIG_CRYPTO_AES ("Herton R. Krzesinski") [1397913]
- [redhat] configs: set CONFIG_CRYPTO_DRBG_MENU=y ("Herton R. Krzesinski") [1397913]
- [redhat] spec: include missing arch/arm/include into devel package (Petr Oros) [1397407]
- [redhat] make sure we create changelogs and look at tags with right package name ("Herton R. Krzesinski")
- [redhat] rh-dist-git.sh: give the package name to clone_tree.sh ("Herton R. Krzesinski")
- [redhat] configs: add missing changes to lib/ configuration (Aristeu Rozanski)
- [init] enable CHECKPOINT_RESTORE (Aristeu Rozanski) [1391536]
- [redhat] Makefiles: remove extra inclusions (Jonathan Toppins)
- [redhat] allow building binaries with different name from src.rpm ("Herton R. Krzesinski")
- [redhat] config review: enable NVME_TARGET_LOOP/NVME_TARGET_RDMA ("Herton R. Krzesinski")
- [redhat] config review: remove/disable deprecated scsi/storage drivers ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_SCSI_SNIC=n ("Herton R. Krzesinski")
- [redhat] config review: delete removed drivers/scsi options ("Herton R. Krzesinski")
- [redhat] configs: merge requested changes for watchdog support (Aristeu Rozanski)
- [redhat] configs: merge changes for RTC (Aristeu Rozanski)
- [redhat] config review: make sure we disable drivers for some obsolete scsi hw ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_SCSI_AIC7XXX_OLD ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_REGULATOR related options ("Herton R. Krzesinski")
- [redhat] configs: merge comments on USB (Aristeu Rozanski)
- [redhat] config review: do not disable CEPH_FS on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: fix/cleanup CONFIG_PWM_LPSS* configs ("Herton R. Krzesinski")
- [redhat] config review: BATTERY_BQ27x00 renamed to BATTERY_BQ27XXX ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_DELL_SMBIOS=m on x86_64 ("Herton R. Krzesinski")
- [redhat] config review: move existing x86 platform options to x86_64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_MTD_BLKDEVS ("Herton R. Krzesinski")
- [redhat] config review: mark some CONFIG_MTD_* options as disabled ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_MTD_NAND_* options ("Herton R. Krzesinski")
- [redhat] configs: merge changes for PCI (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_MMC_SDRICOH_CS ("Herton R. Krzesinski")
- [redhat] configs: merge comments for NVMEM, NVME, OF, NTB (Aristeu Rozanski)
- [redhat] config review: cleanup CONFIG*INTEL_MID* options ("Herton R. Krzesinski")
- [redhat] config review: delete INTEL_MEI/VMWARE_BALLOON from generic ("Herton R. Krzesinski")
- [redhat] config review: cleanup auto selected options from drivers/misc ("Herton R. Krzesinski")
- [redhat] config review: delete hidden drivers/misc options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_SENSORS_BH1780 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ATMEL_PWM ("Herton R. Krzesinski")
- [redhat] config review: mark all new CONFIG_MFD_* options as disabled ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_MEMSTICK_REALTEK_USB=m on x86_64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DM_CACHE_MQ ("Herton R. Krzesinski")
- [redhat] config review: cleanup BCACHE options ("Herton R. Krzesinski")
- [redhat] config review: disable DM_LOG_WRITES/DM_VERITY_FEC ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_XGENE_SLIMPRO_MBOX=m on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_NVM=n ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_LEDS_TRIGGER_PANIC=n ("Herton R. Krzesinski")
- [redhat] config review: LEDS_TRIGGER_IDE_DISK renamed to LEDS_TRIGGER_DISK ("Herton R. Krzesinski")
- [redhat] config review: LEDS_PCA9633 renamed to LEDS_PCA963X ("Herton R. Krzesinski")
- [redhat] config review: ISDN_DRV_AVMB1_VERBOSE_REASON renamed ("Herton R. Krzesinski")
- [redhat] configs: set HZ to 100 across all arches ("Herton R. Krzesinski")
- [redhat] configs: adjust HID options based on feedback (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_AMD_IOMMU_STATS ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_IIO on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_I2C_INTEL_MID ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_SENSORS_I5500=m on x86_64 ("Herton R. Krzesinski")
- [redhat] configs: adjust input config options for arm64 (Aristeu Rozanski)
- [redhat] config review: change/cleanup some drivers/gpu options on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: initial review of drivers/gpu options ("Herton R. Krzesinski")
- [redhat] config review: cleanup some GPIO options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_FW_CFG_SYSFS=n ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_DEV_DAX ("Herton R. Krzesinski")
- [redhat] config review: merge feedback from CONFIG_TCG_* ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_STALDRV ("Herton R. Krzesinski")
- [redhat] configs: update drivers/media config options (Aristeu Rozanski)
- [redhat] config review: cleanup most of options which depends on PCMCIA ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_CRASH settings ("Herton R. Krzesinski")
- [redhat] config review: review CONFIG_DEVMEM and its related settings ("Herton R. Krzesinski")
- [redhat] config review: ARM_CCI500_PMU renamed to ARM_CCI5xx_PMU ("Herton R. Krzesinski")
- [redhat] config review: disable bluetooth on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_PARIDE_* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DRBD_FAULT_INJECTION ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CISS_SCSI_TAPE ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_XEN_BLKDEV_BACKEND ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_BLK_DEV_HD* ("Herton R. Krzesinski")
- [redhat] config review: fix value of CONFIG_BLK_DEV_SKD ("Herton R. Krzesinski")
- [redhat] config review: keep CONFIG_BLK_DEV_SKD disabled ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BLK_CPQ_DA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BCMA_BLOCKIO ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ATM_* options related to drivers ("Herton R. Krzesinski")
- [redhat] configs: disable all sound modules on arm64 (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_A11Y_BRAILLE_CONSOLE ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_UEVENT_HELPER* ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_FW_LOADER_USER_HELPER* ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_KVM_MMIO ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_XEN_NETDEV_BACKEND ("Herton R. Krzesinski")
- [redhat] config review: WL_TI was renamed to WLAN_VENDOR_TI ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ZYDAS=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ST=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_RSI=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_CISCO=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ATMEL=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_ADMTEK=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on NET_VENDOR_WIZNET ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_WL12XX_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_VIA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_USB_CDC_PHONET ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on NET_VENDOR_3COM ("Herton R. Krzesinski")
- [redhat] config review: drop CONFIG_TEHUTI ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on NET_VENDOR_STMICRO ("Herton R. Krzesinski")
- [redhat] config review: don't disable SLIP on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on FDDI ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_SIS* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_SC92031 ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_EXAR ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_RTL8XXXU=m ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_R6040 ("Herton R. Krzesinski")
- [redhat] config review: delete QEDE_GENEVE/QEDE_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_WLAN_VENDOR_INTERSIL=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup some CONFIG_PCMCIA_* options (network drivers) ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PCH_GBE ("Herton R. Krzesinski")
- [redhat] config review: cleanup P54 related options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NET_VENDOR_XIRCOM ("Herton R. Krzesinski")
- [redhat] adjust tty config options (Aristeu Rozanski)
- [redhat] config review: set NET_VENDOR_SAMSUNG/NET_VENDOR_SYNOPSYS=n ("Herton R. Krzesinski")
- [redhat] config review: enable ROCKER ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_RENESAS=n ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_QUALCOMM=y for aarch64 ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_QUALCOMM=n for everyone ("Herton R. Krzesinski")
- [redhat] config review: cleanup NET_VENDOR_FARADAY/NET_VENDOR_FUJITSU ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_EZCHIP=n for everyone ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_NET_VENDOR_CAVIUM on ppc64le/x86_64 ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_NET_VENDOR_AGERE=n for everyone ("Herton R. Krzesinski")
- [redhat] config review: remove NET_VENDOR_8390 and options that depends on it ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_NATSEMI ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NET_CALXEDA_XGMAC ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_MT7601U=m ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_MLXSW_CORE=m on aarch64 and x86_64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_MLX4_EN_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: cleanup remaining HAMRADIO driver related options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_THUNDER_NIC_BGX ("Herton R. Krzesinski")
- [redhat] config review: do not disable MACSEC on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup LIBERTAS options ("Herton R. Krzesinski")
- [redhat] config review: cleanup options related to NET_VENDOR_MICREL ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_IWLWIFI* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_IPW* options ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_IPVLAN=n ("Herton R. Krzesinski")
- [redhat] config review: config changes for removed IP1000 option ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_I40E_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depends on HERMES ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_FORCEDETH ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_FM10K_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: move CONFIG_NET_VENDOR_MICROCHIP to generic ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_EMAC_ROCKCHIP ("Herton R. Krzesinski")
- [redhat] config review: cleanup options which depend on IRDA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DMASCC ("Herton R. Krzesinski")
- [redhat] config review: cleanup NET_VENDOR_DLINK related options ("Herton R. Krzesinski")
- [redhat] config review: cleanup ATALK related options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CHELSIO_T1_1G ("Herton R. Krzesinski")
- [redhat] config review: cleanup options under NET_VENDOR_SUN ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CAN_SJA1000_OF_PLATFORM ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_CAN_M_CAN=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_BRCM* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BPQETHER ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BE2NET_VXLAN ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BCM63XX_PHY ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_BAYCOM_* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_B44_PCI ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_B43LEGACY_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_B43_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ATH9K options ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ATH6KL* settings ("Herton R. Krzesinski")
- [redhat] config review: cleanup ATH5K settings ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ALI_FIR ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ADAPTEC_STARFIRE ("Herton R. Krzesinski")
- [redhat] config review: cleanup ACT200L/ACTISYS_DONGLE ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_ACENIC* settings ("Herton R. Krzesinski")
- [redhat] config review: more misc cleanup on some init/ options (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_6PACK ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ARM_AT91_ETHER ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_TRACE_BRANCH_PROFILING ("Herton R. Krzesinski")
- [redhat] config review: TRACEPOINT_BENCHMARK/TRACE_ENUM_MAP_FILE/TRACING_EVENTS_GPIO ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PREEMPT_TRACER ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_PM_* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PM_OPP ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_VIRT_CPU_ACCOUNTING ("Herton R. Krzesinski")
- [redhat] config review: do not disable NO_HZ_FULL on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_LIVEPATCH ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_INTEGRITY_AUDIT=y ("Herton R. Krzesinski")
- [redhat] config review: mark some IMA options as disabled ("Herton R. Krzesinski")
- [redhat] config review: cleanup/move IMA options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_EVM_LOAD_X509=n ("Herton R. Krzesinski")
- [redhat] config review: replace EVM_HMAC_VERSION with EVM_ATTR_FSUUID ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_GENERIC_CLOCKEVENTS_BUILD ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CLOCKSOURCE_WATCHDOG ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_RD_LZ4=y ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_KEYS_DEBUG_PROC_KEYS ("Herton R. Krzesinski")
- [redhat] config review: set n to KEY_DH_OPERATIONS/SECURITY_LOADPIN ("Herton R. Krzesinski")
- [redhat] config review: do not disable CRYPTO_TEST on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup/delete PKCS7_MESSAGE_PARSER files ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CRYPTO_ZLIB ("Herton R. Krzesinski")
- [redhat] config review: enable requested CRYPTO_SHA* options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_CRYPTO_SALSA20_586 ("Herton R. Krzesinski")
- [redhat] config review: cleanup/check CRYPTO_POLY1305* settings ("Herton R. Krzesinski")
- [redhat] config review: delete CRYPTO_LZO/CRYPTO_MD5 ("Herton R. Krzesinski")
- [redhat] config review: remove/disable CRYPTO_LZ4/CRYPTO_LZ4HC ("Herton R. Krzesinski")
- [redhat] config review: remove CONFIG_CRYPTO_KEYWRAP from aarch64 ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_CRYPTO_CTR=m ("Herton R. Krzesinski")
- [redhat] config review: ensure we set newer *CRYPTO_USER_API* ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_CRYPTO_DES3_EDE_X86_64=m ("Herton R. Krzesinski")
- [redhat] config review: enable chacha20 on other arches ("Herton R. Krzesinski")
- [redhat] config review: cleanup CRYPTO_MCRYPTD specific setting ("Herton R. Krzesinski")
- [redhat] config review: move CRYPTO_CRC32C_INTEL under x86_64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup some unselectable crypto options ("Herton R. Krzesinski")
- [redhat] config review: move some CONFIG_X86_* options under x86_64 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_X86_INTEL_MEMORY_PROTECTION_KEYS=y ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_X86_DEBUG_FPU only on -debug ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_RANDOMIZE_BASE=n ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_TUNE_CELL ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_PPC_RADIX_MMU=y for ppc64le ("Herton R. Krzesinski")
- [redhat] config review: more misc cleanup on some arch options ("Herton R. Krzesinski")
- [redhat] config review: enable/set CONFIG_PERF_EVENTS_* options ("Herton R. Krzesinski")
- [redhat] config review: misc cleanup on some arch options ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NO_BOOTMEM ("Herton R. Krzesinski")
- [redhat] config review: cleanup/delete CONFIG_HAVE_* options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_GCC_PLUGINS=n ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_GEN_RTC_X ("Herton R. Krzesinski")
- [redhat] configs: enable CONFIG_SECTION_MISMATCH_WARN_ONLY for now (Aristeu Rozanski)
- [redhat] config review: delete CONFIG_DIRECT_GBPAGES ("Herton R. Krzesinski")
- [redhat] config review: move some x86_64 CONFIG_DEBUG* options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_DEBUG_WX=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup and fix DEBUG_RODATA* settings ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_DEBUG_ENTRY=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup/fix stack protector settings ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_ARM64_VA_BITS_48=y ("Herton R. Krzesinski")
- [redhat] config review: update ARCH_EXYNOS setting ("Herton R. Krzesinski")
- [redhat] config review: delete MFD_TIMBERDALE/TIMB_DMA settings ("Herton R. Krzesinski")
- [redhat] config review: enable QCOM_HIDMA* on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_PCH_DMA ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_INTEL_MID_DMAC ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NET_DMA_RH_KABI ("Herton R. Krzesinski")
- [redhat] config review: update for IDMA64 config rename ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_DW_DMAC_BIG_ENDIAN_IO ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_EDAC_SKX=m on x86_64 ("Herton R. Krzesinski")
- [redhat] config review: merge lib related options (Aristeu Rozanski)
- [redhat] config review: adjust for mce_amd_inj config option rename ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_ARM_CPUIDLE on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup CONFIG_CPU_IDLE_MULTIPLE_DRIVERS ("Herton R. Krzesinski")
- [redhat] config review: IB driver changes on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete IB options which are gone ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_RDMA_RXE=m ("Herton R. Krzesinski")
- [redhat] config review: don't disable Infiniband on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_TIPC_MEDIA_IB ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_TCP_CONG* settings ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_ROSE ("Herton R. Krzesinski")
- [redhat] config review: cleanup for remaining RFKILL options ("Herton R. Krzesinski")
- [redhat] config review: keep RFKILL_GPIO enabled only on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup any remaining CONFIG_RDS_* ("Herton R. Krzesinski")
- [redhat] config review: set CONFIG_*NETDEV options ("Herton R. Krzesinski")
- [redhat] config review: set NF_LOG_ARP and NF_LOG_BRIDGE for everyone ("Herton R. Krzesinski")
- [redhat] config review: don't disable NF_CT_NETLINK_TIMEOUT on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: don't disable NF_CONNTRACK_TIMEOUT on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: update NF_CONNTRACK_IPV4/6 ("Herton R. Krzesinski")
- [redhat] config review: enable NET_SWITCHDEV on all arches ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_NET_SCH* settings ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NETROM ("Herton R. Krzesinski")
- [redhat] config review: fix renamed NETPRIO cgroup setting ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_NET_NCSI=n ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_NETLINK_MMAP setting ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_NET_L3_MASTER_DEV=n ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_NETFILTER* settings ("Herton R. Krzesinski")
- [redhat] config review: merge CONFIG_NET_* options ("Herton R. Krzesinski")
- [redhat] config review: cleanup NET_9P settings ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_MPLS_ROUTING=n ("Herton R. Krzesinski")
- [redhat] config review: do not unset NET_DEVLINK on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup some unselectable net options ("Herton R. Krzesinski")
- [redhat] config review: always enable IP_VS_FO/IP_VS_OVF ("Herton R. Krzesinski")
- [redhat] config review: don't disable IPV6_GRE on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_IPV6_ILA=n ("Herton R. Krzesinski")
- [redhat] config review: disable net *FOU* options ("Herton R. Krzesinski")
- [redhat] config review: merge config feedback on missing ipset modules ("Herton R. Krzesinski")
- [redhat] config review: fix CONFIG_IP_NF_TARGET_REJECT setting ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_IP_NF_TARGET_ULOG ("Herton R. Krzesinski")
- [redhat] config review: fix IP_NF_FILTER setting ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_INET_LRO ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_HSR/CONFIG_INET_DIAG_DESTROY ("Herton R. Krzesinski")
- [redhat] config review: always disable CONFIG_CGROUP_NET_PRIO ("Herton R. Krzesinski")
- [redhat] config review: fix CONFIG_BRIDGE_NETFILTER=m ("Herton R. Krzesinski")
- [redhat] config review: delete CONFIG_BRIDGE_EBT_ULOG ("Herton R. Krzesinski")
- [redhat] config review: cleanup and enable BPF_JIT also on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup/remove AX25 options ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_AF_KCM=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup fs related options ("Herton R. Krzesinski")
- [redhat] config review: don't disable FS_DAX on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: disable GFS2 and DLM ("Herton R. Krzesinski")
- [redhat] config review: disable btrfs ("Herton R. Krzesinski")
- [redhat] config review: don't disable QUOTA_DEBUG on aarch64 -debug ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_PNFS_FILE_LAYOUT=m ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_ORANGEFS_FS=n ("Herton R. Krzesinski")
- [redhat] config review: additional cleanup/changes for NFS settings ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_NFSD_FAULT_INJECTION=y for aarch64 -debug ("Herton R. Krzesinski")
- [redhat] config review: remove specific CONFIG_NFSD_SCSILAYOUT setting on arm ("Herton R. Krzesinski")
- [redhat] config review: mark NFSD_BLOCKLAYOUT/NFSD_FLEXFILELAYOUT as disabled ("Herton R. Krzesinski")
- [redhat] config review: don't make NFS builtin on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_FS_ENCRYPTION=n ("Herton R. Krzesinski")
- [redhat] config review: make CONFIG_FSCACHE_OBJECT_LIST setting consistent ("Herton R. Krzesinski")
- [redhat] config review: update for renamed CONFIG_EXT4_USE_FOR_EXT23 ("Herton R. Krzesinski")
- [redhat] config review: mark CONFIG_EXT4_ENCRYPTION=n ("Herton R. Krzesinski")
- [redhat] config review: cleanup 9P_FS options ("Herton R. Krzesinski")
- [redhat] config review: cleanup removed acpi options ("Herton R. Krzesinski")
- [redhat] config review: set always CONFIG_ACPI_TABLE_UPGRADE=y ("Herton R. Krzesinski")
- [redhat] config review: review/cleanups of some ACPI configs ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_ACPI_TABLE_UPGRADE on aarch64 non-debug ("Herton R. Krzesinski")
- [redhat] config review: merge acpi debug options ("Herton R. Krzesinski")
- [redhat] config review: disable wlan and wireless on aarch64 and ppc64le ("Herton R. Krzesinski")
- [redhat] config review: disable CONFIG_BPF_SYSCALL ("Herton R. Krzesinski")
- [redhat] config review: don't disable TRANSPARENT_HUGEPAGE on aarch64 ("Herton R. Krzesinski")
- [redhat] config review: cleanup SPARSEMEM options ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_ZSMALLOC_STAT ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_Z3FOLD=n ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_IDLE_PAGE_TRACKING on all configs ("Herton R. Krzesinski")
- [redhat] config review: CONFIG_CMA_DEBUGFS=y and CONFIG_DEBUG_PAGE_REF=y for -debug ("Herton R. Krzesinski")
- [redhat] config review: merge remaining ata related options ("Herton R. Krzesinski")
- [redhat] config review: enable CONFIG_SATA_AHCI_SEATTLE ("Herton R. Krzesinski")
- [redhat] config review: merge block related options ("Herton R. Krzesinski")
- [redhat] Kconfig: Fix CPU_FREQ_STAT setting (Steve Best)
- [redhat] clarify better in the spec why we build headers only for some arches ("Herton R. Krzesinski")
- [redhat] fix architectures being built (Aristeu Rozanski)
- [redhat] get rid of static 'kernel-pegas' and use a central variable (Aristeu Rozanski)
- [redhat] update manually lastcommit (Aristeu Rozanski)
- [redhat] disable hiding of redhat only entries from changelog (Aristeu Rozanski)
- [redhat] change default scratch/official brew build target (Aristeu Rozanski)
- [redhat] disable bootwrapper build if arch is in nobuildarches list ("Herton R. Krzesinski")
- [redhat] disable debug build if arch is in nobuildarches list ("Herton R. Krzesinski")
- [redhat] disable abi whitelists support in the spec file ("Herton R. Krzesinski")
- [redhat] trim/remove old RHEL 7 changelog from the spec file ("Herton R. Krzesinski")
- [redhat] fix make rh-dist-git for kernel-pegas tree ("Herton R. Krzesinski")
- [redhat] rename kernel spec file ("Herton R. Krzesinski")
- [redhat] rename kernel package to kernel-pegas ("Herton R. Krzesinski")
- [redhat] add full support to build aarch64 packages ("Herton R. Krzesinski")
- [redhat] Initial enablement of aarch64 architecture ("Herton R. Krzesinski")
- [redhat] fix-up modules signing (Rafael Aquini)
- [redhat] spec: fix signing_key references (Rafael Aquini)
- [redhat] add missing x509.genkey and extra_certificates files ("Herton R. Krzesinski")
- [redhat] spec: disable arches s390x, ppc64 follow up (Rafael Aquini)
- [redhat] spec: adjust build recipes for the new kernel infrastructure (Rafael Aquini)
- [redhat] disable s390x, s390, i686, ppc64 (Aristeu Rozanski)
- [redhat] move architecture list to Makefile.common (Aristeu Rozanski)
- [redhat] disable kABI check for now (Aristeu Rozanski)
- [redhat] change version to 4.11.0 ("Herton R. Krzesinski")
- [redhat] makefile: make use of proper RHELMAJOR string constant when packaging kabi structures (Rafael Aquini)
- [redhat] configs: match RPMVERSION on generated config files (Rafael Aquini)
- [redhat] import Red Hat specific files (Aristeu Rozanski)


###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
