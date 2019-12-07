import socket
import struct
import sys
import datetime
import threading
import time

#Define all that needs
multicast_group = '224.3.29.72'
multicast_port = 10000
port = 10000
hop_threshold = 3
time_threshold = 1
pesan_buffer = []

# Socket Logic
server_address = ('', port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

def receiver():
    while True:
        data, address = sock.recvfrom(1024)
        data_split = data.split('|')
        pesan = data_split[0]
        hop = int(data_split[1])
        waktu = datetime.datetime.strptime(data_split[2], '%Y-%m-%d %H:%M:%S.%f')

        print("Pesan: {} | Hop: {} | Expired Time: {}".format(pesan,hop,waktu))

        curr_time = datetime.datetime.now()
        current_hop = hop + 1

        if current_hop < hop_threshold:
            print("Jumlah Hop Masih Aman")
            if curr_time < waktu:
                print("Pesan Masih Belum Expired")
                print("Masukan Ke Buffer Pesan")
                addBuffer(pesan,current_hop,waktu)


def addBuffer(pesan,hop,waktu):
    construct_msg = pesan+'|'+str(hop)+'|'+str(waktu)
    global pesan_buffer
    pesan_buffer.append(construct_msg)
    return


def sendBuffer():
    global pesan_buffer
    while True:
        if len(pesan_buffer) > 0:
            for i in range(len(pesan_buffer)):
                data_split = pesan_buffer[i].split('|')
                pesan = data_split[0]
                hop = int(data_split[1])
                waktu = datetime.datetime.strptime(data_split[2], '%Y-%m-%d %H:%M:%S.%f')

                curr_time = datetime.datetime.now()
                if curr_time < waktu:
                    print("Pesan Belum Expired")
                    print("Kirim Pesan ke Multicast Group")
                    sock.sendto(pesan_buffer[i], (multicast_group,multicast_port))
                    time.sleep(5)
                else:
                    pesan_buffer.pop(i)


x = threading.Thread(target=receiver, args=())
x.start()

y = threading.Thread(target=sendBuffer, args=())
y.start()

while True:
    pesan = raw_input('Masukan Pesan: ')
    print("Memasukan Pesan ke Buffer")
    waktu = datetime.datetime.now() + datetime.timedelta(minutes=time_threshold)
    addBuffer(pesan,0,waktu)

