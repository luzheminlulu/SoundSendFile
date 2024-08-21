import pyaudio  
import numpy as np  
from scipy.signal import find_peaks  


# 音频参数  
FORMAT = pyaudio.paInt16  # 音频格式  
CHANNELS = 1  # 单声道  
RATE = 44100  # 采样率  
CHUNK = 800  # 一次读取的数据量  

# 创建PyAudio对象  
p = pyaudio.PyAudio()  

# 开启麦克风流  
stream = p.open(format=FORMAT,  
				channels=CHANNELS,  
				rate=RATE,  
				input=True,  
				frames_per_buffer=CHUNK)  

	
class FREQ:
	IDLE  = 6300
	BIT00 = 5512
	BIT01 = 4900
	BIT10 = 4410
	BIT11 = 4009

class stage:
	IDLE = 0
	NAME = 1
	FILE = 2
	CLIPBOARD = 3
	
 # 定义目标值  
target_values = [
					FREQ.IDLE, 
					FREQ.BIT00, 
					FREQ.BIT01,
					FREQ.BIT10,
					FREQ.BIT11,
					
				]  




state = [FREQ.IDLE for i in range(6)]
#print(state)
strtmp = ''
str = ''
strr = ''

tranStage = stage.IDLE
state_now = FREQ.IDLE
is_file_open = False  
thisFileName = ''

try:  
	while(1):
	
		in_data = stream.read(CHUNK)  
		in_data_int = np.frombuffer(in_data, dtype=np.int16)  # 转换为整数数组  
	
		# 进行FFT变换  
		fft_out = np.fft.fft(in_data_int)
		
		fft_mag = np.abs(fft_out)   
		freqs = np.fft.fftfreq(CHUNK, 1 / RATE)  
		
		freqs = freqs[:len(freqs)//2]  
		fft_mag = fft_mag[:len(fft_mag)//2]  
		
		mask = (freqs >= 3800) & (freqs <= 6500)  
		filtered_magnitudes = fft_mag[mask]  
		filtered_freqs = freqs[mask]  
		
		peaks, _ = find_peaks(filtered_magnitudes, height=7000  )
	
		#for peak in peaks: 
		#	print(f' {filtered_freqs[peak]:.2f} Hz {filtered_magnitudes[peak]:.2f}')  
		#print('\n')
	
		if len(peaks) > 0:  
			highest_peak = filtered_freqs[peaks[np.argmax(filtered_magnitudes[peaks])]]
			
			# 查找与目标值的最小距离  
			closest_target = int(sorted(target_values, key=lambda x: abs(highest_peak - x))[0])
			#print(closest_target)
	

			
			for i in range(4,-1,-1):
				state[i+1] = state[i]
			
			state[0] = closest_target
			#print(closest_target)
			
			if(
				state[0] == FREQ.IDLE and
				state[1] == FREQ.IDLE and
				state[2] == FREQ.IDLE and
				state[3] == FREQ.IDLE and
				state[4] == FREQ.IDLE and
				state[5] == FREQ.IDLE
			):
				
				if(tranStage == stage.NAME):
					if(is_file_open):
						f.close()

					if(thisFileName != strr):
						thisFileName = strr
						print("\nnewFile",thisFileName)
						f = open(thisFileName,'wb')
						is_file_open = True
					else:
						
						print("oldFile",thisFileName)
						is_file_open = False
						
				
				
				str = ''
				strr = ''
				

				tranStage = stage.IDLE
				state_now = FREQ.IDLE

			elif(
				state[0] == FREQ.IDLE and
				state[1] == FREQ.IDLE and
				state[2] == FREQ.IDLE 
			):
				try:
					if(str):
						#print(str)
						
						decimal_value = int(str, 2)  # 将二进制转换为十进制  
						ascii_characters = chr(decimal_value)  # 转换为字符并添加到列表中
						
						if(tranStage == stage.NAME):
	
							strr += ascii_characters
							
						elif(tranStage == stage.FILE):
							if(is_file_open):
								byte_value = decimal_value.to_bytes()
								f.write(byte_value)
							else:
								print(ascii_characters,end='')
						elif(tranStage == stage.CLIPBOARD):
								print(ascii_characters,end='')
							
						#print(ascii_characters)
						
						if(tranStage == stage.IDLE and ascii_characters=='a'):
							tranStage = stage.NAME
						elif(tranStage == stage.IDLE and ascii_characters=='b'):
							tranStage = stage.FILE
						elif(tranStage == stage.IDLE):
							tranStage = stage.CLIPBOARD
					
						#print(ascii_characters,tranStage == stage.IDLE,ascii_characters=='a',tranStage)
				except:
					pass
				str = ''

			elif( state[0] == FREQ.IDLE and state_now in [FREQ.BIT00,FREQ.BIT01,FREQ.BIT10,FREQ.BIT11]):
				str += strtmp
				state_now = FREQ.IDLE
			elif(state[0] == FREQ.BIT00  ):
				strtmp = '00'
				state_now = FREQ.BIT00
			elif(state[0] == FREQ.BIT01 ):
				strtmp = '01'
				state_now = FREQ.BIT01
			elif(state[0] == FREQ.BIT10 ):
				strtmp = '10'
				state_now = FREQ.BIT10
			elif(state[0] == FREQ.BIT11 ):
				strtmp = '11'
				state_now = FREQ.BIT11
				




finally:  
	# 关闭流  
	stream.stop_stream()  
	stream.close()  
	p.terminate()
	