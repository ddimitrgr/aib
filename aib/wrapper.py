from datetime import datetime
from asyncio import Queue, Future
from typing import Tuple, Optional, Callable, Any, Self, Dict
from ibapi.commission_report import CommissionReport
from ibapi.wrapper import EWrapper

from aib.objects import Error, Snap, OrderUpdate, OpenOrder, \
                        CompletedOrder, OpenOrderEnd, CompletedOrdersEnd, \
                        Position, ResponseContractDetails, ResponseContractDetailsEnd, \
                        ResponseExecDetails, ResponseExecDetailsEnd, \
                        ResponseAccountSummary, ResponseAccountSummaryEnd

NoDatetime = None

ConvenientWrapperCallable = Callable[['ConvenientWrapper', Any, Any], Tuple[float, Any]]


class ConvenientWrapper(EWrapper):

    @staticmethod
    def put_and_prior(func: ConvenientWrapperCallable) -> ConvenientWrapperCallable:
        def new_func(self: Self, *args, **kwargs) -> Tuple[float, Any]:
            e = func(self, *args, **kwargs)
            self.rx_queue.put_nowait(e)
            getattr(EWrapper, func.__name__)(self, *args, **kwargs)
            return e
        return new_func

    @property
    def rx_queue(self) -> Queue:
        raise NotImplementedError

    @put_and_prior
    def error(self, *args, **kwargs) -> Tuple[Optional[float], Error]:
        e = (NoDatetime, Error(*args, **kwargs))
        return e

    @put_and_prior
    def tickByTickBidAsk(self, *args) -> Tuple[float, Snap]:
        e = (datetime.now().timestamp(), Snap(*args))
        return e

    @put_and_prior
    def orderStatus(self, *args) -> Tuple[float, OrderUpdate]:
        e = (datetime.now().timestamp(), OrderUpdate(*args))
        return e

    ####################################################################################################################

    @put_and_prior
    def openOrder(self, *args) -> Tuple[Optional[float], OpenOrder]:
        e = (NoDatetime, OpenOrder(*args))
        return e

    @put_and_prior
    def openOrderEnd(self) -> Tuple[Optional[float], OpenOrderEnd]:
        e = (NoDatetime, OpenOrderEnd())
        return e

    @put_and_prior
    def completedOrder(self, *args) -> Tuple[Optional[float], CompletedOrder]:
        e = (NoDatetime, CompletedOrder(*args))
        return e

    @put_and_prior
    def completedOrdersEnd(self) -> Tuple[Optional[float], CompletedOrdersEnd]:
        e = (NoDatetime, CompletedOrdersEnd())
        return e

    @put_and_prior
    def position(self, *args) -> Tuple[Optional[float], Position]:
        e = (NoDatetime, Position(*args))
        return e

    @put_and_prior
    def contractDetails(self, *args) -> Tuple[Optional[float], ResponseContractDetails]:
        e = (NoDatetime, ResponseContractDetails(*args))
        return e

    @put_and_prior
    def contractDetailsEnd(self, *args) -> Tuple[Optional[float], ResponseContractDetailsEnd]:
        e = (NoDatetime, ResponseContractDetailsEnd(*args))
        return e

    @put_and_prior
    def commissionReport(self, commissionReport: CommissionReport) -> Tuple[Optional[float], CommissionReport]:
        e = (NoDatetime, commissionReport)
        return e

    @put_and_prior
    def execDetails(self, *args) -> Tuple[Optional[float], ResponseExecDetails]:
        e = (NoDatetime, ResponseExecDetails(*args))
        return e

    @put_and_prior
    def execDetailsEnd(self, *args) -> Tuple[Optional[float], ResponseExecDetailsEnd]:
        e = (NoDatetime, ResponseExecDetailsEnd(*args))
        return e

    ####################################################################################################################

    @put_and_prior
    def accountSummary(self, *args) -> Tuple[Optional[float], ResponseAccountSummary]:
        e = (NoDatetime, ResponseAccountSummary(*args))
        return e

    @put_and_prior
    def accountSummaryEnd(self, *args) -> Tuple[Optional[float], ResponseAccountSummaryEnd]:
        e = (NoDatetime, ResponseAccountSummaryEnd(*args))
        return e
