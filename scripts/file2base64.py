import base64
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "input_file", help="The file to be converted to base64"
    )
    parser.add_argument("output_file", help="The file to write the base64 to")
    args = parser.parse_args()

    # Open the input file and read the contents
    with open(args.input_file, "rb") as f:
        content = f.read()

    # Convert the content to base64
    base64_content = base64.b64encode(content).decode("utf-8")

    # Write the base64 to the output file
    with open(args.output_file, "w") as f:
        f.write(base64_content)

    print("Done")


if __name__ == "__main__":
    main()
