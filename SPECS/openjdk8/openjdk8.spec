%define _use_internal_dependency_generator 0
%global security_hardening none
%define _jdk_update 292
%define _jdk_build 10
Summary:        OpenJDK
Name:           openjdk8
Version:        1.8.0.292
Release:        2%{?dist}
License:        ASL 1.1 AND ASL 2.0 AND BSD AND BSD WITH advertising AND GPL+ AND GPLv2 AND GPLv2 WITH exceptions AND IJG AND LGPLv2+ AND MIT AND MPLv2.0 AND Public Domain AND W3C AND zlib
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Tools
URL:            https://openjdk.java.net
# Source tarball is generated by AdoptOpenJDK from OpenJDK sources
#Source0:       https://github.com/AdoptOpenJDK/openjdk-jdk8u/archive/jdk8u292-b10.tar.gz
Source0:        openjdk-%{version}.tar.gz
Patch0:         Awt_build_headless_only.patch
Patch1:         check-system-ca-certs-292.patch
BuildRequires:  alsa-lib
BuildRequires:  alsa-lib-devel
BuildRequires:  chkconfig
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  glib-devel
BuildRequires:  pcre-devel
BuildRequires:  unzip
BuildRequires:  which
BuildRequires:  zlib-devel
Requires:       chkconfig
Requires:       openjre8 = %{version}-%{release}
AutoReqProv:    no
Obsoletes:      openjdk <= %{version}
Provides:       java-devel = %{version}-%{release}
ExclusiveArch:  x86_64

%description
The OpenJDK package installs java class library and javac java compiler.

%package	-n openjre8
Summary:        Java runtime environment
Requires:       chkconfig
Requires:       libstdc++
AutoReqProv:    no
Obsoletes:      openjre <= %{version}

%description	-n openjre8
It contains the libraries files for Java runtime environment

%package	sample
Summary:        Sample java applications.
Group:          Development/Languages/Java
Requires:       %{name} = %{version}-%{release}
Obsoletes:      openjdk-sample <= %{version}

%description	sample
It contains the Sample java applications.

%package		doc
Summary:        Documentation and demo applications for openjdk
Group:          Development/Languages/Java
Requires:       %{name} = %{version}-%{release}
Obsoletes:      openjdk-doc <= %{version}

%description	doc
It contains the documentation and demo applications for openjdk

%package 		src
Summary:        OpenJDK Java classes for developers
Group:          Development/Languages/Java
Requires:       %{name} = %{version}-%{release}
Obsoletes:      openjdk-src <= %{version}

%description	src
This package provides the runtime library class sources.

%prep -p exit
%setup -qn openjdk-jdk8u-jdk8u%{_jdk_update}-b%{_jdk_build}
%patch0 -p1
%patch1 -p1
rm jdk/src/solaris/native/sun/awt/CUPSfuncs.c
sed -i "s#\"ft2build.h\"#<ft2build.h>#g" jdk/src/share/native/sun/font/freetypeScaler.c
sed -i '0,/BUILD_LIBMLIB_SRC/s/BUILD_LIBMLIB_SRC/BUILD_HEADLESS_ONLY := 1\nOPENJDK_TARGET_OS := linux\n&/' jdk/make/lib/Awt2dLibraries.gmk

%build
chmod a+x ./configur*
export CFLAGS="%{build_cflags} -Wno-error=format-overflow= -Wno-error=stringop-overflow="
export CXXFLAGS="%{build_cxxflags}-Wno-error=format-overflow= -Wno-error=stringop-overflow="
export CFLAGS=$(echo $CFLAGS | sed "s/-Wall//" | sed "s/-Wformat//" | sed "s/-Werror=format-security//")
export CXXFLAGS=$(echo $CXXFLAGS | sed "s/-Wall//" | sed "s/-Wformat// | sed "s/-Werror=format-security//"")
unset JAVA_HOME &&
./configur* \
	--with-target-bits=64 \
	--with-boot-jdk=%{_libdir}/jvm/OpenJDK-212-b04-bootstrap \
	--disable-headful \
	--with-cacerts-file=%{_libdir}/jvm/OpenJDK-212-b04-bootstrap/jre/lib/security/cacerts \
	--with-extra-cxxflags="-Wno-error -std=gnu++98 -fno-delete-null-pointer-checks -fno-lifetime-dse" \
	--with-extra-cflags="-std=gnu++98 -fno-delete-null-pointer-checks -Wno-error -fno-lifetime-dse" \
	--with-freetype-include=%{_includedir}/freetype2 \
	--with-freetype-lib=%{_libdir} \
	--with-stdc++lib=dynamic \
	--with-native-debug-symbols=none \
	--disable-zip-debug-info

make \
    DEBUG_BINARIES=true \
    BUILD_HEADLESS_ONLY=1 \
    OPENJDK_TARGET_OS=linux \
    JAVAC_FLAGS=-g \
    STRIP_POLICY=no_strip \
    DISABLE_HOTSPOT_OS_VERSION_CHECK=ok \
    CLASSPATH=%{_libdir}/jvm/OpenJDK-212-b04-bootstrap/jre \
    POST_STRIP_CMD="" \
    LOG=trace \
    SCTP_WERROR=

%install
make DESTDIR=%{buildroot} install \
	BUILD_HEADLESS_ONLY=yes \
	OPENJDK_TARGET_OS=linux \
	DISABLE_HOTSPOT_OS_VERSION_CHECK=ok \
	CLASSPATH=%{_libdir}/jvm/OpenJDK-212-b04-bootstrap/jre

install -vdm755 %{buildroot}%{_libdir}/jvm/OpenJDK-%{version}
chown -R root:root %{buildroot}%{_libdir}/jvm/OpenJDK-%{version}
install -vdm755 %{buildroot}%{_bindir}
find %{_prefix}/local/jvm/openjdk-1.8.0-internal/jre/lib/amd64 -iname \*.diz -delete
mv %{_prefix}/local/jvm/openjdk-1.8.0-internal/* %{buildroot}%{_libdir}/jvm/OpenJDK-%{version}/

%post
alternatives --install %{_bindir}/javac javac %{_libdir}/jvm/OpenJDK-%{version}/bin/javac 2000 \
  --slave %{_bindir}/appletviewer appletviewer %{_libdir}/jvm/OpenJDK-%{version}/bin/appletviewer \
  --slave %{_bindir}/extcheck extcheck %{_libdir}/jvm/OpenJDK-%{version}/bin/extcheck \
  --slave %{_bindir}/idlj idlj %{_libdir}/jvm/OpenJDK-%{version}/bin/idlj \
  --slave %{_bindir}/jar jar %{_libdir}/jvm/OpenJDK-%{version}/bin/jar \
  --slave %{_bindir}/jarsigner jarsigner %{_libdir}/jvm/OpenJDK-%{version}/bin/jarsigner \
  --slave %{_bindir}/javadoc javadoc %{_libdir}/jvm/OpenJDK-%{version}/bin/javadoc \
  --slave %{_bindir}/javah javah %{_libdir}/jvm/OpenJDK-%{version}/bin/javah \
  --slave %{_bindir}/javap javap %{_libdir}/jvm/OpenJDK-%{version}/bin/javap \
  --slave %{_bindir}/jcmd jcmd %{_libdir}/jvm/OpenJDK-%{version}/bin/jcmd \
  --slave %{_bindir}/jconsole jconsole %{_libdir}/jvm/OpenJDK-%{version}/bin/jconsole \
  --slave %{_bindir}/jdb jdb %{_libdir}/jvm/OpenJDK-%{version}/bin/jdb \
  --slave %{_bindir}/jdeps jdeps %{_libdir}/jvm/OpenJDK-%{version}/bin/jdeps \
  --slave %{_bindir}/jhat jhat %{_libdir}/jvm/OpenJDK-%{version}/bin/jhat \
  --slave %{_bindir}/jinfo jinfo %{_libdir}/jvm/OpenJDK-%{version}/bin/jinfo \
  --slave %{_bindir}/jmap jmap %{_libdir}/jvm/OpenJDK-%{version}/bin/jmap \
  --slave %{_bindir}/jps jps %{_libdir}/jvm/OpenJDK-%{version}/bin/jps \
  --slave %{_bindir}/jfr jfr %{_libdir}/jvm/OpenJDK-%{version}/bin/jfr \
  --slave %{_bindir}/jrunscript jrunscript %{_libdir}/jvm/OpenJDK-%{version}/bin/jrunscript \
  --slave %{_bindir}/jsadebugd jsadebugd %{_libdir}/jvm/OpenJDK-%{version}/bin/jsadebugd \
  --slave %{_bindir}/jstack jstack %{_libdir}/jvm/OpenJDK-%{version}/bin/jstack \
  --slave %{_bindir}/jstat jstat %{_libdir}/jvm/OpenJDK-%{version}/bin/jstat \
  --slave %{_bindir}/jstatd jstatd %{_libdir}/jvm/OpenJDK-%{version}/bin/jstatd \
  --slave %{_bindir}/native2ascii native2ascii %{_libdir}/jvm/OpenJDK-%{version}/bin/native2ascii \
  --slave %{_bindir}/rmic rmic %{_libdir}/jvm/OpenJDK-%{version}/bin/rmic \
  --slave %{_bindir}/schemagen schemagen %{_libdir}/jvm/OpenJDK-%{version}/bin/schemagen \
  --slave %{_bindir}/serialver serialver %{_libdir}/jvm/OpenJDK-%{version}/bin/serialver \
  --slave %{_bindir}/wsgen wsgen %{_libdir}/jvm/OpenJDK-%{version}/bin/wsgen \
  --slave %{_bindir}/wsimport wsimport %{_libdir}/jvm/OpenJDK-%{version}/bin/wsimport \
  --slave %{_bindir}/xjc xjc %{_libdir}/jvm/OpenJDK-%{version}/bin/xjc
/sbin/ldconfig

%post -n openjre8
alternatives --install %{_bindir}/java java %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/java 2000 \
  --slave %{_libdir}/jvm/jre jre %{_libdir}/jvm/OpenJDK-%{version}/jre \
  --slave %{_bindir}/jjs jjs %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/jjs \
  --slave %{_bindir}/keytool keytool %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/keytool \
  --slave %{_bindir}/orbd orbd %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/orbd \
  --slave %{_bindir}/pack200 pack200 %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/pack200 \
  --slave %{_bindir}/rmid rmid %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/rmid \
  --slave %{_bindir}/rmiregistry rmiregistry %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/rmiregistry \
  --slave %{_bindir}/servertool servertool %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/servertool \
  --slave %{_bindir}/tnameserv tnameserv %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/tnameserv \
  --slave %{_bindir}/unpack200 unpack200 %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/unpack200
/sbin/ldconfig

%postun
alternatives --remove javac %{_libdir}/jvm/OpenJDK-%{version}/bin/javac
/sbin/ldconfig

%postun -n openjre8
alternatives --remove java %{_libdir}/jvm/OpenJDK-%{version}/jre/bin/java
/sbin/ldconfig
rm -rf %{_libdir}/jvm/OpenJDK-%{version}

%clean
rm -rf %{buildroot}/*



%files
%defattr(-,root,root)
%license %{_libdir}/jvm/OpenJDK-%{version}/LICENSE
%{_libdir}/jvm/OpenJDK-%{version}/ASSEMBLY_EXCEPTION
%{_libdir}/jvm/OpenJDK-%{version}/release
%{_libdir}/jvm/OpenJDK-%{version}/THIRD_PARTY_README
%{_libdir}/jvm/OpenJDK-%{version}/lib
%{_libdir}/jvm/OpenJDK-%{version}/include/
%{_libdir}/jvm/OpenJDK-%{version}/bin/extcheck
%{_libdir}/jvm/OpenJDK-%{version}/bin/idlj
%{_libdir}/jvm/OpenJDK-%{version}/bin/jar
%{_libdir}/jvm/OpenJDK-%{version}/bin/jarsigner
%{_libdir}/jvm/OpenJDK-%{version}/bin/java-rmi.cgi
%{_libdir}/jvm/OpenJDK-%{version}/bin/javac
%{_libdir}/jvm/OpenJDK-%{version}/bin/javadoc
%{_libdir}/jvm/OpenJDK-%{version}/bin/javah
%{_libdir}/jvm/OpenJDK-%{version}/bin/javap
%{_libdir}/jvm/OpenJDK-%{version}/bin/jcmd
%{_libdir}/jvm/OpenJDK-%{version}/bin/jconsole
%{_libdir}/jvm/OpenJDK-%{version}/bin/jdb
%{_libdir}/jvm/OpenJDK-%{version}/bin/jdeps
%{_libdir}/jvm/OpenJDK-%{version}/bin/jhat
%{_libdir}/jvm/OpenJDK-%{version}/bin/jinfo
%{_libdir}/jvm/OpenJDK-%{version}/bin/jjs
%{_libdir}/jvm/OpenJDK-%{version}/bin/jfr
%{_libdir}/jvm/OpenJDK-%{version}/bin/jmap
%{_libdir}/jvm/OpenJDK-%{version}/bin/jps
%{_libdir}/jvm/OpenJDK-%{version}/bin/jrunscript
%{_libdir}/jvm/OpenJDK-%{version}/bin/jsadebugd
%{_libdir}/jvm/OpenJDK-%{version}/bin/jstack
%{_libdir}/jvm/OpenJDK-%{version}/bin/jstat
%{_libdir}/jvm/OpenJDK-%{version}/bin/jstatd
%{_libdir}/jvm/OpenJDK-%{version}/bin/native2ascii
%{_libdir}/jvm/OpenJDK-%{version}/bin/rmic
%{_libdir}/jvm/OpenJDK-%{version}/bin/schemagen
%{_libdir}/jvm/OpenJDK-%{version}/bin/serialver
%{_libdir}/jvm/OpenJDK-%{version}/bin/wsgen
%{_libdir}/jvm/OpenJDK-%{version}/bin/wsimport
%{_libdir}/jvm/OpenJDK-%{version}/bin/xjc
%{_libdir}/jvm/OpenJDK-%{version}/bin/clhsdb
%{_libdir}/jvm/OpenJDK-%{version}/bin/hsdb
%exclude %{_libdir}/jvm/OpenJDK-%(version)/bin/*.debuginfo

%files -n openjre8
%defattr(-,root,root)
%dir %{_libdir}/jvm/OpenJDK-%{version}
%{_libdir}/jvm/OpenJDK-%{version}/jre/
%{_libdir}/jvm/OpenJDK-%{version}/bin/java
%{_libdir}/jvm/OpenJDK-%{version}/bin/keytool
%{_libdir}/jvm/OpenJDK-%{version}/bin/orbd
%{_libdir}/jvm/OpenJDK-%{version}/bin/pack200
%{_libdir}/jvm/OpenJDK-%{version}/bin/rmid
%{_libdir}/jvm/OpenJDK-%{version}/bin/rmiregistry
%{_libdir}/jvm/OpenJDK-%{version}/bin/servertool
%{_libdir}/jvm/OpenJDK-%{version}/bin/tnameserv
%{_libdir}/jvm/OpenJDK-%{version}/bin/unpack200
%{_libdir}/jvm/OpenJDK-%{version}/lib/amd64/jli/
%exclude %{_libdir}/jvm/OpenJDK-%{version}/lib/amd64/*.diz

%files sample
%defattr(-,root,root)
%{_libdir}/jvm/OpenJDK-%{version}/sample/

%files doc
%defattr(-,root,root)
%{_libdir}/jvm/OpenJDK-%{version}/man/
%{_libdir}/jvm/OpenJDK-%{version}/demo

%files src
%defattr(-,root,root)
%{_libdir}/jvm/OpenJDK-%{version}/src.zip

%changelog
* Mon Aug 30 2021 Bala <balakumaran.kannan@microsoft.com> - 1.8.0.292-2
- Provide java-devel

*   Fri Apr 16 2021 Nick Samson <nick.samson@microsoft.com> - 1.8.0.292-1
-   Update to 8u292 to address CVEs
-   Switch to AdoptOpenJDK-generated source tarball

*   Thu Jun 11 2020 Henry Beberman <henry.beberman@microsoft.com> - 1.8.0.212-10
-   Disable -Werrors that break the build in cflags and cxxflags.

*   Tue May 26 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 1.8.0.212-9
-   Adding the "%%license" macro.

*   Wed May 06 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 1.8.0.212-8
-   Removing *Requires for "ca-certificates".
-   Fixing changelog version markings.

*   Mon May 04 2020 Emre Girgin <mrgirgin@microsoft.com> 1.8.0.212-7
-   Replace BuildArch with ExclusiveArch

*   Thu Apr 30 2020 Nicolas Ontiveros <niontive@microsoft.com> 1.8.0.212-6
-   Rename freetype2-devel to freetype-devel.

*   Thu Apr 16 2020 Paul Monson <paulmon@microsoft.com> 1.8.0.212-5
-   Remove harfbuzz-devel.  License verified. Fix Source0.

*   Wed Feb 12 2020 Andrew Phelps <anphel@microsoft.com> 1.8.0.212-4
-   Remove ExtraBuildRequires

*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.8.0.212-3
-   Initial CBL-Mariner import from Photon (license: Apache2).

*   Tue May 20 2019 Tapas Kundu <tkundu@vmware.com> 1.8.0.212-2
-   Upgrade to version 1.8.0.212 b04
-   Included fix for performance regression.

*   Thu May 02 2019 Tapas Kundu <tkundu@vmware.com> 1.8.0.212-1
-   Upgrade to version 1.8.0.212
-   Add new clhsdb and hsdb binaries.
-   Fix CVE-2019-2602, CVE-2019-2697, CVE-2019-2698.

*   Wed Jan 23 2019 Srinidhi Rao <srinidhir@vmware.com> 1.8.0.202-1
-   Upgrade to version 1.8.0.202

*   Mon Oct 29 2018 Ajay Kaher <akaher@vmware.com> 1.8.0.192-3
-   Adding BuildArch

*   Mon Oct 29 2018 Alexey Makhalov <amakhalov@vmware.com> 1.8.0.192-2
-   Use ExtraBuildRequires

*   Thu Oct 18 2018 Tapas Kundu <tkundu@vmware.com> 1.8.0.192-1
-   Upgraded to version 1.8.0.192

*   Fri Sep 21 2018 Srinidhi Rao <srinidhir@vmware.com> 1.8.0.181-1
-   Upgraded to 1.8.0.181 version.

*   Mon Apr 23 2018 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.172-1
-   Upgraded to version 1.8.0.172

*   Fri Jan 19 2018 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.162-1
-   Upgraded to version 1.8.0.162

*   Thu Dec 21 2017 Alexey Makhalov <amakhalov@vmware.com> 1.8.0.152-2
-   Reduce list of published rpms dependencies

*   Thu Oct 19 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.152-1
-   Upgraded to version 1.8.0.152

*   Thu Sep 14 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.141-2
-   added ldconfig in post actions.

*   Fri Jul 21 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.141-1
-   Upgraded to version 1.8.0.141-1

*   Thu Jul 6 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.131-4
-   Build AWT libraries as well.

*   Thu Jun 29 2017 Divya Thaluru <dthaluru@vmware.com> 1.8.0.131-3
-   Added obseletes for deprecated openjdk package

*   Tue Jun 06 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.131-2
-   Add requires for libstdc++

*   Mon Apr 10 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.131-1
-   Upgraded to version 1.8.0.131 and building Java from sources

*   Tue Mar 28 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.8.0.112-2
-   add java rpm macros

*   Wed Dec 21 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.8.0.112-1
-   Update to 1.8.0.112. addresses CVE-2016-5582 CVE-2016-5573

*   Tue Oct 04 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.8.0.102-1
-   Update to 1.8.0.102, minor fixes in url, spelling.
-   addresses CVE-2016-3598, CVE-2016-3606, CVE-2016-3610

*   Thu May 26 2016 Divya Thaluru <dthaluru@vmware.com> 1.8.0.92-3
-   Added version constraint to runtime dependencies

*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.8.0.92-2
-   GA - Bump release of all rpms

*   Fri May 20 2016 Divya Thaluru <dthaluru@vmware.com> 1.8.0.92-1
-   Updated to version 1.8.0.92

*   Mon May 2 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.8.0.72-3
-   Move tools like javac to openjdk

*   Thu Apr 28 2016 Divya Thaluru <dthaluru@vmware.com> 1.8.0.72-2
-   Adding openjre as run time dependency for openjdk package

*   Fri Feb 26 2016 Kumar Kaushik <kaushikk@vmware.com> 1.8.0.72-1
-   Updating Version.

*   Mon Nov 16 2015 Sharath George <sharathg@vmware.com> 1.8.0.51-3
-   Change to use /var/opt path

*   Fri Sep 11 2015 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.8.0.51-2
-   Split the openjdk into multiple sub-packages to reduce size.

*   Mon Aug 17 2015 Sharath George <sarahc@vmware.com> 1.8.0.51-1
-   Moved to the next version

*   Tue Jun 30 2015 Sarah Choi <sarahc@vmware.com> 1.8.0.45-2
-   Add JRE path

*   Mon May 18 2015 Sharath George <sharathg@vmware.com> 1.8.0.45-1
-   Initial build. First version
