# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

%global src_pkg_name kernel-alt
%global bin_pkg_name kernel
%global bin_suffix_name %{nil}

Summary: The Linux kernel

# % define buildid .local

# For a kernel released for public testing, released_kernel should be 1.
# For internal testing builds during development, it should be 0.
%global released_kernel 1

%global distro_build 49

%define rpmversion 4.14.0
%define pkgrelease 49.el7a

# allow pkg_release to have configurable %{?dist} tag
%define specrelease 49%{?dist}

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
%define all_arch_configs %{src_pkg_name}-%{version}-aarch64*.config
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
%ifarch x86_64
BuildRequires: pesign >= 0.109-4
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel bison
BuildRequires: audit-libs-devel
BuildRequires: java-devel
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
%if %{?released_kernel}
Source13: securebootca.cer
Source14: secureboot.cer
%define pesign_name redhatsecureboot301
%else
Source13: redhatsecurebootca2.cer
Source14: redhatsecureboot003.cer
%define pesign_name redhatsecureboot003
%endif
Source15: rheldup3.x509
Source16: rhelkpatch1.x509

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

# Setup CONFIG_SYSTEM_TRUSTED_KEYS="certs/rhel.pem" for module signing. And make
# sure we create the file with certificates and copy key generation configuration
for i in *.config
do
  sed -i 's@CONFIG_SYSTEM_TRUSTED_KEYS=.*@CONFIG_SYSTEM_TRUSTED_KEYS="certs/rhel.pem"@' $i
done
cp %{SOURCE11} ./certs # x509.genkey
openssl x509 -inform der -in %{_sourcedir}/rheldup3.x509 -out rheldup3.pem
openssl x509 -inform der -in %{_sourcedir}/rhelkpatch1.x509 -out rhelkpatch1.pem
cat rheldup3.pem rhelkpatch1.pem > ./certs/rhel.pem

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
    Config=%{src_pkg_name}-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
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
    %pesign -s -i $KernelImage -o $KernelImage.signed -a %{SOURCE13} -c %{SOURCE14} -n %{pesign_name}
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
    cp -a --parents arch/$Arch/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
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
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign.debug .tmp_versions \
    mv signing_key.pem.sign.debug signing_key.pem \
    mv signing_key.x509.sign.debug signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVRA}.debug || exit 1 \
  fi \
    if [ "%{with_default}" -ne "0" ]; then \
    Arch=`head -1 configs/%{src_pkg_name}-%{version}-%{_target_cpu}.config | cut -b 3-` \
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

# copy the source over
mkdir -p $docdir
tar -f - --exclude='.*' -c Documentation | tar xf - -C $docdir

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
%{_libdir}/libperf-jvmti.so
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
* Wed Mar 14 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-49.el7a]
- [netdrv] tg3: prevent scheduling while atomic splat (Jonathan Toppins) [1555032]
- [powerpc] KVM: PPC: Book3S HV: Fix guest time accounting with VIRT_CPU_ACCOUNTING_GEN (Laurent Vivier) [1541614]
- [powerpc] KVM: PPC: Book3S HV: Improve handling of debug-trigger HMIs on POWER9 (Gustavo Duarte) [1548423]

* Tue Mar 06 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-48.el7a]
- [s390] s390/entry.S: fix spurious zeroing of r0 (Hendrik Brueckner) [1551586]

* Mon Mar 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-47.el7a]
- [kernel] futex: Prevent overflow by strengthen input validation (Joe Lawrence) [1547583] {CVE-2018-6927}

* Mon Feb 26 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-46.el7a]
- [powerpc] ppc needs macro for spectre v1 mitigation (Christoph von Recklinghausen) [1538186]
- [arm64] Add missing Falkor part number for branch predictor hardening (Spectre/Meltdown) (Steve Ulrich) [1545916]
- [s390] kernel: fix rwlock implementation (Hendrik Brueckner) [1547423]
- [redhat] s390/configs: enable KERNEL_NOBP for s390 (Hendrik Brueckner) [1532726]
- [s390] spinlock: add __nospec_barrier memory barrier (Hendrik Brueckner) [1532726]
- [s390] Replace IS_ENABLED(EXPOLINE_*) with IS_ENABLED(CONFIG_EXPOLINE_*) (Hendrik Brueckner) [1532726]
- [s390] introduce execute-trampolines for branches (Hendrik Brueckner) [1532726]
- [s390] run user space and KVM guests with modified branch prediction (Hendrik Brueckner) [1532726]
- [s390] add options to change branch prediction behaviour for the kernel (Hendrik Brueckner) [1532726]
- [s390] s390/alternative: use a copy of the facility bit mask (Hendrik Brueckner) [1532726]
- [s390] add optimized array_index_mask_nospec (Hendrik Brueckner) [1532726]
- [s390] scrub registers on kernel entry and KVM exit (Hendrik Brueckner) [1532726]
- [s390] enable CPU alternatives unconditionally (Hendrik Brueckner) [1532726]
- [s390] introduce CPU alternatives (Hendrik Brueckner) [1532726]
- [security] KEYS: Use individual pages in big_key for crypto buffers (David Howells) [1510601]
- [powerpc] powerpc/eeh: Fix crashes in eeh_report_resume() (Gustavo Duarte) [1546028]
- [redhat] switch secureboot kernel image signing to release keys ("Herton R. Krzesinski")
- [redhat] RHMAINTAINERS: update power management sections (Al Stone)
- [fs] xfs: validate sb_logsunit is a multiple of the fs blocksize (Bill O'Donnell) [1538496]
- [kernel] bpf: prevent out-of-bounds speculation (Mark Langsdorf) [1536036]
- [arm64] kpti: Fix the interaction between ASID switching and software PAN (Mark Langsdorf) [1536036]
- [arm64] SW PAN: Point saved ttbr0 at the zero page when switching to init_mm (Mark Langsdorf) [1536036]
- [arm64] Re-order reserved_ttbr0 in linker script (Mark Langsdorf) [1536036]
- [arm64] capabilities: Handle duplicate entries for a capability (Mark Langsdorf) [1536036]

* Tue Feb 20 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-45.el7a]
- [netdrv] tg3: APE heartbeat changes (Jonathan Toppins) [1545870]
- [redhat] fix rh_get_maintainer.pl (Andrew Jones)
- [scsi] lpfc Fix SCSI io host reset causing kernel crash (Dick Kennedy) [1540693]

* Mon Feb 19 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-44.el7a]
- [powerpc] powerpc/mm: Flush radix process translations when setting MMU type (Laurent Vivier) [1533718]
- [powerpc] powerpc/mm/radix: Split linear mapping on hot-unplug (Suraj Jitindar Singh) [1516201]
- [powerpc] KVM: PPC: Book3S: Add MMIO emulation for VMX instructions (Laurent Vivier) [1537935]
- [powerpc] KVM: PPC: Book3S HV: Make HPT resizing work on POWER9 (Laurent Vivier) [1535789]
- [powerpc] KVM: PPC: Book3S HV: Fix handling of secondary HPTEG in HPT resizing code (Laurent Vivier) [1535789]
- [powerpc] KVM: PPC: Book3S HV: Drop locks before reading guest memory (Laurent Vivier) [1540077]
- [powerpc] powerpc/64s/radix: Boot-time NULL pointer protection using a guard-PID (Mauricio Oliveira) [1539109]
- [block] blk-mq-debugfs: don't allow write on attributes with seq_operations set (Ming Lei) [1543463]
- [fs] dcache: Revert manually unpoison dname after allocation to shut up kasan's reports (Joe Lawrence) [1539609]
- [fs] fs/dcache: Use read_word_at_a_time() in dentry_string_cmp() (Joe Lawrence) [1539609]
- [lib] lib/strscpy: Shut up KASAN false-positives in strscpy() (Joe Lawrence) [1539609]
- [kernel] compiler.h: Add read_word_at_a_time() function (Joe Lawrence) [1539609]
- [kernel] compiler.h, kasan: Avoid duplicating __read_once_size_nocheck() (Joe Lawrence) [1539609]
- [redhat] update handling for our additional certificates ("Herton R. Krzesinski") [1539015]
- [redhat] make CONFIG_MODULE_SIG_SHA* common through all architectures ("Herton R. Krzesinski") [1539015]
- [redhat] remove extra_certificates file ("Herton R. Krzesinski") [1539015]
- [fs] xfs: truncate pagecache before writeback in xfs_setattr_size() (Bill O'Donnell) [1518553]
- [fs] autofs: revert autofs: take more care to not update last_used on path walk (Ian Kent) [1535760]

* Sat Feb 17 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-43.el7a]
- [netdrv] sfc: don't warn on successful change of MAC (Jarod Wilson) [1448760]
- [netdrv] ibmvnic: Remove skb->protocol checks in ibmvnic_xmit (Steve Best) [1544017]
- [netdrv] ibmvnic: Reset long term map ID counter (Steve Best) [1544017]
- [scsi] qla2xxx: Update driver version to 10.00.00.01.07.5a-k1 (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Fix memory corruption during hba reset test (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Fix logo flag for qlt_free_session_done() (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Fix NULL pointer crash due to probe failure (Himanshu Madhani) [1542778]
- [scsi] qla2xxx: Defer processing of GS IOCB calls (Himanshu Madhani) [1542778]
- [nvme] nvme-pci: allocate device queues storage space at probe (Ming Lei) [1523270]
- [kernel] include/linux/slab.h: add kmalloc_array_node() and kcalloc_node() (Ming Lei) [1523270]
- [nvme] nvme-pci: serialize pci resets (Ming Lei) [1523494]
- [block] blk-mq: fix race between updating nr_hw_queues and switching io sched (Ming Lei) [1523270]
- [block] blk-mq: avoid to map CPU into stale hw queue (Ming Lei) [1523270]
- [block] blk-mq: quiesce queue during switching io sched and updating nr_requests (Ming Lei) [1523270]
- [block] blk-mq: quiesce queue before freeing queue (Ming Lei) [1523270]
- [block] blk-mq: only run the hardware queue if IO is pending (Ming Lei) [1523270]
- [block] Fix a race between blk_cleanup_queue() and timeout handling (Ming Lei) [1538482]

* Fri Feb 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-42.el7a]
- [net] sched: cbq: create block for q->link.block (Davide Caratti) [1544314]
- [net] cls_u32: fix use after free in u32_destroy_key() (Paolo Abeni) [1516696]
- [net] netfilter: xt_osf: Add missing permission checks (Florian Westphal) [1539229] {CVE-2017-17448}
- [net] netfilter: nfnetlink_cthelper: Add missing permission checks (Florian Westphal) [1539229] {CVE-2017-17448}

* Mon Feb 12 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-41.el7a]
- [netdrv] ibmvnic: queue reset when CRQ gets closed during reset (Steve Best) [1543729]
- [kernel] modules: add rhelversion MODULE_INFO tag (Prarit Bhargava) [1542796]
- [kernel] put RHEL info into generated headers (Prarit Bhargava) [1542796]
- [netdrv] ibmvnic: Ensure that buffers are NULL after free (Steve Best) [1543713]
- [netdrv] ibmvnic: fix empty firmware version and errors cleanup (Steve Best) [1543713]
- [powerpc] powerpc/64s: Allow control of RFI flush via debugfs (Mauricio Oliveira) [1543083]
- [powerpc] powerpc/64s: Improve RFI L1-D cache flush fallback (Mauricio Oliveira) [1543083]
- [powerpc] powerpc/xmon: Add RFI flush related fields to paca dump (Mauricio Oliveira) [1543083]
- [powerpc] powerpc/64s: Wire up cpu_show_meltdown() (Mauricio Oliveira) [1543083]
- [base] sysfs/cpu: Add vulnerability folder (Mauricio Oliveira) [1543083]
- [scsi] aacraid: Fix udev inquiry race condition (Gustavo Duarte) [1541141]
- [scsi] aacraid: Do not attempt abort when Fw panicked (Gustavo Duarte) [1541141]
- [scsi] aacraid: Fix hang in kdump (Gustavo Duarte) [1541141]
- [scsi] aacraid: Do not remove offlined devices (Gustavo Duarte) [1541141]
- [scsi] aacraid: Fix ioctl reset hang (Gustavo Duarte) [1541141]
- [redhat] configs: enable CONFIG_USERFAULTFD on s390x (David Hildenbrand) [1540679]
- [pci] PCI/AER: Skip recovery callbacks for correctable errors from ACPI APEI (Steve Ulrich) [1495258]

* Sun Feb 11 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-40.el7a]
- [char] crash driver: fix probe_kernel_read() failure to return -EFAULT (Dave Anderson) [1533712]
- [netdrv] ibmvnic: Fix rx queue cleanup for non-fatal resets (Steve Best) [1543315]
- [scsi] libcxgbi: use GFP_ATOMIC in cxgbi_conn_alloc_pdu() (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: when flushing, complete all wrs in a chain (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: reflect the original WR opcode in drain cqes (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: Only validate the MSN for successful completions (Arjun Vynipadath) [1541086]
- [infiniband] iw_cxgb4: only insert drain cqes if wq is flushed (Arjun Vynipadath) [1541086]
- [usb] USB: core: prevent malicious bNumInterfaces overflow (Torez Smith) [1536888] {CVE-2017-17558}
- [acpi] ACPI: APEI: call into AER handling regardless of severity (Al Stone) [1403771 1288440 1268474]
- [acpi] ACPI: APEI: handle PCIe AER errors in separate function (Al Stone) [1403771 1288440 1268474]
- [i2c] xlp9xx: Check for Bus state after every transfer (Robert Richter) [1504298]
- [i2c] xlp9xx: report SMBus block read functionality (Robert Richter) [1504298]
- [i2c] xlp9xx: Handle transactions with I2C_M_RECV_LEN properly (Robert Richter) [1504298]
- [i2c] xlp9xx: return ENXIO on slave address NACK (Robert Richter) [1504298]
- [acpi] ACPI / APD: Add clock frequency for ThunderX2 I2C controller (Robert Richter) [1504298]
- [i2c] xlp9xx: Get clock frequency with clk API (Robert Richter) [1504298]
- [i2c] xlp9xx: Handle I2C_M_RECV_LEN in msg->flags (Robert Richter) [1504298]
- [pci] quirk: adding Ampere vendor id to ACS quirk list (Iyappan Subramanian) [1539204]
- [fs] disable unsupported new disk formats again (Eric Sandeen) [1514234]

* Thu Feb 08 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-39.el7a]
- [scsi] mpt3sas: fix an out of bound write (Desnes Augusto Nunes do Rosario) [1503961]
- [netdrv] ibmvnic: fix firmware version when no firmware level has been provided by the VIOS server (Steve Best) [1541322]
- [powerpc] powerpc/pseries: Add Initialization of VF Bars (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pseries/pci: Associate PEs to VFs in configure SR-IOV (Gustavo Duarte) [1539902]
- [powerpc] powerpc/eeh: Add EEH notify resume sysfs (Gustavo Duarte) [1539902]
- [powerpc] powerpc/eeh: Add EEH operations to notify resume (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pseries: Set eeh_pe of EEH_PE_VF type (Gustavo Duarte) [1539902]
- [pci] PCI/AER: Add uevents in AER and EEH error/resume (Gustavo Duarte) [1539902]
- [powerpc] powerpc/eeh: Update VF config space after EEH (Gustavo Duarte) [1539902]
- [pci] PCI/IOV: Add pci_vf_drivers_autoprobe() interface (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pseries: Add pseries SR-IOV Machine dependent calls (Gustavo Duarte) [1539902]
- [powerpc] powerpc/pci: Separate SR-IOV Calls (Gustavo Duarte) [1539902]
- [edac] EDAC, sb_edac: Don't create a second memory controller if HA1 is not present (Aristeu Rozanski) [1513814]
- [infiniband] iser-target: avoid reinitializing rdma contexts for isert commands (Jonathan Toppins) [1540435]
- [netdrv] cxgb4: fix possible deadlock (Arjun Vynipadath) [1540018]
- [fs] nfs: don't wait on commit in nfs_commit_inode() if there were no commit requests (Scott Mayhew) [1538083]
- [tools] perf help: Fix a bug during strstart() conversion (Jiri Olsa) [1513107]
- [s390] s390x, crash driver: verify RAM page with probe_kernel_read() (Dave Anderson) [1533712]
- [kernel] lockdep: Increase MAX_STACK_TRACE_ENTRIES for debug kernel (Waiman Long) [1483161]

* Mon Feb 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-38.el7a]
- [ata] fixes kernel crash while tracing ata_eh_link_autopsy event (David Milburn) [1540760]
- [powerpc] KVM: PPC: Book3S: Provide information about hardware/firmware CVE workarounds (Serhii Popovych) [1532074]
- [netdrv] ibmvnic: Wait for device response when changing MAC (Steve Best) [1540839]
- [kernel] kdump: print kdump kernel loaded status in stack dump (Lianbo Jiang) [1535756]
- [netdrv] i40e: restore promiscuous after reset (Stefan Assmann) [1517973]
- [powerpc] KVM: PPC: Book3S HV: Allow HPT and radix on the same core for POWER9 v2.2 (Sam Bobroff) [1535753]
- [powerpc] KVM: PPC: Book3S HV: Do SLB load/unload with guest LPCR value loaded (Sam Bobroff) [1535753]
- [powerpc] KVM: PPC: Book3S HV: Make sure we don't re-enter guest without XIVE loaded (Sam Bobroff) [1535753]
- [sound] ALSA: seq: Make ioctls race-free (CVE-2018-1000004) (Jaroslav Kysela) [1537204] {CVE-2018-1000004}

* Thu Feb 01 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-37.el7a]
- [md] dm mpath: remove annoying message of 'blk_get_request() returned -11' (Gustavo Duarte) [1539251]
- [net] kernel: Missing namespace check in net/netlink/af_netlink.c allows for network monitors to observe systemwide activity (William Townsend) [1538736] {CVE-2017-17449}
- [s390] KVM: s390: wire up bpb feature (David Hildenbrand) [1539637]
- [iommu] iommu/arm-smmu-v3: Cope with duplicated Stream IDs (Robert Richter) [1529518]
- [mm] mm/mprotect: add a cond_resched() inside change_pmd_range() (Desnes Augusto Nunes do Rosario) [1535916]
- [s390] s390/mm: fix off-by-one bug in 5-level page table handling (Oleg Nesterov) [1517792]

* Wed Jan 31 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-36.el7a]
- [powerpc] Don't preempt_disable() in show_cpuinfo() (Gustavo Duarte) [1517679]
- [powerpc] powerpc/powernv/cpufreq: Fix the frequency read by /proc/cpuinfo (Gustavo Duarte) [1517679]
- [drm] drm/ttm: add ttm_bo_io_mem_pfn to check io_mem_pfn (Zhou Wang) [1502558]

* Tue Jan 30 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-35.el7a]
- [powerpc] powerpc/mm: Invalidate subpage_prot() system call on radix platforms (Steve Best) [1538328]
- [arm64] Turn on KPTI only on CPUs that need it (Vadim Lomovtsev) [1537982]
- [arm64] Branch predictor hardening for Cavium ThunderX2 (Vadim Lomovtsev) [1537982]
- [arm64] cputype: Add MIDR values for Cavium ThunderX2 CPUs (Vadim Lomovtsev) [1537982]
- [redhat] use recently created brew target for rhel-alt kernel signing ("Herton R. Krzesinski") [1492103]
- [virt] KVM: arm/arm64: kvm_arch_destroy_vm cleanups (Auger Eric) [1536027]
- [virt] KVM: arm/arm64: vgic: Move kvm_vgic_destroy call around (Auger Eric) [1536027]
- [arm64] KVM: Fix SMCCC handling of unimplemented SMC/HVC calls (Auger Eric) [1536027]
- [virt] KVM: arm64: Fix GICv4 init when called from vgic_its_create (Auger Eric) [1536027]
- [virt] KVM: arm/arm64: Check pagesize when allocating a hugepage at Stage 2 (Auger Eric) [1536027]
- [scsi] mpt3sas: Bump driver version (Julius Milan) [1524723]
- [scsi] mpt3sas: Reduce memory footprint in kdump kernel (Julius Milan) [1524723]
- [scsi] mpt3sas: Fixed memory leaks in driver (Julius Milan) [1524723]
- [scsi] mpt3sas: remove redundant copy_from_user in _ctl_getiocinfo (Julius Milan) [1524723]

* Mon Jan 29 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-34.el7a]
- [netdrv] ibmvnic: Allocate and request vpd in init_resources (Steve Best) [1537431]
- [netdrv] ibmvnic: Revert to previous mtu when unsupported value requested (Steve Best) [1537431]
- [netdrv] ibmvnic: Modify buffer size and number of queues on failover (Steve Best) [1537431]
- [misc] cxl: Add support for ASB_Notify on POWER9 (Steve Best) [1537750]
- [cpuidle] powerpc/pseries/cpuidle: add polling idle for shared processor guests (Steve Best) [1538249]
- [scsi] lpfc: Removing bad lockdep_assert patch (Dick Kennedy) [1482600 1420592 1392037]
- [powerpc] powerpc/spinlock: add gmb memory barrier (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/powernv: Check device-tree for RFI flush settings (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/pseries: Query hypervisor for RFI flush settings (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Support disabling RFI flush with no_rfi_flush and nopti (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Add support for RFI flush of L1-D cache (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Convert slb_miss_common to use RFI_TO_USER/KERNEL (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64: Convert fast_exception_return to use RFI_TO_USER/KERNEL (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64: Convert the syscall exit path to use RFI_TO_USER/KERNEL (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64s: Simple RFI macro conversions (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/64: Add macros for annotating the destination of rfid/hrfid (Mauricio Oliveira) [1531718]
- [powerpc] powerpc/pseries: Add H_GET_CPU_CHARACTERISTICS flags & wrapper (Mauricio Oliveira) [1531718]
- [arm64] mm: Fix pte_mkclean, pte_mkdirty semantics (Steve Ulrich) [1512366]

* Fri Jan 26 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-33.el7a]
- [netdrv] ibmvnic: Fix IPv6 packet descriptors (Steve Best) [1536745]
- [netdrv] ibmvnic: Fix IP offload control buffer (Steve Best) [1536745]
- [misc] cxl: Rework the implementation of cxl_stop_trace_psl9() (Steve Best) [1534499]
- [infiniband] IB/core: Verify that QP is security enabled in create and destroy (Kamal Heib) [1533578]
- [net] Bluetooth: Prevent stack info leak from the EFS element (Gopal Tiwari) [1519629] {CVE-2017-1000410}
- [infiniband] IB/mlx5: Fix mlx5_ib_alloc_mr error flow (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Serialize access to the VMA list (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Fix congestion counters in LAG mode (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Stay in polling mode when command EQ destroy fails (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Cleanup IRQs in case of unload failure (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Fix error flow in CREATE_QP command (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Fix RoCE Address Path fields (Kamal Heib) [1536454]
- [infiniband] IB/mlx5: Assign send CQ and recv CQ of UMR QP (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Avoid NULL pointer dereference on steering cleanup (Kamal Heib) [1536454]
- [netdrv] net/mlx5: Fix creating a new FTE when an existing but full FTE exists (Kamal Heib) [1536454]
- [netdrv] net/mlx5e: Prevent possible races in VXLAN control flow (Kamal Heib) [1535618]
- [netdrv] net/mlx5e: Add refcount to VXLAN structure (Kamal Heib) [1535618]
- [netdrv] net/mlx5e: Fix possible deadlock of VXLAN lock (Kamal Heib) [1535618]
- [netdrv] net/mlx5e: Fix ETS BW check (Kamal Heib) [1535594]
- [powerpc] powernv/kdump: Fix cases where the kdump kernel can get HMI's (Gustavo Duarte) [1521103]
- [powerpc] powerpc/crash: Remove the test for cpu_online in the IPI callback (Gustavo Duarte) [1521103]
- [fs] autofs: revert fix AT_NO_AUTOMOUNT not being honored (Justin Mitchell) [1517279]

* Wed Jan 24 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-32.el7a]
- [scsi] lpfc: fix kzalloc-simple.cocci warnings (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix hard lock up NMI in els timeout handling (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix a precedence bug in lpfc_nvme_io_cmd_wqe_cmpl() (Dick Kennedy) [1396074]
- [scsi] lpfc: change version to 11.4.0.4 (Dick Kennedy) [1396074]
- [scsi] lpfc: correct nvme sg segment count check (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix oops of nvme host during driver unload (Dick Kennedy) [1396074]
- [scsi] lpfc: Extend RDP support (Dick Kennedy) [1396074]
- [scsi] lpfc: Ensure io aborts interlocked with the target (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix secure firmware updates (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix crash in lpfc_nvme_fcp_io_submit during LIP (Dick Kennedy) [1396074]
- [scsi] lpfc: Disable NPIV support if NVME is enabled (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix oops if nvmet_fc_register_targetport fails (Dick Kennedy) [1396074]
- [scsi] lpfc: Revise NVME module parameter descriptions for better clarity (Dick Kennedy) [1396074]
- [scsi] lpfc: Set missing abort context (Dick Kennedy) [1396074]
- [scsi] lpfc: Reduce log spew on controller reconnects (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix FCP hba_wqidx assignment (Dick Kennedy) [1396074]
- [scsi] lpfc: Move CQ processing to a soft IRQ (Dick Kennedy) [1396074]
- [scsi] lpfc: Make ktime sampling more accurate (Dick Kennedy) [1396074]
- [scsi] lpfc: PLOGI failures during NPIV testing (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix warning messages when NVME_TARGET_FC not defined (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix lpfc nvme host rejecting IO with Not Ready message (Dick Kennedy) [1396074]
- [scsi] lpfc: Fix crash receiving ELS while detaching driver (Dick Kennedy) [1396074]
- [scsi] lpfc: fix pci hot plug crash in list_add call (Dick Kennedy) [1396074]
- [scsi] lpfc: fix pci hot plug crash in timer management routines (Dick Kennedy) [1396074]
- [scsi] lpfc: Cocci spatch pool_zalloc-simple (Dick Kennedy) [1396074]
- [scsi] lpfc: remove redundant null check on eqe (Dick Kennedy) [1396074]

* Wed Jan 24 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-31.el7a]
- [fs] udf: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [fs] vfs, fdtable: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [net] ipv4: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [net] ipv6: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [thermal] Thermal/int340x: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [wireless] cw1200: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [scsi] qla2xxx: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [wireless] p54: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [wireless] carl9170: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [usb] uvcvideo: prevent bounds-check bypass via speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [kernel] userns: prevent speculative execution (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [arm64] implement nospec_ptr() (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [documentation] document nospec helpers (Josh Poimboeuf) [1527436] {CVE-2017-5753}
- [kernel] asm-generic/barrier: add generic nospec helpers (Josh Poimboeuf) [1527436] {CVE-2017-5753}

* Tue Jan 23 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-30.el7a]
- [arm64] Implement branch predictor hardening for Falkor (Mark Langsdorf) [1532118]
- [arm64] Implement branch predictor hardening for affected Cortex-A CPUs (Mark Langsdorf) [1532118]
- [arm64] cputype: Add missing MIDR values for Cortex-A72 and Cortex-A75 (Mark Langsdorf) [1532118]
- [arm64] KVM: Make PSCI_VERSION a fast path (Mark Langsdorf) [1532118]
- [arm64] KVM: Use per-CPU vector when BP hardening is enabled (Mark Langsdorf) [1532118]
- [arm64] Add skeleton to harden the branch predictor against aliasing attacks (Mark Langsdorf) [1532118]
- [arm64] Move post_ttbr_update_workaround to C code (Mark Langsdorf) [1532118]
- [firmware] drivers/firmware: Expose psci_get_version through psci_ops structure (Mark Langsdorf) [1532118]
- [arm64] cpufeature: Pass capability structure to ->enable callback (Mark Langsdorf) [1532118]
- [arm64] Take into account ID_AA64PFR0_EL1.CSV3 (Mark Langsdorf) [1532118]
- [arm64] Kconfig: Reword UNMAP_KERNEL_AT_EL0 kconfig entry (Mark Langsdorf) [1532118]
- [arm64] use RET instruction for exiting the trampoline (Mark Langsdorf) [1532118]
- [arm64] entry.S: convert elX_irq (Mark Langsdorf) [1532118]
- [arm64] entry.S convert el0_sync (Mark Langsdorf) [1532118]
- [arm64] entry.S: convert el1_sync (Mark Langsdorf) [1532118]
- [arm64] entry.S: Remove disable_dbg (Mark Langsdorf) [1532118]
- [arm64] Mask all exceptions during kernel_exit (Mark Langsdorf) [1532118]
- [arm64] Move the async/fiq helpers to explicitly set process context flags (Mark Langsdorf) [1532118]
- [arm64] introduce an order for exceptions (Mark Langsdorf) [1532118]
- [arm64] explicitly mask all exceptions (Mark Langsdorf) [1532118]

* Mon Jan 22 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-29.el7a]
- [misc] cxl: Provide debugfs access to PSL_DEBUG/XSL_DEBUG registers (Steve Best) [1534500]
- [cpufreq] powernv-cpufreq: Treat pstates as opaque 8-bit values (Steve Best) [1534472]
- [cpufreq] powernv-cpufreq: Fix pstate_to_idx() to handle non-continguous pstates (Steve Best) [1534472]
- [cpufreq] powernv-cpufreq: Add helper to extract pstate from PMSR (Steve Best) [1534472]
- [net] openvswitch: Fix pop_vlan action for double tagged frames (Eric Garver) [1532639]
- [net] xfrm: Fix stack-out-of-bounds read on socket policy lookup. (Florian Westphal) [1513059]
- [net] xfrm: Forbid state updates from changing encap type (Florian Westphal) [1513059]
- [net] xfrm: Fix stack-out-of-bounds with misconfigured transport mode policies. (Florian Westphal) [1513059]
- [net] xfrm: skip policies marked as dead while rehashing (Florian Westphal) [1513059]
- [net] revert "xfrm: Fix stack-out-of-bounds read in xfrm_state_find." (Florian Westphal) [1513059]
- [net] xfrm: put policies when reusing pcpu xdst entry (Florian Westphal) [1513059]
- [net] xfrm: Copy policy family in clone_policy (Florian Westphal) [1513059]
- [net] netfilter: uapi: correct UNTRACKED conntrack state bit number (Florian Westphal) [1530258]
- [net] netfilter: ip6t_MASQUERADE: add dependency on conntrack module (Florian Westphal) [1527250]
- [net] ipv4: fib: Fix metrics match when deleting a route (Phil Sutter) [1527591]
- [net] ipv4: fix for a race condition in raw_sendmsg (Stefano Brivio) [1527027] {CVE-2017-17712}
- [net] ipv6: remove from fib tree aged out RTF_CACHE dst (Paolo Abeni) [1524275]
- [net] vxlan: fix the issue that neigh proxy blocks all icmpv6 packets (Lorenzo Bianconi) [1523020]
- [net] sched: fix use-after-free in tcf_block_put_ext (Paolo Abeni) [1518144]
- [net] net_sched: get rid of rcu_barrier() in tcf_block_put_ext() (Paolo Abeni) [1518144]
- [net] net_sched: no need to free qdisc in RCU callback (Paolo Abeni) [1518144]
- [net] sched: crash on blocks with goto chain action (Paolo Abeni) [1518144]
- [net] ipv6: set all.accept_dad to 0 by default (Florian Westphal) [1516744]

* Mon Jan 22 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-28.el7a]
- [misc] cxl: Dump PSL_FIR register on PSL9 error irq (Steve Best) [1534493]
- [misc] cxl: Rename register PSL9_FIR2 to PSL9_FIR_MASK (Steve Best) [1534493]
- [crypto] crypto/nx: Do not initialize workmem allocation (Gustavo Duarte) [1534949]
- [crypto] crypto/nx: Use percpu send window for NX requests (Gustavo Duarte) [1534949]
- [fs] debugfs: fix debugfs_real_fops() build error (Gustavo Duarte) [1533827]
- [fs] debugfs: defer debugfs_fsdata allocation to first usage (Gustavo Duarte) [1533827]
- [fs] debugfs: call debugfs_real_fops() only after debugfs_file_get() (Gustavo Duarte) [1533827]
- [fs] debugfs: purge obsolete SRCU based removal protection (Gustavo Duarte) [1533827]
- [infiniband] IB/hfi1: convert to debugfs_file_get() and -put() (Gustavo Duarte) [1533827]
- [fs] debugfs: convert to debugfs_file_get() and -put() (Gustavo Duarte) [1533827]
- [fs] debugfs: debugfs_real_fops(): drop __must_hold sparse annotation (Gustavo Duarte) [1533827]
- [fs] debugfs: implement per-file removal protection (Gustavo Duarte) [1533827]
- [fs] debugfs: add support for more elaborate ->d_fsdata (Gustavo Duarte) [1533827]
- [netdrv] cxgb4vf: Fix SGE FL buffer initialization logic for 64K pages (Arjun Vynipadath) [1533344]
- [redhat] spec: Add new arch/powerpc/kernel/module.lds file to kernel-devel rpm (Desnes Augusto Nunes do Rosario) [1466697]
- [powerpc] powerpc/modules: Fix alignment of .toc section in kernel modules (Desnes Augusto Nunes do Rosario) [1466697]

* Fri Jan 19 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-27.el7a]
- [acpi] ACPI / APEI: Remove arch_apei_flush_tlb_one() (Prarit Bhargava) [1513713]
- [arm64] mm: Remove arch_apei_flush_tlb_one() (Prarit Bhargava) [1513713]
- [acpi] ACPI / APEI: Remove ghes_ioremap_area (Prarit Bhargava) [1513713]
- [acpi] ACPI / APEI: Replace ioremap_page_range() with fixmap (Prarit Bhargava) [1513713]
- [misc] cxl: Add support for POWER9 DD2 (Steve Best) [1534959]
- [netdrv] ibmvnic: Fix pending MAC address changes (Steve Best) [1535360]
- [cpufreq] powernv: Dont assume distinct pstate values for nominal and pmin (Steve Best) [1534464]
- [netdrv] net: hns: add ACPI mode support for ethtool -p (Zhou Wang) [1530124]

* Thu Jan 18 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-26.el7a]
- [drm] uapi: fix linux/kfd_ioctl.h userspace compilation errors (Yaakov Selkowitz) [1510150]
- [net] uapi: fix linux/tls.h userspace compilation error (Yaakov Selkowitz) [1510150]
- [net] uapi: fix linux/rxrpc.h userspace compilation errors (Yaakov Selkowitz) [1510150]

* Tue Jan 16 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-25.el7a]
- [netdrv] ibmvnic: Don't handle RX interrupts when not up (Steve Best) [1532344]
- [redhat] configs: enable SELinux Infiniband access controls (Jonathan Toppins) [1524484]
- [infiniband] IB/mlx4: Fix RSS hash fields restrictions (Jonathan Toppins) [1524484]
- [infiniband] RDMA/netlink: Fix general protection fault (Jonathan Toppins) [1524484]
- [infiniband] IB/core: Bound check alternate path port number (Jonathan Toppins) [1524484]
- [infiniband] IB/core: Don't enforce PKey security on SMI MADs (Jonathan Toppins) [1524484]
- [infiniband] IB/core: Fix use workqueue without WQ_MEM_RECLAIM (Jonathan Toppins) [1524491]
- [infiniband] IB/core: Avoid crash on pkey enforcement failed in received MADs (Jonathan Toppins) [1524491]
- [infiniband] IB/srp: Avoid that a cable pull can trigger a kernel crash (Jonathan Toppins) [1524491]
- [infiniband] IB/cm: Fix memory corruption in handling CM request (Jonathan Toppins) [1524491]
- [infiniband] IB/srpt: Do not accept invalid initiator port names (Jonathan Toppins) [1524491]
- [infiniband] IB/core: Only enforce security for InfiniBand (Jonathan Toppins) [1523309]
- [infiniband] IB/core: Only maintain real QPs in the security lists (Jonathan Toppins) [1523309]
- [infiniband] IB/core: Avoid unnecessary return value check (Jonathan Toppins) [1523309]
- [misc] genwqe: Take R/W permissions into account when dealing with memory pages (Steve Best) [1528751]
- [arm64] Enable Qualcomm erratum 1041 workaround (Steve Ulrich) [1511024]
- [arm64] Add software workaround for Falkor erratum 1041 (Steve Ulrich) [1511024]
- [arm64] Define cputype macros for Falkor CPU (Steve Ulrich) [1511024]

* Mon Jan 15 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-24.el7a]
- [powerpc] KVM: PPC: Book3S HV: Always flush TLB in kvmppc_alloc_reset_hpt() (David Gibson) [1533315]
- [powerpc] pseries: Make RAS IRQ explicitly dependent on DLPAR WQ (David Gibson) [1517598]
- [tools] cpupower: Fix no-rounding MHz frequency output (Prarit Bhargava) [1503286]
- [x86] perf/x86/intel: Hide TSX events when RTM is not supported (Jiri Olsa) [1510552]
- [tools] perf test: Disable test cases 19 and 20 on s390x (Jiri Olsa) [1432652]
- [infiniband] iw_cxgb4: only clear the ARMED bit if a notification is needed (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: atomically flush the qp (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: only call the cq comp_handler when the cq is armed (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: Fix possible circular dependency locking warning (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: remove BUG_ON() usage (Arjun Vynipadath) [1458305]
- [infiniband] RDMA/cxgb4: Protect from possible dereference (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: add referencing to wait objects (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each ep object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each qp object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each cq object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: allocate wait object for each memory object (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: change pr_debug to appropriate log level (Arjun Vynipadath) [1458305]
- [infiniband] iw_cxgb4: Remove __func__ parameter from pr_debug() (Arjun Vynipadath) [1458305]
- [mm] kernel: mm/pagewalk.c: walk_hugetlb_range function mishandles holes in hugetlb ranges causing information leak (Chris von Recklinghausen) [1520395] {CVE-2017-16994}
- [redhat] Disable CONFIG_RC_CORE for s390x and aarch64 ("Herton R. Krzesinski") [1516037]

* Thu Jan 11 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-23.el7a]
- [s390] KVM: s390: Fix skey emulation permission check (Thomas Huth) [1530594]
- [scsi] core: check for device state in __scsi_remove_target() (Ewan Milne) [1513029]
- [virtio] virtio_mmio: fix devm cleanup (Andrew Jones) [1529279]
- [virtio] ptr_ring: add barriers (Andrew Jones) [1529279]
- [tools] virtio: ptr_ring: fix up after recent ptr_ring changes (Andrew Jones) [1529279]
- [netdrv] virtio_net: fix return value check in receive_mergeable() (Andrew Jones) [1529279]
- [virtio] virtio_mmio: add cleanup for virtio_mmio_remove (Andrew Jones) [1529279]
- [virtio] virtio_mmio: add cleanup for virtio_mmio_probe (Andrew Jones) [1529279]
- [netdrv] tap: free skb if flags error (Andrew Jones) [1529279]
- [netdrv] tun: free skb in early errors (Andrew Jones) [1529279]
- [vhost] net: fix skb leak in handle_rx() (Andrew Jones) [1529279]
- [virtio] virtio: release virtio index when fail to device_register (Andrew Jones) [1529279]
- [nvme] call blk_integrity_unregister after queue is cleaned up (Ming Lei) [1521000]
- [redhat] configs: Disable CONFIG_CMA and CONFIG_DMA_CMA support for RHEL archs (Bhupesh Sharma) [1519317]
- [redhat] configs: disable bnx2* storage offload drivers on aarch64 (Michal Schmidt) [1500020]
- [redhat] configs: Enable Qualcomm L2&L3 PMU drivers (Steve Ulrich) [1268469]
- [perf] qcom_l2_pmu: add event names (Steve Ulrich) [1268469]
- [i2c] xgene-slimpro: Support v2 (Iyappan Subramanian) [1524732]
- [hwmon] xgene: Minor clean up of ifdef and acpi_match_table reference (Iyappan Subramanian) [1524732]
- [hwmon] xgene: Support hwmon v2 (Iyappan Subramanian) [1524732]
- [net] Fix double free and memory corruption in get_net_ns_by_id() (Aristeu Rozanski) [1531553] {CVE-2017-15129}

* Tue Jan 09 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-22.el7a]
- [arm64] kaslr: Put kernel vectors address in separate data page (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Introduce TTBR_ASID_MASK for getting at the ASID in the TTBR (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] Kconfig: Add CONFIG_UNMAP_KERNEL_AT_EL0 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Add fake CPU feature for unmapping the kernel at EL0 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] tls: Avoid unconditional zeroing of tpidrro_el0 for native tasks (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] erratum: Work around Falkor erratum #E1003 in trampoline code (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Hook up entry trampoline to exception vectors (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Explicitly pass exception level to kernel_ventry macro (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Map entry trampoline into trampoline and kernel page tables (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] entry: Add exception trampoline page for exceptions from EL0 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Invalidate both kernel and user ASIDs when performing TLBI (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Add arm64_kernel_unmapped_at_el0 helper (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Allocate ASIDs in pairs (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Fix and re-enable ARM64_SW_TTBR0_PAN (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Rename post_ttbr0_update_workaround (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Remove pre_ttbr0_update_workaround for Falkor erratum #E1003 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Move ASID from TTBR0 to TTBR1 (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Temporarily disable ARM64_SW_TTBR0_PAN (Mark Salter) [1531357] {CVE-2017-5754}
- [arm64] mm: Use non-global mappings for kernel space (Mark Salter) [1531357] {CVE-2017-5754}

* Mon Jan 08 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-21.el7a]
- [netdrv] bnx2x: Improve reliability in case of nested PCI errors (Steve Best) [1529861]
- [netdrv] tg3: Fix rx hang on MTU change with 5717/5719 (Mauricio Oliveira) [1526319]
- [target] cxgbit: Abort the TCP connection in case of data out timeout (Arjun Vynipadath) [1458313]
- [scsi] csiostor: enable PCIe relaxed ordering if supported (Arjun Vynipadath) [1458319]
- [crypto] chcr: Replace _manual_ swap with swap macro (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Fix memory leak (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Move DMA un/mapping to chcr from lld cxgb4 driver (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Remove allocation of sg list to implement 2K limit of dsgl header (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Use x8_ble gf multiplication to calculate IV (Arjun Vynipadath) [1458316]
- [crypto] gf128mul: The x8_ble multiplication functions (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Check error code with IS_ERR macro (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Remove unused parameter (Arjun Vynipadath) [1458316]
- [crypto] chelsio: pr_err() strings should end with newlines (Arjun Vynipadath) [1458316]
- [crypto] chelsio: Use GCM IV size constant (Arjun Vynipadath) [1458316]
- [crypto] gcm: add GCM IV size constant (Arjun Vynipadath) [1458316]
- [scsi] libcxgbi: simplify task->hdr allocation for mgmt cmds (Arjun Vynipadath) [1458308]
- [scsi] cxgb4i: fix Tx skb leak (Arjun Vynipadath) [1458308]
- [scsi] libcxgbi: in case of vlan pass 0 as ifindex to find route (Arjun Vynipadath) [1458308]
- [scsi] libcxgbi: remove redundant check and close on csk (Arjun Vynipadath) [1458308]

* Fri Jan 05 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-20.el7a]
- [netdrv] igb: Use smp_rmb rather than read_barrier_depends (Steve Best) [1531097]
- [netdrv] ibmvnic: Include header descriptor support for ARP packets (Steve Best) [1529747]
- [netdrv] ibmvnic: Increase maximum number of RX/TX queues (Steve Best) [1529747]
- [netdrv] ibmvnic: Rename IBMVNIC_MAX_TX_QUEUES to IBMVNIC_MAX_QUEUES (Steve Best) [1529747]
- [powerpc] KVM: PPC: Book3S HV: Fix pending_pri value in kvmppc_xive_get_icp() (Laurent Vivier) [1524884]
- [powerpc] KVM: PPC: Book3S: fix XIVE migration of pending interrupts (Laurent Vivier) [1493453]
- [fs] cifs: fix NULL deref in SMB2_read (Leif Sahlberg) [1524797]
- [powerpc] perf: Dereference BHRB entries safely (Steve Best) [1525101]
- [tools] perf tests attr: Fix group stat tests (Jiri Olsa) [1518232]
- [tools] perf test attr: Fix ignored test case result (Jiri Olsa) [1518232]
- [tools] perf test attr: Fix python error on empty result (Jiri Olsa) [1518232]
- [tools] perf tests attr: Make hw events optional (Jiri Olsa) [1518232]
- [tools] perf tests attr: Fix task term values (Jiri Olsa) [1518232]
- [powerpc] kvm: ppc: book3s hv: Don't call real-mode XICS hypercall handlers if not enabled (Laurent Vivier) [1524664]
- [tools] perf vendor events: Use more flexible pattern matching for CPU identification for mapfile.csv (Jiri Olsa) [1513805]
- [tools] perf pmu: Extract function to get JSON alias map (Jiri Olsa) [1513805]
- [tools] perf pmu: Add helper function is_pmu_core to detect PMU CORE devices (Jiri Olsa) [1513805]

* Thu Jan 04 2018 Herton R. Krzesinski <herton@redhat.com> [4.14.0-19.el7a]
- [redhat] RHMAINTAINERS: Cleanup tabs/spaces (Jeremy Linton)
- [redhat] RHMAINTAINERS: claim orphan sky2 (Jeremy Linton)
- [redhat] RHMAINTAINERS: arch/arm64 is supported (Jeremy Linton)
- [redhat] RHMAINTAINERS: add ARM device IP drivers (Jeremy Linton)
- [powerpc] powerpc/64s/slice: Use addr limit when computing slice mask (Steve Best) [1523265]
- [powerpc] powerpc/64s: mm_context.addr_limit is only used on hash (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Allow MAP_FIXED allocations to cross 128TB boundary (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Fix 128TB-512TB virtual address boundary case allocation (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Fix fork() with 512TB process address space (Steve Best) [1523265]
- [powerpc] powerpc/64s/radix: Fix 128TB-512TB virtual address boundary case allocation (Steve Best) [1523265]
- [powerpc] powerpc/64s/hash: Fix 512T hint detection to use >= 128T (Steve Best) [1523265]

* Fri Dec 08 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-18.el7a]
- [powerpc] powerpc/64s: Initialize ISAv3 MMU registers before setting partition table (Steve Best) [1523226]
- [powerpc] KVM: PPC: Book3S HV: Fix use after free in case of multiple resize requests (Serhii Popovych) [1519046]
- [powerpc] KVM: PPC: Book3S HV: Drop prepare_done from struct kvm_resize_hpt (Serhii Popovych) [1519046]
- [netdrv] net: thunderx: Fix TCP/UDP checksum offload for IPv4 pkts (Florian Westphal) [1518375]
- [netdrv] cxgb4vf: define get_fecparam ethtool callback (Arjun Vynipadath) [1458300]
- [netdrv] cxgb4vf: make a couple of functions static (Arjun Vynipadath) [1458300]
- [virt] KVM: arm/arm64: vgic-v4: Only perform an unmap for valid vLPIs (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic-its: Check result of allocation before use (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic-its: Preserve the revious read from the pending table (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic: Preserve the revious read from the pending table (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: vgic-irqfd: Fix MSI entry allocation (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: VGIC: extend !vgic_is_initialized guard (Auger Eric) [1522852]
- [virt] KVM: arm/arm64: Don't queue VLPIs on INV/INVALL (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: Fix GICv4 ITS initialization issues (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Theory of operations (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Enable VLPI support (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Prevent userspace from changing doorbell affinity (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Prevent a VM using GICv4 from being saved (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Enable virtual cpuif if VLPIs can be delivered (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Hook vPE scheduling into vgic flush/sync (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Use the doorbell interrupt as an unblocking source (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Add doorbell interrupt handling (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Use pending_last as a scheduling hint (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle INVALL applied to a vPE (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Propagate property updates to VLPIs (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle MOVALL applied to a vPE (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle CLEAR applied to a VLPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Propagate affinity changes to the physical ITS (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Unmap VLPI when freeing an LPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Handle INT command applied to a VLPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Wire mapping/unmapping of VLPIs in VFIO irq bypass (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Add init/teardown of the per-VM vPE irq domain (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: GICv4: Add property field and per-VM predicate (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: vITS: Add a helper to update the affinity of an LPI (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: vITS: Add MSI translation helpers (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Fix VPE activate callback return value (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: vgic: restructure kvm_vgic_(un)map_phys_irq (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: register irq bypass consumer on ARM/ARM64 (Auger Eric) [1386368]
- [irqchip] KVM: arm/arm64: Check that system supports split eoi/deactivate (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: Support calling vgic_update_irq_pending from irq context (Auger Eric) [1386368]
- [virt] KVM: arm/arm64: Guard kvm_vgic_map_is_active against !vgic_initialized (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3: pr_err() strings should end with newlines (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3: Fix ppi-partitions lookup (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v4: Clear IRQ_DISABLE_UNLAZY again if mapping fails (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Setup VLPI properties at map time (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Update effective affinity on VPE mapping (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Only send VINVALL to a single ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Limit scope of VPE mapping to be per ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Make its_send_vmapp operate on a single ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Make its_send_vinvall operate on a single ITS (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Make GICv4_ITS_LIST_MAX globally available (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Track per-ITS list number (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Pass its_node pointer to each command builder (Auger Eric) [1386368]
- [irqchip] irqchip/gic-v3-its: Add post-mortem info on command timeout (Auger Eric) [1386368]
- [irqchip] irqchip/gic: Make quirks matching conditional on init return value (Auger Eric) [1386368]
- [kernel] genirq/irqdomain: Update irq_domain_ops.activate() signature (Auger Eric) [1386368]
- [net] openvswitch: datapath: fix data type in queue_gso_packets (Davide Caratti) [1519190]
- [net] accept UFO datagrams from tuntap and packet (Davide Caratti) [1519190]
- [net] Remove unused skb_shared_info member (Davide Caratti) [1519190]
- [redhat] configs: Enable CONFIG_VIRTIO_BLK_SCSI (Fam Zheng) [1487183]

* Fri Dec 08 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-17.el7a]
- [mm] kernel: pmd can become dirty without going through a COW cycle (Chris von Recklinghausen) [1518612] {CVE-2017-1000405}
- [powerpc] powerpc/perf: Fix oops when grouping different pmu events (Steve Best) [1520838]
- [net] sctp: use right member as the param of list_for_each_entry (Xin Long) [1520264]
- [netdrv] cxgb4: add new T6 pci device id's (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: add new T5 pci device id's (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: add new T6 pci device id's (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: do DCB state reset in couple of places (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: avoid stall while shutting down the adapter (Arjun Vynipadath) [1458297]
- [netdrv] cxgb4: add new T5 pci device id's (Arjun Vynipadath) [1458297]
- [powerpc] Revert powerpc: Do not call ppc_md.panic in fadump panic notifier (David Gibson) [1513858]
- [arm64] KVM: fix VTTBR_BADDR_MASK BUG_ON off-by-one (Andrew Jones) [1520938]
- [firmware] Revert efi/arm: Don't mark ACPI reclaim memory as MEMBLOCK_NOMAP (Bhupesh Sharma) [1512379]
- [gpio] dwapb: Add wakeup source support (Iyappan Subramanian) [1497813]
- [redhat] configs: zram, ppc64: enable zram on ppc64 (Jerome Marchand) [1499197]
- [redhat] configs: Enable MMC DesignWare (Slava Shwartsman) [1477045]

* Thu Dec 07 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-16.el7a]
- [powerpc] Do not assign thread.tidr if already assigned (Gustavo Duarte) [1320916]
- [powerpc] Avoid signed to unsigned conversion in set_thread_tidr() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Export chip_to_vas_id() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Add support for user receive window (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Define vas_win_id() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Define vas_win_paste_addr() (Gustavo Duarte) [1320916]
- [powerpc] Define set_thread_uses_vas() (Gustavo Duarte) [1320916]
- [powerpc] Add support for setting SPRN_TIDR (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Export HVWC to debugfs (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas, nx-842: Define and use chip_to_vas_id() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Create cpu to vas id mapping (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: poll for return of window credits (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Save configured window credits (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Reduce polling interval for busy state (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Use helper to unpin/close window (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Drop poll_window_cast_out() (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Cleanup some debug code (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: Validate window credits (Gustavo Duarte) [1320916]
- [powerpc] powerpc/vas: init missing fields from rxattr/txattr (Gustavo Duarte) [1320916]
- [vfio] vfio/type1: silence integer overflow warning (Auger Eric) [1515981]
- [vfio] vfio/pci: Virtualize Maximum Read Request Size (Auger Eric) [1515981]
- [kernel] sysctl: check for UINT_MAX before unsigned int min/max (Joe Lawrence) [1499478]
- [fs] pipe: add proc_dopipe_max_size() to safely assign pipe_max_size (Joe Lawrence) [1499478]
- [fs] pipe: avoid round_pipe_size() nr_pages overflow on 32-bit (Joe Lawrence) [1499478]
- [fs] pipe: match pipe_max_size data type with procfs (Joe Lawrence) [1499478]
- [iommu] iommu/iova: Make rcache flush optional on IOVA allocation failure (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Don't try to copy anchor nodes (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Try harder to allocate from rcache magazine (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Make rcache limit_pfn handling more robust (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Simplify domain destruction (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Simplify cached node logic (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Add rbtree anchor node (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Make dma_32bit_pfn implicit (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Extend rbtree node caching (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Optimise the padding calculation (Steve Ulrich) [1514191]
- [iommu] iommu/iova: Optimise rbtree searching (Steve Ulrich) [1514191]
- [powerpc] powerpc/kexec: Fix kexec/kdump in P9 guest kernels (David Gibson) [1513905]
- [powerpc] KVM: PPC: Book3S HV: Fix migration and HPT resizing of HPT guests on radix hosts (Suraj Jitindar Singh) [1517052]

* Tue Dec 05 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-15.el7a]
- [virtio] virtio_balloon: fix increment of vb->num_pfns in fill_balloon() (Andrew Jones) [1516486]
- [redhat] RHMAINTAINERS: add vfio sections (Andrew Jones)
- [redhat] RHMAINTAINERS: update virtio sections (Andrew Jones)
- [redhat] RHMAINTAINERS: update KVM sections (Andrew Jones)
- [net] ip6_tunnel: clean up ip4ip6 and ip6ip6's err_handlers (Xin Long) [1510242]
- [net] ip6_tunnel: process toobig in a better way (Xin Long) [1510242]
- [net] ip6_tunnel: add the process for redirect in ip6_tnl_err (Xin Long) [1510242]
- [net] ip6_gre: process toobig in a better way (Xin Long) [1509915]
- [net] ip6_gre: add the process for redirect in ip6gre_err (Xin Long) [1509915]
- [net] route: also update fnhe_genid when updating a route cache (Xin Long) [1509098]
- [net] route: update fnhe_expires for redirect when the fnhe exists (Xin Long) [1509098]
- [net] ip_gre: add the support for i/o_flags update via ioctl (Xin Long) [1489338]
- [net] ip_gre: add the support for i/o_flags update via netlink (Xin Long) [1489338]

* Tue Dec 05 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-14.el7a]
- [block] drain queue before waiting for q_usage_counter becoming zero (Ming Lei) [1513036]
- [block] wake up all tasks blocked in get_request() (Ming Lei) [1513036]
- [block] Make q_usage_counter also track legacy requests (Ming Lei) [1513036]

* Tue Dec 05 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-13.el7a]
- [redhat] configs: disable ATA on s390x ("Herton R. Krzesinski") [1514589]
- [iommu] Print a message with the default domain type created (Al Stone) [1518977]
- [iommu] aarch64: Set bypass mode per default (Al Stone) [1518977]
- [tools] perf bench numa: Fixup discontiguous/sparse numa nodes (Steve Best) [1516472]

* Mon Dec 04 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-12.el7a]
- [powerpc] KVM: PPC: Book3S HV: Cosmetic post-merge cleanups (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Run HPT guests on POWER9 radix hosts (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Allow for running POWER9 host in single-threaded mode (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Add infrastructure for running HPT guests on radix host (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Unify dirty page map between HPT and radix (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Rename hpte_setup_done to mmu_ready (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Don't rely on host's page size information (Suraj Jitindar Singh) [1485099]
- [powerpc] Revert KVM: PPC: Book3S HV: POWER9 does not require secondary thread management (Suraj Jitindar Singh) [1485099]
- [powerpc] KVM: PPC: Book3S HV: Explicitly disable HPT operations on radix guests (Suraj Jitindar Singh) [1485099]

* Fri Dec 01 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-11.el7a]
- [powerpc] powerpc/mce: hookup memory_failure for UE errors (Steve Best) [1517693]
- [powerpc] powerpc/mce: Hookup ierror (instruction) UE errors (Steve Best) [1517693]
- [powerpc] powerpc/mce: Hookup derror (load/store) UE errors (Steve Best) [1517693]
- [powerpc] powerpc/mce: Align the print of physical address better (Steve Best) [1517693]
- [powerpc] powerpc/mce: Remove unused function get_mce_fault_addr() (Steve Best) [1517693]
- [virtio] virtio_balloon: fix deadlock on OOM (Andrew Jones) [1516486]

* Thu Nov 30 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-10.el7a]
- [block] bio: ensure __bio_clone_fast copies bi_partno (Ming Lei) [1516243]
- [net] icmp: don't fail on fragment reassembly time exceeded (Matteo Croce) [1495458]
- [netdrv] geneve: only configure or fill UDP_ZERO_CSUM6_RX/TX info when CONFIG_IPV6 (Hangbin Liu) [1511839]
- [netdrv] geneve: fix fill_info when link down (Hangbin Liu) [1511839]
- [redhat] allow specifying BUILDID on the command line (Andrew Jones)
- [redhat] also ignore .old config files (Andrew Jones)
- [redhat] stop leaving empty temp files (Andrew Jones)

* Wed Nov 29 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-9.el7a]
- [netdrv] i40e: Use smp_rmb rather than read_barrier_depends (Mauricio Oliveira) [1513182]
- [netdrv] ixgbe: Fix skb list corruption on Power systems (Mauricio Oliveira) [1513182]

* Wed Nov 29 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-8.el7a]
- [netdrv] ibmvnic: fix dma_mapping_error call (Steve Best) [1515330]
- [netdrv] ibmvnic: Feature implementation of Vital Product Data (VPD) for the ibmvnic driver (Steve Best) [1515330]
- [netdrv] ibmvnic: Add vnic client data to login buffer (Steve Best) [1515330]
- Revert "[block] Make q_usage_counter also track legacy requests" ("Herton R. Krzesinski")
- Revert "[block] wake up all tasks blocked in get_request()" ("Herton R. Krzesinski")
- Revert "[block] run queue before waiting for q_usage_counter becoming zero" ("Herton R. Krzesinski")
- Revert "[block] drain blkcg part of request_queue in blk_cleanup_queue()" ("Herton R. Krzesinski")

* Tue Nov 28 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-7.el7a]
- [block] drain blkcg part of request_queue in blk_cleanup_queue() (Ming Lei) [1513036]
- [block] run queue before waiting for q_usage_counter becoming zero (Ming Lei) [1513036]
- [block] wake up all tasks blocked in get_request() (Ming Lei) [1513036]
- [block] Make q_usage_counter also track legacy requests (Ming Lei) [1513036]

* Tue Nov 28 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-6.el7a]
- [tools] perf vendor events powerpc: Update POWER9 events (Steve Best) [1509681]

* Mon Nov 27 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-5.el7a]
- [pci] Vulcan: AHCI PCI bar fix for Broadcom Vulcan early silicon (Torez Smith) [1508505 1513168]
- [iommu] arm-smmu, acpi: Enable Cavium SMMU-v3 (Torez Smith) [1508505 1513168]
- [iommu] arm-smmu, acpi: Enable Cavium SMMU-v2 (Torez Smith) [1508505 1513168]
- [netdrv] net: thunderx: Fix TCP/UDP checksum offload for IPv6 pkts (Florian Westphal) [1511683]
- [net] ipv6: Fixup device for anycast routes during copy (Florian Westphal) [1508339]

* Wed Nov 22 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-4.el7a]
- [powerpc] revert powerpc/powernv/cpufreq: Fix the frequency read by /proc/cpuinfo (Steve Best) [1514611]

* Tue Nov 21 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-3.el7a]
- [cpufreq] stats: Handle the case when trans_table goes beyond PAGE_SIZE (Desnes Augusto Nunes do Rosario) [1499411]
- [virt] KVM: arm/arm64: vgic-its: Implement KVM_DEV_ARM_ITS_CTRL_RESET (Auger Eric) [1490315]
- [documentation] KVM: arm/arm64: Document KVM_DEV_ARM_ITS_CTRL_RESET (Auger Eric) [1490315]
- [virt] KVM: arm/arm64: vgic-its: Free caches when GITS_BASER Valid bit is cleared (Auger Eric) [1490315]
- [virt] KVM: arm/arm64: vgic-its: New helper functions to free the caches (Auger Eric) [1490315]
- [virt] KVM: arm/arm64: vgic-its: Remove kvm_its_unmap_device (Auger Eric) [1490315]
- [tools] cpupower : Fix cpupower working when cpu0 is offline (Steve Best) [1495559]
- [scsi] scsi_sysfs: make unpriv_sgio queue attribute accessible for non-block devices (Paolo Bonzini) [1492769]
- [block] sg_io: introduce unpriv_sgio queue flag (Paolo Bonzini) [1492769]
- [block] sg_io: pass request_queue to blk_verify_command (Paolo Bonzini) [1492769]
- [kernel] locking/qrwlock: Prevent slowpath writers getting held up by fastpath (Waiman Long) [1507568]
- [arm64] locking/qrwlock, arm64: Move rwlock implementation over to qrwlocks (Waiman Long) [1507568]
- [kernel] locking/qrwlock: Use atomic_cond_read_acquire() when spinning in qrwlock (Waiman Long) [1507568]
- [kernel] locking/atomic: Add atomic_cond_read_acquire() (Waiman Long) [1507568]
- [kernel] locking/qrwlock: Use 'struct qrwlock' instead of 'struct __qrwlock' (Waiman Long) [1507568]

* Fri Nov 17 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-2.el7a]
- [powerpc] powerpc/powernv/cpufreq: Fix the frequency read by /proc/cpuinfo (Steve Best) [1501944]
- [netdrv] ibmvnic: Set state UP (Steve Best) [1512272]
- [powerpc] powerpc/64s: Add workaround for P9 vector CI load issue (Steve Best) [1501403]

* Mon Nov 13 2017 Herton R. Krzesinski <herton@redhat.com> [4.14.0-1.el7a]
- [redhat] kernel-alt rebased to 4.14 ("Herton R. Krzesinski") [1492717]
- [scsi] cxlflash: Derive pid through accessors (Steve Best) [1510168]
- [scsi] cxlflash: Allow cards without WWPN VPD to configure (Steve Best) [1510168]
- [scsi] cxlflash: Use derived maximum write same length (Steve Best) [1510168]
- [redhat] configs: Enable hardlockup detector for powerpc64le (Bhupesh Sharma) [1478225]
- [redhat] configs: Enable softlockup detector by default (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/powernv: Implement NMI IPI with OPAL_SIGNAL_SYSTEM_RESET (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/xmon: Avoid tripping SMP hardlockup watchdog (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/watchdog: Do not trigger SMP crash from touch_nmi_watchdog (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/watchdog: Do not backtrace locked CPUs twice if allcpus backtrace is enabled (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/watchdog: Do not panic from locked CPU's IPI handler (Bhupesh Sharma) [1478225]
- [powerpc] powerpc/64s: Implement system reset idle wakeup reason (Bhupesh Sharma) [1478225]
- [misc] cxl: Enable global TLBIs for cxl contexts (Gustavo Duarte) [1498927]
- [powerpc] powerpc/mm: Export flush_all_mm() (Gustavo Duarte) [1498927]
- [misc] cxl: Set the valid bit in PE for dedicated mode (Gustavo Duarte) [1498927]
- [kernel] kdump: support crashkernel=auto for compatibility (Pingfan Liu) [1431982]
- [kernel] kdump/parse_crashkernel_mem: round up the total memory size to 128M (Dave Young) [1431982]
- [x86] x86/kdump: crashkernel=X try to reserve below 896M first then below 4G and MAXMEM (Dave Young) [1431982]
- [netdrv] ibmvnic: Fix failover error path for non-fatal resets (Steve Best) [1464528]
- [netdrv] ibmvnic: Update reset infrastructure to support tunable parameters (Steve Best) [1464528]
- [netdrv] ibmvnic: Let users change net device features (Steve Best) [1464528]
- [netdrv] ibmvnic: Enable TSO support (Steve Best) [1464528]
- [netdrv] ibmvnic: Enable scatter-gather support (Steve Best) [1464528]
- [powerpc] KVM: PPC: Tie KVM_CAP_PPC_HTM to the user-visible TM feature (Steve Best) [1498555]
- [powerpc] powerpc/tm: P9 disable transactionally suspended sigcontexts (Steve Best) [1498555]
- [powerpc] powerpc/powernv: Enable TM without suspend if possible (Steve Best) [1498555]
- [powerpc] Add PPC_FEATURE2_HTM_NO_SUSPEND (Steve Best) [1498555]
- [powerpc] powerpc/tm: Add commandline option to disable hardware transactional memory (Steve Best) [1498555]
- [arm64] DO NOT UPSTREAM - topology: Adjust sysfs topology (Andrew Jones) [1501443]
- [arm64] DO NOT UPSTREAM - pmuv3: disable PMUv3 in VM when vPMU=off (Andrew Jones) [1501452]
- [redhat] configs: s390: Enable CONFIG_FTRACE_SYSCALLS option (Jiri Olsa) [1469687]
- [redhat] configs: s390x: Disable CONFIG_S390_GUEST_OLD_TRANSPORT (David Hildenbrand) [1495197]
- [redhat] configs: enable CONFIG_MEM_SOFT_DIRTY on ppc64le (Adrian Reber) [1496347]
- [redhat] configs: enable CHECKPOINT_RESTORE on s390x (Adrian Reber) [1457968]
- [redhat] remove usage of mandocs target for kernel-doc, avoid running htmldocs ("Herton R. Krzesinski")


###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
