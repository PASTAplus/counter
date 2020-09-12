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
from datetime import datetime
from typing import List

import daiquiri
from lxml import etree
import requests

from counter.config import Config


logger = daiquiri.getLogger(__name__)


def get_entities(scope: str, newest: bool, end: str) -> List:
    entities = list()
    name_url = f"{Config.BASE_PACKAGE_URL}/name/eml/"
    pids = get_pids(scope, newest)
    for pid in pids:
        scope, identifier, revision = pid.split(".")
        url = f"{name_url}/{scope}/{identifier}/{revision}"
        r = requests.get(url, auth=(Config.DN, Config.PW))
        r.raise_for_status()
        rids = [_.split(",")[0] for _ in r.text.strip().split("\n")]
        for rid in rids:
            logger.info(f"get_entities: {rid}")
            rid = rid.replace("%", "%25")  # Percent encode percent literal
            rid = (
                f"{Config.BASE_PACKAGE_URL}/data/eml/{scope}/{identifier}"
                f"/{revision}/{rid}"
            )
            rmd_url = rid.replace("/data/eml/", "/data/rmd/eml/")
            date_created = get_entity_date_created(rmd_url)
            entities.append((rid, date_created))
            logger.info(f"get_entities: {rid} - {date_created}")
        if end is not None:
            end_date = datetime.fromisoformat(end)
            for entity in entities:
                if entity[1] > end_date:
                    logger.info(f"get_entities: removing {entity[0]}")
                    entities.remove(entity)
    return entities


def get_entity_count(rid: str, start: str, end: str) -> int:
    count_url = (
        Config.BASE_AUDIT_URL +
        "/count?serviceMethod=readDataEntity&status=200"
    )
    if start is not None:
        count_url += f"&fromTime={start}"
    if end is not None:
        count_url += f"&toTime={end}"
    rid = rid.replace("%", "%25")  # Percent encode percent literal
    count_url += f"&resourceId={rid}"
    logger.info(f"get_entity_count: {count_url}")
    r = requests.get(count_url, auth=(Config.DN, Config.PW))
    r.raise_for_status()
    count = int(r.text.strip())
    return count


def get_entity_date_created(rmd_url: str) -> datetime:
    r = requests.get(rmd_url, auth=(Config.DN, Config.PW))
    r.raise_for_status()
    try:
        rmd = etree.fromstring(r.text.encode("utf-8"))
        date_created = rmd.find("./dateCreated").text.strip()
        dp = date_created.find(".")
    except Exception as e:
        logger.error(rmd_url)
        logger.error(r.text)
        logger.error(e)
    if dp != -1:
        # Remove fractional seconds
        date_created = date_created[:dp]
    dt = datetime.fromisoformat(date_created)
    logger.info(f"get_entity_date_created: {dt}")
    return dt


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
                logger.info(f"get_pids: {scope}.{identifier}.{revision}")
    if newest:
        for scope_id, revision in series.items():
            pids.append(f"{scope_id}.{revision}")
            logger.info(f"get_pids: {scope_id}.{revision}")
    return pids
