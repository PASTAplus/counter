#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: test_pasta_db

:Synopsis:

:Author:
    servilla

:Created:
    8/30/20
"""
import pytest

import counter.pasta_db as pasta_db


def test_get_entities():
    scope = "knb-lter-ble"
    newest = False
    end = "2020-08-30T00:00:00"
    entities = pasta_db.get_entities(scope, newest, end)
    assert len(entities) != 0


def test_get_entity_count():
    count_url = (
        "https://pasta.lternet.edu/package/data/eml/knb-lter-ble/1/1/"
        "a1723e0e5f3c4881f1a7ede1b036aba6"
    )
    start = "20200101T00:00:00"
    end = "20200830T00:00:00"
    count = pasta_db.get_entity_count(count_url, start, end)
    assert isinstance(count, int)

