import logging as _logging

from typing import Optional
from argparse import ArgumentParser
from asyncio import run, CancelledError
from ibapi.contract import Contract

from aib import ConvenientIB

_logging.basicConfig(level=_logging.ERROR)
_logger = _logging.getLogger(__name__)
_logger_ibapi = _logging.getLogger('ibapi')
_logger_ibapi.setLevel(_logging.ERROR)
_logger_aib = _logging.getLogger('aib')
_logger_aib.setLevel(_logging.ERROR)


class ExampleIB(ConvenientIB):
    def __init__(self, client_id: int, host: str, port: int,
                 ticker: str, exchange: str, contract_type: str, currency: str, series: Optional[str] = None):
        super().__init__(client_id, host, port)
        self.client_initiated_disconnect_flag = False
        self.contract = Contract()
        self.contract.symbol = ticker
        self.contract.exchange = exchange
        self.contract.secType = contract_type
        self.contract.currency = currency
        self.contract.lastTradeDateOrContractMonth = series
        self.stored_req_id = None

    async def a_client_run(self):
        self.req_tick_by_tick_data(self.contract, 'BidAsk', 0, False)
        self.stored_req_id = self.req_id - 1
        while True:
            ts, i = await self.rx_queue.get()
            print(i)

    async def a_run(self):
        try:
            await super().a_run()
        except CancelledError as ce:
            pass


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", default='127.0.0.1', required=False, help="Host (default: 127.0.0.1)")
    parser.add_argument("-P", "--port", type=int, default=7497, required=False, help="Host (default: 7497)")
    parser.add_argument("-C", "--client-id", type=int, default=1, required=False, help="TWS/IB gateway Client ID (default: 1)")
    parser.add_argument("-e", "--exchange", required=True, help="Exchange (IDEALPRO for FX or SMART for stocks)")
    parser.add_argument("-t", "--ticker", required=True, help="Ticker symbol")
    parser.add_argument("-c", "--contract-type", required=True, choices=["STK", "OPT", "FUT", "CASH"], help="Contract type")
    parser.add_argument("-b", "--currency", default="USD", required=False, help="Currency (default: USD)")
    parser.add_argument("-s", "--series", required=False, help="Futures series: contract YYYYMM or last trade date YYYYMMDD")

    args = parser.parse_args()
    kwargs = {attr: getattr(args, attr) for attr in vars(args)}
    ib = ExampleIB(**kwargs)
    try:
        run(ib.a_run())
    except KeyboardInterrupt:
        print('Ctrl+C pressed. Exiting.')



