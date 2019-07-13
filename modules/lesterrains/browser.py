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
from weboob.browser import PagesBrowser, URL
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

    search = URL('/index.php\?mode_aff=liste&(?P<query>.*)', SearchPage)

    #housing = URL('/index.php\?mode_aff=maisonterrain&idter=(?P<_id>\d+)', HousingPage)

    housing = URL('http://www.les-terrains.com/index.php?page=terrains&mode_aff=maisonterrain&idter=3192269&ville=montastruc%20la%20conseillere&departement=31', HousingPage)
    
    def get_cities(self, pattern):
        return self.cities.open(city=pattern).get_cities()

    def search_housings(
        self, type, cities, nb_rooms, area_min, area_max,
        cost_min, cost_max, house_types, advert_types
    ):
            if type not in self.TYPES:
                raise TypeNotSupported()
            ret = []
            if type == POSTS_TYPES.VIAGER:
                ret = ['Viager']
            else:
                for house_type in house_types:
                    if house_type in self.RET:
                        ret.append(self.RET.get(house_type))

            # data = {'location': ','.join(cities).encode('iso 8859-1'),
            #         'furnished': type == POSTS_TYPES.FURNISHED_RENT,
            #         'areaMin': area_min or '',
            #         'areaMax': area_max or '',
            #         'priceMin': cost_min or '',
            #         'priceMax': cost_max or '',
            #         'transaction': self.TYPES.get(type, 'location'),
            #         'recherche': '',
            #         'mode': '',
            #         'proximity': '0',
            #         'roomMin': nb_rooms or '',
            #         'page': '1'}

            data = {
                'ville': "montastruc la conseillere",
                'ongletAccueil': 'Terrains'
            }

            # data = {
            #     'ville': ','.join(cities).encode('iso 8859-1'),
            #     'ongletAccueil': 'Terrains'
            # }

            query = urlencode(data)

            return self.search.go(query=query).iter_housings(
                query_type=type,
                advert_types=advert_types
            )

    def get_housing(self, _id, housing=None):
        return self.housing.go(_id=_id).get_housing(obj=housing)