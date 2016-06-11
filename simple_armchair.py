import armchair

def full(a):
    print("Looking for new items")
    a.index_items()
    print("Downloading new items")
    a.grab_items()
    print("Extracting new items with jusText")
    a.process_items()
 

def main():
    a = armchair.Armchair()
    full(a)  # TODO: offer fine grained controls via arguments


if __name__ == "__main__":
    main()