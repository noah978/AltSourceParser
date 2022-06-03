import argparse
import os

from sourceUtil import (AltSourceManager, AltSourceParser, GithubParser, Unc0verParser)

print("Beginning testing.")
filepath = Path("example.json")
with open(filepath, "r", encoding="utf-8") as fp:
    altsrc = json.load(fp)
altsrc = AltSource(src)
altsrc.apps[0].developerName = "Noah Keck"
with open(filepath.parent / "output.json", "w", encoding="utf-8") as fp:
    json.dump(altsrc, fp, indent = 2)
    fp.write("\n") # add missing newline to EOF