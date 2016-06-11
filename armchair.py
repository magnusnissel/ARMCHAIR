import os
import re
import feedparser
import requests
import email.utils
import hashlib
import chardet
import datetime
import fake_useragent
import sqlite3 as sql
import pandas as pd
import numpy as np
import lxml.etree as etree
import justext

class Armchair():
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.feed_path = os.path.join(self.base_dir, "rss_feeds.csv")
        self.index_dir = os.path.join(self.base_dir, "indices")
        self.raw_dir = os.path.join(self.base_dir, "original_html")
        self.proc_dir = os.path.join(self.base_dir, "processed_xml")
        self.monitor_dir = os.path.join(self.base_dir, "monitor_corpus")
        try: 
            self.user_agent = None
            #self.user_agent = fake_useragent.UserAgent()
        except Exception:
            self.user_agent = None
        try:
            os.makedirs(self.index_dir)
        except IOError:
            pass
        try:
            os.makedirs(self.raw_dir)
        except IOError:
            pass
        try:
            os.makedirs(self.proc_dir)
        except IOError:
            pass
        try:
            os.makedirs(self.monitor_dir)
        except IOError:
            pass


        try:
            self.feed_list_df = pd.read_csv(self.feed_path)
        except IOError:
            self.feed_list_df = pd.DataFrame()
        """
            "feed_url","feed_name","website","country","language","category"
        """

    @staticmethod
    def standardize_pub_date(pub):
        s_pub = "0000-00-00"
        try:
            s_pub = datetime.datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(pub)))
            s_pub = str(s_pub)[:10]
        except Exception as x:
            print(x)
            if "T" in pub:  # looks like ISO 8601
                s_pub = pub.replace('Z', '')
                # 2013-10-24T14:53:13-04:00
                # unconverted data remains: -04:00
                num_colons = s_pub.count(':')
            # looks like we need to remove timezone substr next
                if num_colons == 3:
                    s_pub = s_pub[:-6]
                try:
                    s_pub = datetime.datetime.strptime(s_pub, "%Y-%m-%dT%H:%M:%S")
                except Exception as x:
                    print(x)
                    s_pub = "0000-00-00"
        return s_pub


    @staticmethod
    def create_hash_identifier(r):
        item_hash = hashlib.sha1()
        hash_str = "{}{}".format(str(r["published"])[:6], r["link"])
        hash_str = hash_str.encode('utf-8')
        item_hash.update(hash_str)
        hash_str = item_hash.hexdigest()
        return hash_str


    def apply_feed_indexer(self, r):
        print("\t", r["feed_url"])
        url = str(r["feed_url"])
        if url:
            entry_list = []
            feed = feedparser.parse(url)
            for i, e in enumerate(feed.entries):
                if e["published"]:
                    e["published"] = self.standardize_pub_date(e["published"])
                else:
                    e["published"] = "0000-00-00"
                e = dict(e)
                e.update(dict(r))
                e["armchair_identifier"] = self.create_hash_identifier(e)
                entry_list.append(e)
            if entry_list:
                df = pd.DataFrame.from_records(entry_list)
                df = df.set_index("armchair_identifier")
                self.feed_items_df = self.feed_items_df.append(df, ignore_index=False)

    def index_items(self):
        self.feed_items_df = pd.DataFrame()
        self.new_feed_items_df = pd.DataFrame()
        # get feed items
        if len(self.feed_list_df.index) > 0:
            self.feed_list_df.apply(self.apply_feed_indexer, axis=1) 
            if len(self.feed_items_df.index) > 0:
                for i, r in self.feed_list_df.iterrows():
                    fn = "index_{}_{}_{}".format(r["country"], r["website"], r["feed_name"])
                    fn = "{}.csv".format(self.escape_filename(fn))
                    index_path = os.path.join(self.index_dir, fn)
                    new_df = self.feed_items_df[self.feed_items_df["feed_url"]==r["feed_url"]]
                    cols = [c for c in new_df.columns if "Unnamed:" not in c]
                    new_df=new_df[cols]
                    new_df["downloaded"] = False
                    new_df["processed"] = False
                    new_df["justext_comment"] = np.nan
                    new_df["original_html_file"] = np.nan
                    new_df["extraction_method"] = np.nan
                    #new_df = new_df.set_index("armchair_identifier")
                    try:
                        df = pd.read_csv(index_path, index_col=0)
                    except OSError:  # e.g if not exist then save all
                        new_df.to_csv(index_path)
                        self.new_feed_items_df = self.new_feed_items_df.append(new_df, ignore_index=False)
                    else:  # check which new
                        existing_identifiers = set(df.index)
                        #new_df = new_df[~new_df["armchair_identifier"].isin(existing_identifiers)]  # only rows with new identifiers
                        new_df = new_df[~new_df.index.isin(existing_identifiers)]  # only rows with new identifiers
                        if len(new_df.index)>0:
                            df = df.append(new_df, ignore_index=False)
                            df.to_csv(index_path)
                            self.new_feed_items_df = self.new_feed_items_df.append(new_df, ignore_index=False)
                        else:
                            print("No new items found for", r["feed_url"])
                    

    def load_indices(self, which=[]):
        self.index_files = [os.path.join(dp, f) for dp, dn, fn in 
                            os.walk(os.path.expanduser(self.index_dir))
                            for f in fn if '.csv' in os.path.basename(f)]
        self.index_df = {}
        for f in self.index_files:
            fn = os.path.basename(f)
            self.index_df[fn] = pd.read_csv(f, index_col=0)
            #self.index_df[fn] = self.index_df[fn].set_index("armchair_identifier")

 

    def download_file(self, url, file_path):
        if self.user_agent:
            headers = {'user-agent': self.user_agent.random, 'referer': 'http://www.google.com'}
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'referer': 'http://www.google.com'}
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.TooManyRedirects as e:
            print("WARNING: Unable to download", url, ":", e)
            return False
        else:
            content = response.content
            try:
                text = content.decode("utf-8")
            except Exception as e:
                detected = chardet.detect(content)
                text = content.decode(detected["encoding"])
            if text:
                with open(file_path, "w") as h:
                    h.write(text)
                print("Downloaded", url)
                return True
            else:
                return False

    @staticmethod
    def escape_filename(s):
        s = "".join([c for c in s if c.isalnum() or c in {"-", "_", " "}]).replace(" ", "-")
        s = re.sub(r"-{2,}", r"-", s)
        return s

    def apply_item_grabber(self, r):
        w = self.escape_filename(r["website"])
        fn = self.escape_filename(r["feed_name"])

        index_key = "index_{}_{}_{}".format(r["country"], r["website"], r["feed_name"]) 
        index_key = "{}.csv".format(self.escape_filename(index_key))
        filename = "{}_{}_{}_{}".format(w, fn, r["published"], r.name)
        filename = "{}.html".format(self.escape_filename(filename))
        file_dir = os.path.join(self.raw_dir, w, fn)
        try:
            os.makedirs(file_dir)
        except IOError as e:
            pass
        file_path = os.path.join(file_dir, filename)
        success = self.download_file(r["link"], file_path)
        self.index_df[index_key].loc[r.name, "original_html_file"] = filename
        self.index_df[index_key].loc[r.name, "downloaded"] = success

    def grab_items(self): 
        if len(self.new_feed_items_df.index) > 0:
            self.load_indices()
            self.new_feed_items_df.apply(self.apply_item_grabber, axis=1)
            for key, df in self.index_df.items():
                index_path = os.path.join(self.index_dir, key)
                df.to_csv(index_path)


    def process_items(self, use_justext=True, only_unprocessed=True):
        self.load_indices()
        self.new_feed_items_df = pd.DataFrame()
        for index_file in self.index_files:
            print(index_file)
            df = pd.read_csv(index_file, index_col=0)
            self.new_feed_items_df = self.new_feed_items_df.append(df, ignore_index=False)

        process_df = self.new_feed_items_df[self.new_feed_items_df["downloaded"]==True]
        if only_unprocessed:
            process_df = process_df[process_df["processed"]==False] 
            
        if len(process_df.index) > 0:
            if use_justext:
                process_df.apply(self.apply_justext_boilerplate_stripper, axis=1)
            for key, df in self.index_df.items():
                index_path = os.path.join(self.index_dir, key)
                df.to_csv(index_path)


    def apply_justext_boilerplate_stripper(self, r):
        index_key = "index_{}_{}_{}".format(r["country"], r["website"], r["feed_name"]) 
        index_key = "{}.csv".format(self.escape_filename(index_key))
        w = self.escape_filename(r["website"])
        feed_name = self.escape_filename(r["feed_name"])
        original_html_path = os.path.join(self.raw_dir, w, feed_name, r["original_html_file"])
        xml_dir = os.path.join(self.proc_dir, w, feed_name)
        try:
            os.makedirs(xml_dir)
        except IOError:
            pass
        processed_xml_path = os.path.join(xml_dir, r["original_html_file"].replace(".html", ".xml"))
        try:
            with open(original_html_path, "r") as h:
                text = h.read()
        except FileNotFoundError:
            text = None
            self.index_df[index_key].loc[r.name, "downloaded"] = False
            self.index_df[index_key].loc[r.name, "processed"] = False
            self.index_df[index_key].loc[r.name, "justext_comment"] = np.nan
        if text:
            paragraphs = justext.justext(text, justext.get_stoplist("English"))
            to_keep = []
            bp_count = 0
            for paragraph in paragraphs:
                if not paragraph.is_boilerplate:
                    to_keep.append(paragraph)
                else:
                    bp_count += 1
            if to_keep:
                root = etree.Element("text")
                tree = etree.ElementTree(root)
                for paragraph in to_keep:
                    p_elem = etree.Element("p")
                    p_elem.text = paragraph.text
                    root.append(p_elem)
                xml_str = etree.tounicode(tree)
                try:
                    tree.write(processed_xml_path, pretty_print=True, encoding='utf-8', xml_declaration=True)
                except IOError as e:
                    print("WARNING: Could not write XML file:", e)
                    self.index_df[index_key].loc[r.name, "processed"] = False
                else:
                    self.index_df[index_key].loc[r.name, "processed"] = True
            else:
                print("WARNING: No non-boilerplate code found for", original_html_path)
            self.index_df[index_key].loc[r.name, "justext_comment"] = "{}/{}".format(len(to_keep), bp_count)
            self.index_df[index_key].loc[r.name, "extraction_method"] = "jusText"

 

def main():
    print("Are you debugging?")
    a = Armchair()
    a.index_items()
    a.grab_items()
    a.process_items(only_unprocessed=False) 

if __name__ == "__main__":
    main()