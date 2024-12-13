from app import *
from telegram.telegram import *

def main():
    result = process()
    send_message(result)

if __name__=="__main__":
    main()