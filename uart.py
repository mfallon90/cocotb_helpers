

import random
import cocotb
import logging
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, RisingEdge, ClockCycles, First, Combine, FallingEdge


def even_parity(data):
    '''
    Method to caluclate even parity bit
    :param self: class instance (automatic)
    :param data: data for parity calculation
    :return: returns either a 1 or 0 parity bit
    '''
    str = bin(data)
    if (str.count('1') % 2 == 0):
        return 0
    else:
        return 1


def odd_parity(data):
    '''
    Method to caluclate odd parity bit
    :param self: class instance (automatic)
    :param data: data for parity calculation
    :return: returns either a 1 or 0 parity bit
    '''
    str = bin(data)
    if (str.count('1') % 2 == 0):
        return 1
    else:
        return 0

class UartMonitor():
    def __init__(self, clk, rx, baud=9600, bits=8, stop=1, parity=None, sb=None):
        '''
        Initializes Monitor

        :param clk: dut clock
        :param tx: dut uart_rx signal
        :param baud: Desired baud rate. Default is 9600
        :param bits: number of bits in word. Default is 8
        :param stop: number of stop bits. Default is 1
        :param parity: parity bit, 1 for even, 2 for odd. Default is none
        :param sb: scoreboard object (cocotb.queue.Queue()) Default is none
        '''
        self.clk = clk
        self.rx = rx
        self.baud = baud
        self.bits =bits
        self.stop = stop
        self.parity = parity
        self.sb = sb
        self.bit_prd = int(1e9/self.baud)

    async def get(self):
        data = 0

        # Wait for start bit to begin
        if self.rx != 0:
            await FallingEdge(self.rx)
            
        # Wait for start bit to end
        await Timer(self.bit_prd, units='ns')

        for i in range(self.bits):
            # Wait till halfway through bit
            await Timer(self.bit_prd/2, units='ns')
            if self.rx == 1: 
                data = ((2**i)) + data
            await Timer(self.bit_prd/2, units='ns')

        if self.parity == 1:
            # Wait till halfway through bit
            await Timer(self.bit_prd/2, units='ns')
            if (self.rx != even_parity(data)):
                assert (1 == 0)
            await Timer(self.bit_prd/2, units='ns')
        elif self.parity == 2:
            await Timer(self.bit_prd/2, units='ns')
            if (self.rx != odd_parity(data)):
                assert (1 == 0)
            await Timer(self.bit_prd/2, units='ns')

        # Wait for stop bit to end
        for _ in range(self.stop):
            await Timer(self.bit_prd, units='ns')

        return data



class UartDriver():
    def __init__(self, clk, tx, baud=9600, bits=8, stop=1, parity=None, sb=None):
        '''
        Initializes Driver

        :param clk: dut clock
        :param tx: dut uart_rx signal
        :param baud: Desired baud rate. Default is 9600
        :param bits: number of bits in word. Default is 8
        :param stop: number of stop bits. Default is 1
        :param parity: parity bit, 1 for even, 2 for odd. Default is none
        :param sb: scoreboard object (cocotb.queue.Queue()) Default is none
        '''
        self.clk = clk
        self.tx = tx
        self.baud = baud
        self.bits =bits
        self.stop = stop
        self.parity = parity
        self.sb = sb

        self.bit_prd = int(1e9/self.baud)
        self.tx.value = 1

    async def send(self, data=None):
        '''
        Method to send UART data
        :param data: accepts single word or list. Default is single random
        '''

        # If no data is provided, randomize data
        if data==None:
            data_int = random.randint(0, 2**self.bits-1)
        else:
            data_int = data
        
        data_reg = data_int

        # If scoreboard is provided, put data
        if self.sb != None:
            await self.sb.put(data_int)

        # Send start bit
        self.tx.value = 0
        await Timer(self.bit_prd, units='ns')

        # Send data bits
        for _ in range(self.bits):
            if (data_int % 2 == 1):
                self.tx.value = 1
            else:
                self.tx.value = 0

            data_int = data_int >> 1
            await Timer(self.bit_prd, units='ns')

        # Send parity bit
        if self.parity == 1:
            self.tx.value = even_parity(data_reg)
            await Timer(self.bit_prd, units='ns')
        elif self.parity == 2:
            self.tx.value = odd_parity(data_reg)
            await Timer(self.bit_prd, units='ns')

        # Send stop bits
        for _ in range(self.stop):
            self.tx.value = 1
            await Timer(self.bit_prd, units='ns')
