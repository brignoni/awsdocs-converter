import sys
import Converter


def main(args):

    doc = Converter.init(args)

    doc.validate()

    doc.to_mobi()


if __name__ == "__main__":
    main(sys.argv[1:])
