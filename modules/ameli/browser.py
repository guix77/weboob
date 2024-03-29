# -*- coding: utf-8 -*-

# Copyright(C) 2013-2015      Christophe Lampin
#
# This file is part of a weboob module.
#
# This weboob module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This weboob module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this weboob module. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from weboob.browser import LoginBrowser, URL, need_login
from weboob.exceptions import BrowserIncorrectPassword, ActionNeeded
from .pages import (
    LoginPage, HomePage, CguPage, AccountPage, LastPaymentsPage, PaymentsPage, PaymentDetailsPage, Raw, UnavailablePage,
)
from weboob.tools.compat import basestring


__all__ = ['AmeliBrowser']


class AmeliBrowser(LoginBrowser):
    BASEURL = 'https://assure.ameli.fr'

    loginp = URL(r'/PortailAS/appmanager/PortailAS/assure\?.*_pageLabel=as_login_page', LoginPage)
    homep = URL(r'/PortailAS/appmanager/PortailAS/assure\?_nfpb=true&_pageLabel=as_accueil_page', HomePage)
    cgup = URL(r'/PortailAS/appmanager/PortailAS/assure\?_nfpb=true&_pageLabel=as_conditions_generales_page', CguPage)
    accountp = URL(r'/PortailAS/appmanager/PortailAS/assure\?_nfpb=true&_pageLabel=as_info_perso_page', AccountPage)
    paymentsp = URL(r'/PortailAS/appmanager/PortailAS/assure\?_nfpb=true&_pageLabel=as_paiements_page', PaymentsPage)
    paymentdetailsp = URL(r'/PortailAS/paiements.do\?actionEvt=chargerDetailPaiements.*', PaymentDetailsPage)
    lastpaymentsp = URL(r'/PortailAS/paiements.do\?actionEvt=afficherPaiements.*', LastPaymentsPage)
    pdf_page = URL(r'PortailAS/PDFServletReleveMensuel.dopdf\?PDF.moisRecherche=.*', Raw)
    unavailablep = URL(r'/vu/INDISPO_COMPTE_ASSURES.html', UnavailablePage)

    def do_login(self):
        self.logger.debug('call Browser.do_login')

        # set this cookie to get login form in response
        self.session.cookies['hbc'] = ''
        self.loginp.stay_or_go()
        if self.homep.is_here():
            return True

        self.page.login(self.username, self.password)

        error = self.page.is_error()
        if error:
            raise BrowserIncorrectPassword(error)

        self.page.locate_to_cgu_page()
        if self.cgup.is_here():
            raise ActionNeeded(self.page.get_cgu())

        self.homep.stay_or_go()  # Redirection not interpreted by browser. Manually redirect on homep

        if not self.homep.is_here():
            raise BrowserIncorrectPassword()

    @need_login
    def iter_subscription_list(self):
        self.logger.debug('call Browser.iter_subscription_list')
        self.accountp.stay_or_go()
        return self.page.iter_subscription_list()

    @need_login
    def get_subscription(self, id):
        self.logger.debug('call Browser.get_subscription')
        assert isinstance(id, basestring)
        for sub in self.iter_subscription_list():
            if id == sub._id:
                return sub
        return None

    @need_login
    def iter_history(self, sub):
        transactions = []
        self.logger.debug('call Browser.iter_history')
        self.paymentsp.stay_or_go()
        payments_url = self.page.get_last_payments_url()
        self.location(payments_url)
        assert self.lastpaymentsp.is_here()
        urls = self.page.iter_last_payments()
        for url in urls:
            self.location(url)
            assert self.paymentdetailsp.is_here()
            for payment in self.page.iter_payment_details(sub):
                transactions.append(payment)

        # go to a page with a "deconnexion" link so that logged property
        # stays True and next call to do_login doesn't crash when using the
        # blackbox
        self.accountp.go()

        return transactions

    @need_login
    def iter_documents(self, sub):
        self.logger.debug('call Browser.iter_documents')
        self.paymentsp.stay_or_go()
        payments_url = self.page.get_last_payments_url()
        self.location(payments_url)
        assert self.lastpaymentsp.is_here()
        for document in self.page.iter_documents(sub):
            yield document

    @need_login
    def get_document(self, id):
        self.logger.debug('call Browser.get_document')
        assert isinstance(id, basestring)
        subs = self.iter_subscription_list()
        for sub in subs:
            for b in self.iter_documents(sub):
                if id == b.id:
                    return b
        return False
