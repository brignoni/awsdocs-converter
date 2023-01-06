import sys
import Scrapper


def main(args):

    scrapper = Scrapper.init(args)

    scrapper.validate()

    scrapper.markdown()


if __name__ == "__main__":
    main(sys.argv[1:])
