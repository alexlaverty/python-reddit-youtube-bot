import config.settings as settings

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--disable-selftext',
                        action='store_true',
                        help='Disable selftext video generation')

    parser.add_argument('--voice-engine',
                        help='Specify which text to speech engine to use',
                        choices=["polly",
                                 "balcon",
                                 "gtts",
                                 "tiktok",
                                 "edge-tts",
                                 "streamlabspolly"])

    parser.add_argument('-c',
                        '--comment-style',
                        help='Specify text based or reddit image comments',
                        choices=['text', 'reddit'])

    parser.add_argument('-l', '--video-length',
                        help='Set how long you want the video to be',
                        type=int)

    parser.add_argument('-n', '--enable-nsfw',
                        action='store_true',
                        help='Allow NSFW Content')

    parser.add_argument('-o', '--disable-overlay',
                        action='store_true',
                        help='Disable video overlay')

    parser.add_argument('-s', '--story-mode',
                        action='store_true',
                        help='Generate video for post title and selftext only,\
                            disables user comments')

    parser.add_argument('-t', '--thumbnail-only',
                        action='store_true',
                        help='Generate thumbnail image only')

    parser.add_argument('-p', '--enable-upload',
                        action='store_true',
                        help='Upload video to youtube, \
                             requires client_secret.json and \
                             credentials.storage to be valid')

    parser.add_argument('-u', '--url',
                        help='Specify Reddit post url, \
                        seperate with a comma for multiple posts.')

    parser.add_argument('--subreddits',
                        help='Specify Subreddits, seperate with +')

    parser.add_argument('-b', '--enable-background',
                        action='store_true',
                        help='Enable video backgrounds')

    args = parser.parse_args()

    if args.comment_style:
        logging.info(f'Setting comment style to : {args.comment_style}')
        settings.commentstyle = args.comment_style

    if args.voice_engine:
        logging.info(f'Setting speech engine to : {args.voice_engine}')
        settings.voice_engine = args.voice_engine

    if args.video_length:
        logging.info(f'Setting video length to : \
                    {str(args.video_length)} seconds')
        settings.max_video_length = args.video_length

    if args.disable_overlay:
        logging.info('Disabling Video Overlay')
        settings.enable_overlay = False

    if args.enable_nsfw:
        logging.info('Enable NSFW Content')
        settings.enable_nsfw_content = True

    if args.story_mode:
        logging.info('Story Mode Enabled!')
        settings.enable_comments = False

    if args.disable_selftext:
        logging.info('Disabled SelfText!')
        settings.enable_selftext = False

    if args.enable_upload:
        logging.info('Upload video enabled!')
        settings.enable_upload = True

    if args.subreddits:
        logging.info('Subreddits :')
        settings.subreddits = args.subreddits.split("+")
        print(settings.subreddits)

    if args.enable_background:
        logging.info('Upload video enabled!')
        settings.enable_background = True

    return args