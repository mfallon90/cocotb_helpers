

import random
import zlib

def test_frame(max_size=1500, dst=None, src=None, type=None, data=None):

        pkt_len = random.randint(46,max_size)

        dst_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF' if dst==None else dst
        src_mac = random.randbytes(6) if src==None else src
        type_len = random.randbytes(2) if type==None else type
        data_pkt = random.randbytes(pkt_len) if data==None else data

        crc_bytes = b"".join([dst_mac,src_mac,type_len,data_pkt])
               
        crc_out = "%0.8X" % zlib.crc32(crc_bytes)
        crc_rev = crc_out[::-1]
        crc = ''.join([ crc_rev[x:x+2][::-1] for x in range(0, len(crc_rev), 2) ])

        frame = crc_bytes + crc

        return frame