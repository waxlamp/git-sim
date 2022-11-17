import git_sim as gs
import os
import argparse
import pathlib
import time, datetime
import cv2
from manim import config, WHITE
from manim.utils.file_ops import open_file as open_media_file

def main():
    parser = argparse.ArgumentParser("git-sim", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--commits", help="The number of commits to display in the Git animation", type=int, default=8)
    parser.add_argument("--hide-merged-chains", help="Hide commits from merged branches, i.e. only display mainline commits", action="store_true")
    parser.add_argument("--reverse", help="Display commits in reverse order in the Git animation", action="store_true")
    parser.add_argument("--title", help="Custom title to display at the beginning of the animation", type=str, default="Git Sim, by initialcommit.com")
    parser.add_argument("--logo", help="The path to a custom logo to use in the animation intro/outro", type=str, default=os.path.join(str(pathlib.Path(__file__).parent.resolve()), "logo.png"))
    parser.add_argument("--outro-top-text", help="Custom text to display above the logo during the outro", type=str, default="Thanks for using Initial Commit!")
    parser.add_argument("--outro-bottom-text", help="Custom text to display below the logo during the outro", type=str, default="Learn more at initialcommit.com")
    parser.add_argument("--show-intro", help="Add an intro sequence with custom logo and title", action="store_true")
    parser.add_argument("--show-outro", help="Add an outro sequence with custom logo and text", action="store_true")
    parser.add_argument("--max-branches-per-commit", help="Maximum number of branch labels to display for each commit", type=int, default=2)
    parser.add_argument("--max-tags-per-commit", help="Maximum number of tags to display for each commit", type=int, default=1)
    parser.add_argument("--media-dir", help="The path to output the animation data and video file", type=str, default=".")
    parser.add_argument("--low-quality", help="Render output video in low quality, useful for faster testing", action="store_true")
    parser.add_argument("--light-mode", help="Enable light-mode with white background", action="store_true")
    parser.add_argument("--invert-branches", help="Invert positioning of branches where applicable", action="store_true")
    parser.add_argument("--speed", help="A multiple of the standard 1x animation speed (ex: 2 = twice as fast, 0.5 = half as fast)", type=float, default=1.5)
    parser.add_argument("--animate", help="Animate the simulation and output as an mp4 video", action="store_true")

    subparsers = parser.add_subparsers(dest="subcommand", help="subcommand help")

    reset = subparsers.add_parser("reset", help="reset help")
    reset.add_argument("commit", nargs="?", help="The ref (branch/tag), or first 6 characters of the commit ID to simulate reset to", type=str, default="HEAD")
    reset.add_argument("--mode", help="Either mixed (default), soft, or hard", type=str, default="default")
    reset.add_argument("--soft", help="Simulate a soft reset, shortcut for --mode=soft", action="store_true")
    reset.add_argument("--mixed", help="Simulate a mixed reset, shortcut for --mode=mixed", action="store_true")
    reset.add_argument("--hard", help="Simulate a soft reset, shortcut for --mode=hard", action="store_true")

    revert = subparsers.add_parser("revert", help="revert help")
    revert.add_argument("commit", nargs="?", help="The ref (branch/tag), or first 6 characters of the commit ID to simulate revert", type=str, default="HEAD")

    branch = subparsers.add_parser("branch", help="branch help")
    branch.add_argument("name", help="The name of the new branch", type=str)

    tag = subparsers.add_parser("tag", help="tag help")
    tag.add_argument("name", help="The name of the new tag", type=str)

    status = subparsers.add_parser("status", help="status help")

    add = subparsers.add_parser("add", help="add help")
    add.add_argument("name", nargs="+", help="The names of one or more files to add to Git's staging area", type=str) 

    commit = subparsers.add_parser("commit", help="commit help")
    commit.add_argument("-m", "--message", help="The commit message of the new commit", type=str, default="New commit")

    stash = subparsers.add_parser("stash", help="stash help")
    stash.add_argument("name", nargs="?", help="The name of the file to stash changes for", type=str, default=None)

    args = parser.parse_args()

    config.media_dir = os.path.join(args.media_dir, "git-sim_media")
    config.verbosity = "ERROR"

    if ( args.low_quality ):
        config.quality = "low_quality"

    if ( args.light_mode ):
        config.background_color = WHITE

    scene = gs.GitSim(args)
    scene.render()

    if not args.animate:
        video = cv2.VideoCapture(str(scene.renderer.file_writer.movie_file_path))
        success, image = video.read()
        if success:
            t = datetime.datetime.fromtimestamp(time.time()).strftime("%m-%d-%y_%H-%M-%S")
            image_file_name = "git-sim-" + args.subcommand + "_" + t + ".jpg"
            image_file_path = os.path.join(os.path.join(config.media_dir, "images"), image_file_name)
            cv2.imwrite(image_file_path, image)

    try:
        if not args.animate:
            open_media_file(image_file_path)
        else:
            open_media_file(scene.renderer.file_writer.movie_file_path)
    except FileNotFoundError:
        print("Error automatically opening video player, please manually open the video file to view animation.")

if __name__ == "__main__":
    main()
