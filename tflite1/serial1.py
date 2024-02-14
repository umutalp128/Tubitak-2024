import serial , time
def lora(port = "/dev/serial0",oda = 'test odasi 1'):

    ser = serial.Serial(port,baudrate=9600,timeout=1)
    durum1 = 'y'  
    output = oda + '§' + durum1 
    ser.write(str.encode(output))
    time.sleep(10)
    durum1 = 'n'  
    output = oda + '§' + durum1 
    ser.write(str.encode(output))