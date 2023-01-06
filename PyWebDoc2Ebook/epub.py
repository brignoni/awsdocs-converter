import sys
import Scrapper


def main(args):

    scrapper = Scrapper.init(args)

    scrapper.validate()

    scrapper.epub()


if __name__ == "__main__":
    main(sys.argv[1:])
