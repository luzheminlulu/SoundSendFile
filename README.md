利用声音传递数据

项目基于pyAudio，numpy库

transmit.py发送数据
receive.py接收数据

第一版本的数据使用 4QAM、无纠错码、归零码 传递，传输速率很低，约3Byte/s，无纠错码导致误码无法发现和纠错；
音频的频率在4KHz~6.3KHz之间，这是受制于我的麦克风频率响应上限只有8KHz，如何有更好的麦克风，可以尝试用20Khz或更高的频率来降低噪音

未来考虑使用非归零码，并添加纠错码来提高带宽利用率
