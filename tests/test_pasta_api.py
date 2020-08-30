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
import pytest

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
    end = None
    entities = pasta_api.get_entities(scope, newest, end)
    assert len(entities) != 0

