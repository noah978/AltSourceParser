"""
Project: altparse
Module: tests
Created Date: 30 Jul 2022
Author: Noah Keck
:------------------------------------------------------------------------------:
MIT License
Copyright (c) 2022
:------------------------------------------------------------------------------:
"""

import sys
import logging

# required for testing in an environment without altparse installed as a package
sys.path.insert(0, './src')
sys.path.insert(1, './src/altparse')

from altparse import AltSourceManager, Parser, altsource_from_file

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

sourcesData = [
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://provenance-emu.com/apps.json"},
        "ids": ["org.provenance-emu.provenance"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://alt.getutm.app"},
        "ids": ["com.utmapp.UTM", "com.utmapp.UTM-SE"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://demo.altstore.io"},
        "ids": ["com.rileytestut.GBA4iOS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "iNDS-Team", "repo_name": "iNDS"},
        "ids": ["net.nerd.iNDS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "yoshisuga", "repo_name": "MAME4iOS"},
        "ids": ["com.example.mame4ios"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "Wh0ba", "repo_name": "XPatcher"},
        "ids": ["com.wh0ba.xpatcher"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "litchie", "repo_name": "dospad"},
        "ids": ["com.litchie.idosgames"]
    },
    {
        "parser": Parser.UNC0VER,
        "kwargs": {"url": "https://unc0ver.dev/releases.json"},
        "ids": ["science.xnu.undecimus"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "ianclawson", "repo_name": "Delta-iPac-Edition"},
        "ids": ["com.ianclawson.DeltaPacEdition"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "T-Pau", "repo_name": "Ready", "ver_parse": lambda x: x.replace("release-", "")},
        "ids": ["at.spiderlab.c64"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "yoshisuga", "repo_name": "activegs-ios"},
        "ids": ["com.yoshisuga.activeGS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "zzanehip", "repo_name": "The-OldOS-Project"},
        "ids": ["com.zurac.OldOS"]
    },
    {
        "parser": Parser.GITHUB,
        "kwargs": {"repo_author": "n3d1117", "repo_name": "appdb", "prefer_date": True},
        "ids": ["it.ned.appdb-ios"]
    },
    {
        "parser": Parser.ALTSOURCE,
        "kwargs": {"filepath": "https://pokemmo.eu/altstore/"},
        "ids": ["eu.pokemmo.client"]
    }
]
alternateAppData = {
    "eu.pokemmo.client": {
        "beta": False
    },
    "com.flyinghead.Flycast": {
      "localizedDescription": "Flycast is a multi-platform Sega Dreamcast, Naomi and Atomiswave emulator derived from reicast.\nInformation about configuration and supported features can be found on TheArcadeStriker's [flycast wiki](https://github.com/TheArcadeStriker/flycast-wiki/wiki).",
      "screenshotURLs": ["https://i.imgur.com/47KjD5a.png", "https://i.imgur.com/MfhD1h1.png", "https://i.imgur.com/wO88IVP.png"]
    },
    "com.rileytestut.GBA4iOS": {
        "iconURL": "https://i.imgur.com/SBrqO9g.png",
        "screenshotURLs": [
            "https://i.imgur.com/L4H0yM3.png",
            "https://i.imgur.com/UPGYLVr.png",
            "https://i.imgur.com/sWpUAii.png",
            "https://i.imgur.com/UwnDXRc.png"
          ]
    },
    "org.provenance-emu.provenance": {
        "localizedDescription": "Provenance is a multi-system emulator frontend for a plethora of retro gaming systems. You can keep all your games in one place, display them with cover art, and play to your heart's content.\n\nSystems Supported:\n\n• Atari\n  - 2600\n  - 5200\n  - 7800\n  - Lynx\n  - Jaguar\n• Bandai\n  - WonderSwan / WonderSwan Color\n• NEC\n  - PC Engine / TurboGrafx-16 (PCE/TG16)\n  - PC Engine Super CD-ROM² System / TurboGrafx-CD\n  - PC Engine SuperGrafx\n  - PC-FX\n• Nintendo\n  - Nintendo Entertainment System / Famicom (NES/FC)\n  - Famicom Disk System\n  - Super Nintendo Entertainment System / Super Famicom (SNES/SFC)\n  - Game Boy / Game Boy Color (GB/GBC)\n  - Virtual Boy\n  - Game Boy Advance (GBA)\n  - Pokémon mini\n• Sega\n  - SG-1000\n  - Master System\n  - Genesis / Mega Drive\n  - Game Gear\n  - CD / MegaCD\n  - 32X\n• SNK\n  - Neo Geo Pocket / Neo Geo Pocket Color\n• Sony\n  - PlayStation (PSX/PS1)",
        "tintColor": "#1c7cf3",
        "permissions": [
            {
              "type": "camera",
              "usageDescription": "Used for album artwork."
            },
            {
              "type": "photos",
              "usageDescription": "Provenance can set custom artworks from your photos or save screenshots to your photos library."
            },
            {
              "type": "music",
              "usageDescription": "This will let you play your imported music on Spotify."
            },
            {
              "type": "bluetooth",
              "usageDescription": "Provenance uses Bluetooth to support game controllers."
            },
            {
              "type": "background-fetch",
              "usageDescription": "Provenance can continue running while in the background."
            },
            {
              "type": "background-audio",
              "usageDescription": "Provenance can continue playing game audio while in the background."
            }
        ]
    }
}

src = altsource_from_file("quantumsource.json")
srcmgr = AltSourceManager(src, sourcesData)

srcmgr.update()
srcmgr.update_hashes()
srcmgr.alter_app_info(alternateAppData)
srcmgr.save(prettify=True) # if prettify is true, output will have indents and newlines
