import armchair
import time

INTERVAL = 60  # TODO:  every 60 minutes, move setup to config file eventually


def full(a):
    seconds = INTERVAL * 60
    while True:
        print("Looking for new items")
        a.index_items()
        print("Downloading new items")
        a.grab_items()
        print("Extracting new items with jusText")
        a.process_items()
        print("Waiting for {} minutes.".format(INTERVAL))
        time.sleep(seconds)


def main():
    a = armchair.Armchair()
    full(a)  # TODO: offer fine grained controls via arguments



if __name__ == "__main__":
    main()