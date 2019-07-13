# -*- coding: utf-8 -*-

# Copyright(C) 2019      Guntra
#
# This file is part of a weboob module.
#
# This weboob module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This weboob module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this weboob module. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from weboob.tools.backend import Module
from weboob.capabilities.housing import CapHousing
from .browser import LesterrainsBrowser


__all__ = ['LesterrainsModule']

class LesterrainsModule(Module, CapHousing):

    NAME = 'lesterrains'
    DESCRIPTION = 'lesterrains website'
    MAINTAINER = 'Guntra'
    EMAIL = 'guntra@example.com'
    LICENSE = 'LGPLv3+'
    VERSION = '1.6'
    BROWSER = LesterrainsBrowser

    def search_city(self, pattern):
        return self.browser.get_cities(pattern)

    def search_housings(self, query):
        cities = ['%s' % c.id for c in query.cities if c.backend == self.name]
        if len(cities) == 0:
            return list()
        return self.browser.search_housings(
            query.type,
            cities,
            query.nb_rooms,
            query.area_min,
            query.area_max,
            query.cost_min,
            query.cost_max,
            query.house_types,
            query.advert_types
        )
    
    def get_housing(self, housing):
        return self.browser.get_housing(housing)