import struct

class Packet(object):
    _PACKET_FORMAT = "!B B B b 11I"

    def __init__(self, version=2, mode=3, tx_timestamp=0):
        # 8 bits
        self.leap = 0
        self.version = version
        self.mode = mode
        # 1 byte unsigned
        self.stratum = 0
        # 1 byte unsigned
        self.poll = 0
        # 1 byte signed
        self.precision = 0  
        # 4 bytes
        self.root_delay = 0
        # 4 bytes
        self.root_dispersion = 0
        # 4 bytes
        self.ref_id = 0 
        # 8 bytes
        self.ref_timestamp = 0 
        # 8 bytes
        self.orig_timestamp = 0 
        # 8 bytes
        self.recv_timestamp = 0 
        # 8 bytes
        self.tx_timestamp = tx_timestamp 

    def marshal(self):
        try:
            packed = struct.pack(
                Packet._PACKET_FORMAT,
                (self.leap << 6 | self.version << 3 | self.mode),
                self.stratum,
                self.poll,
                self.precision,
                int(self.root_delay) << 16 | self._to_frac(self.root_delay, 16),
                int(self.root_dispersion) << 16 |
                self._to_frac(self.root_dispersion, 16),
                self.ref_id,
                int(self.ref_timestamp),
                self._to_frac(self.ref_timestamp),
                int(self.orig_timestamp),
                self._to_frac(self.orig_timestamp),
                int(self.recv_timestamp),
                self._to_frac(self.recv_timestamp),
                int(self.tx_timestamp),
                self._to_frac(self.tx_timestamp))
        except struct.error:
            raise Exception("Invalid NTP packet fields.")
        return packed

    def unmarshal(self, data):
        try:
            unpacked = struct.unpack(
                Packet._PACKET_FORMAT,
                data[0:struct.calcsize(Packet._PACKET_FORMAT)]
            )
        except struct.error:
            raise Exception("Invalid NTP packet.")
        
        print(unpacked)
        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4])/2**16
        self.root_dispersion = float(unpacked[5])/2**16
        self.ref_id = unpacked[6]
        self.ref_timestamp = self._to_time(unpacked[7], unpacked[8])
        self.orig_timestamp = self._to_time(unpacked[9], unpacked[10])
        self.recv_timestamp = self._to_time(unpacked[11], unpacked[12])
        self.tx_timestamp = self._to_time(unpacked[13], unpacked[14])


    def _to_frac(self,timestamp, n=32):
        return int(abs(timestamp - int(timestamp)) * 2**n)

    def _to_time(self,integ, frac, n=32):
        return integ + float(frac)/2**n
