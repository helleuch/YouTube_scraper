# YouTube Channel Audio / Video Scraper
This script enables the download all videos from a given YouTube channel 
and export the audio to mp3 and wav.  

If you do not want to export audio to wav format, you'll have to set it to False in the code
as there is no line argument for that.  

### Setup
In order to run this script, do the following:  
1. Create a virtual environment using virtualEnv, Pipenv or conda
2. Install the requirements using:
```shell
pip install -r requirements.txt
```
3. Do the PyTube fix (see instructions below)

### How to run:
Simply use the following command: ```python3 scraper.py <args>``` to run the script.  
Args can be the following:  
* `-f` or `--file` if the channel URL is specified in a file.
The default file name is `link.txt`
* `-p` or `--path` to override the default file name.
* `-c` or `--channel` to specify the channel URL directly inline.


### PyTube fix:

In order to account for the new YouTube channel name starting with "@", 
you need to modify the `extract.py` file inside the pytube library.  
Replace the ```channel_name()``` function code with this one:  

```python
def channel_name(url: str) -> str:
    """Extract the ``channel_name`` or ``channel_id`` from a YouTube url.

    This function supports the following patterns:

    - :samp:`https://youtube.com/c/{channel_name}/*`
    - :samp:`https://youtube.com/channel/{channel_id}/*
    - :samp:`https://youtube.com/u/{channel_name}/*`
    - :samp:`https://youtube.com/user/{channel_id}/*
    - :samp:`https://youtube.com/@{channel_name}/*`

    :param str url:
        A YouTube url containing a channel name.
    :rtype: str
    :returns:
        YouTube channel name.
    """
    patterns = [
        r"(?:\/(c)\/([%\d\w_\-]+)(\/.*)?)",
        r"(?:\/(channel)\/([%\w\d_\-]+)(\/.*)?)",
        r"(?:\/(u)\/([%\d\w_\-]+)(\/.*)?)",
        r"(?:\/(user)\/([%\w\d_\-]+)(\/.*)?)",
        r"(?:(@[%\w\d_-]+)(.*)?)"
    ]
    for pattern in patterns:
        regex = re.compile(pattern)
        function_match = regex.search(url)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            uri_style = function_match.group(1)
            uri_identifier = function_match.group(2)
            return f'/{uri_style}/{uri_identifier}'

    raise RegexMatchError(
        caller="channel_name", pattern="patterns"
    )
```