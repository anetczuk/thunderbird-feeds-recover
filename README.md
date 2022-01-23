# Fix Thunderbird corrupted or gone Feeds

Rebuild corrupted or empty *feeds.json* by recovering data based on other files in *Feeds* directory.

Have You lost Your feeds? Did You delete `feeds.json` by accident? 
Are You victim of [Bug 1701414](https://bugzilla.mozilla.org/show_bug.cgi?id=1701414)? 
This program will restore Your belowed feeds configuration!

Recovery is especially dedicated for modern Thunderbird users (around TB version 78).


## Running

To fix the feeds execute following command `./src/startfeedsfix`. Script will try to deduce Thunderbird's
home path and read default profile. Optionally it is possible to pass path to `feeditems.json`.


## Feeds files structure

- `feeds.json` -- feeds configuration
- `feeditems.json` -- all feed items list
- `<name>` -- file contains email-like feed items content
- `<name>.msf` -- file-based Mork database
- `<name>.sbd` -- directory containing nested feeds

Other files:
- `msgFilterRules.dat`
- `filterlog.html`


## `feeds.json` structure

```
[{'destFolder': 'mailbox://nobody@<thunderbird_feed_path>',
'lastModified': 'Sat, 22 Jan 2022 00:34:48 GMT',
'link': '<feed_website_url>',
'options': {'category': {'enabled': False,
                         'prefix': '',
                         'prefixEnabled': False},
            'updates': {'enabled': True,
                        'lastDownloadTime': None,
                        'lastUpdateTime': <last_update_timestamp>,
                        'updateBase': '',
                        'updateFrequency': '',
                        'updateMinutes': 100,
                        'updatePeriod': '',
                        'updateUnits': 'min'},
            'version': 2},
'quickMode': False,
'title': '<feed_title>',
'url': '<feed_url>'}
...
]

```

Fields:
- `<thunderbird_feed_path>` -- path of feed in Thunderbird's Folder Pane
- `<last_update_timestamp>` -- time of last update (Unix time in milliseconds)
- `<feed_url>` -- url of feed
- `<feed_title>` -- title of feed (not important)
- `<feed_website_url>` -- general website url (not important)


## How to restore lost feeds list?

1. Read *message id*s and feed urls from `feeditems.json`
2. Find feed's proper subdirectory based on *message id* (`<thunderbird_feed_path>`)
3. Fill `<feed_url>` taken directly from `feeditems.json`
4. Read `<feed_title>` and `<feed_website_url>` directly from `<feed_url>`
5. Loosely set `<last_update_timestamp>`


## References:

- Mork file format (https://en.wikipedia.org/wiki/Mork_%28file_format%29)
- RSS Issue (https://support.mozilla.org/it/questions/1331792)
- Bug 1701414 (https://bugzilla.mozilla.org/show_bug.cgi?id=1701414)
