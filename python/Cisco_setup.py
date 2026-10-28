"""Enkelt pySerial-eksempel: bootstrap SSH via Cisco CONSOLE.

VIKTIG: Du har allerede et fungerende Python-script. Bruk helst din
original til innlevering. Denne filen er et gjenbrukbart utgangspunkt.
"""
import getpass
import time
import serial


def send(ser, cmd, delay=1.0, show=True):
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    response = ser.read_all().decode(errors="replace")
    if show:
        print(response)
    return response


def main():
    device_type = input("Enhetstype (router/switch): ").strip().lower()
    if device_type not in {"router", "switch"}:
        raise ValueError("Velg router eller switch")
    port = input("COM-port / serialport: ").strip()
    baud = int(input("Baudrate [9600]: ").strip() or "9600")
    hostname = input("Hostname: ").strip()
    ip = input("IP-adresse: ").strip()
    mask = input("Nettmaske: ").strip()
    domain = input("Domain [lab.local]: ").strip() or "lab.local"
    user = input("SSH-brukernavn: ").strip()
    pwd = getpass.getpass("SSH-passord: ")
    enable_pwd = getpass.getpass("Enable-passord: ")
    if device_type == "router":
        interface = input("IP-interface (eks. GigabitEthernet0/0): ").strip()
    else:
        vlan = input("Management-VLAN [1]: ").strip() or "1"
        gateway = input("Default gateway (tom = ingen): ").strip()

    # Man maa foerst avslutte oppstartsveiviser hvis den vises.
    with serial.Serial(port, baudrate=baud, timeout=1) as ser:
        time.sleep(2)
        start = send(ser, "", 2)
        if "initial configuration dialog" in start.lower():
            send(ser, "no", 2)
            send(ser, "", 1)
        send(ser, "enable")
        send(ser, "configure terminal")
        send(ser, "hostname " + hostname)
        send(ser, "ip domain name " + domain)
        send(ser, "username " + user + " privilege 15 secret " + pwd, show=False)
        send(ser, "enable secret " + enable_pwd, show=False)
        if device_type == "router":
            send(ser, "interface " + interface)
            send(ser, "ip address " + ip + " " + mask)
            send(ser, "no shutdown")
            send(ser, "exit")
        else:
            send(ser, "interface vlan " + vlan)
            send(ser, "ip address " + ip + " " + mask)
            send(ser, "no shutdown")
            send(ser, "exit")
            if gateway:
                send(ser, "ip default-gateway " + gateway)
        send(ser, "crypto key generate rsa modulus 2048", 5)
        send(ser, "ip ssh version 2")
        send(ser, "line vty 0 4")
        send(ser, "login local")
        send(ser, "transport input ssh")
        send(ser, "end")
        send(ser, "write memory", 3)
    print("Kommandoer sendt. KONTROLLER med 'show ip ssh' og 'show ip interface brief'.")


if __name__ == "__main__":
    main()
