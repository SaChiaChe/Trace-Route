'''
Trace Route implemented with Python 3.6.0 :: Anaconda custom (64-bit)
Problems:
	1.	Windows has a very annoying firewall ***Windows Defender***
		It blocks the ICMP replys that we need, remenber to shut it
		down before running the program.
	2.	A problem that I still don't know why it occurs:
		When sending the packet immediately after receiving it, somehow I
		can't receive the packets normally, and the time becomes very weird.
		I added a time.sleep(0.1) to prevent from sending too fast, and it 
		works fine now.
'''		

import socket
import sys
import struct
import time
from random import randint

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
CODE = 0
IDENTIFIER = 1
MAX_HOPS = 30
TIMEOUT = 5.0
TRIES = 3
PORT = randint(1024, 49151)
SLEEPTIME = 0.1

def inverter16(N):
	return 65535 - N

def checksum(Type, Code, Identifier, SeqNum):
	# print([hex(x) for x in [Type, Code, Identifier, SeqNum]])
	shiftType = Type<<8
	tempSum = shiftType + Code + Identifier + SeqNum
	Top, Bottom = tempSum>>16, tempSum&0b1111111111111111
	Sum = Top + Bottom
	CheckSum = inverter16(Sum)
	# print("CheckSum:", hex(CheckSum))
	return CheckSum

def MakeHeader(Type, Code, Identifier, SeqNum):
	CheckSum = checksum(Type, Code, Identifier, SeqNum)
	return struct.pack("!BBHHh", Type, Code, CheckSum, Identifier, SeqNum)

# Return False if the packet is incorrect
# Else return True
def CheckPacket(Origin_ID, Origin_SeqNum, IDENTIFIER, SeqNum, Reply_Type):
	# Check Reply ID
	if Origin_ID != IDENTIFIER:
		print("Incorrect identifier")
		print("Received identifier:", Origin_ID)
		return False

	# Check Reply SeqNum
	if Origin_SeqNum != SeqNum:
		print("Incorrect sequence number")
		print("Received sequence number:", Origin_SeqNum)
		return False

	# Check Reply Type
	if Reply_Type != ICMP_TIME_EXCEEDED:
		print("Not ICMP_TIME_EXCEEDED")
		print("Received reply type:", Reply_Type)
		return False

	return True

def CheckArrived(Reply_Type):
	if Reply_Type == ICMP_ECHO_REPLY:
		return True
	return False

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Format: python TraceRoute.py Destination")
		exit(0)

	DestinationHost = sys.argv[1]
	print("Destination:", DestinationHost)

	# Create socket
	ICMPSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
	# print("==========Socket created==========")
	ICMPSocket.settimeout(TIMEOUT)
	ICMPSocket.bind(("0.0.0.0", PORT))

	TTL = 0
	Arrived = False
	SeqNum = randint(123, 456)
	while(TTL < MAX_HOPS and not Arrived):
		TTL += 1
		ReplyTime = []

		ICMPSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, TTL)

		Tries = 0
		addr = ""
		while(Tries < TRIES):
			SeqNum += randint(1, 333)
			# Create header
			Header = MakeHeader(ICMP_ECHO_REQUEST, CODE, IDENTIFIER, SeqNum)
			# print(Header)

			# Send packet
			# print("Send packet to", DestinationHost)
			# print(ICMP_ECHO_REQUEST, CODE, checksum(ICMP_ECHO_REQUEST, CODE, IDENTIFIER, SeqNum), IDENTIFIER, SeqNum)
			ICMPSocket.sendto(Header, (DestinationHost, PORT))
			SendTime = time.time()
			# print("Send time", SendTime, end = "\t")

			while(1):
				try:
					# Receive packet
					# print("Waiting for packet")
					RecvPacket, addr = ICMPSocket.recvfrom(1024)
					RecvTime = time.time()
					RecvICMPHeder = RecvPacket[20:28]
					Reply_Type, Reply_Code, Reply_Checksum, Reply_Other = struct.unpack("!BBHI", RecvICMPHeder)
					# print(Reply_Type)
					# Check if arrived
					if CheckArrived(Reply_Type):
						ReplyTime.append(str(round((RecvTime - SendTime) * 1000, 3)))
						Arrived = True
						break
					RecvOriginICMPHeader = RecvPacket[48:56]
					Origin_Type, Origin_Code, Origin_Checksum, Origin_ID, Origin_SeqNum = struct.unpack("!BBHHh", RecvOriginICMPHeader)
					# print(Origin_Type, Origin_Code, Origin_Checksum, Origin_ID, Origin_SeqNum)
					# Check everthing
					if not CheckPacket(Origin_ID, Origin_SeqNum, IDENTIFIER, SeqNum, Reply_Type):
						continue
					# The packet is correct!!!
					else:
						# print("Receive time", RecvTime)
						ReplyTime.append(str(round((RecvTime - SendTime) * 1000, 3)))
						break

				except socket.timeout:
					# print("Time out")
					ReplyTime.append("*")
					break

			# End of one try
			Tries += 1
			# Sending too fast will cause packet drop(for whatever unknown reason)
			# Also the 
			time.sleep(SLEEPTIME)

		# All Tries ended
		if addr != "":
			print(TTL, addr[0], end = "")
		else:
			print(TTL, end = "")
		for t in ReplyTime:
			if t == "*":
				print("  ", t, end = "")
			else:
				print("  %sms" % t, end = "")
		print("")