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
from counter import pasta_api
from counter import pasta_db
from counter.model import EntityDB, PackageDB
from counter.package import Package

cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + "/counter.log"
daiquiri.setup(
    level=logging.WARN, outputs=(daiquiri.output.File(logfile), "stdout",)
)
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


start_help = (
    "Start date from which to begin search in ISO 8601 format"
    "(default is 2013-01-01T00:00:00)"
)
end_help = (
    "End date from which to end search in ISO 8601 format"
    " (default is today)"
)
newest_help = "Report only on newest data package entities"
db_help = "Use the PASTA+ database directly (must have authorization)"
quiet_help = "Silence standard output"


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("scope", nargs=1, required=True)
@click.argument("credentials", nargs=1, required=True)
@click.option("-s", "--start", default="2013-01-01T00:00:00", help=start_help)
@click.option("-e", "--end", default=None, help=end_help)
@click.option("-n", "--newest", is_flag=True, default=False, help=newest_help)
@click.option("-d", "--db", is_flag=True, default=False, help=db_help)
@click.option("-q", "--quiet", is_flag=True, default=False, help=quiet_help)
def main(
    scope: str,
    credentials: str,
    start: str,
    end: str,
    newest: bool,
    db: bool,
    quiet: bool
):
    """
        Perform analysis of data entity downloads for given SCOPE from
        START_DATA to END_DATE.

        \b
            SCOPE: PASTA+ scope value
            CREDENTIALS: User credentials in the form 'DN:PW', where DN is the
                EDI LDAP distinguished name and PW is the corresponding password
    """
    dn, pw = credentials.split(":")
    Config.DN = dn
    Config.PW = pw

    if db:
        pasta = pasta_db
    else:
        pasta = pasta_api

    entities = pasta.get_entities(scope, newest, end)
    e_db = EntityDB(scope)
    for entity in entities:
        e = e_db.get(entity[0])
        if e is None:
            pid = entity_to_pid(entity[0])
            count = pasta.get_entity_count(entity[0], start, end)
            if not quiet:
                print(f"{entity[0]} - {entity[1]}: {count}")
            e_db.insert(
                rid=entity[0], pid=pid, datecreated=entity[1], count=count
            )

    pids = e_db.get_pids()
    p_db = PackageDB(scope)
    for pid in pids:
        if p_db.get(pid[0]) is None:
            if not quiet:
                print(pid[0])
            eml = get_eml(pid[0])
            p = Package(eml)
            entities = e_db.get_entities_by_pid(pid[0])
            count = 0
            for entity in entities:
                count += entity.count
                if not quiet:
                    print("    " + entity.rid)
                entity_name = p.get_entity_name(entity.rid)
                e_db.update(entity.rid, entity_name)
            p_db.insert(pid=pid[0], doi=p.doi, title=p.title, count=count)

    return 0


if __name__ == "__main__":
    main()
