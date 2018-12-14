#Code inspiration for the spider from Stephen on http://www.netinstructions.com/how-to-make-a-web-crawler-in-under-50-lines-of-python-code/
from socket import timeout
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import urllib.request
import csv
from threading import Thread, Lock
from sys import argv, exit
from time import sleep
from tkinter import *
from tkinter.filedialog import *
import random
import tkinter as tk

urls = dict()
lock = Lock()

    
class LinkParser(HTMLParser):
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    if "\n" not in newUrl:
                        self.links = self.links + [newUrl]

    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        try: 
            response = urllib.request.urlopen(url, timeout=10).read().decode('utf-8')
            self.feed(response)
            return response, self.links
        except urllib.error.HTTPError:
            return "",[]
        except urllib.error.URLError:
            return "",[]
        except UnicodeDecodeError:
            return "", []
#the crawler function

def spider(url):
    #sets the first url to be checked as the one sent to the function
    pagesToVisit = [url]
    while len(pagesToVisit) > 0:
        url = pagesToVisit[0]
        #removes the current url being checked
        pagesToVisit = pagesToVisit[1:]
        #if the url is new then check it
        if url not in urls:
            parser = LinkParser()
            data, links = parser.getLinks(url)
            lock.acquire()
            urls[url] = []
            for u in links:
                #if the url is not a duplicate of one already checked then add it to the list
                if u not in urls[url]:
                    urls[url].append(u)
                #if the page has not been visited add it to the pagesToVisit list
                if u not in urls:
                    pagesToVisit.append(u)
            lock.release()
        #once the pages column reaches 75 urls stop the crawler
        if len(urls) >= 75:
            break
#the function to draw the graph
def draw_graph(dictionary):
    #assign each url a number counterpart
    all_links = convert_to_numbers(dictionary)
    xcoor = dict()
    ycoor = dict()
    root = Tk()
    dim = 800
    cnv = Canvas(root, width = dim, height = dim)
    #every unique link is put on a random point on the canvas
    for link in all_links:
        #assign each url a random point on the canvas
        x = random.randint(20, dim - 20)
        y = random.randint(20, dim - 20)
        xcoor[link] = x
        ycoor[link] = y
        #draw the number on the canvas
        cnv.create_text(x, y, anchor=W, font="Purisa",
            text=all_links[link])
    #get each link's coordinates
    for links in dictionary:
        x = xcoor[links]
        y = ycoor[links]
        for link in dictionary[links]:
            x2 = xcoor[link]
            y2 = ycoor[link]
            #create an arrow from the "links" to the "pages"
            cnv.create_line(x2, y2, x, y, arrow=tk.LAST)       
    cnv.pack()
    

#every unique link is put into a single list with the indexes being the number they are assigned
def convert_to_numbers(dictionary):
    all_links = dict()
    count = 0
    for links in dictionary:
        all_links[links] = count
        count+=1
          
    for links in dictionary:
        for link in dictionary[links]:
            if link not in all_links:
                all_links[link] = count
                count+=1
    return all_links
#counts the number of links pointing to the url and finds the largest amount of links pointing to a single url
def most_popular():
    max_urls = 0
    links = convert_to_numbers(urls)
    link_count = dict()
    #initializes the count for each url as 0
    for link in links:
        link_count[link] = 0
    #goes through all the urs    
    for url in urls:
        for link in link_count:
            #if the link is visited by a page increment the count
            if link in urls[url]:
                link_count[link]+=1
                #if the count exceeds the max then set the max to the current count
                if link_count[link] > max_urls:
                    max_urls = link_count[link]
    
    return max_urls, link_count

def main():
    #change name to check diffent text files
    with open('urls6.txt') as fp:
        line = fp.readline()
        
        while line:
            line2 = fp.readline()
            if line2:
                #each thread crawls one of the webpages given in the text file
                thread1 = Thread(target=spider, args=(line.rstrip(),))
                thread2 = Thread(target=spider, args=(line2.rstrip(),))
                thread1.start()
                thread2.start()
                thread1.join()
                thread2.join()
            else:
                thread1 = Thread(target=spider, args=(line.rstrip(),))
                thread1.start()
                thread1.join()
            line = fp.readline()
    draw_graph(urls)
    max_urls, link_count = most_popular()
    #writes the data to a csv file
    with open('crawlerData.csv', mode='w', encoding='utf-8') as crawl:
        crawl_writer = csv.writer(crawl, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        crawl_writer.writerow(['PAGE', 'LINKS'])
        for u in urls:
            if len(urls[u]) > 0:
                crawl_writer.writerow([u, urls[u]])
            else:
                crawl_writer.writerow([u])
        #writes the most popular page to the csv file        
        crawl_writer.writerow(["Most Popular Page Count:", max_urls])
        #check for ties. 
        for link in link_count:
            #if the count equals the max then write it to the csv
            if link_count[link] == max_urls:
                crawl_writer.writerow([link])
        
