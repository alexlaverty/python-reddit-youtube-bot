# Automated Reddit to Youtube Bot

<!-- vscode-markdown-toc -->
* [Description](#Description)
* [Example Videos](#ExampleVideos)
* [Windows](#Windows)
	* [ Install Prerequisite Components](#InstallPrerequisiteComponents)
	* [ Clone the Git Repository](#ClonetheGitRepository)
	* [ Configure a Virtual Environment](#ConfigureaVirtualEnvironment)
	* [ Configure Playwright](#ConfigurePlaywright)
	* [ Install the pip package](#Installthepippackage)
	* [ Generate a Reddit token](#GenerateaReddittoken)
	* [ Set up your credentials](#Setupyourcredentials)
	* [ Run the CLI utility](#RuntheCLIutility)
* [Configuration](#Configuration)
	* [Configuring the CLI](#ConfiguringtheCLI)
	* [ Downloading video backgrounds using yt-dlp](#Downloadingvideobackgroundsusingyt-dlp)
	* [ Help](#Help)
* [Customising](#Customising)
	* [ Specify Subreddits to Scrape](#SpecifySubredditstoScrape)
	* [ Exclude Subreddits](#ExcludeSubreddits)
	* [ Filter Reddit submissions by keyword](#FilterRedditsubmissionsbykeyword)
	* [ Change the Text to Speech Engine](#ChangetheTexttoSpeechEngine)
	* [ Limit the number of generated videos](#Limitthenumberofgeneratedvideos)
	* [ Skip Reddit posts by submission score](#SkipRedditpostsbysubmissionscore)
	* [ Filter Reddit posts by title length](#FilterRedditpostsbytitlelength)
	* [ Filter Reddit posts by self text length](#FilterRedditpostsbyselftextlength)
	* [ Filter Reddit posts by comment count](#FilterRedditpostsbycommentcount)
	* [Limit number of posts to process](#Limitnumberofpoststoprocess)
	* [ Configure number of thumbnails to generate](#Configurenumberofthumbnailstogenerate)
	* [ Set the maximum video length](#Setthemaximumvideolength)
	* [ Set maximum number of comments to include](#Setmaximumnumberofcommentstoinclude)
	* [ Specify folder paths](#Specifyfolderpaths)
	* [ Set video dimensions](#Setvideodimensions)
	* [ Skip video compilation](#Skipvideocompilation)
	* [ Skip YouTube uploading](#SkipYouTubeuploading)
	* [ Add a video overlay](#Addavideooverlay)
	* [ Add a Newscaster](#AddaNewscaster)
	* [ Add a pause after each TTS file](#AddapauseaftereachTTSfile)
	* [Modify appearnace of text](#Modifyappearnaceoftext)
	* [ Download images from Lexica](#DownloadimagesfromLexica)
* [ Tips and Tricks](#TipsandTricks)
	* [Generate a Video for a Specific Post](#GenerateaVideoforaSpecificPost)
	* [Generate Only Thumbnails](#GenerateOnlyThumbnails)
	* [Enable a Newscaster](#EnableaNewscaster)
<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Description'></a>Description

Scrape posts from Reddit and automatically generate Youtube Videos and Thumbnails

## <a name='ExampleVideos'></a>Example Videos

Checkout my Youtube Channel for example videos made by this repo :

[What crime are you okay with people committing?](https://youtu.be/gOX1Uhxba-g)
[![Watch the video](assets/images/xm5gsv_thumbnail.png)](https://youtu.be/gOX1Uhxba-g)

[What show has no likable characters?](https://youtu.be/xAaPbntOVb8)
[![Watch the video](assets/images/Whatshowhasnolikablecharacters.png)](https://youtu.be/xAaPbntOVb8)

# Quickstart Guide

## <a name='Windows'></a>Windows

[Watch the Python Reddit Youtube Bot Tutorial Video :](https://youtu.be/LaFFU9EskfA)
[![Watch the video](assets/images/python-reddit-youtube-bot-tutorial.png)](https://youtu.be/LaFFU9EskfA)

### <a name='InstallPrerequisiteComponents'></a> Install Prerequisite Components

Install these prerequisite components first :

* Git - https://git-scm.com/download/win

* Python 3.11 - https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe

* Microsoft C++ Build Tools - https://visualstudio.microsoft.com/visual-cpp-build-tools/

* ImageMagick - https://imagemagick.org/script/download.php#windows

### <a name='ClonetheGitRepository'></a> Clone the Git Repository

```powershell
> git clone git@github.com:alexlaverty/python-reddit-youtube-bot.git
> cd python-reddit-youtube-bot
```

### <a name='ConfigureaVirtualEnvironment'></a> Configure a Virtual Environment

Create a virtual environment, and install package dependencies :

```powershell
> python -m venv venv
...
> .\venv\Scripts\activate.ps1
...
> pip install -r requirements.txt
Collecting boto3==1.26.123
  Using cached boto3-1.26.123-py3-none-any.whl (135 kB)
Collecting bs4==0.0.1
  Using cached bs4-0.0.1.tar.gz (1.1 kB)
  Preparing metadata (setup.py) ... done
...
```

### <a name='ConfigurePlaywright'></a> Configure Playwright

Install and configure playwright by running :

```powershell
> playwright install
```

### <a name='Installthepippackage'></a> Install the pip package

Install the command-line utility used to run the bot :

```powershell
> pip install --user --editable .
Obtaining file:///workspaces/python-reddit-youtube-bot-forked
  ...
Building wheels for collected packages: rybo
  ...
Successfully built rybo
Installing collected packages: rybo
  ...
Successfully installed rybo-0.0.1
```

### <a name='GenerateaReddittoken'></a> Generate a Reddit token

Generate Reddit OAuth credentials via https://www.reddit.com/prefs/apps/.

### <a name='Setupyourcredentials'></a> Set up your credentials

Add the Reddit token via environment variables, or in a YAML configuration
file. The default expected location for this file is `$HOME/rybo.yaml`.

| Environment Variable           | Configuration File Option | Description                                                |
|--------------------------------|---------------------------|------------------------------------------------------------|
| `RYBO_REDDIT_CLIENT_ID`        | `reddit.client_id`        | Client id used to authenticate against the Reddit API.     |
| `RYBO_REDDIT_CLIENT_SECRET`    | `reddit.client_secret`    | Client secret used to authenticate against the Reddit API. |
| `RYBO_REDDIT_USERNAME`         | `reddit.username`         | Username used to log in to the Reddit Web UI.              |
| `RYBO_REDDIT_PASSWORD`         | `reddit.password`         | Password used to log in to the Reddit Web UI.              |
| `RYBO_POLLY_ACCESS_KEY`        | `polly.access_key`        | AWS Access Key used to interact with the Polly service.    |
| `RYBO_POLLY_SECRET_ACCESS_KEY` | `polly.secret_access_key` | AWS secret used to interact with the Polly service.        |
| `RYBO_RUMBLE_USERNAME`         | `rumble.username`         | Username used to interact with the Rumble Web UI.          |
| `RYBO_RUMBLE_PASSWORD`         | `rumble.password`         | Password used to interact with the Rumble Web UI.          |

### <a name='RuntheCLIutility'></a> Run the CLI utility

```powershell
> rybo
```

When it completes, the video will be generated into the `videos` folder and
will be named `final.mp4`.

## <a name='Configuration'></a>Configuration

### <a name='ConfiguringtheCLI'></a>Configuring the CLI

Configuration options can be specified via CLI parameters, environment variables, or a
yaml configuration file.

The order of precedence is as follows:

1. Yaml configuration file (default location: `$HOME/rybo.yaml`)
2. Environment variables.
3. User-specified CLI parameters.

For example, if `disable_overlay: True` is set in `$HOME/rybo.yaml`, and
the `RYBO_DISABLE_OVERLAY=False` environment variable is also set, then
video overlay will be disabled (false) in the runtime configuration.

<details>
<summary>Click to view the list of configuration options</summary>

| Argument                 | Environment Variable           | Configuration File Option | Default Value        | Description                                                                                                                                                          |
|--------------------------|--------------------------------|---------------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-h`/`--help`            |                                |                           |                      | Display the help menu.                                                                                                                                               |
| `--config`               | `RYBO_CONFIG`                  |                           | `$HOME/rybo.yaml`    | Load settings from a configuration file.                                                                                                                             |
| `--version `             |                                |                           |                      | Display version information.                                                                                                                                         |
| `--background-directory` | `RYBO_BACKGROUND_DIRECTORY`    | `background_directory`    | `assets/backgrounds` | Folder path to videos that will be used for the video background.                                                                                                    |
| `--comment-style`        | `RYBO_COMMENT_STYLE`           | `comment_style`           |  `reddit`            | Use text based, or image based Reddit comments. Choices are **text** or **image**.                                                                                   |
| `--disable-overlay`      | `RYBO_DISABLE_OVERLAY`         | `disable_overlay`         | `False`              | Enable or disable the video overlay.                                                                                                                                 |
| `--disable-selftext`     | `RYBO_DISABLE_SELFTEXT`        | `disable_selftext`        | `False`              | Enable or disable self-text video generation.                                                                                                                        |
| `--enable-background`    | `RYBO_ENABLE_BACKGROUND`       | `enable_background`       | `False`              | Enable or disable adding a background to the video.                                                                                                                  |
| `--enable-mentions`      | `RYBO_ENABLE_MENTIONS`         | `enable_mentions`         | `False`              | Check the reddit account for user mentions.                                                                                                                          |
| `--enable-nsfw`          | `RYBO_ENABLE_NSFW`             | `enable_nsfw`             | `False`              | Include, or ignore posts tagged as Not Safe for Work.                                                                                                                |
| `--enable-upload`        | `RYBO_ENABLE_UPLOAD`           | `enable_upload`           | `False`              | Enable or disable uploading videos to YouTube.                                                                                                                       |
| `--orientation`          | `RYBO_ORIENTATION`             | `orientation`             | `landscape`          | Set the video orientation. Choices are **portrait** or **Landscape**.                                                                                                |
| `--shorts`               | `RYBO_SHORTS`                  | `shorts`                  | `False`              | Enable or disable generating a YouTube shorts video.                                                                                                                 |
|  `--sort`                | `RYBO_SORT`                    | `sort`                    | `hot`                | Set the sorting order when scanning Reddit posts. Choices are **top** or **hot**.                                                                                    |
| `--submission-score`     | `RYBO_SUBMISSION_SCORE`        | `submission_score`        | `5000`               | Minimum submission score threshold.                                                                                                                                  |
| `--subreddits`           | `RYBO_SUBREDDITS`              | `subreddits`              |                      | List of subreddits to scan, where each subreddit is separated with a **+**.                                                                                          |
| `--story-mode`           | `RYBO_STORY_MODE`              | `story_mode`              | `False`              | Enable or disable video generation for the post title and selftext only, disables user comments.                                                                     |
| `--thumbnail-only`       | `RYBO_THUMBNAIL_ONLY`          | `thumbnail_only`          | `False`              | Enable or disable generation of just the video thumbnails.                                                                                                           |
| `--time`                 | `RYBO_TIME`                    | `time`                    | `day`                | Filter Reddit submissions by time. Choices are **all**, **day**, **hour**, **month**, **week** or **year**.                                                          |
| `--total-posts`          | `RYBO_TOTAL_POSTS`             | `total_posts`             | `10`                 | Total number of reddit submissions to process.                                                                                                                       |
| `--url`                  | `RYBO_URL`                     | `url`                     |                      | Generate a video for a single Reddit submission.                                                                                                                     |
| `--video-length`         | `RYBO_VIDEO_LENGTH`            | `video_length`            | `600`                | Sets how long the generated video will be, in seconds.                                                                                                               |
| `--voice-engine`         | `RYBO_VOICE_ENGINE`            | `voice_engine`            | `edge-tts`           | Specify which text-to-speech engine should be used to narrate the video. Choices are **polly**, **balcon**, **gtts**, **tiktok**, **edge-tts**, **streamlabspolly**. |

</details>

### <a name='Downloadingvideobackgroundsusingyt-dlp'></a> Downloading video backgrounds using yt-dlp

If you want to add a video background then install yt-dlp :

[yt-dlp](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe)

then create a `backgrounds` folder and run the following command :

```
mkdir -p assets/backgrounds
cd assets/backgrounds
yt-dlp --playlist-items 1:10 -f 22 --output "%(uploader)s_%(id)s.%(ext)s" https://www.youtube.com/playlist?list=PLGmxyVGSCDKvmLInHxJ9VdiwEb82Lxd2E
```

### <a name='Help'></a> Help

You can view available parameters by passing in `--help` :

```powershell
rybo --help

============================== YOUTUBE REDDIT BOT ===============================
OS Version           : Linux 5.15.90.1-microsoft-standard-WSL2
Python Version       : 3.11.3 (main, May  4 2023, 05:53:32) [GCC 10.2.1 20210110]
Rybo Version         : 0.0.1

usage: rybo [-h] [--config CONFIG] [--version] [--background-directory] [-c {text,reddit}] [-o] [--disable-selftext] [-b] [--enable-mentions] [-n] [-p]
            [--orientation {landscape,portrait}] [--shorts] [--sort {top,hot}] [--submission-score SUBMISSION_SCORE] [--subreddits SUBREDDITS] [-s] [-t]
            [--time {all,day,hour,month,week,year}] [--total-posts TOTAL_POSTS] [-u URL] [-l VIDEO_LENGTH]
            [--voice-engine {polly,balcon,gtts,tiktok,edge-tts,streamlabspolly}]

Generate vidoes from reddit posts.

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to the configuration file.
  --version             show programs version number and exit
  --background-directory
                        Folder path to video backgrounds.
  -c {text,reddit}, --comment-style {text,reddit}
                        Specify text based or reddit image comments.
  -o, --disable-overlay
                        Disable video overlay.
  --disable-selftext    Disable selftext video generation.
  -b, --enable-background
                        Enable video backgrounds.
  --enable-mentions     Check reddit account for u mentions.
  -n, --enable-nsfw     Allow NSFW Content.
  -p, --enable-upload   Upload video to youtube,requires client_secret.json and credentials. storage to be valid.
  --orientation {landscape,portrait}
                        Sort Reddit posts by.
  --shorts              Generate Youtube Shorts Video.
  --sort {top,hot}      Sort Reddit posts by.
  --submission-score SUBMISSION_SCORE
                        Minimum submission score threshold.
  --subreddits SUBREDDITS
                        Specify Subreddits, seperate with +.
  -s, --story-mode      Generate video for post title and selftext only, disables user comments.
  -t, --thumbnail-only  Generate thumbnail image only.
  --time {all,day,hour,month,week,year}
                        Filter by time.
  --total-posts TOTAL_POSTS
                        Enable video backgrounds.
  -u URL, --url URL     Specify Reddit post url, seperate with a comma for multiple posts.
  -l VIDEO_LENGTH, --video-length VIDEO_LENGTH
                        Set how long you want the video to be.
  --voice-engine {polly,balcon,gtts,tiktok,edge-tts,streamlabspolly}
                        Specify which text to speech engine to use.
```

## <a name='Customising'></a>Customising

Theres quite a few options you can customise in the `settings.py` file.

These will at some point be moved into the main `rybo.yaml` configuration file.

<details>
<summary>Click to view all available customisation options</summary>

### <a name='SpecifySubredditstoScrape'></a> Specify Subreddits to Scrape

```python
subreddits = [
    "AmItheAsshole",
    "antiwork",
    "AskMen",
    "ChoosingBeggars",
    "hatemyjob",
    "NoStupidQuestions",
    "pettyrevenge",
    "Showerthoughts",
    "TooAfraidToAsk",
    "TwoXChromosomes",
    "unpopularopinion",
    "confessions",
    "confession"
    ]
```

### <a name='ExcludeSubreddits'></a> Exclude Subreddits

```python
subreddits_excluded = [
    "r/CFB",
]
```

### <a name='FilterRedditsubmissionsbykeyword'></a> Filter Reddit submissions by keyword

```python
banned_keywords =["my", "nasty", "keywords"]
```

### <a name='ChangetheTexttoSpeechEngine'></a> Change the Text to Speech Engine

note AWS Polly requires and AWS account and auth tokens and can incur costs :

Supports Speech Engines :

* [AWS Polly](https://aws.amazon.com/polly/)
* [Balcon](http://www.cross-plus-a.com/bconsole.htm)
* Python [gtts](https://gtts.readthedocs.io/en/latest/)

```python
# choices "polly","balcon","gtts"
voice_engine = "polly"
```

### <a name='Limitthenumberofgeneratedvideos'></a> Limit the number of generated videos

```python
total_posts_to_process = 5
```

The next settings are to automatically filter out posts

### <a name='SkipRedditpostsbysubmissionscore'></a> Skip Reddit posts by submission score

Skip reddit posts that less than this amount of updates

```python
minimum_submission_score = 5000
```

### <a name='FilterRedditpostsbytitlelength'></a> Filter Reddit posts by title length

Filtering out reddit posts based on the reddit post title length

```python
title_length_minimum = 20
title_length_maximum = 100
```

### <a name='FilterRedditpostsbyselftextlength'></a> Filter Reddit posts by self text length

Filter out posts that exceed the maximum self text length

```python
maximum_length_self_text = 5000
```

### <a name='FilterRedditpostsbycommentcount'></a> Filter Reddit posts by comment count

Filter out reddit posts that don't have enough comments

```python
minimum_num_comments = 200
```

### <a name='Limitnumberofpoststoprocess'></a>Limit number of posts to process

Only attempt to process a maximum amount of reddit posts

```python
submission_limit = 1000
```

### <a name='Configurenumberofthumbnailstogenerate'></a> Configure number of thumbnails to generate

Specify how many thumbnail images you want to generate

```python
number_of_thumbnails = 3
```

### <a name='Setthemaximumvideolength'></a> Set the maximum video length
Specify the maximum video length

```python
max_video_length = 600 # Seconds
```

### <a name='Setmaximumnumberofcommentstoinclude'></a> Set maximum number of comments to include

Specify maximum amount of comments to generate in the video

```python
comment_limit = 600
```

### <a name='Specifyfolderpaths'></a> Specify folder paths

```python
assets_directory = "assets"
temp_directory = "temp"
audio_directory = str(Path("temp"))
fonts_directory = str(Path(assets_directory,"fonts"))
image_backgrounds_directory = str(Path(assets_directory,"image_backgrounds"))
images_directory = str(Path(assets_directory,"images"))
thumbnails_directory = str(Path(assets_directory,"images"))
background_directory = str(Path(assets_directory,"backgrounds"))
video_overlay_filepath = str(Path(assets_directory,"particles.mp4"))
videos_directory = "videos"
```

### <a name='Setvideodimensions'></a> Set video dimensions

```python
video_height = 720
video_width = 1280
clip_size = (video_width, video_height)
```

### <a name='Skipvideocompilation'></a> Skip video compilation

Skip compiling the video and just exit instead.

```python
enable_compilation = True
```

### <a name='SkipYouTubeuploading'></a> Skip YouTube uploading

```python
enable_upload = False
```

### <a name='Addavideooverlay'></a> Add a video overlay

Add a video overlay to the video, for example snow falling effect

```python
enable_overlay = True
```

### <a name='AddaNewscaster'></a> Add a Newscaster

Add in a newscaster reader to the video

```python
enable_newscaster = True
```

If the newcaster video is a green screen, attempt to remove the green screen

```python
newscaster_remove_greenscreen = True
```

Specify the color of the green screen in RGB

```python
newscaster_greenscreen_color = [1, 255, 17] # Enter the Green Screen RGB Colour
```

The higher the greenscreen threshold number the more it will attempt to remove.

```python
newscaster_greenscreen_remove_threshold = 100
```

Path to newcaster file

```python
newscaster_filepath = str(Path(assets_directory,"newscaster.mp4").resolve())
```

Position on the screen of the newscaster

```python
newscaster_position = ("left","bottom")
```

The size of the newscaster

```python
newcaster_size = (video_width * 0.5, video_height * 0.5)
```

### <a name='AddapauseaftereachTTSfile'></a> Add a pause after each TTS file

Add a pause after each text to speech audio file

```python
pause = 1 # Pause after speech
```

### <a name='Modifyappearnaceoftext'></a>Modify appearnace of text

```python
text_bg_color = "#1A1A1B"
text_bg_opacity = 1
text_color = "white"
text_font = "Verdana-Bold"
text_fontsize = 32
```

### <a name='DownloadimagesfromLexica'></a> Download images from Lexica

Download images from lexica or skip trying to download

```python
lexica_download_enabled = True
```
</details>

## <a name='TipsandTricks'></a> Tips and Tricks

### <a name='GenerateaVideoforaSpecificPost'></a>Generate a Video for a Specific Post

or if you want to generate a video for a specific reddit post you can specify it via the `--url` param :

```powershell
rybo --url https://www.reddit.com/r/AskReddit/comments/hvsxty/which_legendary_reddit_post_comment_can_you_still/
```

or you can do multiple url's by seperating with a comma, ie :

```powershell
rybo --url https://www.reddit.com/r/post1,https://www.reddit.com/r/post2,https://www.reddit.com/r/post3
```

### <a name='GenerateOnlyThumbnails'></a>Generate Only Thumbnails

if you want to generate only thumbnails you can specify `--thumbnail-only` mode, this will skip video compilation process :

```powershell
rybo --thumbnail-only
```

### <a name='EnableaNewscaster'></a>Enable a Newscaster

If you want to enable a Newscaster, edit settings.py and set :

```python
enable_newscaster = True
```

![](assets/newscaster.png)

If the newcaster video has a green screen you can remove it with the following settings,
use an eye dropper to get the RGB colour of the greenscreen and set it to have it removed :

```python
newscaster_remove_greenscreen = True
newscaster_greenscreen_color = [1, 255, 17] # Enter the Green Screen RGB Colour
newscaster_greenscreen_remove_threshold = 100
```