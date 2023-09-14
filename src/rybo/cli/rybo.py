"""Command line utility to generate YouTube videos from Reddit posts."""

import logging
import logging.config
import os
import platform
import sys
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import colorama
from colorama import Fore
from ruamel.yaml import YAML

from rybo import __version__
from rybo.commands import RyboCommand
from rybo.config import settings
from rybo.logging import DEFAULT_LOG_CONFIG
from rybo.utils import EnvDefault, EnvFlagDefault

# TODO: Placeholder for sub-commands.
# from rybo.commands.thumbnails import CreateThumbnailCommand
# from rybo.commands.video import CreateVideoCommand
# from rybo.commands.reddit import ExtractRedditCommand
# from rbo.commands.youtube import PublishYouTubeCommand


DEFAULT_CONFIG_FILE: Path = Path.joinpath(Path.home(), "rybo.yaml")
logger = logging.getLogger(__name__)


def cli() -> None:
    """Create the rybo command line utility.

    Configuration options are loaded in the following order:

    1. From a configuration file (default: $HOME/rybo.yaml).
    2. From environment variables that start with the prefix `RYBO_`.
    3. From user provided CLI parameters.

    Returns:
        Returns an ArgumentParser that contains all of the sub-commands by rybo.
    """
    _display_banner()

    # TODO: This needs refactoring
    config_argparse: ArgumentParser = _configfile_parser()
    config_args, _ = config_argparse.parse_known_args()

    defaults: Dict[str, Any] = DEFAULT_LOG_CONFIG

    if config_args.config is None:
        config_args.config = DEFAULT_CONFIG_FILE

    cfg: Dict[str, Any] = _load_config(config_args)
    cfg |= defaults

    # There are some additional environment variables that can be set to
    # override configuration provided as CLI parameters, or via a configuration
    # file, so need to load these last and write over the top of any values
    # that already exist in the defaults dictionary.
    envvars: Dict[str, Any] = _parse_env_overrides()
    cfg |= envvars

    # Allows the user to change logging behaviour via a configuration file.
    logging.config.dictConfig(cfg)

    parser: ArgumentParser = _cli(config_argparse, cfg)
    _add_standard_args(parser)

    # TODO: placeholder for sub-commands
    #     subparser = parser.add_subparsers()
    #     _add_create_command(subparser)

    args: Namespace = parser.parse_args()
    _log_configuration(args)

    print(args)

    command: Any = args.cmd
    command.execute(args)


def _add_standard_args(parser: ArgumentParser) -> None:
    """Common CLI command arguments.

    Args:
        parser: Main parser that provides the rybo utility.
    """  # noqa: D401
    # TODO: Needs refactoring
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    parser.add_argument(
        "--background-directory",
        action=EnvFlagDefault,
        envvar="RYBO_BACKGROUND_DIRECTORY",
        help="Folder path to video backgrounds (env var: RYBO_BACKGROUND_DIRECORY).",
    )
    parser.add_argument(
        "-c",
        "--comment-style",
        action=EnvDefault,
        envvar="RYBO_COMMENT_STYLE",
        help="Specify text based or reddit image comments \
              (env var: RYBO_COMMENT_STYLE).",
        choices=["text", "reddit"],
    )
    parser.add_argument(
        "-o",
        "--disable-overlay",
        action=EnvFlagDefault,
        envvar="RYBO_DISABLE_OVERLAY",
        help="Disable video overlay (env var: RYBO_DISABLE_OVERLAY).",
    )
    parser.add_argument(
        "--disable-selftext",
        action=EnvFlagDefault,
        envvar="RYBO_DISABLE_SELFTEXT",
        help="Disable selftext video generation (env var: RYBO_DISABLE_SELFTEXT).",
    )
    parser.add_argument(
        "-b",
        "--enable-background",
        action=EnvFlagDefault,
        envvar="RYBO_ENABLE_BACKGROUND",
        help="Enable video backgrounds (env var: RYBO_ENABLE_BACKGROUND).",
    )
    parser.add_argument(
        "--enable-mentions",
        action=EnvFlagDefault,
        envvar="RYBO_ENABLE_MENTIONS",
        help="Check reddit account for user mentions (env var: RYBO_ENABLE_MENTIONS).",
    )
    parser.add_argument(
        "-n",
        "--enable-nsfw",
        action=EnvFlagDefault,
        envvar="RYBO_ENABLE_NSFW",
        help="Allow NSFW Content (env var: RYBO_ENABLE_NSFW).",
    )
    parser.add_argument(
        "-p",
        "--enable-upload",
        action=EnvFlagDefault,
        envvar="RYBO_ENABLE_UPLOAD",
        help="Upload video to youtube,requires client_secret.json and credentials.\
             storage to be valid (env var: RYBO_ENABLE_UPLOAD).",
    )
    parser.add_argument(
        "--orientation",
        choices=["landscape", "portrait"],
        action=EnvDefault,
        envvar="RYBO_ORIENTATION",
        default="landscape",
        help="Sort Reddit posts by (env var: RYBO_ORIENTATION).",
    )
    parser.add_argument(
        "--shorts",
        action=EnvFlagDefault,
        envvar="RYBO_SHORTS",
        help="Generate Youtube Shorts Video (env var: RYBO_SHORTS).",
    )
    parser.add_argument(
        "--sort",
        action=EnvDefault,
        envvar="RYBO_SORT",
        choices=["top", "hot"],
        help="Sort Reddit posts by (env var: RYBO_SORT).",
    )
    parser.add_argument(
        "--submission-score",
        action=EnvDefault,
        envvar="RYBO_SUBMISSION_SCORE",
        type=int,
        help="Minimum submission score threshold (env var: RYBO_SUBMISSION_SCORE).",
    )
    parser.add_argument(
        "--subreddits",
        action=EnvDefault,
        envvar="RYBO_SUBREDDITS",
        help="Specify Subreddits, seperate with + (env var: RYBO_SUBREDDITS).",
    )
    parser.add_argument(
        "-s",
        "--story-mode",
        action=EnvFlagDefault,
        envvar="RYBO_STORY_MODE",
        help="Generate video for post title and selftext only, disables user comments \
              (env var: RYBO_STORY_MODE).",
    )
    parser.add_argument(
        "-t",
        "--thumbnail-only",
        action=EnvFlagDefault,
        envvar="RYBO_THUMBNAIL_ONLY",
        help="Generate thumbnail image only (env var: RYBO_THUMBNAIL_ONLY).",
    )
    parser.add_argument(
        "--time",
        action=EnvDefault,
        envvar="RYBO_TIME",
        choices=["all", "day", "hour", "month", "week", "year"],
        default="day",
        help="Filter by time (env var: RYBO_TIME).",
    )
    parser.add_argument(
        "--total-posts",
        action=EnvDefault,
        envvar="RYBO_TOTAL_POSTS",
        type=int,
        help="Number of posts to process (env var: RYBO_TOTAL_POSTS).",
    )
    parser.add_argument(
        "-u",
        "--url",
        action=EnvDefault,
        envvar="RYBO_URL",
        help="Specify Reddit post url, seperate with a comma for multiple posts \
              (env var: RYBO_URL).",
    )
    parser.add_argument(
        "-l",
        "--video-length",
        action=EnvDefault,
        envvar="RYBO_VIDEO_LENGTH",
        type=int,
        help="Set how long you want the video to be (env var: RYBO_VIDEO_LENGTH).",
    )
    parser.add_argument(
        "--voice-engine",
        action=EnvDefault,
        envvar="RYBO_VOICE_ENGINE",
        choices=["polly", "balcon", "gtts", "tiktok", "edge-tts", "streamlabspolly"],
        help="Specify which text to speech engine to use (env var: RYBO_VOICE_ENGINE).",
    )

    args = parser.parse_args()

    if args.orientation:
        settings.orientation = args.orientation
        if args.orientation == "portrait":
            settings.video_height = settings.vertical_video_height
            settings.video_width = settings.vertical_video_width

    if args.shorts:
        logger.info("Generating Youtube Shorts Video")
        settings.orientation = "portrait"
        settings.video_height = settings.vertical_video_height
        settings.video_width = settings.vertical_video_width
        settings.max_video_length = 59
        settings.add_hashtag_shorts_to_description = True

    if args.enable_mentions:
        settings.enable_reddit_mentions = True

    if args.submission_score:
        settings.minimum_submission_score = args.submission_score

    if args.sort:
        settings.reddit_post_sort = args.sort

    if args.time:
        settings.reddit_post_time_filter = args.time

    if args.background_directory:
        settings.background_directory = args.background_directory

    if args.total_posts:
        settings.total_posts_to_process = args.total_posts

    if args.comment_style:
        settings.commentstyle = args.comment_style

    if args.voice_engine:
        settings.voice_engine = args.voice_engine

    if args.video_length:
        settings.max_video_length = args.video_length

    if args.disable_overlay:
        settings.enable_overlay = False

    if args.enable_nsfw:
        settings.enable_nsfw_content = True

    if args.story_mode:
        settings.enable_comments = False

    if args.disable_selftext:
        settings.enable_selftext = False

    if args.enable_upload:
        settings.enable_upload = True

    if args.subreddits:
        settings.subreddits = args.subreddits.split("+")
        logger.info("Subreddits :")
        logger.info(settings.subreddits)

    if args.enable_background:
        settings.enable_background = True

    parser.set_defaults(cmd=RyboCommand(parser))


def _cli(parser: ArgumentParser, defaults: Dict[str, Any]) -> ArgumentParser:
    """Create the main CLI parser.

    Where a configuration file is found, this will load CLI options from the
    file, over-riding any configuration set via environment variables.

    Args:
        parser: Parser used to read the configuration file.
        defaults: Dictionary that contains the CLI argument default values.

    Returns:
        The main rybo parser.
    """
    parsers: List[ArgumentParser] = [parser]
    parser: ArgumentParser = ArgumentParser(
        description="Generate vidoes from reddit posts.", parents=parsers
    )
    parser.set_defaults(**defaults)
    return parser


def _configfile_parser() -> ArgumentParser:
    """Add the CLI argument used to load a custom config file.

    Returns:
        An `ArgumentParser` instance with the nargument used to specify the
        location of a custom configuration file.
    """
    parser: ArgumentParser = ArgumentParser(prog=__file__, add_help=False)
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_FILE,
        action=EnvDefault,
        envvar="RYBO_CONFIG_FILE",
        help="Path to the configuration file.",
    )
    return parser


def _display_banner() -> None:
    """Display the CLIs banner."""
    colorama.init(autoreset=True)

    python_version: str = f"{'Python Version':<20} : {sys.version}"
    os_version: str = f"{'OS Version':<20} : {platform.system()} {platform.release()}"
    rybo_version: str = f"{'Rybo Version':<20} : {__version__}"
    title: str = "YOUTUBE REDDIT BOT"

    python_version_width: int = len(python_version)
    os_version_width: int = len(os_version)

    if len(python_version) > len(os_version):
        title = f"{' YOUTUBE REDDIT BOT ':=^{python_version_width}}"
    else:
        title = f"{' YOUTUBE REDDIT BOT ':=^{os_version_width}}"

    print(f"{Fore.CYAN}{title}\n{os_version}\n{python_version}\n{rybo_version}\n")


def _load_config(args: Namespace) -> Dict[str, Any]:
    """Load and parser a configuration file.

    Args:
        args: CLI arguments.

    Returns:
        A dictionary containing configuration options.
    """
    config: Dict[str, Any] = {}
    config_file: Path = Path(args.config)
    if config_file.is_file():
        yaml: YAML = YAML(typ="safe")

        # ruamel doesn't have the same vulnerability as the standard yaml
        # library, so it's safe to ignore SCS105 here.
        config = yaml.load(config_file)  # noqa: SCS105

    return config


def _log_configuration(args: Namespace) -> None:
    """Log the bot configuration settings.

    Args:
        args: ArgumentParser containing the user provided runtime parameters.
    """
    if args.orientation:
        logger.info(f"{'Set orientation to':<45} : %s", settings.orientation)
        logger.info(f"{'Set video height to':<45} : %s", settings.video_height)
        logger.info(f"{'Set video width to':<45} : %s", settings.video_width)

    if args.shorts:
        logger.info("Generating Youtube Shorts Video")

    if args.enable_mentions:
        logger.info("Enable Generate Videos from User Mentions")

    if args.submission_score:
        logger.info(
            f"{'Setting Reddit Post Minimum Submission Score':<45} : %s",
            settings.minimum_submission_score,
        )

    if args.sort:
        logger.info(f"{'Setting Reddit Post Sort':<45} : %s", settings.reddit_post_sort)

    if args.time:
        logger.info(
            f"{'Setting Reddit Post Time Filter':<45} : %s",
            settings.reddit_post_time_filter,
        )

    if args.background_directory:
        logger.info(
            f"{'Setting video background directory':<45} : %s",
            args.background_directory,
        )

    if args.total_posts:
        logger.info(f"{'Total Posts to process':<45} : %s", args.total_posts)

    if args.comment_style:
        logger.info(f"{'Setting comment style to':<45} : %s", args.comment_style)

    if args.voice_engine:
        logger.info(f"{'Setting speech engine to':<45} : %s", args.voice_engine)

    if args.video_length:
        logger.info(f"{'Setting video length to':<45} : %s seconds", args.video_length)

    if args.disable_overlay:
        logger.info("Disabling Video Overlay")

    if args.enable_nsfw:
        logger.info("Enable NSFW Content")

    if args.story_mode:
        logger.info("Story Mode Enabled!")

    if args.disable_selftext:
        logger.info("Disabled SelfText!")

    if args.enable_upload:
        logger.info("Upload video enabled!")

    if args.subreddits:
        logger.info("Subreddits :")
        settings.subreddits = args.subreddits.split("+")
        logger.info(settings.subreddits)

    if args.enable_background:
        logger.info("Enabling Video Background!")


def _parse_env_overrides() -> Dict[str, Any]:
    """Load rybo configuration provided as environment variables.

    Returns:
        A dictionary containing the configuration specified as
        environment variables.
    """
    cfg: Dict[str, Any] = defaultdict(dict)

    if os.environ.get("RYBO_REDDIT_CLIENT_ID"):
        cfg["reddit"]["client_id"] = os.environ["RYBO_REDDIT_CLIENT_ID"]

    if os.environ.get("RYBO_REDDIT_CLIENT_SECRET"):
        cfg["reddit"]["client_secret"] = os.environ["RYBO_REDDIT_CLIENT_SECRET"]

    if os.environ.get("RYBO_REDDIT_USERNAME"):
        cfg["reddit"]["username"] = os.environ["RYBO_REDDIT_USERNAME"]

    if os.environ.get("RYBO_REDDIT_PASSWORD"):
        cfg["reddit"]["password"] = os.environ["RYBO_REDDIT_PASSWORD"]

    if os.environ.get("RYBO_POLLY_ACCESS_KEY"):
        cfg["polly"]["access_key_id"] = os.environ["RYBO_POLLY_ACCESS_KEY"]

    if os.environ.get("RYBO_POLLY_SECRET_ACCESS_KEY"):
        cfg["polly"]["secret_access_key"] = os.environ["RYBO_POLLY_SECRET_ACCESS_KEY"]

    if os.environ.get("RYBO_RUMBLE_USERNAME"):
        cfg["rumble"]["username"] = os.environ["RYBO_RUMBLE_USERNAME"]

    if os.environ.get("RYBO_RUMBLE_PASSWORD"):
        cfg["rumble"]["password"] = os.environ["RYBO_RUMBLE_PASSWORD"]

    return dict(cfg)


# TODO: Placeholder for sub-commands.
# def _add_create_command(subparser: _SubParsersAction):
#     """Sub-command used to create new Zephyr folders.

#     Args:
#         subparser: Parent that the sub-command will belong to.
#     """
#     parser = subparser.add_parser('create', help='Create a new folder.')
#     parser.add_argument(
#         '--project',
#         required=True,
#         help='Project key of the project that the folder will be created under.'
#     )
#     parser.add_argument(
#         '--name',
#         required=False,
#         help='Name of the folder.'
#     )
#     parser.add_argument(
#         '--type',
#         required=False,
#         choices=['plan', 'case', 'cycle'],
#         help='Type of folder to create.',
#     )
#     parser.set_defaults(cmd=CreateFolderCommand(parser))
