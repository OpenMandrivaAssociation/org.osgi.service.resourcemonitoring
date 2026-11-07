Name:		org.osgi.service.resourcemonitoring
Version:	1.0.1
Release:	1
Summary:	OSGi Resource Monitoring API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.resourcemonitoring/%{version}/org.osgi.service.resourcemonitoring-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/r8-cmpn-final/LICENSE#/org.osgi.service.resourcemonitoring-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:osgi.core)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Resource Monitoring 1.0. Resource contexts, monitors, and the CPU,
memory, thread, socket, and disk storage monitor types. Bundle and
ServiceListener appear only in javadoc, so OSGi Core is provided.
Upstream asked for osgi.annotation 8.0.1 and org.osgi.framework 1.8.0.
This build uses the packaged osgi.annotation 8.1.0 and osgi.core 6.0.0.
The build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/service/resourcemonitoring")
names = sorted(path.name for path in root.glob("*.java"))
expect = [
    "ResourceContext.java",
    "ResourceContextEvent.java",
    "ResourceContextException.java",
    "ResourceContextListener.java",
    "ResourceEvent.java",
    "ResourceListener.java",
    "ResourceMonitor.java",
    "ResourceMonitorException.java",
    "ResourceMonitorFactory.java",
    "ResourceMonitoringService.java",
    "package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
monitor = sorted(path.name for path in (root / "monitor").glob("*.java"))
expect_monitor = [
    "CPUMonitor.java",
    "DiskStorageMonitor.java",
    "MemoryMonitor.java",
    "SocketMonitor.java",
    "ThreadMonitor.java",
    "package-info.java",
]
if monitor != expect_monitor:
    raise SystemExit("monitor java files " + " ".join(monitor))
for path in (root / "package-info.java", root / "monitor" / "package-info.java"):
    if '@Version("1.0.1")' not in path.read_text(encoding="utf-8"):
        raise SystemExit("package-info version changed " + str(path))
if list(Path(".").rglob("packageinfo")):
    raise SystemExit("unexpected packageinfo")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.resourcemonitoring</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.resourcemonitoring</name>
  <description>OSGi Resource Monitoring.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.resourcemonitoring</artifactId>",
    "<artifactId>osgi.core</artifactId>",
    "<version>6.0.0</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin", "<version>8.0.1</version>", "<version>1.8.0</version>", "org.osgi.framework", "projectbuild.sourceEncoding"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.resourcemonitoring-%{version}.jar --describe-module org.osgi.service.resourcemonitoring > module-describe.txt
grep -q '^org.osgi.service.resourcemonitoring' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.resourcemonitoring-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
required = {
    "org/osgi/service/resourcemonitoring/package-info.class",
    "org/osgi/service/resourcemonitoring/ResourceContext.class",
    "org/osgi/service/resourcemonitoring/ResourceContextEvent.class",
    "org/osgi/service/resourcemonitoring/ResourceContextException.class",
    "org/osgi/service/resourcemonitoring/ResourceContextListener.class",
    "org/osgi/service/resourcemonitoring/ResourceEvent.class",
    "org/osgi/service/resourcemonitoring/ResourceListener.class",
    "org/osgi/service/resourcemonitoring/ResourceMonitor.class",
    "org/osgi/service/resourcemonitoring/ResourceMonitorException.class",
    "org/osgi/service/resourcemonitoring/ResourceMonitorFactory.class",
    "org/osgi/service/resourcemonitoring/ResourceMonitoringService.class",
    "org/osgi/service/resourcemonitoring/monitor/package-info.class",
    "org/osgi/service/resourcemonitoring/monitor/CPUMonitor.class",
    "org/osgi/service/resourcemonitoring/monitor/DiskStorageMonitor.class",
    "org/osgi/service/resourcemonitoring/monitor/MemoryMonitor.class",
    "org/osgi/service/resourcemonitoring/monitor/SocketMonitor.class",
    "org/osgi/service/resourcemonitoring/monitor/ThreadMonitor.class",
}
missing = sorted(required - names)
if missing:
    raise SystemExit("missing " + " ".join(missing))
if any(name.endswith("packageinfo") for name in names):
    raise SystemExit("unexpected packageinfo")
PY

%files -f .mfiles
%doc LICENSE
