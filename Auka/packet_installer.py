###===================WARNING===================###
''' 
Þegar þessi hluti er keyrður þá mun hann reyna að 
pip intsall-a numpy, prettytable og matplotlib.

Kóðin mun spyrja um leyfi y/n fyrir hvern package
ef hann er ekki nú þegar til staðar.

Ef þeir eru nú þegar í tölvunni mun kóðin skila 
"{package name} is already installed."
'''
###=============================================###

import subprocess
import sys


required_packages = []

with open("requirements.txt", "r") as f:
    for line in f:
        package = line.strip()
        if package and not package.startswith("#"):
            required_packages.append(package)

def install_if_missing(package):
    try:
        __import__(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} is missing.")
        choice = input(f"Do you want to install '{package}'? (y/n): ").strip().lower()

        if choice == "y":
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        else:
            print(f"Skipped installing {package}.")

for pkg in required_packages:
    install_if_missing(pkg)