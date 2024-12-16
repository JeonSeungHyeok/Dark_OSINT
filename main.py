from app import *
from telegram.telegram import *

def main():
    result = process()
    monitor_and_notify()

if __name__=="__main__":
    main()