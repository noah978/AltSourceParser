"""
Project: altparse
Module: altparse
Created Date: 30 Jul 2022
Author: Noah Keck
:------------------------------------------------------------------------------:
MIT License
Copyright (c) 2022
:------------------------------------------------------------------------------:
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests
from packaging import version

from altparse.errors import *
from altparse.helpers import *
from altparse.ipautil import extract_altstore_metadata
from altparse.ipautil.helpers import download_tempfile
from altparse.model import AltSource, update_props_from_new_version
from altparse.parsers import Parser


class AltSourceManager:
    def __init__(self, src: AltSource | None = None, sources_data: list[dict[str]] | None = None, **kwargs):
        """Creates a new AltSourceManager instance to maintain an AltSource.

        If no filepath is provided, a brand new blank source is created.

        Args:
            filepath (Path | str | None, optional): The location of the source to be parsed. Defaults to None.
            sources_data (list | None, optional): A list of sources stored in a dictionary format to be used for adding/updating apps, see examples. Defaults to None.
        """
        self.src_data = sources_data

        if src is None:
            self.src = AltSource(path=(Path.cwd / "altsource.json"))
        else:
            self.src = src

    def create_app(self, download_url: str = "", ipa_path: Path | str = None, **kwargs) -> AltSource.App:
        if download_url=="":
            logging.warning("Users will be unable to download to download the app until a valid download url is set.")
        if not ipa_path and is_url(download_url):
            ipa_path = download_tempfile(download_url)
        if ipa_path:
            if isinstance(str, ipa_path):
                ipa_path = Path(ipa_path)
            metadata = extract_altstore_metadata(ipa_path)
            
            # create initial version
            new_ver = {
                "date": fmt_github_datetime(datetime.utcnow()),
                "size": metadata.get("size"),
                "sha256": metadata.get("sha256"),
                "version": metadata.get("version"),
                "downloadURL": download_url
            }
            new_ver = AltSource.App.Version(new_ver)
            
            # then create the overall app
            metadata = {**metadata,
                "name": "Example App", 
                "developerName": "Example.com", 
                "versions": [],
                "localizedDescription": "An app that is an example.", 
                "iconURL": "https://example.com/icon.png"
            }
            
            if not metadata.get("bundleIdentifier"):
                logging.error("No bundleIdentifier found in IPA.")

            app = AltSource.App(metadata)
            app.add_version(new_ver)
            return app
        return None

    def add(self, app: AltSource.App, **kwargs):
        if not isinstance(app, AltSource.App):
            logging.error("No app added.")
            return
        
        if app.appID is None:
            app.appID = app.bundleIdentifier
            
        if not app.is_valid():
            logging.error("App is invalid.")
        elif app.appID in [app.appID or app.bundleIdentifier for app in self.src.apps]:
            logging.error("Could not add app. Bundle Identifier already exists in AltSource.")
        else:
            self.src.apps.append(app)
            logging.info(f"Adding {app.name} to {self.src.name}")

    def update(self, **kwargs):
        """Updates the primary AltSource using the source data provided to the AltSourceManager.

        Raises:
            ArgumentTypeError: the source data / config has incorrect values
            NotImplementedError: only raised if anything other than exactly one bundleID has been passed to a GithubParser
        """
        logging.info(f"Starting on {self.src.name}")
        existingAppIDs = [app.appID or app.bundleIdentifier for app in self.src.apps]
        existingNewsIDs = [article.identifier for article in self.src.news]
        updatedAppsCount = addedAppsCount = addedNewsCount = 0

        for data in self.src_data:
            try:
                cls = data["parser"].value
                parser = cls(**data["kwargs"])

                # perform different actions depending on the type of file being parsed
                if isinstance(parser, Parser.ALTSOURCE.value):
                    apps = parser.parse_apps(None if data.get("getAllApps") else data.get("ids"))
                    for app in apps:
                        bundleID = app.appID
                        if bundleID in existingAppIDs:
                            # save the old versions property to ensure old versions aren't lost even if the other AltSource isn't tracking them
                            old_app = self.src.apps[existingAppIDs.index(bundleID)]
                            # version will be a lower value if the version is 'older'
                            new_ver = app.latest_version()
                            if new_ver > self.src.apps[existingAppIDs.index(bundleID)].latest_version():
                                updatedAppsCount += 1
                                update_props_from_new_version(old_app, new_ver) # handles incompatibilities with older format AltSources
                                old_app.add_version(new_ver)
                            app._src = old_app._src # use the _src property to avoid overwrite warnings
                            self.src.apps[existingAppIDs.index(bundleID)] = app # note that this actually updates the app regardless of whether the version is newer
                        else:
                            addedAppsCount += 1
                            self.src.apps.append(app)

                    if not data.get("ignoreNews"):
                        news = parser.parse_news(None if data.get("getAllNews") else data.get("ids"))
                        for article in news:
                            newsID = article.identifier
                            if newsID in existingNewsIDs:
                                self.src.news[existingNewsIDs.index(newsID)] = article # overwrite existing news article
                            else:
                                addedNewsCount += 1
                                self.src.news.append(article)

                elif isinstance(parser, Parser.GITHUB.value) or isinstance(parser, Parser.UNC0VER.value):
                    ids = data.get("ids")
                    
                    if ids is None:
                        raise NotImplementedError("Support for updating without specified ids is not supported.")
                    if len(ids) > 1:
                        raise NotImplementedError("Support for parsing multiple ids from one GitHub release is not supported.") # TODO: Fix GithubParser class to be able to process multiple apps using ids to fetch them
                    
                    #fetch_ids = flatten_ids(ids)
                    app_ids = flatten_ids(ids, use_keys=False)
                    #id_conv_tbl = gen_id_parse_table(ids)
                    
                    for i, id in enumerate(app_ids):
                        if not isinstance(id, str):
                            raise ArgumentTypeError("Values in `ids` must all be of type `str`.")
                        if id not in existingAppIDs:
                            logging.warning(f"{id} not found in {self.src.name}. Create an app entry with this bundleID first.")
                            continue

                        app = self.src.apps[existingAppIDs.index(id)]
                        
                        # try to use absoluteVersion if the App contains it
                        if version.parse(app.versions[0].absoluteVersion if app.versions[0].absoluteVersion else app.versions[0].version) < version.parse(parser.version) or (parser.prefer_date and parse_github_datetime(app.versions[0].date) < parse_github_datetime(parser.versionDate)): 
                            metadata = parser.get_asset_metadata()
                            
                            new_ver = {
                                "absoluteVersion": parser.version,
                                "date": parser.versionDate,
                                "localizedDescription": parser.versionDescription,
                                "size": metadata.get("size"),
                                "sha256": metadata.get("sha256"),
                                "version": metadata.get("version") or parser.version,
                                "buildVersion": metadata.get("buildVersion"),
                                "downloadURL": metadata.get("downloadURL")
                            }
                            
                            new_ver = AltSource.App.Version(new_ver)
                            
                            if not metadata.get("bundleIdentifier"):
                                logging.error("No bundleIdentifier found in IPA.")
                            elif metadata["bundleIdentifier"] != app.bundleIdentifier:
                                logging.warning(app.name + " BundleID has changed to " + metadata["bundleIdentifier"])
                                app.bundleIdentifier = metadata["bundleIdentifier"]
                                new_ver.localizedDescription += "\n\nNOTE: BundleIdentifier changed in this version and automatic updates have been disabled until manual install occurs."

                            if app.appID is None:
                                app.appID = id
                            
                            app.add_version(new_ver)
                            app.appPermissions = AltSource.App.Permissions(metadata.get("appPermissions"))
                            updatedAppsCount += 1
                else:
                    raise NotImplementedError("The specified parser class is not supported.")
            except json.JSONDecodeError as err:
                logging.error(f"Unable to process {data.get('ids')}.")
                errstr = str(err).replace('\n', '\n\t') #indent newlines for prettier printing
                logging.error(f"{type(err).__name__}: {errstr[:300]}...") #only print first 300 chars
                continue
            except (version.InvalidVersion, requests.RequestException, requests.ConnectionError, AltSourceError) as err:
                logging.error(f"Unable to process {data.get('ids')}.")
                logging.error(f"{type(err).__name__}: {str(err)}")
                continue
            except StopIteration as err:
                logging.error(f"Unable to process {data.get('ids')}.")
                logging.error(f"{type(err).__name__}: Could not find download asset with matching criteria.")
                continue
            
            # end of for loop
            
        logging.info(f"{updatedAppsCount} app(s) updated.")
        logging.info(f"{addedAppsCount} app(s) added, {addedNewsCount} news article(s) added.")

    def update_hashes(self, only_latest: bool = True, force_update: bool = False):
        """Updates the sha256 hashes for the apps in the AltSource.

        Args:
            only_latest (bool, optional): Only updates missing hashes for the latest version. Defaults to True.
            force_update (bool, optional): Forces every app, every version to update its hash. Defaults to False.
        """
        for app in self.src.apps:
            if only_latest:
                latest_ver = app.latest_version()
                if force_update or latest_ver.sha256 is None:
                    logging.debug(f"Updating {app.name} sha256 checksum.")
                    latest_ver.calculate_sha256()
            else:
                for ver in app.versions:
                    if force_update or ver.sha256 is None:
                        ver.calculate_sha256()

    def alter_app_info(self, alternate_data: dict[str, dict[str, any]]):
        """Uses the provided alternate source info to automatically modify the data in the json.
        
        Caution: this method bypasses the built-in safety and formatting checks.
        
        alternate_data (dict | None, optional): A dictionary containing preferred AltStore app metadata using the bundleID as the key. Defaults to None.
        """
        for i in range(len(self.src.apps)):
            bundleID = self.src.apps[i].appID
            if bundleID in alternate_data.keys():
                for key in alternate_data[bundleID].keys():
                    if key == "appPermissions":
                        self.src.apps[i]._src[key] = AltSource.App.Permissions(alternate_data[bundleID][key])
                    elif key == "versions":
                        self.src.apps[i]._src[key] = [AltSource.App.Version(ver) for ver in alternate_data[bundleID][key]]
                    else:
                        self.src.apps[i]._src[key] = alternate_data[bundleID][key]

    def save(self, alternate_dir: Path | str | None = None, prettify: bool = True, only_standard_props: bool = True):
        """Saves the AltSource the manager is in charge of to file.

        Args:
            prettify (bool, optional): If False, the file will saved as a minified file. Defaults to True.
            alternate_dir (Path | str | None, optional): _description_. Defaults to None.
            only_standard_props (bool, optional): If False, the entire dict used as the backend storage will be output instead of only "normal" AltSource properties. Defaults to True.
        """
        full_src = dict(self.src) if only_standard_props else self.src.to_dict() 
        with open(alternate_dir or self.src.path, "w", encoding="utf-8") as fp:
            json.dump(full_src, fp, indent = 2 if prettify else None)
            fp.write("\n") # add missing newline to EOF
