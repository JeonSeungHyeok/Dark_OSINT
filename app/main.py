from app import *
import time

def main():
    process()

if __name__=="__main__":
    hours = int(input('몇시간마다 수집할 것인가요?: '))
    while True:
        main()
        time.sleep(hours*60*60)