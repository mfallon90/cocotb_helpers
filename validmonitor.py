import os
import sys
from pathlib import Path
from random import getrandbits
from typing import Any, Dict, List

import cocotb
import pytest
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb.handle import SimHandleBase
from cocotb.queue import Queue
from cocotb.runner import get_runner
from cocotb.triggers import RisingEdge, FallingEdge

class DataValidMonitor:
    """
    Reusable Monitor of one-way control flow (data/valid) streaming data interface

    Args
        clk: clock signal
        valid: control signal noting a transaction occured
        datas: named handles to be sampled when transaction occurs
    """

    def __init__(self, clk, data, valid, error=None):
        self.values = Queue()
        self._clk = clk
        self._data = data
        self._valid = valid
        self._error = error
        self._coro = None

    def start(self) -> None:
        """Start monitor"""
        if self._coro is not None:
            raise RuntimeError("Monitor already started")
        self._coro = cocotb.start_soon(self._run())

    def stop(self) -> None:
        """Stop monitor"""
        if self._coro is None:
            raise RuntimeError("Monitor never started")
        self._coro.kill()
        self._coro = None

    async def _run(self) -> None:
        while True:
            await RisingEdge(self._clk)
            if self._valid.value.binstr != "1":
                await RisingEdge(self._valid)
                continue
            if self._error != None and self._error != "0":
                await FallingEdge(self._error)
                continue
            self.values.put_nowait(self._data)
