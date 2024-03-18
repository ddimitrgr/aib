from dataclasses import dataclass,field
from typing import Optional
from ibapi.wrapper import TickerId, TickAttribBidAsk, Contract, Order, OrderState, ContractDetails, Execution
from ibapi.utils import Decimal


@dataclass
class Error:
    reqId: TickerId
    errorCode: int
    errorString: str
    advancedOrderRejectJson: str = field(default='')


@dataclass
class OrderUpdate:
    orderId: int
    status: str
    filled: float
    remaining: float
    avgFillPrice: float
    permId: int
    parentId: int
    lastFillPrice: float
    clientId: int
    whyHeld: str
    mktCapPrice: float = 0.0


@dataclass
class OpenOrder:
    orderId: int
    contract: Contract
    order: Order
    orderState: OrderState


@dataclass
class OpenOrderEnd:
    pass


@dataclass
class CompletedOrder:
    contract: Contract
    order: Order
    orderState: OrderState


@dataclass
class CompletedOrdersEnd:
    pass


@dataclass
class Snap:
    reqId: int
    time: int
    bidPrice: float
    askPrice: float
    bidSize: float
    askSize: float
    tickAttribBidAsk: TickAttribBidAsk


@dataclass
class ResponseContractDetails:
    reqId: int
    contractDetails: ContractDetails


@dataclass
class ResponseContractDetailsEnd:
    reqId: int


@dataclass
class ResponseExecDetails:
    reqId: int
    contract: Contract
    execution: Execution


@dataclass
class ResponseExecDetailsEnd:
    reqId: int


@dataclass
class Position:
    account: str
    contract: Contract
    position: Decimal
    avgCost: float


@dataclass
class ResponseAccountSummary:
    reqId: int
    account: str
    tag: str
    value: str
    currency: str


@dataclass
class ResponseAccountSummaryEnd:
    reqId: int
