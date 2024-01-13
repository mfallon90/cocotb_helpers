

import random
import cocotb
import logging
import zlib
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import Timer, RisingEdge, ClockCycles, First, Combine, FallingEdge

'''
This is a known working frame with a correct CRC
to be used for testing purposes

DEST    = b'\x01\x00\x5E\x28\x64\x01'
SRC     = b'\x2C\xFA\xA2\xA7\x4F\x81'
TYPE    = b'\x08\x00'
DATA1   = b'\x46\xC0\x00\x20\xC6\xC9\x00\x00'
DATA2   = b'\x01\x02\xF4\xE6\x82\xBF\xA0\xFE'
DATA3   = b'\xE0\xA8\x64\x01\x94\x04\x00\x00'
DATA4   = b'\x11\x0A\xAA\x4B\xE0\xA8\x64\x01'
DATA5   = b'\x00\x00\x00\x00\x00\x00\x00\x00'
DATA6   = b'\x00\x00\x00\x00\x00\x00'
CRC     = b'\xD0\x1D\x41\x1B'
'''

class EtherFrame():
    def __init__(self, dst=None, src=None, type=None, payload=None):
        self.dest_mac = dst
        self.src_mac = src
        self.type = type
        self.payload = payload


class RmiiDriver():
    def __init__(self, tb, dut):
        '''
        Initializes Driver

        :param clk: dut clock
        :param tx_data: dut rmii rx signal
        :param tx_data_vld: dut rmii rx valid signal
        '''
        self.rmii_rx_clk = dut.rmii_rx_clk
        self.rmii_rx_data = dut.rmii_rx_data
        self.rmii_rx_dv = dut.rmii_rx_dv
        self.rmii_rx_er = dut.rmii_rx_er
        self.rmii_col = dut.rmii_col
        self.rmii_crs = dut.rmii_crs

        self.rmii_rx_data.value = 0
        self.rmii_rx_dv.value = 0
        self.rmii_rx_er.value = 0
        self.rmii_col.value = 0
        self.rmii_crs.value = 0

        self.preamble = b'\x55\x55\x55\x55\x55\x55\x55\xD5'
        self.broadcast = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        self.sb = tb.sb
        self.ifg = 96
        self.bytes_sent = 0
        self.tb = tb

    async def gen_frame_bytes(self, max_size=1500, dst=None, src=None, type=None, data=None):

        pkt_len = random.randint(46,max_size)

        dst_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF' if dst==None else dst
        src_mac = random.randbytes(6) if src==None else src
        type_len = random.randbytes(2) if type==None else type
        data_pkt = random.randbytes(pkt_len) if data==None else data

        crc_bytes = dst_mac+src_mac+type_len+data_pkt
               
        crc_32 = (zlib.crc32(crc_bytes)).to_bytes(4, 'little')

        frame = crc_bytes+crc_32

        self.bytes_sent = len(data_pkt)

        if (self.sb != None):
            for byte in data_pkt:
                await self.sb.put(byte)

        return frame

    async def send_frame(self, max_size=1500, dst=None, src=None, type=None, data=None):

        frame = await self.gen_frame_bytes(max_size, dst, src, type, data)
        self.tb.bytes_sent += self.bytes_sent

        self.rmii_rx_dv.value = 1
        tx_frame = self.preamble+frame

        for byte in tx_frame:

            msn = byte >> 4
            lsn = byte & 0x0F

            await cocotb.triggers.RisingEdge(self.rmii_rx_clk)
            self.rmii_rx_data.value = lsn

            await cocotb.triggers.RisingEdge(self.rmii_rx_clk)
            self.rmii_rx_data.value = msn

        await RisingEdge(self.rmii_rx_clk)
        self.rmii_rx_dv.value = 0
        self.rmii_rx_data.value = 0

    async def send_rand_frames(self, num_frames=1, max_size=1500, max_delay=None):
        for _ in range(num_frames):
            if max_delay <= self.ifg:
                ifg = self.ifg
            else:
                ifg = random.randint(self.ifg, max_delay)

            await self.send_frame(max_size)
            await Timer(ifg, units='ns')
            await RisingEdge(self.rmii_rx_clk)

        self.tb.send_done = True
