import asyncio
import logging as _logging

from typing import Optional
from ibapi.wrapper import EWrapper, Contract, TagValueList
from ibapi.client import FaDataType, ScannerSubscription, ExecutionFilter, Order

from aib import AsyncRxClient, ConvenientWrapper

_logger = _logging.getLogger(__name__)
_logger.setLevel(_logging.ERROR)


class IB(EWrapper, AsyncRxClient):
    def __init__(self, client_id=1, host='127.0.0.1', port=7497):
        AsyncRxClient.__init__(self, wrapper=self)
        self.ib_client_id = client_id
        self.ib_host = host
        self.ib_port = port
        self.req_id: Optional[int] = None

    async def a_client_run(self):
        raise NotImplementedError

    ####################################################################################################################

    @property
    def ready(self) -> bool:
        return self.req_id is not None

    def nextValidId(self, orderId: int):
        self.req_id = orderId
        _logging.debug(f'[IB.nextValidId] use request id = {self.req_id}')

    async def _a_client_run_if_ready(self):
        while not self.ready:
            note = 'Waiting for connection'
            print(note)
            _logger.debug(f'[IB._a_client_run_if_ready] {note}')
            await asyncio.sleep(2)
        await self.a_client_run()

    async def a_run(self):
        note = f'Connecting to {self.ib_host}:{self.ib_port} with client id = {self.ib_client_id}'
        print(note)
        _logger.debug(f'[IB.a_run] {note}')
        # TODO: add exception handling
        await self.connect(self.ib_host, self.ib_port, self.ib_client_id)
        note2 = f'Starting run'
        print(note2)
        _logger.debug(f'[IB.a_run] {note2}')
        await asyncio.gather(self._a_client_run_if_ready(), self.run())

    ####################################################################################################################

    def req_mkt_data(self,
                     contract: Contract, genericTickList: str, snapshot: bool,
                     regulatorySnapshot: bool, mktDataOptions: TagValueList):
        self.reqMktData(self.req_id, contract, genericTickList, snapshot, regulatorySnapshot, mktDataOptions)
        self.req_id += 1

    def req_smart_components(self, bboExchange: str):
        self.reqSmartComponents(self.req_id, bboExchange)
        self.req_id += 1

    def req_tick_by_tick_data(self, contract: Contract, tickType: str, numberOfTicks: int, ignoreSize: bool):
        self.reqTickByTickData(self.req_id, contract, tickType, numberOfTicks, ignoreSize)
        self.req_id += 1

    def calculate_implied_volatility(self,
                                     contract: Contract, optionPrice: float,
                                     underPrice: float, implVolOptions: TagValueList):
        self.calculateImpliedVolatility(self.req_id, contract, optionPrice, underPrice, implVolOptions)
        self.req_id += 1

    def calculate_option_price(self,
                               contract: Contract, volatility: float, underPrice: float, optPrcOptions: TagValueList):
        self.calculateOptionPrice(self.req_id, contract, volatility, underPrice, optPrcOptions)
        self.req_id += 1

    def exercise_options(self,
                          contract:Contract,
                          exerciseAction: int, exerciseQuantity: int, account: str, override: int):
        self.exerciseOptions(self.req_id, contract, exerciseAction, exerciseQuantity, account, override)
        self.req_id += 1

    def place_order(self, contract: Contract, order: Order):
        order.orderId = self.req_id
        self.placeOrder(self.req_id, contract, order)
        self.req_id += 1

    def req_account_summary(self, groupName: str, tags: str):
        self.reqAccountSummary(self.req_id, groupName, tags)
        self.req_id += 1

    def req_positions_multi(self, account: str, modelCode: str):
        self.reqPositionsMulti(self.req_id, account, modelCode)
        self.req_id += 1

    def req_account_updates_multi(self, account: str, modelCode: str, ledgerAndNLV: bool):
        self.reqAccountUpdatesMulti(self.req_id, account, modelCode, ledgerAndNLV)
        self.req_id += 1

    def req_pnl(self, account: str, modelCode: str):
        self.reqPnL(self.req_id, account, modelCode)
        self.req_id += 1

    def req_pnl_single(self, account: str, modelCode: str, conid: int):
        self.reqPnLSingle(self.req_id, account, modelCode, conid)
        self.req_id += 1

    def req_executions(self, execFilter: ExecutionFilter):
        self.reqExecutions(self.req_id, execFilter)
        self.req_id += 1

    def req_contract_details(self, contract: Contract):
        self.reqContractDetails(self.req_id, contract)
        self.req_id += 1

    def req_mkt_depth(self,
                      contract: Contract, numRows: int,
                      isSmartDepth: bool, mktDepthOptions: TagValueList):
        self.reqMktDepth(self.req_id, contract, numRows, isSmartDepth, mktDepthOptions)
        self.req_id += 1

    def replace_fa(self, faData: FaDataType, cxml: str):
        self.replaceFA(self.req_id, faData, cxml)
        self.req_id += 1

    def req_historical_data(self, contract: Contract, endDateTime: str,
                            durationStr: str, barSizeSetting: str, whatToShow: str,
                            useRTH: int, formatDate: int, keepUpToDate: bool, chartOptions: TagValueList):
        self.reqHistoricalData(self.req_id, contract, endDateTime, durationStr, barSizeSetting,
                               whatToShow, useRTH, formatDate, keepUpToDate, chartOptions)
        self.req_id += 1

    def req_head_time_stamp(self, contract: Contract, whatToShow: str, useRTH: int, formatDate: int):
        self.reqHeadTimeStamp(self.req_id, contract, whatToShow, useRTH, formatDate)
        self.req_id += 1

    def req_historical_ticks(self, contract: Contract, startDateTime: str,
                             endDateTime: str, numberOfTicks: int, whatToShow: str,
                             useRth: int, ignoreSize: bool, miscOptions: TagValueList):
        self.reqHistoricalTicks(self.req_id, contract, startDateTime, endDateTime,
                                numberOfTicks, whatToShow, useRth, ignoreSize, miscOptions)
        self.req_id += 1

    def req_scanner_subscription(self,
                                 subscription: ScannerSubscription,
                                 scannerSubscriptionOptions: TagValueList,
                                 scannerSubscriptionFilterOptions: TagValueList):
        self.reqScannerSubscription(self.req_id, subscription,
                                    scannerSubscriptionOptions, scannerSubscriptionFilterOptions)
        self.req_id += 1

    def req_real_time_bars(self,
                           contract: Contract, barSize: int,
                           whatToShow: str, useRTH: bool, realTimeBarsOptions: TagValueList):
        self.reqRealTimeBars(self.req_id, contract, barSize, whatToShow, useRTH, realTimeBarsOptions)
        self.req_id += 1

    def req_fundamental_data(self, contract: Contract, reportType: str, fundamentalDataOptions: TagValueList):
        self.reqFundamentalData(self.req_id, contract, reportType, fundamentalDataOptions)
        self.req_id += 1

    def req_new_article(self, providerCode: str, articleId: str, newsArticleOptions: TagValueList):
        self.reqNewsArticle(self.req_id, providerCode, articleId, newsArticleOptions)
        self.req_id += 1

    def req_historical_news(self,
                            conId: int, providerCodes: str, startDateTime: str, endDateTime: str,
                            totalResults: int, historicalNewsOptions: TagValueList):
        self.reqHistoricalNews(self.req_id, conId, providerCodes,
                               startDateTime, endDateTime, totalResults, historicalNewsOptions)
        self.req_id += 1

    def query_display_groups(self):
        self.queryDisplayGroups(self.req_id)
        self.req_id += 1

    def subscribe_to_group_events(self, groupId: int):
        self.subscribeToGroupEvents(self.req_id, groupId)
        self.req_id += 1

    def update_display_group(self, contractInfo: str):
        self.updateDisplayGroup(self.req_id, contractInfo)
        self.req_id += 1

    def req_sec_def_opt_params(self,
                               underlyingSymbol: str, futFopExchange: str,
                               underlyingSecType: str, underlyingConId: int):
        self.reqSecDefOptParams(self.req_id, underlyingSymbol, futFopExchange, underlyingSecType, underlyingConId)
        self.req_id += 1

    def req_soft_dollar_tiers(self):
        self.reqSoftDollarTiers(self.req_id)
        self.req_id += 1

    def req_matching_symbols(self, pattern: str):
        self.reqMatchingSymbols(self.req_id, pattern)
        self.req_id += 1

    def req_wsh_meta_data(self):
        self.reqWshMetaData(self.req_id)
        self.req_id += 1

    def req_wsh_event_data(self, wshEventData):
        self.reqWshEventData(self.req_id, wshEventData)

    def req_user_info(self):
        self.reqUserInfo(self.req_id)
        self.req_id += 1


class ConvenientIB(ConvenientWrapper, IB):
    def __init__(self, client_id=1, host='127.0.0.1', port=7497):
        self._rx_queue = asyncio.Queue()
        IB.__init__(self, client_id=client_id, host=host, port=port)

    @property
    def rx_queue(self):
        return self._rx_queue

    def nextValidId(self, orderId: int):
        _logger.debug(f'[ConvenientIB.nextValidId]')
        IB.nextValidId(self, orderId)
