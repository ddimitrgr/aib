# aib

Python async client for Interactive Brokers

## Installation
Install with:
```bash
pip install git+https://github.com/ddimitrgr/aib.git@master
```
The TWS API must also be installed. The code has been tested to work with TWS API v10.19.3.

## Usage

See examples/stream.py. For example to fetch tick data for the S&P June 2024 futures contract:
```bash
python stream.py -H 127.0.0.1 -P 7497 -C 1 -e CME -t ES -c FUT -s 20240621
```

## Implementation
<div style="text-align: justify;">
The library is a thin wrapper around the TWS API (ibapi) package. 
It just replaces the <code><strong>Connection</strong></code> and <code><strong>EReader</strong></code>, and subclasses <code><strong>EClient</strong></code>. 
To get asynchronous functionality it substitutes the socket in the <code><strong>Connection</strong></code> class and the queue in <code><strong>EClient</strong></code> with their asynchronous versions. 
</div><br>

New classes:
- <code><strong>AsyncRxClient</strong></code> is the base class for async functionality.
- <code><strong>IB</strong></code> is an async client that also handles the <code><strong>nextValidId()</strong></code> and runs with a single coroutine. To use: subclass and at a minimum implement <code><strong>a_client_run</strong></code>.
- <code><strong>ConvenientIB</strong></code> also uses <code><strong>ConvenientWrapper</strong></code> to wrap the callbacks and capture the results in an async queue. <code><strong>ConvenientWrapper</strong></code> only includes a few IB callbacks, missing callbacks have to added if needed. 
