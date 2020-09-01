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
from pathlib import Path

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
    _ = rid.replace("https://pasta.lternet.edu/package/data/eml/", "").split(
        "/"
    )
    scope, identifier, revision = _[0], _[1], _[2]
    pid = f"{scope}.{identifier}.{revision}"
    return pid


def get_eml(pid: str) -> str:
    scope, identifier, revision = pid.split(".")
    url = (
        Config.BASE_PACKAGE_URL
        + f"/metadata/eml/{scope}/{identifier}/{revision}"
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
path_help = "Directory path for which to write SQLite database and CSVs"
newest_help = "Report only on newest data package entities"
db_help = "Use the PASTA+ database directly (must have authorization)"
csv_help = "Write out CSV tables in addition to the SQLite database"
quiet_help = "Silence standard output"


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("scope", nargs=1, required=True)
@click.argument("credentials", nargs=1, required=True)
@click.option("-s", "--start", default="2013-01-01T00:00:00", help=start_help)
@click.option("-e", "--end", default=None, help=end_help)
@click.option("-p", "--path", default=".", help=path_help)
@click.option("-n", "--newest", is_flag=True, default=False, help=newest_help)
@click.option("-d", "--db", is_flag=True, default=False, help=db_help)
@click.option("-c", "--csv", is_flag=True, default=False, help=csv_help)
@click.option("-q", "--quiet", is_flag=True, default=False, help=quiet_help)
def main(
    scope: str,
    credentials: str,
    start: str,
    end: str,
    path: str,
    newest: bool,
    db: bool,
    csv: bool,
    quiet: bool,
):
    """
        Perform analysis of data entity downloads for the given PASTA+ SCOPE
        from START_DATE to END_DATE.

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
        Config.USE_DB = True
    else:
        pasta = pasta_api

    if path is not None:
        if Path(path).exists() and Path(path).is_dir():
            db_path = f"{path}/{scope}"
        else:
            msg = f"'{path}' does not exist or is not a directory"
            raise ValueError(msg)
    else:
        db_path = f"./{scope}"

    entities = pasta.get_entities(scope, newest, end)
    e_db = EntityDB(db_path)
    for entity in entities:
        e = e_db.get(entity[0])
        if e is None:
            pid = entity_to_pid(entity[0])
            count = pasta.get_entity_count(entity[0], start, end)
            if not quiet:
                print(f"{entity[0]} - {entity[1]}: {count}")
            e_db.insert(
                rid=entity[0], pid=pid, date_created=entity[1], count=count
            )

    pids = e_db.get_pids()
    p_db = PackageDB(db_path)
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

    if csv:
        entities_path = f"{db_path}-entities.csv"
        with open(entities_path, "w") as f:
            header = "rid,pid,date_created,count,name\n"
            if not quiet:
                print(header, end="")
            f.write(header)
            entities = e_db.get_all()
            for entity in entities:
                row = (
                    f"{entity.rid},{entity.pid},{entity.date_created},"
                    f'{entity.count},"{entity.name}"\n'
                )
                if not quiet:
                    print(row, end="")
                f.write(row)
        packages_path = f"{db_path}-packages.csv"
        with open(packages_path, "w") as f:
            header = "pid,doi,title,count\n"
            if not quiet:
                print(header, end="")
            f.write(header)
            packages = p_db.get_all()
            for package in packages:
                row = (
                    f"{package.pid},{package.doi},"
                    f'"{package.title}",{package.count}\n'
                )
                if not quiet:
                    print(row, end="")
                f.write(row)

    return 0


if __name__ == "__main__":
    main()
