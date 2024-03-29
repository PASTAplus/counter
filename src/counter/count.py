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
from datetime import datetime
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
    level=logging.WARN, outputs=(daiquiri.output.File(logfile), "stdout")
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
    r = requests.get(url, auth=Config.AUTH)
    r.raise_for_status()
    return r.text


def get_work_time(start_time: datetime, end_time: datetime) -> str:
    delta = end_time - start_time
    total_minutes, seconds = divmod(delta.seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    work_time = f"{hours}:{minutes}:{seconds}"
    return work_time


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
verbose_help = (
    "Send output to standard out (-v or -vv or -vvv for increasing output)"
)
one_help = "Include downloads from DataONE"


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
@click.option("-v", "--verbose", count=True, help=verbose_help)
@click.option("-o", "--one", is_flag=True, default=False, help=one_help)
def main(
    scope: str,
    credentials: str,
    start: str,
    end: str,
    path: str,
    newest: bool,
    db: bool,
    csv: bool,
    verbose: int,
    one: bool,
):
    """
        Perform analysis of data entity downloads for the given PASTA+ SCOPE
        from START_DATE to END_DATE.

        \b
            SCOPE: PASTA+ scope value
            CREDENTIALS: User credentials in the form 'DN:PW', where DN is the
                full EDI LDAP distinguished name (e.g., uid=USER,o=EDI,
                dc=edirepository,dc=org) and PW is the corresponding password
    """
    dn, pw = credentials.split(":")
    Config.AUTH = (dn, pw)
    Config.VERBOSE = verbose

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

    start_time = datetime.now()

    if Config.VERBOSE > 0:
        msg = f"Identifying data entities for scope '{scope}':"
        print(msg)
    entities = pasta.get_entities(scope, newest, end)
    ec = len(entities)
    if Config.VERBOSE > 0:
        print("")
    if Config.VERBOSE == 1:
        print("")

    if Config.VERBOSE > 0:
        print(f"Computing counts for {ec} data entities:")
    e_db = EntityDB(db_path)
    for entity in entities:
        e = e_db.get(entity[0])
        if e is None:
            pid = entity_to_pid(entity[0])
            count = pasta.get_entity_count(entity[0], start, end, one)
            if Config.VERBOSE == 1:
                print(".", end="", flush=True)
            elif Config.VERBOSE > 1:
                print(f"{entity[0]} - {count}")
            e_db.insert(
                rid=entity[0], pid=pid, date_created=entity[1], count=count
            )
    if Config.VERBOSE > 0:
        print("")
    if Config.VERBOSE == 1:
        print("")

    pc = e_db.get_pid_count()
    if Config.VERBOSE > 0:
        msg = (
            f"Obtaining title, DOI, and data entity names for "
            f"{pc} data packages:"
        )
        print(msg)
    pids = e_db.get_pids()
    p_db = PackageDB(db_path)
    for pid in pids:
        if p_db.get(pid[0]) is None:
            eml = get_eml(pid[0])
            p = Package(eml)
            if Config.VERBOSE == 1:
                print(".", end="", flush=True)
            elif Config.VERBOSE > 1:
                print(f"{pid[0]} - {p.title} - {p.doi}")
            entities = e_db.get_entities_by_pid(pid[0])
            count = 0
            for entity in entities:
                count += entity.count
                entity_name = p.get_entity_name(entity.rid)
                if Config.VERBOSE == 1:
                    print(".", end="", flush=True)
                elif Config.VERBOSE > 1:
                    print(f"    {entity_name} - {entity.rid}")
                e_db.update(entity.rid, entity_name)
            p_db.insert(pid=pid[0], doi=p.doi, title=p.title, count=count)
    if Config.VERBOSE > 0:
        print("")
    if Config.VERBOSE == 1:
        print("")

    if csv:
        entities_path = f"{db_path}-entities.csv"
        with open(entities_path, "w") as f:
            header = "rid,pid,date_created,count,name\n"
            f.write(header)
            entities = e_db.get_all()
            for entity in entities:
                row = (
                    f"{entity.rid},{entity.pid},{entity.date_created},"
                    f'{entity.count},"{entity.name}"\n'
                )
                f.write(row)
        packages_path = f"{db_path}-packages.csv"
        with open(packages_path, "w") as f:
            header = "pid,doi,title,count\n"
            f.write(header)
            packages = p_db.get_all()
            for package in packages:
                row = (
                    f"{package.pid},{package.doi},"
                    f'"{package.title}",{package.count}\n'
                )
                f.write(row)

    work_time = get_work_time(start_time, datetime.now())
    if Config.VERBOSE > 0:
        msg = (
            f"Total work time for {ec} data entities in {pc} data packages is "
            f"{work_time}"
        )
        print(msg)

    return 0


if __name__ == "__main__":
    main()
