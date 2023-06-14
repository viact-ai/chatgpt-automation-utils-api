import base64
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "input_file", help="The file to read base64 string from"
    )
    parser.add_argument("output_file", help="The file to write result to")
    args = parser.parse_args()

    # Open the input file and read the contents
    with open(args.input_file, "r") as f:
        content = f.read()

    data = base64.b64decode(content).decode("utf-8")

    with open(args.output_file, "w") as f:
        f.write(data)


if __name__ == "__main__":
    main()
