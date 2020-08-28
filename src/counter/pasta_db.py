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
import daiquiri
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from counter.config import Config


logger = daiquiri.getLogger(__name__)


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
        logger.error(e)
        raise e
    return rs
