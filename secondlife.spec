%define name secondlife
%define version 1.15.0.0
%define beta 1
%define snapshot 0
%if %{snapshot}
%define release %mkrel 0.%{snapshot}.1
%define oname slviewer-src
%define distname %{oname}-%{snapshot}
%else
%define release %mkrel 1
%if %{beta}
%define oname slviewer-src-beta
%else
%define oname slviewer-src
%endif
%define distname %{oname}-%{version}
%endif

Summary: Online 3-D virtual world
Name: %{name}
Version: %{version}
Release: %{release}
Source0: http://secondlife.com/developers/opensource/downloads/%{distname}.tar.bz2
Patch0: slviewer-src-1.15.0.0-releasefiles.patch
Patch1: slviewer-src-20070108c-cplusplus.patch
Patch2: slviewer-src-beta-1.14.1.2-boost.patch
Patch3: slviewer-src-beta-1.14.1.2-no_fmod.patch
Patch6: slviewer-src-beta-1.14.1.2-ELFIO.patch
Patch7: slviewer-src-beta-1.13.4.7-datapath.patch
Patch8: moz15.patch
License: GPL
Group: Games/Other
Url: http://secondlife.com/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: SDL-devel
BuildRequires: apr-util-devel bison boost-devel curl-devel elfio-devel expat-devel
BuildRequires: freetype2-devel gtk2-devel jpeg-devel flex libxmlrpc-devel
BuildRequires: mesaglu-devel oggvorbis-devel openjpeg-devel scons zlib-devel
BuildConflicts: freetype-devel
Requires: fonts-ttf-bitstream-vera
Requires: secondlife-artwork

%description
Second Life is a 3-D virtual world entirely built and owned by its residents.

%prep
%setup -q -n linden
%if %{beta}
%patch0 -p1 -b .releasefiles
%endif
%patch1 -p1 -b .cplusplus
%patch2 -p1 -b .boost
%patch3 -p1 -b .no_fmod
%patch6 -p1 -b .ELFIO
%patch7 -p1 -b .datapath
%patch8 -p1 -b .nomozlib

perl -pi -e 's/\Qg++-3.4\E/g++/' indra/SConstruct

mkdir libraries/include/expat
ln -s %{_includedir}/expat.h libraries/include/expat
mkdir -p libraries/include/llfreetype2/freetype
ln -s %{_includedir}/ft2build.h libraries/include/llfreetype2/freetype
mkdir libraries/include/jpeglib
ln -s %{_includedir}/{jpeglib,jerror}.h libraries/include/jpeglib
> libraries/include/jpeglib/jinclude.h
mkdir libraries/include/openjpeg
ln -s %{_includedir}/openjpeg.h libraries/include/openjpeg
mkdir libraries/include/xmlrpc-epi
ln -s %{_includedir}/xmlrpc.h libraries/include/xmlrpc-epi
mkdir libraries/include/zlib
ln -s %{_includedir}/zlib.h libraries/include/zlib

%build
CLIENT_CPPFLAGS=`pkg-config --cflags gtk+-2.0`
%if %mdkversion < 200710
  CLIENT_CPPFLAGS="$CLIENT_CPPFLAGS -I/usr/include/freetype2 -I/usr/include/libpng12"
%endif
export CLIENT_CPPFLAGS

pushd indra
scons BUILD=release BTARGET=client DISTCC=no MOZLIB=no
popd

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_gamesbindir}
install -m 755 indra/newview/%{name}-*-bin-globalsyms %{buildroot}%{_gamesbindir}/%{name}.bin
install -m 755 indra/newview/linux_tools/wrapper.sh %{buildroot}%{_gamesbindir}/%{name}

pushd indra/newview
  install -d %{buildroot}%{_gamesdatadir}/%{name}
  cp -a app_settings character fonts skins res-sdl \
        featuretable.txt gpu_table.txt \
        %{buildroot}%{_gamesdatadir}/%{name}
popd

install -m 644 scripts/messages/message_template.msg %{buildroot}%{_gamesdatadir}/%{name}/app_settings/
ln -s /usr/share/fonts/TTF/Vera.ttf %{buildroot}%{_gamesdatadir}/%{name}/unicode.ttf

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc indra/newview/linux_tools/client-readme.txt indra/newview/releasenotes.txt indra/newview/lsl_guide.html
%{_gamesbindir}/%{name}
%{_gamesbindir}/%{name}.bin
%{_gamesdatadir}/%{name}


