# NK2 – Automatisering

Python brukes til å sette opp SSH via konsoll. Ansible brukes til å konfigurere Cisco-enhetene R3, R4, MLS2, SW3 og SW4.

## 1. Python

Koble til konsollporten og kjør fra prosjektmappen:

```bash
pip install -r python/requirements.txt
python python/Cisco_setup.py
```

Scriptet spør om port, IP-adresse, brukernavn og passord. Kontroller SSH på enheten etterpå.

## 2. Ansible

Enhetene må ha SSH, og IP-adressene/portene i `inventory.yml` og `host_vars/` må stemme med nettverket.

Installer nødvendige samlinger og gå til Ansible-mappen:

```bash
cd ansible
ansible-galaxy collection install -r requirements.yml
```

Kjør playbookene i denne rekkefølgen:

**Først: Tilgang til MLS2, R3 og R4**

```bash
ansible-playbook playbooks/00_test.yml --limit 'MLS2,R3,R4' -u cisco -k -K
ansible-playbook playbooks/05_kartlegg.yml --limit 'MLS2,R3,R4' -u cisco -k -K
ansible-playbook playbooks/10_routers.yml -u cisco -k -K
```

**Deretter: Tilgang til SW3 og SW4**

Maskinen som kjører Ansible må kunne nå switchene over SSH. Ved første oppsett kan det være nødvendig å koble seg til VLAN 1 på SW3 for å nå de gamle IP-adressene.

```bash
ansible-playbook playbooks/05_kartlegg.yml --limit 'SW3,SW4' -u cisco -k -K
ansible-playbook playbooks/20_switches_l2.yml --limit SW3 -u cisco -k -K
ansible-playbook playbooks/20_switches_l2.yml --limit SW4 -u cisco -k -K
```

**Til slutt: Management-IP, EtherChannel, kontroll og lagring**

```bash
# Bytter management-IP på SW3 og SW4
ansible-playbook playbooks/30_migrate_mgmt.yml -u cisco -k -K -e bekreft_migrering=JA

# EtherChannel på SW4 (begge kabelender må være konfigurert)
ansible-playbook playbooks/40_etherchannel.yml -u cisco -k -K -e bekreft_etherchannel=JA

# Kontroll
ansible-playbook playbooks/50_verify.yml -u cisco -k -K

# Lagre
ansible-playbook playbooks/60_save.yml -u cisco -k -K
```

**Viktig ved `30_migrate_mgmt.yml`:** SSH kan bli brutt ved IP-bytte. SW3 endres fra `172.16.27.23` til `172.16.28.23`, og SW4 fra `172.16.27.24` til `172.16.28.24`. Etterpå må IP-adressene oppdateres i `inventory.yml`. Maskinen som kjører Ansible må ha rute til `172.16.28.0/24` via R3 (`172.16.27.20`), og forbindelsen må testes før `40`, `50` og `60` kjøres. Lagre switchene med `60_save.yml` så snart de nye adressene er tilgjengelige.

**Viktig ved `40_etherchannel.yml`:** Portene i begge ender må ha kompatibelt LACP-oppsett. Kontroller portnumrene før kjøring.

`-u cisco` velger SSH-bruker, `-k` spør etter SSH-passord og `-K` etter enable-passord. Ingen passord skal legges i GitHub.
