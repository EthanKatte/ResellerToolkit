# ResellerToolkit

# What is it
This is a script (That only works with links from JBHIFI.com at the moment) that can get the current listed products and check their most recent sale price on ebay.com.
It uses Selenium to scrape both sites using 4 threads. It is set up in a way that should work with many other websites by defining the class and type of the
HTML element that holds the name and price of the item.

This script does not do any sophisticated filtering of the sold items or the prices and will not be 100% accurate but can provide a shortlist that is useful to check.

# How to use it
At the moment, the script does not support any commands and must be editted for any other websites.
`python ./Scraper.py` runs the check. The console is filled with various outputs from the creation and closure of hundreds of selenium instances.
The output will be stored in "CatchMain.csv" this can be opened in excel and then assessed further.

![image](https://user-images.githubusercontent.com/61607335/222873366-461059db-e0d8-48b8-9d2f-ec45e4c77b1a.png)

# How to install it
Clone the repository using `git clone https://github.com/EthanKatte/ResellerToolkit.git`
Ensure that selenium and beautiful soup are installed `pip install selenium` and `pip install bs4` respectively
 
 
