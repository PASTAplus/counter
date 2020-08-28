#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: package

:Synopsis:

:Author:
    servilla

:Created:
    8/27/20
"""
from lxml import etree

from counter.config import Config
from counter import pasta_db


def clean(text):
    return " ".join(text.split())


def get_entity_name(dataset, rid: str):
    name = None
    urls = dataset.findall("./physical/distribution/online/url")
    for url in urls:
        if rid == url.text.strip():
            name = dataset.find("./entityName").text.strip()
            break
    return name


class Package:
    def __init__(self, eml: str):
        self._eml = etree.fromstring(eml.encode("utf-8"))
        self._title = self._get_title()
        self._doi = self._get_doi()

    @property
    def doi(self):
        return self._doi

    @property
    def title(self):
        return self._title

    def _get_doi(self) -> str:
        doi = None
        alt_ids = self._eml.findall("./dataset/alternateIdentifier")
        for alt_id in alt_ids:
            if alt_id.get("system") == "https://doi.org":
                doi = clean(alt_id.xpath("string()"))
        if doi is None:
            pid = self._get_package_id()
            sql = (
                "SELECT doi FROM datapackagemanager.resource_registry "
                f"WHERE package_id='{pid}' "
                "AND resource_type='dataPackage'"
            )
            _ = pasta_db.query(Config.DB_HOST_PACKAGE, sql)
            doi = _[0][0]
        return doi

    def _get_package_id(self) -> str:
        pid = self._eml.get("packageId")
        return pid

    def _get_title(self) -> str:
        title = clean(self._eml.find("./dataset/title").xpath("string()"))
        return title

    def get_entity_name(self, rid: str) -> str:
        name = None
        datatables = self._eml.findall("./dataset/dataTable")
        for datatable in datatables:
            name = get_entity_name(datatable, rid)
            if name is not None: return name
        otherentities = self._eml.findall("./dataset/otherEntity")
        for otherentity in otherentities:
            name = get_entity_name(otherentity, rid)
            if name is not None: return name
        spatialrasters = self._eml.findall("./dataset/spatialRaster")
        for spatialraster in spatialrasters:
            name = get_entity_name(spatialraster, rid)
            if name is not None: return name
        spatialvectors = self._eml.findall("./dataset/spatialVector")
        for spatialvector in spatialvectors:
            name = get_entity_name(spatialvector, rid)
        return name


