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
import math
from weboob.browser.filters.standard import (CleanDecimal, CleanText, Env, Lower, Regexp, QueryValue)
from weboob.browser.filters.json import Dict
from weboob.browser.filters.html import Attr, AbsoluteLink
from weboob.browser.elements import ItemElement, ListElement, DictElement, method
from weboob.browser.pages import JsonPage, HTMLPage, pagination
from weboob.capabilities.base import NotAvailable, NotLoaded, Currency as BaseCurrency
from weboob.capabilities.housing import (
    Housing, HousingPhoto, City,
    POSTS_TYPES, HOUSE_TYPES, ADVERT_TYPES
)
from weboob.tools.compat import unquote
from .constants import BASE_URL


class CitiesPage(JsonPage):

    ENCODING = 'UTF-8'

    def build_doc(self, content):
        content = super(CitiesPage, self).build_doc(content)
        if content:
            return content
        else:
            return [{"locations": []}]

    @method

    class get_cities(DictElement):

        item_xpath = 'cities'

        class item(ItemElement):

            klass = City

            obj_id = Dict('id')

            obj_name = Dict('id') & CleanText() & Lower() & Regexp(pattern='\d+;(.+)')


class SearchPage(HTMLPage):
    @pagination
    @method
    
    class iter_housings(ListElement):

        item_xpath = '//article[has-class("itemListe")]'

        next_page = AbsoluteLink('./div[@class="pagination-foot-bloc"]/a[@class="pageActive"][2]')

        class item(ItemElement):

            klass = Housing

            obj_type = POSTS_TYPES.SALE

            obj_advert_type = ADVERT_TYPES.PROFESSIONAL

            obj_house_type = HOUSE_TYPES.LAND

            obj_id = QueryValue(
                Attr(
                    './/div[has-class("presentationItem")]/h2/a',
                    'href'
                ),
                'idter'
            )

            def obj_photos(self):
                url = BASE_URL + '/' + Attr(
                    './/div[has-class("photoItemListe")]/img',
                    'data-src'
                )(self)
                if url: return [HousingPhoto(url)]
                else: return []

class HousingPage(HTMLPage):
    @method

    class get_housing(ItemElement):
        
        klass = Housing

        obj_id = Attr(
            './a[has-class("add-to-selection")]',
            'data-id'
        )

        obj_advert_type = ADVERT_TYPES.PROFESSIONAL

        def obj_type(self):
            type = Env('type')(self)
            if type == 'location':
                if 'appartement-meuble' in self.page.url:
                    return POSTS_TYPES.FURNISHED_RENT
                else:
                    return POSTS_TYPES.RENT
            elif type == 'achat':
                return POSTS_TYPES.SALE
            else:
                return NotAvailable

        def obj_url(self):
            return self.page.url

        def obj_house_type(self):
            url = self.obj_url()
            for house_type, types in QUERY_HOUSE_TYPES.items():
                for type in types:
                    if ('/%s/' % type) in url:
                        return house_type
            return NotAvailable

        obj_title = CleanText('//h1[has-class("OfferTop-title")]')

        obj_area = CleanDecimal(
            Regexp(
                CleanText(
                    '//article/header/h1/strong'
                ),
                r'(\d+)',
            ),
            default=NotAvailable
        )

        obj_cost = CleanDecimal(
            '//span[has-class("OfferTop-price")]',
            default=NotAvailable
        )

        obj_text = CleanText('//div[has-class("OfferDetails-content")]/p[1]')

        def obj_photos(self):
            photos = []
            for photo in self.xpath('//div[has-class("OfferSlider")]//img'):
                photo_url = Attr('.', 'src')(photo)
                photo_url = photo_url.replace('640/480', '800/600')
                photos.append(HousingPhoto(photo_url))
            return photos

        obj_rooms = CleanDecimal(
            '//div[has-class("MiniData")]//p[has-class("MiniData-item")][2]',
            default=NotAvailable
        )
        
        obj_bedrooms = CleanDecimal(
            '//div[has-class("MiniData")]//p[has-class("MiniData-item")][3]',
            default=NotAvailable
        )
