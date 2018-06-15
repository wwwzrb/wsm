
import os
import sys

def load(seedFile):
    """
    Load seeds from file [seedFile]
    return a list of seed

    """
    retList = []

    try:
        with open(seedFile, "r") as fr:
            while True:
                line = fr.readline()
                if not line:
                    break
                if line == "":
                    continue
                if line[-1] == "\n":
                    line = line[:-1]
                if line[-1] == "\r":
                    line = line[:-1]
                retList.append(line)
    except Exception as exp:
        var = "Load seed [%s] failed!" % seedFile
        var += "\n" + str(exp)
        print var

    return retList


if __name__ == '__main__':
    "test"
    test = "test.txt"
    ret = load(test)
