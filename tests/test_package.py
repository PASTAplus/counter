#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: test_package

:Synopsis:

:Author:
    servilla

:Created:
    8/31/20
"""
import pytest
import requests

from counter.config import Config
from counter.package import Package


@pytest.fixture()
def package():
    package_url = f"{Config.BASE_PACKAGE_URL}/metadata/eml/knb-lter-nin/1/1"
    r = requests.get(package_url, auth=Config.AUTH)
    r.raise_for_status()
    return Package(r.text)


def test_git_doi(package):
    doi = package.doi
    assert doi is not None
