from typing import Type
from pathlib import Path
import os
import re

from aqt import mw
from aqt.utils import showText

from .compat import compat

config = mw.addonManager.getConfig(__name__)


class Version:
    @classmethod
    def from_string(cls: Type["Version"], ver_str: str) -> "Version":
        ver = [int(i) for i in ver_str.split(".")]
        version = Version(from_config=False)
        version.set_version(ver[0], ver[1])
        return version

    def __init__(self, from_config: bool = True) -> None:
        if from_config:
            self.load()

    def load(self) -> None:
        # Default to -1.-1 if version is missing from config
        v = config.get("version", {"major": -1, "minor": -1})
        self.set_version(v.get("major", -1), v.get("minor", -1))

    def set_version(self, major: int, minor: int) -> None:
        self.major = major
        self.minor = minor

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            ver = [int(i) for i in other.split(".")]
            return self.major == ver[0] and self.minor == ver[1]
        return False

    def __gt__(self, other: str) -> bool:
        ver = [int(i) for i in other.split(".")]
        return self.major > ver[0] or (self.major == ver[0] and self.minor > ver[1])

    def __lt__(self, other: str) -> bool:
        ver = [int(i) for i in other.split(".")]
        return self.major < ver[0] or (self.major == ver[0] and self.minor < ver[1])

    def __ge__(self, other: str) -> bool:
        return self == other or self > other

    def __le__(self, other: str) -> bool:
        return self == other or self < other

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


def show_changelog(prev_ver: Version) -> None:
    version_file = Path(__file__).parent / "VERSION"
    if not version_file.exists():
        return
        
    curr_version_str = version_file.read_text().strip()
    
    # Don't show if version hasn't changed or if it's a fresh install from scratch
    if prev_ver == curr_version_str or prev_ver == "-1.-1":
        return

    readme_file = Path(__file__).parent / "README.md"
    if not readme_file.exists():
        return

    content = readme_file.read_text(encoding="utf-8")
    # Extract the Changelog section
    match = re.search(r"# Changelog\s*(.*)", content, re.DOTALL)
    if match:
        changelog_text = match.group(1).strip()
        # showText renders markdown as HTML in Anki
        showText(f"### Review Hotmouse Updated to {curr_version_str}\n\n{changelog_text}", 
                 title="Review Hotmouse Updated", type="markdown")

def save_current_version_to_conf(prev_ver: Version) -> None:
    version_file = Path(__file__).parent / "VERSION"
    if not version_file.exists():
        return
        
    version_string = version_file.read_text().strip()
    
    # If the version in the file is different from the config, update config and show changelog
    if version_string != str(prev_ver):
        show_changelog(prev_ver)
        
        parts = version_string.split(".")
        if "version" not in config:
            config["version"] = {}
        config["version"]["major"] = int(parts[0])
        config["version"]["minor"] = int(parts[1])
        mw.addonManager.writeConfig(__name__, config)


def detect_version() -> Version:
    """Detection for very old versions missing the 'version' key."""
    if "threshold_angle" in config:
        return Version.from_string("1.0")
    if "q_wheel_down" in config:
        return Version.from_string("1.1")
    else:
        return Version.from_string("-1.-1")


# 1. Load the version currently stored in the user's config
prev_version = Version()

# 2. If no version was found, try to detect if it's an old install
if prev_version == "-1.-1":
    prev_version = detect_version()

# 3. Compare with the new version in the VERSION file and update if needed
save_current_version_to_conf(prev_version)

# 4. Run any necessary compatibility migrations
compat(prev_version)
