# ARMCHAIR
**A**utomated **R**SS **M**onitor **C**orpus **H**elper **A**nd **I**nformation **R**eporter 

![ARMCHAIR logo](/icons/armchair_logo_512x512.png)

## About ##

ARMCHAIR can help you create large corpora based on web data that is accessible via RSS feeds (newspapers and magazines, but also many blogs and some social media sites).
You can provide any number of RSS feeds alongside some metadata (website, feed name, category, country, language) by editing the "rss_feeds.csv" file. Use the "comfy_armchair.py" GUI to run or use one of the command line scripts.

**Now you can proudly admit to being an ARMCHAIR linguist!**


## What can ARMCHAIR do right now? ##
 * Check all feeds for new items
 * Keep an index and metadata of all collected items in CSV files (one per feed)
 * Create unique identifiers for each item (based on the publication date and the URL)
 * Download all new items (full html)
 * Start the process either directly (using simple_armchair.py or endless_armchair.py) or via GUI (comfy_armchair.py)


## What will ARMCHAIR be able to do? ##
 * Automatically strip boilerplate text (using the excellent jusText package) from the raw html files
 * Convert the extracted "article text" to XML files with the metadata as attributes
 * Compile multiple articles into larger files. 
 * Gather and report information on the full monitor corpus (as well as the individual feed subcorpora), such as token lists and stylistic metrics
 * Add/Edit the RSS feeds from a GUI (currently a .csv file needs to be edited in the spreadsheet software of your choice, e.g. Miscrosoft Excel or LibreOffice Calc)

## Files ##
 * rss_feeds.csv contains the RSS feeds from which to gather data.
 * armchair.py contains most of the actual code, but shouldn't normally be run directly.
 * comfy_armchair.py offers a to start the collection of texts manually (once or repeated runs). Eventually RSS settings should be editable from here as well.
 * simple_armchair.py this script will gather data from all feeds once when it is run. This is useful if you have a way to automatically start it (multiple times) each day( e.g. with a cronjob).
 * endless_armchair.py this script can can be left running and will automatically collect data every hour.

## Requirements ##
For now, ARMCHAIR needs to be run using an installed version of Python. A Windows EXE file will be available soon. To run the .py files you need:

  * Python 3.x 
  * The following modules:
      * feedparser
      * lxml
      * pandas
      * chardet
      * justext
      * fake_useragent (optional)

All modules except "justExt" and "fake_useragent" are included in the "Anaconda Python distribution". The justExt module will soon be optional, but is required if you desire automated boilerplate removal and XML conversion.
