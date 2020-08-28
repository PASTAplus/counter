#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: count

:Synopsis:

:Author:
    servilla

:Created:
    8/27/2020
"""
import logging
import os
from typing import Set

import click
import daiquiri
import requests

from counter.config import Config
from counter import pasta_db
from counter.model import EntityDB, PackageDB
from counter.package import Package

cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + "/download_counter.log"
daiquiri.setup(level=logging.INFO, outputs=(daiquiri.output.File(logfile), "stdout",))
logger = daiquiri.getLogger(__name__)


def entity_to_pid(rid: str) -> str:
    _ = (
        rid.replace("https://pasta.lternet.edu/package/data/eml/", "")
        .split("/")
    )
    scope, identifier, revision = _[0], _[1], _[2]
    pid = f"{scope}.{identifier}.{revision}"
    return pid


def get_eml(pid: str) -> str:
    scope, identifier, revision = pid.split(".")
    url = (
        Config.BASE_PACKAGE_URL +
        f"/metadata/eml/{scope}/{identifier}/{revision}"
    )
    r = requests.get(url, auth=(Config.DN, Config.PW))
    r.raise_for_status()
    return r.text


def get_entities(sql: str) -> Set:
    entities = pasta_db.query(Config.DB_HOST_PACKAGE, sql)
    e = set()
    for entity in entities:
        e.add(entity[0])
    return e


start_help = (
    "Start date from which to begin search in ISO 8601 format"
    "(default is 20130101T00:00:00)"
)
end_help = (
    "End date from which to end search in ISO 8601 format"
    " (default is today)"
)
recent_help = "Report only on newest data package entities"


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("scope", nargs=1, required=True)
@click.option("-s", "--start", default="20130101T00:00:00", help=start_help)
@click.option("-e", "--end", default=None, help=end_help)
@click.option("-n", "--newest", is_flag=True, default=False, help=recent_help)
def main(scope: str, start: str, end: str, newest: bool):
    """
        Perform analysis of data entity downloads for given SCOPE from
        START_DATA to END_DATE.

        \b
            SCOPE: PASTA+ scope value
    """
    sql_entities_all = (
        "SELECT resource_id FROM datapackagemanager.resource_registry "
        "WHERE datapackagemanager.resource_registry.resource_type='data' "
        "AND scope='<SCOPE>' AND date_deactivated IS NULL"
    )
    sql_entities_newest = (
        "SELECT resource_id FROM datapackagemanager.resource_registry "
        "JOIN most_recent_package_ids "
        "ON resource_registry.package_id=most_recent_package_ids.package_id "
        "WHERE datapackagemanager.resource_registry.resource_type='data' "
        "AND scope='<SCOPE>' AND date_deactivated IS NULL"
    )
    sql_count = (
        "SELECT COUNT(*) FROM auditmanager.eventlog "
        "WHERE servicemethod='readDataEntity' AND statuscode=200 "
        "AND NOT userid='robot' AND resourceid='<RID>'"
    )

    if start is not None:
        sql_count += f" AND entrytime >= '{start}'"

    if end is not None:
        sql_count += f" AND entrytime <= '{end}'"

    if newest:
        sql_entities = sql_entities_newest.replace("<SCOPE>", scope)
    else:
        sql_entities = sql_entities_all.replace("<SCOPE>", scope)

    entities = get_entities(sql_entities)
    e_db = EntityDB(scope)
    for entity in entities:
        e = e_db.get(entity)
        if e is None:
            pid = entity_to_pid(entity)
            sql = sql_count.replace("<RID>", entity)
            count = pasta_db.query(Config.DB_HOST_AUDIT, sql)
            print(f"{entity}: {count[0][0]}")
            e_db.insert(rid=entity, pid=pid, count=count[0][0])

    pids = e_db.get_pids()
    p_db = PackageDB(scope)
    for pid in pids:
        print(pid[0])
        eml = get_eml(pid[0])
        p = Package(eml)
        entities = e_db.get_entities_by_pid(pid[0])
        count = 0
        for entity in entities:
            count += entity.count
            print("\t" + entity.rid)
            entity_name = p.get_entity_name(entity.rid)
            e_db.update(entity.rid, entity_name)
        p_db.insert(pid=pid[0], doi=p.doi, title=p.title, count=count)

    return 0


if __name__ == "__main__":
    main()
