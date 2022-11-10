import sys
import AWSDocsConverter


def main(args):

    doc = AWSDocsConverter.init(args)

    doc.validate()

    doc.to_epub()

    return True


if __name__ == "__main__":
    main(sys.argv[1:])
