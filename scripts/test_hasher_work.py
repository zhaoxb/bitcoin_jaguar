k = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,\
   0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,\
   0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,\
   0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,\
   0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,\
   0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,\
   0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,\
   0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]


def idx(x, y):
	return (x >> (y * 32)) & 0xFFFFFFFF

def ror(x, y):
	return (x >> y) | ((x << (32 - y)) & 0xFFFFFFFF)

def round(a, b, c, d, e, f, g, h, data, k):
	w14 = idx(data, 14)
	w9 = idx(data, 9)
	w1 = idx(data, 1)
	w0 = idx(data, 0)
	s0 = ror(w1, 7) ^ ror(w1, 18) ^ (w1 >> 3)
	s1 = ror(w14, 17) ^ ror(w14, 19) ^ (w14 >> 10)
	w16 = (w0 + s0 + s1 + w9) & 0xFFFFFFFF

	data = (data >> 32) | (w16 << 480)

	e0 = ror(a, 2) ^ ror(a, 13) ^ ror(a, 22)
	e1 = ror(e, 6) ^ ror(e, 11) ^ ror(e, 25)
	maj = (a & b) ^ (a & c) ^ (b & c)
	ch = (e & f) ^ ((~e) & g)

	t2 = (e0 + maj) & 0xFFFFFFFF
	t1 = (h + e1 + ch + k + w0) & 0xFFFFFFFF

	h = g
        g = f
        f = e
        e = (d + t1) & 0xFFFFFFFF
        d = c
        c = b
        b = a
        a = (t1 + t2) & 0xFFFFFFFF
	
	return (a, b, c, d, e, f, g, h, data)

def hash(state, data):
	a = idx(state, 0)
	b = idx(state, 1)
	c = idx(state, 2)
	d = idx(state, 3)
	e = idx(state, 4)
	f = idx(state, 5)
	g = idx(state, 6)
	h = idx(state, 7)

	for i in range(64):
		(a, b, c, d, e, f, g, h, data) = round(a, b, c, d, e, f, g, h, data, k[i])

		print "\t[%d]\t\t%08x%08x%08x%08x%08x%08x%08x%08x" % (i, h, g, f, e, d, c, b, a)
	
	a = (a + idx(state, 0)) & 0xFFFFFFFF
	b = (b + idx(state, 1)) & 0xFFFFFFFF
	c = (c + idx(state, 2)) & 0xFFFFFFFF
	d = (d + idx(state, 3)) & 0xFFFFFFFF
	e = (e + idx(state, 4)) & 0xFFFFFFFF
	f = (f + idx(state, 5)) & 0xFFFFFFFF
	g = (g + idx(state, 6)) & 0xFFFFFFFF
	h = (h + idx(state, 7)) & 0xFFFFFFFF
	
	return (h << 224) | (g << 192) | (f << 160) | (e << 128) | (d << 96) | (c << 64) | (b << 32) | a

def rev_hex(s):
	s1 = s[::-1]
	s2 = ""
	for i in range(len(s1)/2):
		s2 = s2 + s1[i*2+1] + s1[2*i]
	
	return int("0x" + s2, 0)
	
def rev_s(s):
	s1 = s[::-1]
	s2 = ""
	for i in range(len(s1)/2):
		s2 = s2 + s1[i*2+1] + s1[2*i]
	
	return s2

midstate = 0xCF2C2284BB5840F49C4C66EB4058DB48FEB3668596CA9EE0AA93BECDF981B6AD
data = 0x0000028000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000D40CCA299DB001911DB33532471F4B2

submit_work = "000000029c5ddf3d40bdfd367ad3bc4b0eafab3b129a8d2fafd265a300000000000000003fe20f6d5ebcce84dc6201185d4fe9bff63fcb1fcbd173b1844d0d68ccb0af5533d308a1900db998C0F5A1D00000080000000000000000000000000000000000000000000000000000000000000000000000000000000080020000"
midstate_work = "15bbe675036e3ce712f57f420744cbeb1452bcfe37299d27a30e6572d2ea86c6"

block_data = rev_hex(submit_work[128:152:1])
submit_nonce = rev_hex(submit_work[152:160:1])

block_data = rev_hex("8C1C673F5347ABF61900B3AA")
submit_nonce = rev_hex("aa96f934")
midstate_work = "2C2D4B48AA2DFCA168A8D9B989630531AB380E238E592B7F1C5ADE17BA74C99E"

data = block_data | (submit_nonce << 96) | (0x000002800000000000000000000000000000000000000000000000000000000000000000000000000000000080000000 << 128)
midstate = rev_hex(midstate_work)

hash1 = hash(midstate, data)

print "-------------------------------------------------------------------------"
print "block data = \t\t%32X" %data
print "nonce = \t\t%32X" % submit_nonce
print "midstate = \t\t%32X" % midstate

print "hash1 = \t\t%32X" % hash1
print "-------------------------------------------------------------------------"
hash2 = hash(0x5be0cd191f83d9ab9b05688c510e527fa54ff53a3c6ef372bb67ae856a09e667, (0x0000010000000000000000000000000000000000000000000000000080000000 << 256) | hash1)
print "hash2 = \t\t\t%032X" % hash2
