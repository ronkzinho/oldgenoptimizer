import os
import json
from multiprocessing import Process
from gen import get_gen
import subprocess
import signal
import shutil
import re
import time


def run_seed(generator: str):
    seed = ""
    token = ""
    seed_type = ""
    seedCount = ""
    start = time.time()
    while seed == "":
        cmd = os.popen("cd generator && ./seed").read().strip()
        listedCmd = re.sub("[.|,|@|\\n]", " ", cmd).split(" ")
        if "Seed:" in listedCmd:
            if not(any((map(lambda x: ")" in x, listedCmd)))):
                seed_type = listedCmd[listedCmd.index("Seed") - 1]

            seed = listedCmd[listedCmd.index("Seed:") + 1]
            token = listedCmd[listedCmd.index("Token:") + 1]
            seedCount = listedCmd[listedCmd.index("Seed:") + 3]
    if(seed != "" and token != ""):
        print(f"Generator: {generator} ")
        print(f"Seed: {seed} ")
        print(f"Verification Token: {token} ")
        if seed_type != "":
            print(f"Type: {seed_type} ")
        if seedCount != "":
            print(f"Filtered: {seedCount} ")
        print(f"Duration: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start))} \n")


def start_run():
    with open('settings.json') as filter_json:
        read_json = json.load(filter_json)
        generator = read_json["generator"]
        if not os.path.exists("./generator/seed"):
            if not read_json["generator"]: return print("Invalid generator.")
            if not get_gen(): return print("Invalid generator or something went wrong.")
        else:
            with open("./generator/generator.txt", "r") as file:
                content = file.read()
                if content != read_json["generator"]:
                    shutil.rmtree("./generator/", ignore_errors=True)
                    if not get_gen(True, True): return print("Invalid generator or something went wrong.")
                    else: get_gen()
        num_processes = read_json["thread_count"]
    if(num_processes == 1):
        return run_seed(generator)
    processes = []
    for i in range(num_processes):
        processes.append(Process(target=run_seed, args=(generator,)))
        processes[-1].start()
    i = 0
    while True:
        for j in range(len(processes)):
            if not processes[j].is_alive():
                for k in range(len(processes)):
                    processes[k].kill()
                    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
                    out, err = p.communicate()
                    if(err): return                     
                    for line in out.splitlines():
                        if b'seed' in line:
                            pid = int(line.split(None, 1)[0])
                            os.kill(pid, signal.SIGKILL)
                return
        i = (i + 1) % num_processes


if __name__ == '__main__':
    start_run()
