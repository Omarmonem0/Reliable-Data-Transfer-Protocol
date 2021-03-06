import socket
import json
import time
import random
import Shared
import math
import main

SEQ_NUMBER = 0


def send_file_name(data, client_socket):
    new_packet = main.Packet(data, SEQ_NUMBER)
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=main.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def plp():
    return random.uniform(0, 1)


def send_acks(client_socket, seq_num):
    if seq_num == 1:
        new_packet = main.Packet("Ack", ack=1,seq=SEQ_NUMBER)
        toggle()
    else:
        new_packet = main.Packet("Ack", ack=1, seq=1)
    new_packet.deadline = time.time() + 100
    print("sending ack with seq num = ",new_packet.seq_num)
    client_socket.sendto(json.dumps(new_packet, cls=main.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def listen(client_socket):
    while True:
        (packet, address) = client_socket.recvfrom(10000)
        packet = packet.decode()
        packet = main.Packetize(json.loads(packet))
        print("packet found with seq_num = ",packet.seq_num,"My seq_num = ")
        if packet is not None:
            if packet.is_Ack() or packet.seq_num != SEQ_NUMBER:
                if packet.seq_num != SEQ_NUMBER:
                    send_acks(client_socket, 0)
                    print('out of order')
                elif packet.is_Ack():
                    print("Ack")
                else:
                    continue
            else:
                file = open("packet.txt", "a")
                file.write(packet.data)
                file.close()
                send_acks(client_socket, 1)


def client():
    information_list = Shared.read_information_file()
    Shared.SERVER_IP = information_list[0]
    Shared.SERVER_PORT = int(information_list[1])
    Shared.My_Port = int(information_list[2])
    Shared.FILE_NAME = information_list[3]
    Shared.WINDOW_SIZE = int(information_list[4])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((Shared.MY_IP, Shared.My_Port))
    send_file_name(Shared.FILE_NAME, sock)
    listen(sock)


def calculate_checksum(pkt):
    temp = pkt.check_sum
    pkt.check_sum = 0
    text = json.dumps(pkt, cls=main.MyEncoder)
    ascii = ''
    ascii = ascii.join(format(ord(char), 'b')for char in text)
    splitted = split_by_length(ascii,16)
    ans = 0
    for i in range(0, len(splitted)):
        word = int(splitted[i], 2)
        ans += word
    ans = bin(ans)[2:].zfill(16)
    pkt.check_sum=temp
    return ans


def split_by_length(s, block_size):
    w = []
    n = len(s)
    for i in range(0, n, block_size):
        w.append(s[i:i+block_size])
    return w


def toggle():
    global SEQ_NUMBER
    if SEQ_NUMBER == 0:
        SEQ_NUMBER = 1
    else:
        SEQ_NUMBER = 0


client()
