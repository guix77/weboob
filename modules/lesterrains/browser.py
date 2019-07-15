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
import re
from weboob.browser import PagesBrowser, URL
from weboob.browser.filters.standard import CleanText, Lower, Regexp
from weboob.capabilities.housing import (TypeNotSupported, POSTS_TYPES, HOUSE_TYPES)
from weboob.tools.compat import urlencode
from .pages import CitiesPage, SearchPage, HousingPage
from .constants import BASE_URL


class LesterrainsBrowser(PagesBrowser):

    BASEURL = BASE_URL

    TYPES = {
        POSTS_TYPES.SALE: 'vente'
    }
    
    RET = {
        HOUSE_TYPES.LAND: 'Terrain seul'
    }

    cities = URL('/api/get-search.php\?q=(?P<city>.*)', CitiesPage)

    search = URL('/index.php\?mode_aff=liste&ongletAccueil=Terrains&(?P<query>.*)&distance=0', SearchPage)

    housing = URL('/index.php\?page=terrains&mode_aff=un_terrain&idter=(?P<_id>\d+).*', HousingPage)
    
    def get_cities(self, pattern):
        return self.cities.open(city=pattern).get_cities()

    def search_housings(self, cities, area_min, area_max, cost_min, cost_max):

        def get_departement(city):
            return re.split(";", city)[0][:2]

        def get_ville(city):
            return re.split(";", city)[1].lower()

        city = cities[0]
        query = urlencode({
            "departement": get_departement(city),
            "ville": get_ville(city),
            "prixMin": cost_min or '',
            "prixMax": cost_max or '',
            "surfMin": area_min or '',
            "surfMax": area_max or '',
        })
        return self.search.go(query=query).iter_housings()

        # results = []
        # for city in cities:
        #     query = urlencode({
        #         "departement": get_departement(city),
        #         "ville": get_ville(city),
        #         "prixMin": cost_min or '',
        #         "prixMax": cost_max or '',
        #         "surfMin": area_min or '',
        #         "surfMax": area_max or '',
        #     })
        #     result = self.search.go(query=query).iter_housings()
        #     results.append(result)
        # return results

    def get_housing(self, _id, housing=None):
        return self.housing.go(_id = _id).get_housing(obj=housing)