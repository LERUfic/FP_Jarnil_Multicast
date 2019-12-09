import socket
import struct
import sys
import datetime
import threading
import time
import random
import math
from geopy.distance import geodesic

#Define all that needs
multicast_group = '224.4.20.12'
multicast_port = 10000
port = 10000
hop_threshold = 3
time_threshold = 1
pesan_buffer = []
base_latitude = 19.99
base_longitude = 73.78
exist_config = False #True jika pesan yang sudah ada di config tidak dimasukan ke buffer lagi. False sebaliknya.

# Socket Configuration
server_address = ('', port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Generate random long lat
dec_lat = random.random()/100
dec_lon = random.random()/100
fix_latitude = base_latitude+dec_lat
fix_longitude = base_longitude+dec_lon
        

def receiver():
    while True:
        data, address = sock.recvfrom(1024)
        data_split = data.split('|')
        pesan = data_split[0]
        hop = int(data_split[1])
        waktu = datetime.datetime.strptime(data_split[2], '%Y-%m-%d %H:%M:%S.%f')
        lat = data_split[3]
        lon = data_split[4]

        jarak = calcDistance(lat,lon)
        time_delay = jarak / 10
        time.sleep(time_delay)

        print("Pesan: {} | Hop: {} | Expired Time: {} | Sender_lat: {} | Sender_lon: {} | Distance: {} meter".format(pesan,hop,waktu,lat,lon, jarak))

        curr_time = datetime.datetime.now()
        current_hop = hop + 1

        if current_hop < hop_threshold:
            print("Jumlah Hop Masih Aman")
            if curr_time < waktu:
                print("Pesan Masih Belum Expired")
                print("Masukan Ke Buffer Pesan")
                addBuffer(pesan,current_hop,waktu,fix_latitude,fix_longitude)


def addBuffer(pesan,hop,waktu,lat,lon):
    construct_msg = pesan+'|'+str(hop)+'|'+str(waktu)+'|'+str(lat)+'|'+str(lon)
    global pesan_buffer
    if exist_config:
        if hop > 0 and len(pesan_buffer) > 0:
            prev_count = hop - 1
            prev_hop = pesan+'|'+str(prev_count)+'|'+str(waktu)
            if prev_hop in pesan_buffer:
                print("Sudah ada di buffer. Tidak Perlu dimasukan kembali")
            else:
                pesan_buffer.append(construct_msg)
        else:
            pesan_buffer.append(construct_msg)    
    else:
        pesan_buffer.append(construct_msg)
    return


def sendBuffer():
    global pesan_buffer
    while True:
        remove_index = []
        if len(pesan_buffer) > 0:
            print pesan_buffer
            for i in range(len(pesan_buffer)):
                data_split = pesan_buffer[i].split('|')
                pesan = data_split[0]
                hop = int(data_split[1])
                waktu = datetime.datetime.strptime(data_split[2], '%Y-%m-%d %H:%M:%S.%f')
                lat = data_split[3]
                lon = data_split[4]

                curr_time = datetime.datetime.now()
                if curr_time < waktu:
                    print("Pesan Belum Expired")
                    print("Kirim Pesan ke Multicast Group")
                    sock.sendto(pesan_buffer[i], (multicast_group,multicast_port))
                    time.sleep(5)
                else:
                    remove_index.append(i)
            init_index = 0
            for i in remove_index:
                i = i - init_index
                pesan_buffer.pop(i)
                init_index = init_index + 1

def calcDistance(sender_latitude, sender_longitude):
    origin = (fix_latitude, fix_longitude)
    dist = (sender_latitude, sender_longitude)

    return geodesic(origin, dist).meters


x = threading.Thread(target=receiver, args=())
x.start()
y = threading.Thread(target=sendBuffer, args=())
y.start()

while True:
    pesan = raw_input('Masukan Pesan: ')
    print("Memasukan Pesan ke Buffer")
    waktu = datetime.datetime.now() + datetime.timedelta(minutes=time_threshold)
    addBuffer(pesan,0,waktu,fix_latitude,fix_longitude)

