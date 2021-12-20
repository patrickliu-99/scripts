from PyPDF2 import PdfFileReader, PdfFileWriter
import argparse
import sys


def open_and_rotate_pdf(filepath, dest, rotation):
    pdf_in = open(filepath, 'rb')
    pdf_reader = PdfFileReader(pdf_in)
    pdf_writer = PdfFileWriter()

    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        page.rotateClockwise(rotation)
        pdf_writer.addPage(page)
    out_file = open(dest, 'wb')
    pdf_writer.write(out_file)
    out_file.close()
    pdf_in.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rotates pages in a PDF.')
    parser.add_argument('file', help='Path to the file to be rotated')
    parser.add_argument('dest', help='Destination path for output file')
    parser.add_argument('--dir', required=False,
                        help='Direction to rotate the pages. Enter cw ' +
                        'or ccw. Default is cw')
    parser.add_argument('--angle', type=int,
                        help='Angle to rotate the pages, in degrees.')

    args = parser.parse_args()

    if args.dir is None or args.dir == "cw":
        open_and_rotate_pdf(args.file, args.dest, args.angle)
    elif args.dir == "ccw":
        open_and_rotate_pdf(args.file, args.dest, -args.angle)
    else:
        print("Invalid direction. Options are cw or ccw.")
        sys.exit(1)

    print("Done!")
    sys.exit(0)
