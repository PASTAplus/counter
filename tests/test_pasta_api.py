#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: test_pasta_api

:Synopsis:

:Author:
    servilla

:Created:
    8/29/20
"""
from datetime import datetime

import requests

import counter.pasta_api as pasta_api


def test_get_pids():
    scope = "knb-lter-ble"
    newest = False
    pids_all = pasta_api.get_pids(scope, newest)
    assert len(pids_all) != 0
    newest = True
    pids_newest = pasta_api.get_pids(scope, newest)
    assert len(pids_newest) != 0
    assert len(pids_all) >= len(pids_newest)
    print(len(pids_all), len(pids_newest))


def test_get_entities():
    scope = "knb-lter-ble"
    newest = False
    end = "2020-08-30T00:00:00"
    entities = pasta_api.get_entities(scope, newest, end)
    assert len(entities) != 0


def test_get_entity_date_created():
    rmd_url = (
        "https://pasta.lternet.edu/package/data/rmd/eml/knb-lter-ble/1/1/"
        "a1723e0e5f3c4881f1a7ede1b036aba6"
    )
    date_created = pasta_api.get_entity_date_created(rmd_url)
    assert isinstance(date_created, datetime)


def test_get_entity_count():
    count_url = (
        "https://pasta.lternet.edu/package/data/eml/knb-lter-ble/1/1/"
        "a1723e0e5f3c4881f1a7ede1b036aba6"
    )
    start = "20200101T00:00:00"
    end = "20200830T00:00:00"
    try:
        count = pasta_api.get_entity_count(count_url, start, end)
        assert isinstance(count, int)
    except requests.exceptions.HTTPError as ex:
        assert isinstance(ex, requests.exceptions.HTTPError)




