import os
import subprocess
from contextlib import contextmanager

@contextmanager
def cd(path):
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)

def git_command(command):
    try:
        print(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        return [True, result.returncode, result.stdout, result.stderr]
        # print(f"Command: {command}\nReturn Code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}\n")
    except subprocess.CalledProcessError as e:

        return [False, e.stderr.decode()]
