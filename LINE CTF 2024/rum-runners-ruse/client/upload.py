import json
from pwn import remote


SERVER_ADDRESS = 'localhost'
PORT = 11224


def main():
    nc = remote(SERVER_ADDRESS, PORT)

    with open('sign.der', 'rb') as f:
        sign = f.read()
        hex_sign = sign.hex()
    
    nc.send(hex_sign + '\n')
    ret = nc.read().decode('utf-8')
    flag = json.loads(ret)
    print(flag)

main()