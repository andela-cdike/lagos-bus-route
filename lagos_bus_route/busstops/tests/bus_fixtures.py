from django.test import TestCase

from factories.factories import BusStopFactory


class BusStopDataSetup(TestCase):

    def setUp(self):
        self.ojuelegba = BusStopFactory(
            name='ojuelegba',
            area='surulere',
            latitude=6.5116042,
            longitude=3.3632648,
            place_id='ChIJkY1cZEaMOxARvEIX3shw_Cw'
        )
        self.ishaga = BusStopFactory(
            name='ishaga',
            area='surulere',
            latitude=6.511819999999999,
            longitude=3.3588687,
            place_id='ChIJNefNeTiMOxARIpN7Ab6DTOM'
        )
        self.municipal = BusStopFactory(
            name='municipal',
            area='surulere',
            latitude=6.511819999999999,
            longitude=3.3588687,
            place_id='ChIJNefNeTiMOxARIpN7Ab6DTOM'
        )
        self.ogunlana = BusStopFactory(
            name='ogunlana',
            area='surulere',
            latitude=6.5122091,
            longitude=3.3530858,
            place_id='ChIJOb37OzqMOxAREIqWVfMLCQk'
        )
        self.lawanson = BusStopFactory(
            name='lawanson',
            area='surulere',
            latitude=6.5124942,
            longitude=3.3485878,
            place_id='ChIJEWdpNiWMOxAR80IQy39jaB8'
        )
        self.itire_rd_jn = BusStopFactory(
            name='itire road junction',
            area='surulere',
            latitude=6.5,
            longitude=3.349999,
            place_id='ChIJz_BscheMOxARahqh9EabAWQ'
        )
        self.okota_ln_rd = BusStopFactory(
            name='okota link road',
            area='ijesha',
            latitude=6.504786999999999,
            longitude=3.325993,
            place_id='ChIJ9zcCSpaOOxARjkFVTcx0t9A'
        )
        self.cele = BusStopFactory(
            name='cele',
            area='express',
            latitude=6.505908000000001,
            longitude=3.3236003,
            place_id='ChIJu6JR1JWOOxARctzaE_eA5y4'
        )
        self.empire = BusStopFactory(
            name='empire',
            area='surulere',
            latitude=6.5182797,
            longitude=3.3653891,
            place_id='ChIJhUgwlk6MOxAR61SvotJLS3s'
        )
        self.mosalashi = BusStopFactory(
            name='moshalasi',
            area='mushin',
            latitude=6.4554155,
            longitude=3.3404996,
            place_id='ChIJVdytzNiLOxARJXz4y3Gcmxs'
        )
        self.idi_oro = BusStopFactory(
            name='idi-oro',
            area='mushin',
            latitude=6.5239452,
            longitude=3.3625889,
            place_id='ChIJx8rQNkuMOxARuy0H5fsuVSo'
        )
        self.olosha = BusStopFactory(
            name='olosha',
            area='mushin',
            latitude=6.5265114,
            longitude=3.3579996,
            place_id='ChIJt3N2ksqNOxARVuloFL9iQtI'
        )
        self.mushin = BusStopFactory(
            name='mushin',
            area='mushin',
            latitude=6.5298744,
            longitude=3.3534721,
            place_id='ChIJGwWeAsyNOxARofhNbapiAHE'
        )
        self.yaba = BusStopFactory(
            name='yaba',
            area='lagos mainland',
            latitude=6.5124729,
            longitude=3.3704156,
            place_id='ChIJ4zBSlVqMOxAROjC8CPCZnXo'
        )
        self.sabo = BusStopFactory(
            name='sabo',
            area='lagos mainland',
            latitude=6.5059306,
            longitude=3.3778238,
            place_id='ChIJe7sCC1-MOxARgia6isloMPs'
        )
