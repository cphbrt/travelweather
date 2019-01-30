# [Travelcast.me][1]

This repository contains the source code for [https://travelcast.me][1],
i.e. your **travel forecast**!

We began this project at HackMT 2019, a 36 hour hackathon for students, aided by professionals,
and hosted by Middle Tennessee State University.

## Should You Contribute?

Yes! If you are an absolute beginner, please interact with this repository! This project spawned out of a
student-oriented hackathon. Half of our original team never even used `git` before this project!

We're working to make this `README.md` and the code itself as informative and educational as possible.
Give it a read and see if you learn anything new!

## Table of Contents

- [Objectives](#objectives)
  - [Jukebox Model](#jukebox-model)
- [Architecture](#architecture)
  - [GitHub Pages](#github-pages)
  - [Google Cloud Functions](#google-cloud-functions)
  - [Google Maps API](#google-maps-api)
  - [Dark Sky Weather API](#dark-sky-weather-api)
- [Contributors](#contributors)
## Objectives

During the hackathon, we met our basic objectives:

1. Create a tool that forecasts the weather you'll encounter over time as you travel.
1. Construct this tool out of free-tier APIs and developer tools.

Our objectives going forward are similarly humble:

1. Improve [travelcast.me][1]'s accuracy and user experience.
1. Overcome the restrictions of the free-tier APIs through the [Jukebox Model](#jukebox-model).

### Jukebox Model

The Jukebox Model (if you know the "real" name for this, let me know with a pull request!) works like a real-world
old-school jukebox:

- I want to listen to music, but no music is playing
- I happen to have a quarter on hand
- So I plop in my quarter, select the song of my choice, and press play!
- Now I get music, _and everyone else in the diner enjoys the music as well!_

We aren't _tied_ to this model, but we're very interested in alternative ways to keep a tool
like this alive and thriving _without_ resorting to lame stuff like ads.

## Architecture

```
+--------+     1    +---------+
| GitHub | <------- | User    | <----+
| Pages  | -------> | Browser | ---+ |
+--------+     2    +---------+    | | 
                                 3 | | 8
                   +----------+    | |
+----------+   4   | Google   | <--+ |
| Google   | <---- | Cloud    | -----+
| Maps API | ----> | Function |
+----------+   5   +----------+
                         | ^
        +----------+   6 | | 
        | Dark Sky | <---+ | 7
        | Weather  | ------+
        | API      |
        *----------+
```

### [GitHub Pages][2]

[GitHub Pages][2] hosts static content from your repository for _**free**_!

So our website's `index.html`, `scripts.js`, `styles.css`, and other web-facing files are served
to the world at no cost to us. All we do is push any updates to our `master` branch, and the
updated site is live in _seconds_.

[GitHub Pages][2] permits our site to use 
[up to 100GB per month](https://help.github.com/articles/what-is-github-pages/#usage-limits)!
Our whole repository is currently about 148 KB, so our site could get over 675,000 visits before
we even approach this limit.

One restriction is that we musn't use [GitHub Pages][2] as hosting for a _commercial_ site.
Fortunately, our current objectives are in no way commercial.

_(Note that GitHub Pages hosts your website at `https://username.github.io` by default.
We cheated on the "free-tier" rule and purchased the `travelcast.me` domain for $3.49
because it sounded awesome.)_

tldr; [GitHub Pages][2] sends the website to the user's browser.

### [Google Cloud Functions][3]

#### What it is

[Google Cloud Functions][3] run your code for you. Instead of setting up an old desktop
computer in your closet or renting a hosted web server at $`X` per month and figuring
out how to keep it running smoothly, the process of using a [Google Cloud Function][3]
is like so:

1. Navigate the Google Cloud Console to click "Create Function"
1. Paste code into the textbox (Python, Node.js, or Go; we use Python, which you can see in `functions.py`)
1. Specify what function in that code is supposed to get called
1. Click "Save"

Boom. It gives you a URL that triggers the code. The Console even has a tab for testing
the function live with JSON input copy-pasted into another textbox.

#### How we use it
The magic of [travelcast.me][1] happens on our Function like so:

1. After retrieving the `index.html`, etc. from GitHub Pages, the user inputs start and
   end locations and clicks the "Route" button.
1. When the "Route" button is clicked, code in `scripts.js` sends a request to the URL
   of our [Google Cloud Functions][3]. This request contains JSON not much more complex than this:
   ```json
   {
       "start_location": "New York, NY",
       "end_location"  : "San Francisco, CA"
   }
   ```
1. The Function receives that JSON as input, reads it, and makes a request to the [Google Maps API][4].
   The [Google Maps API][4] returns more JSON that contains the path the user should take to get from
   their start location to their end location and how long it will take the user to do so.
1. The Function reads the data from the [Google Maps API][4] to find out what intermediate locations
   the user will travel through and what time they'll be there.
1. The Function uses its new knowledge of the future locations of the user on their journey to make
   a series of requests to the [Dark Sky Weather API][5] to find out what the weather will be like
   at each location at the corresponding time.
1. Finally, the Function organizes the important information into a nice little bit of JSON and sends
   that back to the user's browser to be processed by the code `scripts.json` and displayed for the
   user to see.

_Whew!_ That's a mouthful. We accidentally covered almost the whole architecture right there.
And as you'll see, the [Google Cloud Functions][3] made it easier than ever.

#### Why it is cool

Not only is the Function ridiculously easy to use (copy & paste code to update a website's core
functionality in seconds), but it is free, like _super_ free.

The pricing calculations for the Function's free tier are a little more complicated than
the easy 100 GB / month of GitHub Pages, but, according to my estimates (accounting for the small size
of our requests and simple Python code but numerous outgoing API calls), we can probably call
our Function 1,000,000 times per month at no cost.

#### But wait... Why not do all this logic in `scripts.js` from the user's browser?

It would be _way_ simpler to just have the javascript in the user's browser make all these API calls and
process the relevant data without a [Google Cloud Functions][3] in the middle.

_**BUT**_, APIs like [Google Maps][4] and [Dark Sky][5] require you to provide a secret _API key_
every time you make a call to their API so that they can count your requests and bill you appropriately
(and make sure you're not abusing their free-tier).

We can't put those API keys in the `scripts.js` code, because then they would be sent to the user's
browser where a mean user could steal them and use them for their own site! (Even now, a malicious
individually could send thousands of automated requests to our site to use up all our free-tier
API calls 😰)

To avoid this, we put our API keys in _environment variables_ provided to the Function (again, 
just copy & paste into a little text box next to where you paste the Python code). The Python
code then accesses the environment variables through calls like so:

```python
import os

mapsApiKey = os.getenv('MAP_API_KEY')
```

This way, the keys stay secret, the code stays public, and the site works great!

tldr; [Google Cloud Functions][3] are super cool and cheap, and we use them to gather all the map and weather data.

### [Google Maps API][4]

I got excited and explained how these fit into our architecture pretty thoroughly in the [Google Cloud
Functions section](#google-cloud-functions).

Basically, you send the Maps API your start location and end location as well as additional
information like departure time and mode of transportation, then it sends back to you all the directions
you should follow and how long it will take you to get there.

The free-tier of this API can supply thousands of requests per month. I'm still working out the details on how much exactly.

### [Dark Sky Weather API][5]

I explained this one in the [Google Cloud Functions section](#google-cloud-functions) also.

Simpler even than the Maps API, you send the weather API a single location and it returns the fully forecast for that location broken down into hourly, daily, and weekly increments.

The free-tier of this API is the most restrictive, with a hard cap of 1,000 requests per day.

[1]: https://travelcast.me
[2]: https://pages.github.com/
[3]: https://cloud.google.com/functions/
[4]: https://developers.google.com/maps/documentation/
[5]: https://darksky.net/dev
