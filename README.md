# ARMCHAIR
**A**utomated **R**SS **M**onitor **C**orpus **H**elper **A**nd **I**nformation **R**eporter 

## About ##

ARMCHAIR can help you create large corpora based on web data that is accessible via RSS feeds (newspapers and magazines, but also many blogs and some social media sites).
You can provide any number of RSS feeds alongside some metadata (website, feed name, category, country, language) by editing the "rss_feeds.csv" file in the spreadsheet 
software of your choice. Eventually, I hope to provide a GUI for this as well.
Now you can proudly admit to being an ARMCHAIR linguist.


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
 * Add/Edit the RSS feeds from a GUI (Currently a .csv file needs to be edited in the spreadsheet software of your choice, e.g. Miscrosoft Excel or LibreOffice Calc)

 ## Files ##e
 * rss_feeds.csv contains the RSS feeds from which to gather data.
 * armchair.py contains most of the actual code, but shouldn't normally be run directly.
 * comfy_armchair.py offers a to start the collection of texts manually (once or repeated runs). Eventually RSS settings should be editable from here as well.
 * simple_armchair.py this script will gather data from all feeds once when it is run. This is useful if you have a way to automatically start it (multiple times) each day( e.g. with a cronjob).
 * endless_armchair.py this script can can be left running and will automatically collect data every 2/4/6 etc. hours.