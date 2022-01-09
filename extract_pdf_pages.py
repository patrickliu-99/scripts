import PyPDF2
import argparse

from util import check_input_path, check_output_path


def get_range(value, pagecount):
    """
    Checks that a string can be parsed as a range in the format:
        start-end
    Or simply as an integer on its own:
        x
    Where start < end.

    Returns a list of pages to extract.
    """
    parts = [int(x) for x in value.split('-')]
    
    # check all page numbers are within the page count of the PDF
    if any(i > pagecount for i in parts):
        raise argparse.ArgumentTypeError('Page is outside of range.')

    if len(parts) == 2:
        if parts[0] > parts[1]:
            raise argparse.ArgumentTypeError('Start of range is greater than end of range.')
        # range is non-inclusive, so add 1 to the end
        # pages are 0-indexed with PyPDF2, but user input starts at 1, so decrement everything by 1
        # therefore, start - 1, end + 1 - 1 = end
        pagerange = range(parts[0] - 1, parts[1])
    elif len(parts) == 1:
        # User provides a single number as a page
        pagerange = [parts[0] - 1]
    else:
        # Unknown format
        raise argparse.ArgumentTypeError(f'Unable to parse page specification {value}. Please check format.')

    return pagerange


def main(args):
    f_in = open(args.file, 'rb')
    
    reader = PyPDF2.PdfFileReader(f_in)
    pagecount = reader.getNumPages()
    writer = PyPDF2.PdfFileWriter()

    for pagespec in args.pages:
        for pagenum in get_range(pagespec, pagecount):
            page = reader.getPage(pagenum)
            writer.addPage(page)

    out_file = open(args.dest, 'wb')
    writer.write(out_file)
    out_file.close()

    f_in.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='PDF File to process.', type=check_input_path)
    parser.add_argument('dest', help='Output file path/name.', type=check_output_path)
    parser.add_argument('pages', nargs='*', help='Pages to extract (inclusive). Example: 1 4-6 8')

    args = parser.parse_args()

    main(args)
