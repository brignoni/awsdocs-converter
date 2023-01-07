import sys
import PyWebDoc2Ebook


def main(args):

    PyWebDoc2Ebook.input(args).epub()


if __name__ == "__main__":
    main(sys.argv[1:])
