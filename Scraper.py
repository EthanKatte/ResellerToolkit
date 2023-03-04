import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from enum import Enum
import time


class item:
    def __init__(self, title, buySite, price, resell, numSales, ebayUrl, worth):
        self.title =title
        self.buySite =buySite
        self.price =price
        self.resell =resell
        self.numSales =numSales
        self.ebayUrl =ebayUrl
        self.worth = worth 

    def __str__(self):
        csv = str(self.worth) + ", " + str(self.title) + ", " + str(self.price) + ", " + str(self.resell) + ", " + str(self.numSales) + ", " + str(self.buySite) + ", " + str(self.ebayUrl) + "\n"
        return csv

def condenseFiles(numChild):
    with open(f'catchMain.csv', 'a') as fMain:
        for child in range(1, numChild+1):
            print(child)
            with open(f'catchChild{child}.csv', 'r') as f:
                f.readline()
                for line in f:
                    fMain.write(line)



class site(Enum):
    jbhifi = 0

urls = ["https://www.jbhifi.com.au/collections/movies-tv-shows/movies-all-genres?page=1&hitsPerPage=500&sortBy=price_asc",
        "https://www.jbhifi.com.au/collections/movies-tv-shows/all-tv-genres?page=1&hitsPerPage=500&sortBy=price_asc"
        ]

#the container class name for each site 
containers = [("product-tile__container", "div")]

def cleanFile():
    with open("catchMain.csv", "w") as f:
        f.write("worth it?,  title,  price,  resell,  numSales,  buySite,  ebayUrl\n")

def marginCheck(resale, new):
    return resale > new

def uncsv(csvFormat):
    splitVals = csvFormat.split(",")
    newItem = item(splitVals[1], splitVals[5], splitVals[2], splitVals[3], splitVals[4], splitVals[6], splitVals[0])
    return newItem

def writeToJbFile(entries, child):
    with open(f'catchChild{child}.csv', 'w') as f:
        f.write("worth it?,  title,  price,  resell,  numSales,  buySite,  ebayUrl\n")
        for obj in entries:
            f.write(str(obj.worth) + ", " + str(obj.title) + ", " + str(obj.price) + ", " + str(obj.resell) + ", " + str(obj.numSales) + ", " + str(obj.buySite) + ", " + str(obj.ebayUrl) + "\n")


def ebayCheck(csventries, child):
    entries = []
    for csvEntry in csventries:
        entries.append(uncsv(csvEntry))

    #HTML Data
    container = "s-item__wrapper"
    containerType = "div"

    titleClass = "s-item__title"
    titleType = "div"

    priceClass = "s-item__price"
    priceType = "span"

    for entryObj in entries:

        #print("TITLE = " + entryObj.title)
        
        entry = entryObj.title
        entry = entry.replace(" ", "+")

        url = f"https://www.ebay.com.au/sch/i.html?_nkw={entry}&LH_Sold=1&LH_Complete=1"

        #reduces console output
        chromeOptions = Options()
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--log-level=0")

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(options=chromeOptions, service_log_path='NUL')

        # Wait up to 10 seconds for the page to load
        driver.implicitly_wait(10)

        # Load the page
        driver.get(url)

        # Wait for the div with the specified class to load
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, container)))

        # Get the page source after the content has loaded
        html = driver.page_source

        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(html, "html.parser")

        # Find all div tags with the specified class
        items = soup.find_all(containerType, class_=container)
        

        #total sold prices
        sum = 0
        #number of items
        counter = 0

        for item in items:

            ignore = False


            title = "Error"
            price = "Error"

            if title:
                try:
                    title = item.find(titleType, titleClass).text
                    if "," in title:
                        title.remove(",")
                except:
                    title = "Error"
            if price:
                try:
                    price = item.find(priceType, priceClass).text.split("$")[1]
                except:
                    price = "Error"

            if title == "Shop on eBay" or title == "Error":
                ignore = True
            
            if not ignore:
                for word in entryObj.title.split(" "):
                    if word not in title:
                        ignore = True

            if not ignore: 
                try:
                    sum+=float(price)
                    counter+=1
                except:
                    ignore = True
            
        if counter != 0:
            sum = sum/counter

        entryObj.numSales = counter
        entryObj.resell = sum
        entryObj.ebayUrl = url
        if "$" in entryObj.price:
            ogPrice = float(entryObj.price.replace("$", ""))
        else:
            ogPrice = float(entryObj.price)

        if marginCheck(sum, ogPrice):
            entryObj.worth = True
        else:
            entryObj.worth = False
    
    writeToJbFile(entries, child)
    
def seperatecodes(codes): #seperates the codes into 4 subsets for the children
    
    code1 = []
    code2 = []
    code3 = []
    code4 = []
    codeNum = 0

        #newItem = item()
        #newItem.title =code.title
        #newItem.buysite =code.buysite
        #newItem.price =code.price
        #newItem.resell =code.resell
        #newItem.numSales =code.numSales
        #newItem.ebayUrl =code.ebayUrl
        #newItem.worth =code.worth


    for code in codes:
        if codeNum == 0:
            code1.append(code)
            codeNum += 1
        elif codeNum == 1:
            code2.append(code)
            codeNum += 1
        elif codeNum == 2:
            code3.append(code)
            codeNum += 1
        elif codeNum == 3:
            code4.append(code)
            codeNum -= 3

    return code1,code2,code3,code4


def jbhificheck(items):

    resultObjs = []
    #HTML Information for JBHIFI.com.au
    titleClass = "product-tile__title"
    typeClass = "product-preamble"
    dollarClass = "ais-hit--price"
    #Backup Dollar is required for some sale items
    backupDollarClass = "currency"

    titleDivType = "h4"
    typeDivType = "div"
    dollarDivType = "span"
    backupDollarDivType = "div"

    for element in items:
        itemObj = item("", "", "", "", "", "", False)
        titlePreSplit = element.find(titleDivType, titleClass)
        type = element.find(typeDivType, typeClass)
        dollar = element.find(dollarDivType, dollarClass)

        #handles Null Values and fixs some sale prices
        if True:
            if not titlePreSplit:
                titlePreSplit = "error: title not found"
            else:
                titlePreSplit = titlePreSplit.text
            if not type:
                type = "error: type not found"
            else:
                type = type.text
            if not dollar:
                dollar = element.find(backupDollarDivType, backupDollarClass)
                if not dollar:
                    dollar = "error: dollar not found"
                else:
                    dollar = dollar.text
            else:
                dollar = dollar.text

        #removes commas from the titles
        if "," in titlePreSplit:
            title = ' '.join([titlePreSplit.split(',')[1].strip(), titlePreSplit.split(',')[0].strip()]) 
        else:
            title = titlePreSplit

        itemObj.title = title + " " + type
        itemObj.buySite = "jbhifi"
        itemObj.price = dollar
        resultObjs.append(str(itemObj))

    code1, code2, code3, code4 = seperatecodes(resultObjs) #divy up the code arr to the 4 children
    print(code4)

    print("Allocating Processes")
    proc1 = multiprocessing.Process(target=ebayCheck, args = (code1, 1)) #create the children
    proc2 = multiprocessing.Process(target=ebayCheck, args = (code2, 2))
    proc3 = multiprocessing.Process(target=ebayCheck, args = (code3, 3))
    proc4 = multiprocessing.Process(target=ebayCheck, args = (code4, 4))

    print("Start Processes")
    proc1.start() #start the children
    proc2.start()
    proc3.start()
    proc4.start()

    print("kill Processes")
    proc1.join() #join the children
    print("proc1  closed")
    proc2.join()
    print("proc2  closed")
    proc3.join()
    print("proc3  closed")
    proc4.join()
    print("proc4  closed")

    condenseFiles(4)

def core():
    cleanFile()
    for url in urls:
        
        #gets the name of the site i.e. jbhifi from www.jbhifi.com.au/...
        siteString = url[url.find(".")+1:url.find(".", url.find(".")+1)]
        
        #determines the offset for each site
        siteNum = 0
        siteNum = site[siteString].value

        #sets the class to look for for each url
        container = containers[siteNum][0]
        containerType = containers[siteNum][1]

        print("Finding hits for ", url)

        #Specify Headless operation
        chromeOptions = Options()
        chromeOptions.add_argument("--headless")

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(options=chromeOptions)

        # Wait up to 10 seconds for the page to load
        driver.implicitly_wait(10)

        # Load the page
        driver.get(url)

        # Wait for the div with the specified class to load
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, container)))

        # Get the page source after the content has loaded
        html = driver.page_source

        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(html, "html.parser")

        # Find all div tags with the specified class
        items = soup.find_all(containerType, class_=container)




        if "jbhifi" in url:
            start_time = time.perf_counter()
            
            jbhificheck(items)

            end_time = time.perf_counter()
            print("runtime : {}s".format(end_time - start_time))
            
        
    
        

        # Close the driver
        driver.quit()

if __name__ == '__main__':
    core()
