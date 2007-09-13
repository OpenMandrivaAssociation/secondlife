%define name secondlife
%define version 1.18.2.0
%define beta 0
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
%define Summary Second Life online 3-D virtual world

Summary: %{Summary}
Name: %{name}
Version: %{version}
Release: %{release}
Source0: http://secondlife.com/developers/opensource/downloads/%{distname}.tar.gz
# missing files for png support, from https://jira.secondlife.com/browse/VWR-79
Source1: https://jira.secondlife.com/secure/attachment/10030/png-support-20070127a.zip
Patch0: slviewer-src-1.15.0.0-releasefiles.patch
Patch1: slviewer-src-1.17.1.0-size_t.patch
Patch2: slviewer-src-1.18.2.0-const_char.patch
Patch4: slviewer-src-1.18.2.0-resolv.patch
Patch7: slviewer-src-1.18.2.0-datapath.patch
# adapted from http://www.haxxed.com/code/slviewer-1.17.0.12-openal-20070625.patch
Patch9: slviewer-1.18.2.0-openal-20070625.patch
Patch10: slviewer-src-1.18.2.0-get_factor.patch
License: GPL
Group: Games/Other
Url: http://secondlife.com/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: SDL-devel
BuildRequires: apr-util-devel bison curl-devel elfio-devel expat-devel
BuildRequires: freetype2-devel gtk2-devel jpeg-devel flex libxmlrpc-devel
BuildRequires: mesaglu-devel oggvorbis-devel openjpeg-devel scons zlib-devel
BuildRequires: freealut-devel openal-devel google-perftools-devel
#BuildRequires: libgstreamer-plugins-base-devel
BuildConflicts: freetype-devel
Requires: fonts-ttf-bitstream-vera
Requires: secondlife-artwork

%description
Second Life is an online 3-D virtual world entirely built and owned by
its residents.

%prep
%setup -q -n linden -a 1
%if %{beta}
%patch0 -p1 -b .releasefiles
%endif
%patch1 -p1 -b .size_t
%patch2 -p1 -b .const_char
%patch4 -p1 -b .resolv
%patch7 -p1 -b .datapath
%patch9 -p1 -b .openal
%patch10 -p1 -b .get_factor

cp -a png-support-20070127a/linden/indra/llimage/* indra/llimage/
perl -pi -e 's/LLImage\.h/llimage.h/' indra/llimage/*png*
perl -pi -e 's,libpng/png\.h,png.h,' indra/llimage/*png*

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
%if %mdkversion < 200710
  CLIENT_CPPFLAGS="$CLIENT_CPPFLAGS -I/usr/include/freetype2 -I/usr/include/libpng12"
  export CLIENT_CPPFLAGS
%endif

pushd indra
scons BUILD=release BTARGET=client STANDALONE=yes DISTCC=no MOZLIB=no FMOD=no GSTREAMER=no
popd

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_gamesbindir}
install -m 755 indra/newview/%{name}-*-bin-globalsyms %{buildroot}%{_gamesbindir}/%{name}.bin
install -m 755 indra/newview/linux_tools/wrapper.sh %{buildroot}%{_gamesbindir}/%{name}

install -d %{buildroot}%{_libdir}
install -m644 indra/lib_release_client/i686-linux/libll*.so %{buildroot}%{_libdir}

install -d %{buildroot}%{_gamesdatadir}/%{name}/fonts
pushd indra/newview
  cp -a app_settings skins \
        featuretable.txt gpu_table.txt \
        %{buildroot}%{_gamesdatadir}/%{name}
popd

install -m 644 scripts/messages/message_template.msg %{buildroot}%{_gamesdatadir}/%{name}/app_settings/
for f in MtBdLfRg.ttf MtBkLfRg.ttf profontwindows.ttf unicode.ttf; do
  ln -s /usr/share/fonts/TTF/Vera.ttf %{buildroot}%{_gamesdatadir}/%{name}/fonts/$f
done

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Second Life
Comment=%{Summary}
Exec=soundwrapper %{_gamesbindir}/%{name}
Icon=%{_gamesdatadir}/%{name}/res/ll_icon.ico
Terminal=false
Type=Application
Categories=Game;AdventureGame;X-MandrivaLinux-MoreApplications-Games-Adventure;
EOF

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc indra/newview/linux_tools/client-readme.txt indra/newview/releasenotes.txt indra/newview/lsl_guide.html
%{_gamesbindir}/%{name}
%{_gamesbindir}/%{name}.bin
%{_libdir}/libll*.so
%defattr(0644,root,root,0755)
%{_gamesdatadir}/%{name}
%{_datadir}/applications/mandriva-%{name}.desktop
