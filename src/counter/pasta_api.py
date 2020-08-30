#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: pasta_api

:Synopsis:

:Author:
    servilla

:Created:
    8/29/20
"""
from typing import List

import daiquiri
from lxml import etree
import requests

from counter.config import Config


logger = daiquiri.getLogger(__name__)


def get_entities(scope: str, newest: bool, end: str) -> List:
    entitities = list()
    name_url = f"{Config.BASE_PACKAGE_URL}/name/eml/"
    pids = get_pids(scope, newest)
    for pid in pids:
        scope, identifier, revision = pid.split(".")
        url = f"{name_url}/{scope}/{identifier}/{revision}"
        r = requests.get(url, auth=(Config.DN, Config.PW))
        r.raise_for_status()
        rids = [_.split(",")[0] for _ in r.text.strip().split("\n")]
        for rid in rids:
            rid = (
                f"{Config.BASE_PACKAGE_URL}/data/eml/{scope}/{identifier}"
                f"/{revision}/{rid}"
            )
            entitities.append((rid,))
    return entitities


def get_pids(scope: str, newest: bool) -> List:
    pids = list()
    series = dict()
    scope_url = Config.BASE_PACKAGE_URL + f"/eml/{scope}"
    r = requests.get(scope_url, auth=(Config.DN, Config.PW))
    r.raise_for_status()
    identifiers = [_.strip() for _ in r.text.split("\n")]
    for identifier in identifiers:
        revision_url = scope_url + f"/{identifier}"
        r = requests.get(revision_url, auth=(Config.DN, Config.PW))
        r.raise_for_status()
        revisions = [_.strip() for _ in r.text.split("\n")]
        for revision in revisions:
            if newest:
                rev = series.get(f"{scope}.{identifier}")
                if rev is None:
                    series[f"{scope}.{identifier}"] = revision
                else:
                    if int(revision) > int(rev):
                        series[f"{scope}.{identifier}"] = revision
            else:
                pids.append(f"{scope}.{identifier}.{revision}")
    if newest:
        for scope_id, revision in series.items():
            pids.append(f"{scope_id}.{revision}")
    return pids
