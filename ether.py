import zlib
import random

class EtherFrame():
    def __init__(self, dst=None, src=None, type=None, payload=None):
        self.dest_mac = dst
        self.src_mac = src
        self.type = type
        self.payload = payload

        self.preamble = b'\x55\x55\x55\x55\x55\x55\x55\xD5'
        self.broadcast = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        self.ifg = 96
        self.bytes_sent = 0

    def gen_frame(self, max_size=1500, dst=None, src=None, type=None, data=None):

        pkt_len = random.randint(46,max_size)
        dst_mac = self.broadcast if dst==None else dst
        src_mac = random.randbytes(6) if src==None else src
        eth_type = random.randbytes(2) if type==None else type
        data_pkt = random.randbytes(pkt_len) if data==None else data
        frame = dst_mac + src_mac + eth_type + data_pkt

        return frame

    def get_crc32(self, data):
        return (zlib.crc32(data)).to_bytes(4, 'little')
