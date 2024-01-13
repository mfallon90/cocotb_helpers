

import random
import cocotb
import logging
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, RisingEdge, ClockCycles, First, Combine, FallingEdge

class RgmiiDriver():
    def __init__(self, clk, data, ctl):

        self.clk  = clk
        self.data = data
        self.ctl  = ctl

        self.data.value = 0
        self.ctl.value  = 0

    async def send_byte(self, data, valid=True, error=False):
        byte = data & 0xFF
        upper_nibble = byte >> 4
        lower_nibble = data & 0x0F

        await cocotb.triggers.FallingEdge(self.clk)
        self.data.value = lower_nibble
        self.ctl.value  = valid

        await cocotb.triggers.RisingEdge(self.clk)
        self.data.value = upper_nibble
        self.ctl.value  = error

