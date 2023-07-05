# Spielkram
# Experimente

def eins ():
    print("1")
    return(1)

def zwei ():
    print("2")
    return(2)

def drei ():
    print("3")
    return(3)

spieldict = {
    "one" : eins,
    "two" : zwei,
    "three": drei
}


if __name__ == '__main__':
    
    print("Start")
    erg = spieldict["three"]()
    print (erg)
    print("Stop")