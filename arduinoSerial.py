'''
AUTHOR: Logan Foreman
GitHub Link: https://github.com/
RedID: 825056655
'''
import serial.tools.list_ports
import time 
import pandas as pd
import requests
import re
import math as math
from bs4 import BeautifulSoup
print("hello")

# *********- INTERAL ARDUINO COMMUNICATION SETUP -***************************************************************************
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

serialInst.baudrate = 115200
serialInst.port = "/dev/cu.usbmodem1101" # On windows it'll be 'COM4'
serialInst.open()
#   WINDOWS VERSION => arduino = serial.Serial(port = 'COM4', baudrate=11520, timeout=.1) 
# ***********************************************************************************************

# ***********************************************************************************************

# *********- URL DATABASE -***************************************************************************
# Here define the file(website) we will be importing, which is in HTML format

url_1_0 = "https://www.ndbc.noaa.gov/station_page.php?station=46225" # <- Torrey Pines Outer 1
url_1_1 = "https://wind.willyweather.com/ca/san-diego-county/la-jolla.html" #wind

url_2_0 = "https://www.ndbc.noaa.gov/station_page.php?station=46275" # <- Trestles (OC) 2
url_2_1 = "https://wind.willyweather.com/ca/san-diego-county/trestles.html" #wind

url_3_0 = "https://www.ndbc.noaa.gov/station_page.php?station=51201" # <- Hawaii North Shore 3 
url_3_1 = "https://wind.willyweather.com/hi/honolulu/haleiwa-beach-park.html" #wind

url_4_0 = "https://www.ndbc.noaa.gov/station_page.php?station=41113" # <- Cocoa Beach 4
url_4_1 = "https://wind.willyweather.com/fl/brevard-county/cocoa-beach.html" #wind
# ***********************************************************************************************


# ******- HELPER FUNCTIONS -*************************************************************************
'''
Request handler for url
which will get readable versions 

@param url: URL 
returns: response in JSON
'''
def getHTMLdocument(url):
    # request for HTML document of given url
    response = requests.get(url)
    # response will be provided in JSON format
    return response.text
'''
Function to obtain wave height 
with a function described by 
regression-predicted variables 

@param: swell height (H), swell period (P)
returns: waveHeight{3-4ft}: this is the wave face height prediction 
'''
def waveHeightFunc(H,P):
    iH = float(H)
    iP = float(P)
    numerator = iH*(math.log10(iH+2)+0.5)
    Power1 = math.pow(iP,float(5/3))
    Power2 = math.pow(iP,float(2/3))
    waveHeight = ((Power1 * numerator) / (Power2 * 6))
    if waveHeight <= 5: # If waves are small (5ft or less), discrepancy can be less
        x = math.floor(waveHeight)
        y = math.ceil(waveHeight)
    elif waveHeight > 5: # When waves are bigger(6ft or more), discrepancy can be more
        x = math.floor(waveHeight)-1
        y = math.ceil(waveHeight)+1
    xx = str(x)
    yy = str(y)
    waveHeightRounded = xx + "-" + yy + "ft"    # Should be String type
    return waveHeightRounded

# ***********************************************************************************************


# ***- WEB SCRAPING FUNCTIONS -******************************************************************

# Function to get a list of relevant lines from bouy website, which can be for any spot
'''
Function to get a list 
of relevant lines from 
bouy website, which can 
be for any spot

@param urlNum: url from available bouy data sites of spots available 
returns: list of relevant data from bouy website

'''
def parseSwellSite(urlNum):
    url = urlNum
    html_doc = getHTMLdocument(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    output = soup.get_text()

    dataList = []
    nextLine = 0

    for idx, row in enumerate(output.splitlines()):
        if(row.startswith("Swell Height (SwH):")):
            nextLine = idx + 2
        if(idx < nextLine):
            #print(row + "\n")
            dataList.append(row)
        if(idx == nextLine and idx !=0):
            break
    Height = re.sub('[^0-9,.]', '', dataList[0])
    Period = re.sub('[^0-9,.]', '', dataList[1])
    '''for i in range(16,len(lineOne),1):

        # Should append the number alongside "Swell Height:"
        
        if(not char.isnumeric and char != '.'): # Breaks parsing when it reaches "ft"
            break
    lineTwo = dataList[1]
    Period = ""
    for char in range(16,len(lineTwo),1):
        Period.append(char) # Should append the number alongside "Swell Period:"
        if(not char.isnumeric and char != '.'): # Breaks parsing when it reaches "sec"
            break'''
    '''iLine = dataList[0]
    iFixed = iLine[111:len(iLine):1]
    dataList[0] = iFixed'''
    waveHeight = waveHeightFunc(Height, Period)
    return waveHeight

'''
Function to get the
wind (mph) from a given
spot from a different site

@param urlNum: url from available wind data sites
returns: wind data
'''
def parseWindSite(urlNum):
    url2 = urlNum
    html_doc2 = getHTMLdocument(url2)
    soup2 = BeautifulSoup(html_doc2, 'html.parser')
    output2 = soup2.get_text()
    windList = []
    two = 0
    windL = ""
    for idx, row in enumerate(output2.splitlines()):
        if(row.endswith("DirectionStrengthLightTrendDecreasing")):
            windL = row
            break
    if(windL == ""):
        return windL + "5mph W"
    windLineRaw = windL.replace(" ", "")
    windSpeedRaw = re.sub('[^0-9,.]', '', windLineRaw) # converts to purely '3.4'
    windLine = windLineRaw.lstrip('0123456789.- ')
    # Match all digits in the string and replace them with an empty string
    windDirRaw = windLine[3:4:1] # should be able to read WNW
    
    if(windDirRaw.endswith("S")):
        windDir = windDirRaw.replace("S", "")
    if(windDirRaw.endswith("Sp")):
        windDir = windDirRaw.replace("Sp", "")
    if(windDirRaw.endswith("Spe")):
        windDir = windDirRaw.replace("Spe", "")
    else:
        windDir = windDirRaw
    windSpeed = (windSpeedRaw + "mph ")
    Wind = windSpeed + "" + windDir
    #print(Wind)

    # Here we need to convert this list into form: String wind = {5mph E}
    return Wind # Should be String type

# ***********************************************************************************************

'''
Function to summarize given 
datalist and spit out title 

@param spotID (1,2,3,4,exit, or other(fail))
returns: data summary to be output to lcd screen

'''
def summarizeData(spotID):
    # Swell Period, Feet, Wind
    # TODO: add formula to convert swell period to wave height / forecast
    #list will contain the following:
    # SWHT, Swell Height, Swell Period, Swell Direction, 
    # Wind Wave Height, Wind Wave Period, Wind Wave Direction, 
    # Wave Steepness, Average Wave Period
    # (We're mostly interested in swell height, swell period, and wind speed  )
    # from the given datalist of swell we want to extract
    # waveData will be fetched in form of String: {3-4ft}
    # windData will be fetched in form of String: {5MPH E}
    if spotID == '1':
        spotName = "Blacks_Beach"
        waveData = parseSwellSite(url_1_0) # Fetches estimated/predicted wave height
        windData = parseWindSite(url_1_1) # Fetches wind speed and direction
        # WILL RETURN STRING FORM TO MAKE BUFFER TO ARDUINO IDE EASIER
        retStr = spotName+ " "+ waveData+ " "+ windData
        return retStr
    elif spotID == '2':
        spotName = "Trestles"
        waveData = parseSwellSite(url_2_0) # Fetches estimated/predicted wave height
        windData = parseWindSite(url_2_1) # Fetches wind speed and direction
        # WILL RETURN STRING FORM TO MAKE BUFFER TO ARDUINO IDE EASIER
        retStr = spotName+ " "+ waveData+ " "+ windData
        return retStr

    elif spotID == '3':
        spotName = "North_Shore"
        waveData = parseSwellSite(url_3_0) # Fetches estimated/predicted wave height
        windData = parseWindSite(url_3_1) # Fetches wind speed and direction
        # WILL RETURN STRING FORM TO MAKE BUFFER TO ARDUINO IDE EASIER
        retStr = spotName+ " "+ waveData+ " "+ windData
        return retStr

    elif spotID == '4':
        spotName = "Cocoa_Beach"
        waveData = parseSwellSite(url_4_0) # Fetches estimated/predicted wave height
        windData = parseWindSite(url_4_1) # Fetches wind speed and direction
        # WILL RETURN STRING FORM TO MAKE BUFFER TO ARDUINO IDE EASIER
        retStr = spotName+ " "+ waveData+ " "+ windData
        return retStr

    elif spotID == "exit":
        return "...exiting..."
    elif spotID != '1' and spotID != '2' and spotID != '3' and spotID != '4' and spotID != 'exit':
        return "unrecognized input. Try Again:\n"
    
# ***********************************************************************************************

# *** - TEST DATA - ***************************

# *********************************************


# Arduino Loop (Driver Code)
print("\nWelcome to WaveTrak! \n")
print("Spots to choose from: \n'1' - San Diego CA, (Black's Beach)\n'2' - Orange County, CA(Trestle's)\n'3' - North Shore of Oahu, HI\n'4' - Cocoa Beach, FL\n")
print("\nType the number of a surf spot, or type 'exit' to end the program: ")
while True:
    userInput = input("-> ")

    print("\n...Connecting to Arduino...\n")
     # The data summary will be one long string with all the key information
     # In Arduino IDE, char buffer will take care of string so that the
     # proper buffering can be transmitted to LCD screen
    summary = summarizeData(userInput) 
    print(summary)
    serialInst.write(summary.encode('utf-8'))
    if(userInput == 'exit'):
        print("...exiting...")
        exit()
    time.sleep(10)
    