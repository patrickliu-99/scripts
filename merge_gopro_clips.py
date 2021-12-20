from moviepy.editor import VideoFileClip, concatenate_videoclips
import pathlib
import os
import sys
import argparse
import wakepy


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f'{value} must be positive integer.')
    return ivalue


def check_isdir(value):
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError('Directory provided is not valid!')
    return value


def get_subclips_from_dir(dir):
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
    files = list(p.glob('GX*.mp4'))
    if len(files) == 0:
        sys.exit('Directory does not appear to contain any GoPro files.')

    # Organize files by which clips they belong to
    files_by_clips = {}
    for filepath in files:
        # split into groups of clips
        fname = filepath.parts[-1]
        clip = fname[5:8]
        subclip = fname[2:4]

        if clip in files_by_clips:
            files_by_clips[clip].append((subclip, filepath))
        else:
            files_by_clips[clip] = [(subclip, filepath)]

    return files_by_clips


def main(args):
    files_by_clips = get_subclips_from_dir(args.dir)
    

    # Set up output path. Will create path if not exist.
    if args.dest is not None:
        output_path = pathlib.Path(args.dest)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = pathlib.Path(args.dir)

    # Merge clips
    # subclips consists of tuples:
    #   first value is the subclip number
    #   second value is the path
    n_clips = len(files_by_clips)
    for i, (clip, subclips) in enumerate(files_by_clips.items()):
        print(f'Processing {i+1} out of {n_clips}...')
        if len(subclips) == 0:
            continue

        sorted(subclips)

        # open all subclips
        videoclips = [VideoFileClip(str(fp)) for (_, fp) in subclips]
        merged_clip = concatenate_videoclips(videoclips)
        output_clip_path = output_path / f'{clip}_merged.mp4'
        merged_clip.write_videofile(str(output_clip_path), threads=args.threads, codec='h264_nvenc')

    # Delete files
    if args.delete_merged:
        for filepath in files:
            filepath.unlink(missing_ok=True)

    print('Done!')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merges GoPro clips.')
    parser.add_argument('dir', help='Directory containing clips.', type=check_isdir)
    parser.add_argument('--dest', help='Destination for merged clips.', type=check_isdir)
    parser.add_argument('--delete_merged', action='store_true', help='Delete clips after merging.')
    parser.add_argument('--threads', type=check_positive, default=8, help='Threads to use for ffmpeg.')

    args = parser.parse_args()

    with wakepy.keepawake(keep_screen_awake=False):
        main(args)
