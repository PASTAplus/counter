#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: pasta_db

:Synopsis:

:Author:
    servilla

:Created:
    8/27/20
"""
from datetime import datetime
from typing import Set

import daiquiri
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from counter.config import Config


logger = daiquiri.getLogger(__name__)


def get_entity_count(rid: str, start: str, end: str, one: bool) -> int:

    if one:
        sql_count = (
            "SELECT COUNT(*) FROM auditmanager.eventlog "
            "WHERE servicemethod='readDataEntity' AND statuscode=200 "
            "AND userid NOT LIKE '%%robot%%' AND resourceid='<RID>'"
        )
    else:
        sql_count = (
            "SELECT COUNT(*) FROM auditmanager.eventlog "
            "WHERE servicemethod='readDataEntity' AND statuscode=200 "
            "AND useragent NOT LIKE '%%DataONE%%' "
            "AND userid NOT LIKE '%%robot%%' AND resourceid='<RID>'"
        )

    sql_count = sql_count.replace("<RID>", rid.replace("%", "%%"))

    if start is not None:
        sql_count += f" AND entrytime >= '{start}'"

    if end is not None:
        sql_count += f" AND entrytime <= '{end}'"

    count = query(Config.DB_HOST_AUDIT, sql_count)
    if Config.VERBOSE == 3:
        print(f"{sql_count}")
        print(f"{rid} - {count[0][0]}")
    return count[0][0]


def get_entities(scope: str, newest: bool, end: str) -> Set:
    sql_entities_all = (
        "SELECT resource_id, date_created "
        "FROM datapackagemanager.resource_registry "
        "WHERE datapackagemanager.resource_registry.resource_type='data' "
        "AND scope='<SCOPE>' AND date_deactivated IS NULL"
    )
    sql_entities_newest = (
        "SELECT resource_id, date_created "
        "FROM datapackagemanager.resource_registry "
        "JOIN most_recent_package_ids "
        "ON resource_registry.package_id=most_recent_package_ids.package_id "
        "WHERE datapackagemanager.resource_registry.resource_type='data' "
        "AND scope='<SCOPE>' AND date_deactivated IS NULL"
    )

    if newest:
        sql_entities = sql_entities_newest.replace("<SCOPE>", scope)
    else:
        sql_entities = sql_entities_all.replace("<SCOPE>", scope)

    if end is not None:
        sql_entities += f" AND date_created <= '{end}'"

    entities = query(Config.DB_HOST_PACKAGE, sql_entities)
    if Config.VERBOSE == 3:
        print(f"{sql_entities}")

    e = set()
    for entity in entities:
        date_created = entity[1].isoformat()
        dp = date_created.find(".")
        if dp != -1:
            # Remove fractional seconds
            date_created = date_created[:dp]
        date_created = datetime.fromisoformat(date_created)
        e.add((entity[0], date_created))
        if Config.VERBOSE == 1:
            print(".", end="", flush=True)
        elif Config.VERBOSE > 1:
            print(f"{entity[0]} - {date_created}")
    return e


def query(host: str, sql: str):
    rs = None
    db = (
        Config.DB_DRIVER
        + "://"
        + Config.DB_USER
        + ":"
        + Config.DB_PW
        + "@"
        + host
        + "/"
        + Config.DB_DB
    )
    engine = create_engine(db)
    try:
        with engine.connect() as connection:
            rs = connection.execute(sql).fetchall()
    except NoResultFound as e:
        logger.warning(e)
        rs = list()
    except Exception as e:
        logger.error(sql)
        logger.error(e)
        raise e
    return rs
