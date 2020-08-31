#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: model

:Synopsis:

:Author:
    servilla

:Created:
    8/27/20
"""
from datetime import datetime

import daiquiri
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    desc,
    asc,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import not_

from counter.config import Config

logger = daiquiri.getLogger(__name__)
Base = declarative_base()


class Package(Base):
    __tablename__ = "packages"

    pid = Column(String(), primary_key=True)
    doi = Column(String(), nullable=True, default=None)
    title = Column(String(), nullable=False)
    count = Column(Integer(), nullable=False)


class PackageDB:
    def __init__(self, db: str):
        from sqlalchemy import create_engine

        engine = create_engine("sqlite:///" + db + ".sqlite")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_all(self) -> Query:
        try:
            p = (
                self.session.query(Package)
                .order_by(Package.pid.asc())
            )
        except NoResultFound as ex:
            logger.error(ex)
        return p

    def get(self, pid: str) -> Query:
        try:
             p = (
                self.session.query(Package)
                .filter(Package.pid == pid)
                .first()
            )
        except NoResultFound as ex:
            logger.error(ex)
        return p

    def insert(
        self,
        pid: str,
        doi: str,
        title: str,
        count: int
    ):
        p = Package(
            pid=pid,
            doi=doi,
            title=title,
            count=count
        )
        try:
            self.session.add(p)
            self.session.commit()
            pk = p.pid
        except IntegrityError as ex:
            logger.error(ex)
            self.session.rollback()
            raise ex
        return pk


class Entity(Base):
    __tablename__ = "entities"

    rid = Column(String(), primary_key=True)
    pid = Column(String(), nullable=False)
    date_created = Column(DateTime(), nullable=False)
    count = Column(Integer(), nullable=False)
    name = Column(String(), nullable=True)


class EntityDB:
    def __init__(self, db: str):
        from sqlalchemy import create_engine

        engine = create_engine("sqlite:///" + db + ".sqlite")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get(self, rid: str):
        e = None
        try:
            e = (
                self.session.query(Entity)
                .filter(Entity.rid == rid)
                .first()
            )
        except NoResultFound as ex:
            logger.error(ex)
            self.session.rollback()
        return e

    def get_all(self) -> Query:
        try:
            e = (
                self.session.query(Entity)
                .order_by(Entity.rid.asc())
            )
        except NoResultFound as ex:
            logger.error(ex)
        return e

    def get_pids(self):
        e = None
        try:
            e = self.session.query(Entity.pid).distinct()
        except NoResultFound as ex:
            logger.error(ex)
            self.session.rollback()
        return e

    def get_entities_by_pid(self, pid: str):
        e = None
        try:
            e = (
                self.session.query(Entity)
                .filter(Entity.pid == pid)
            )
        except NoResultFound as ex:
            logger.error(ex)
            self.session.rollback()
        return e

    def insert(
        self,
        rid: str,
        pid: str,
        date_created: datetime,
        name: str = None,
        count: int = 0,
    ):
        e = Entity(
            rid=rid,
            pid=pid,
            date_created=date_created,
            count=count,
            name=name
        )
        try:
            self.session.add(e)
            self.session.commit()
            pk = e.rid
        except IntegrityError as ex:
            logger.error(ex)
            self.session.rollback()
            raise ex
        return pk

    def update(self, rid: str, name: str):
        try:
            e = (
                self.session.query(Entity)
                .filter(Entity.rid == rid)
                .first()
            )
            e.name = name
            self.session.commit()
        except NoResultFound as ex:
            logger.error(ex)
            self.session.rollback()
        return e

