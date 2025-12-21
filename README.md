# HOW I CREATED THIS PROJECTS
## 01. LOGIN TO MARIADB
```bash
┌──(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS/bestsecurity-bench]
└─$ sudo mariadb -u root -p
[sudo] password for ricksy: 
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 183
Server version: 11.8.3-MariaDB-1+b1 from Debian -- Please help get to 10k stars at https://github.com/MariaDB/Server

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> 
``` 

## 02. SET `root` PASSWORD
```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY 'hidden';
```

## 03. CREATE PYTHON VIRTUAL ENVIRONMENT
```bash
┌──(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS/]
└─$ python3 -m venv frappe-bench-env-bestsecurity
```
## 04. ACTIVATED THE PYTHON VIRTUAL ENVIRONMENT
```bash
┌──(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS]
└─$ source frappe-bench-env-bestsecurity/bin/activate

┌──(frappe-bench-env-bestsecurity)─(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS]
└─$ 

```
## 05. UPGRADED `pip` INSIDE PYTHON VIRTUAL ENVIRONMENT:

```bash
pip install --upgrade pip
```

## 06. INSTALLED `Frappe Bench` INSIDE PYTHON VIRTUAL ENVIRONMENT

```bash
pip install frappe-bench
```

## 07. CREATED NEW BENCH `bestsecurity-bench`
```bash
bench init bestsecurity-bench 
```

## 08. CREATED THE NEW `bestsecurity.local` SITE
```bash
┌──(frappe-bench-env-bestsecurity)─(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS]
└─$ cd bestsecurity-bench

┌──(frappe-bench-env-bestsecurity)─(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS/bestsecurity-bench]
└─$ bench new-site bestsecurity.local \
  --mariadb-root-username root \
  --mariadb-root-password "hidden" \
  --admin-password "hidden" \
  --db-name best_security \
  --db-user frappeuser \
  --db-password "hidden";

Installing frappe...
Updating DocTypes for frappe        : [========================================] 100%
Updating Dashboard for frappe
bestsecurity.local: SystemSettings.enable_scheduler is UNSET
*** Scheduler is disabled ***
```

## 09. ADD `bestsecurity.local` TO `/etc/host`
```bash
┌──(frappe-bench-env-bestsecurity)─(ricksy㉿Ricksy)-[~/Documents/FRAPPER_PROJECTS/bestsecurity-bench]
└─$ bench --site bestsecurity.local add-to-hosts
[sudo] password for ricksy: 
127.0.0.1	bestsecurity.local
::1	bestsecurity.local
```