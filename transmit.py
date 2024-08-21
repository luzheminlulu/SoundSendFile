import pyaudio
import struct as st
import os

FileName = "./transmit.py"


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
	
def callback(in_data, frame_count, time_info, status):
	#print(in_data)
	patch = st.unpack(f'<2048h', bytes(in_data)) 
	print(patch)

	in_data = data[frame_count*CHUNK*2:(frame_count+1)*CHUNK*2]
	return (in_data, pyaudio.paContinue) 
	
	
stream = p.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	#input=True,
	output=True,
	frames_per_buffer=CHUNK,
	#stream_callback=callback
)

stream.start_stream()

def genCode(dataIn):
	oneCode = []
	length = 1250
	
	if(dataIn==-1):
		code = -1
	elif(dataIn=='00'):
		code = 0
	elif(dataIn=='01'):
		code = 1
	elif(dataIn=='10'):
		code = 2
	elif(dataIn=='11'):
		code = 3
	
	c = length//(8+code)
	
	
	for i in range(c):
		for j in range(code+7):
			oneCode+=[0,0]
		oneCode+= [255,127]
	return oneCode

def genAudio(data, type='str', tag='b'):
	if(type=='str'):
		dataB = [format(ord(oneChar),'08b') for oneChar in data]
	elif(type=='bin'):
		dataB = [format(int(oneChar),'08b') for oneChar in data]
		
	dataList = []
	
	for i in range(20):
		dataList += genCode(-1)
	
	s = format(ord(tag),'08b')
	for b in range(4):
		dataList += genCode(s[2*b:2*b+2])
		dataList += genCode(-1)
	dataList += genCode(-1)
		
	for s in dataB:
		for b in range(4):
			dataList += genCode(s[2*b:2*b+2])
			dataList += genCode(-1)
		dataList += genCode(-1)
	return dataList

def send():
	
	BaseName = os.path.basename(FileName)
	
	with open(FileName,'rb') as f:
		oneStr = f.read()
	#oneStr = "Hello, audio from python ! \n"
	
	ones = []
	print('gen name')
	ones += genAudio(BaseName,'str','a')
	print('gen file')
	ones += genAudio(oneStr,'bin','b')

	
	return bytes(ones)
	
	
data = send()

while True:
	stream.write(data)
		
