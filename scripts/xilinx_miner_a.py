#!/usr/bin/env python

# by teknohog

# Python wrapper for Xilinx Serial Miner

user = "shingbo_a"
password = "x"
host = "127.0.0.1"
http_port = "8332"

serial_port = "COM7"

askrate = 10

###############################################################################

from jsonrpc import ServiceProxy
#from bitcoinrpc import authproxy
from time import ctime, sleep, time
from serial import Serial
from threading import Thread, Event
from Queue import Queue
import pprint

def stats(count, starttime):
    # 2**32 hashes per share (difficulty 1)
    mhshare = 4294.967296

    s = sum(count)
    tdelta = time() - starttime
    rate = s * mhshare / tdelta

    # This is only a rough estimate of the true hash rate,
    # particularly when the number of events is low. However, since
    # the events follow a Poisson distribution, we can estimate the
    # standard deviation (sqrt(n) for n events). Thus we get some idea
    # on how rough an estimate this is.

    # s should always be positive when this function is called, but
    # checking for robustness anyway
    if s > 0:
        stddev = rate / s**0.5
    else:
        stddev = 0

    return "[%i accepted, %i failed, %.2f +/- %.2f Mhash/s]" % (count[0], count[1], rate, stddev)

class Reader(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.daemon = True

        # flush the input buffer
        ser.flushInput()

    def run(self):
        while True:
            ser_data = ser.readline()
            #print("read from serial port:",  ser_data , "with length = " + str(len(ser_data)))
            #for i in range(len(ser_data)): 
            #        print("ser_data[%2d], is %s" %(i, ser_data[i]))

            if len(ser_data) == 5:
                if (ser_data[4] == "\n"):
                    ser.flushInput()
                    temp = int("0x" + ser_data[0:4:1], 0)
                    temp = temp * 503.975/65536 - 273.15
                    print("[" + ctime() + "] fpga temperature: " + str(temp))
            else: 
                if (len(ser_data) == 9 and ser_data[8] == "\n"):
                    ser.flushInput()
                    nonce = ser_data[0:8:1] 
                    print("yay, nonce hit!!!!!!!!!!!!!!!!!! " + nonce)
                    # Keep this order, because writer.block will be
                    # updated due to the golden event.
                    submitter = Submitter(writer.block, nonce)
                    submitter.start()
                    golden.set()


class Writer(Thread):
    def __init__(self):
        Thread.__init__(self)

        # Keep something sensible available while waiting for the
        # first getwork
        self.block = "0" * 256
        self.midstate = "0" * 64

        self.daemon = True

        # flush write buffer
        ser.flushOutput()

    def run(self):
        while True:
            try:
                work = bitcoin.getwork()
                self.block = work['data']
                self.midstate = work['midstate']
            except:
                print("RPC getwork error")
                # In this case, keep crunching with the old data. It will get 
                # stale at some point, but it's better than doing nothing.

            # Just a reminder of how Python slices work in reverse
            #rdata = self.block.decode('hex')[::-1]
            #rdata2 = rdata[32:64]

            #rdata2 = "2194261a9395e64dbed17115"
			#send data, LSB first, with the 4 msbit first
            rdata = self.block[128:152:1].upper()

            #rmid2 = "228ea4732a3c9ba860c009cda7252b9161a5e75ec8c582a5f106abb3af41f790"
            rmid = self.midstate.upper()
            
            print("<<<<<<<<<<<<<<<get_work-------------------------------")
            pp.pprint(work);
            print("------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            
            #rdata2 = rdata[::-1]
            #rdata1 = ""
            #for i in range(len(rdata2)/2):
            #    rdata1 = rdata1 + rdata2[2*i+1] + rdata2[2*i]
            #
            #rmid2 = rmid[::-1]
            #rmid1 = ""
            #for i in range(len(rmid2)/2):
            #    rmid1 = rmid1 + rmid2[2*i+1] + rmid2[2*i]
            
            #print("test block data: %s" %rdata1)
            #print("test midstate: %s" %rmid1)

			#send tx data first, and then midstate, then the new line symbol
            payload = rdata + rmid + "\n"
            
            ser.write(payload)
            
            result = golden.wait(askrate)
            #result = golden.wait()

            if result:
                golden.clear()

class Submitter(Thread):
    def __init__(self, block, nonce):
        Thread.__init__(self)

        self.block = block
        self.nonce = nonce

    def run(self):
        # This thread will be created upon every submit, as they may
        # come in sooner than the submits finish.

        print("Block found on " + ctime())

        hrnonce = self.nonce[::-1]
        snonce = ""
        for i in range(len(hrnonce)/2):
            snonce = snonce + hrnonce[2*i+1] + hrnonce[2*i]

        data = self.block[:152] + snonce + self.block[160:]

        print("************************submit work---------------------")
        pp.pprint(data)
        print("----------------------------------**********************")

        try:
            result = bitcoin.getwork(data)
            print("Upstream result: " + str(result))
        except:
            print("RPC send error")
            # a sensible boolean for stats
            result = False

        results_queue.put(result)

class Display_stats(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.count = [0, 0]
        self.starttime = time()
        self.daemon = True

        print("Miner started on " + ctime())

    def run(self):
        while True:
            result = results_queue.get()
            
            if result:
                self.count[0] += 1
            else:
                self.count[1] += 1
                
            print(stats(self.count, self.starttime))
                
            results_queue.task_done()

golden = Event()

url = 'http://' + user + ':' + password + '@' + host + ':' + http_port

bitcoin = ServiceProxy(url)
#bitcoin = authproxy.AuthServiceProxy(url)

pp = pprint.PrettyPrinter(indent=4)

results_queue = Queue()

ser = Serial(serial_port, 115200, timeout=askrate)

reader = Reader()
writer = Writer()
disp = Display_stats()

reader.start()
writer.start()
disp.start()

try:
    while True:
        # Threads are generally hard to interrupt. So they are left
        # running as daemons, and we do something simple here that can
        # be easily terminated to bring down the entire script.
        sleep(10000)
except KeyboardInterrupt:
    print("Terminated")

