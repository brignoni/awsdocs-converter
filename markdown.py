from AWSDocsConverter import AWSDocs, ENTER_DOC_URL


def main():

    url = input(ENTER_DOC_URL)

    doc = AWSDocs(url)

    doc.validate()

    doc.to_markdown()

    return True


if __name__ == "__main__":
    main()
