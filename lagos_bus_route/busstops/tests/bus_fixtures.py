from django.test import TestCase

from factories.factory import BusStopFactory


class BusStopDataSetup(TestCase):

    def setUp(self):
        self.ojuelegba = BusStopFactory(name='ojuelegba', area='surulere')
        self.ishaga = BusStopFactory(name='ishaga', area='surulere')
        self.municipal = BusStopFactory(name='municipal', area='surulere')
        self.ogunlana = BusStopFactory(name='ogunlana', area='surulere')
        self.lawanson = BusStopFactory(name='lawanson', area='surulere')
        self.itire_rd_jn = BusStopFactory(
            name='itire road junction', area='surulere')
        self.okota_ln_rd = BusStopFactory(
            name='okota link road', area='ijesha')
        self.cele = BusStopFactory(name='cele', area='alimosho')
        self.empire = BusStopFactory(name='empire', area='surulere')
        self.mosalashi = BusStopFactory(name='mosalashi', area='mushin')
        self.idi_oro = BusStopFactory(name='idi oro', area='mushin')
        self.olosha = BusStopFactory(name='olosha', area='mushin')
        self.mushin = BusStopFactory(name='mushin', area='mushin')
        self.yaba = BusStopFactory(name='yaba', area='lagos mainland')
        self.sabo = BusStopFactory(name='sabo', area='lagos mainland')
