import pathlib
import os
import sys
import argparse
import wakepy
import tempfile
import subprocess

from typing import Dict, List, Tuple
from util import check_input_dir, check_output_dir, check_positive


def get_gopro_files_from_dir(dir):
    """
    Search the directory for GoPro clips

    Clip names will have format (without spaces):
      GX 00 0000.mp4
      First two digits are subclip
      Last four digits are clip number
    Example:
      GX010533.mp4
      First subclip (01) of video 533
    """

    p = pathlib.Path(dir)
    files = list(p.glob('GX*.[Mm][Pp]4'))
    
    if len(files) == 0:
        sys.exit('Directory does not appear to contain any GoPro files.')

    return files


def get_subclips_from_dir(files) -> Dict[str, List[Tuple[int, pathlib.Path]]]:
    """
    Returns a dictionary of clip_num : [tuple(subclip_num, subclip_path), ...]

    The list of tuples is sorted by subclip number.
    """
    files_by_clips = {}
    for filepath in files:
        # split into groups of clips
        fname = filepath.parts[-1]
        clip = fname[4:8]
        subclip = int(fname[2:4])

        if clip in files_by_clips:
            files_by_clips[clip].append((subclip, filepath))
        else:
            files_by_clips[clip] = [(subclip, filepath)]
    for _, subclips in files_by_clips.items():
        sorted(subclips)

    return files_by_clips


def main(args):
    files = get_gopro_files_from_dir(args.dir)
    files_by_clips = get_subclips_from_dir(files)

    # Merge clips
    # subclips consists of tuples:
    #   first value is the subclip number
    #   second value is the path
    n_clips = len(files_by_clips)
    for i, (clip, subclips) in enumerate(files_by_clips.items()):
        print(f'Processing {i+1} out of {n_clips}...')
        
        if len(subclips) == 1:
            # Clip only has 1 file, do nothing
            files.remove(subclips[0][1])  # remove from list so we don't delete it later
            print(f'Skipping clip {clip} as there is only one subclip. Files will not be removed.\n')
            continue

        if args.clips is not None and int(clip) not in args.clips:
            print(f'Skipping clip {clip}, files will not be removed.\n')
            for _, fp in subclips:
                files.remove(fp)
            continue

        # Create a temporary file for ffmpeg to read
        # Each line in file is a file to be concatenated
        # Concatenation will be done in the order of the file
        subclip_fp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        subclip_fp.writelines([f"file '{str(fp)}'\n" for (_, fp) in subclips])
        subclip_fp.close()

        if args.dest is not None:
            output_filepath = pathlib.Path(args.dest) / f'{clip}_merged.mp4'
        else:
            output_filepath = pathlib.Path(args.dir) / f'{clip}_merged.mp4'

        ffmpeg_cmd = f'ffmpeg -safe 0 -f concat -i "{subclip_fp.name}" -c copy "{output_filepath}"'
        if args.dry_run:
            print(f'Command to run: \n  {ffmpeg_cmd}\n')
        else:
            subprocess.run(ffmpeg_cmd, shell=True, check=True)

        os.unlink(subclip_fp.name)

    # Delete files
    if args.delete_merged:
        if args.dry_run:
            files_to_delete_str = '\n  '.join([str(fp) for fp in files])
            print(f'\nFiles will be deleted:\n  {files_to_delete_str}\n')
        else:
            for filepath in files:
                filepath.unlink(missing_ok=True)

    print('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merges GoPro clips.')
    parser.add_argument('dir', help='Directory containing clips.', type=check_input_dir)
    parser.add_argument('--dest', help='Destination for merged clips.', type=check_output_dir)
    parser.add_argument('--delete_merged', action='store_true', help='Delete clips after merging.')
    parser.add_argument('--dry_run', action='store_true', help='Show ffmpeg command but do not run ffmpeg.')
    parser.add_argument('--clips', nargs='*', type=check_positive, 
                        help='Provide list of specific clips to process, for example (leading zeros optional):\n\t' + 
                        ' --clips 0001 006 0003',)

    args = parser.parse_args()

    with wakepy.keepawake(keep_screen_awake=False):
        main(args)
