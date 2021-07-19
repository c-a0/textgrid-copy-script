#Script to copy a section of a TextGrid from one place in the TextGrid to another
#C.A. 2021
#Last updated 7/19/21
#   Use:
#         python tgcopy.py [TextGrid filename] [Start time of section to copy] [End time of section to copy] [Time to paste to] [Optional: Microtiming offset]

import sys
import re
import copy

try: #If the user calls the script with at least 1 paramater (e.g. at least 3 words typed in the command line)...
    filename = sys.argv[1]
    startCopy = float(sys.argv[2])
    endCopy = float(sys.argv[3])
    paste = float(sys.argv[4])
    try: #If user provides an offset for layer 8, use it.
        microtimingOffset = float(sys.argv[5])
    except IndexError:
        microtimingOffset = 0.0
except IndexError: #If the user only types "python tgcopy.py"...  
    sys.exit("Usage: python tgcopy.py [TextGrid filename] [Start time of section to copy] [End time of section to copy] [Time to paste to] [Optional: Microtiming offset]")
    
    '''
    print("╔══════════════════════════════════════════════════════════════════════════════════╗")
    print("║            This script allows you to copy a section of a TextGrid file           ║")
    print("║                     from one place in the TextGrid to another.                   ║")
    print("║                   The script will not overwrite your TextGrid,                   ║")
    print("║        it will just make a copy of the TextGrid file in the same folder.         ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════╝")
    filename = input("               .TextGrid file: ")
    startCopy = input("Start time of section to copy: ")
    endCopy = input("  End time of section to copy: ")
    paste = input("             Time to paste to: ")
    '''

with open(filename) as f: #Open the file into a list of strings, called "lines". Each line is one string.
    lines = [line.rstrip() for line in f]
f.close()

#Define a new data type, "interval"                                                             int     float   float   string
class interval: #a variable of this type can be created like this: [variable name] = interval([number], [xmin], [xmax], [text])
    def __init__(self, number, xmin, xmax, text): #Any one of a variable's parameters can be returned from that variable like this: [variable name].[parameter name]
        self.number = number
        self.xmin = xmin
        self.xmax = xmax
        self.length = xmax-xmin
        self.text = text


### Routine for turning TextGrid file information into lists of interval objects ###
tiers = [] #List of lists, one for each tier.
curTier = [] #List of intervals that the loop below will be adding to. When a tier is finished being added, this list will be added to the "tiers" list.
curNumber = 0 #These "cur" variables are for keeping track of the parameters of the current interval in the tier the script is looping through.
curXmin = 0.0
curXmax = 0.0
curText = ""
i = 0 #This (and the checkIfLast string) will be used to check whether or not the loop has reached the end of the TextGrid file.
checkIfLast = ""
for line in lines:
    if re.search("item ", line): #In the TextGrid file, each tier starts with "item[x]:". So if we see that string, we know we hit a new tier.
        tiers.append(curTier) #Before resetting the "cur" paramaters, add the current tier to the "tiers" list. Because there are two instances of "item" in the header of every TextGrid, tiers[0] and tiers[1] will be empty. So tier 1 is actually tiers[2], tier 9 is tiers[10].
        curTier = [] #At the beginning of each tier, set the list to be empty.
        curNumber = 0 #Set the interval number back to 0.
    if re.search("intervals ", line): #Each interval is written "intervals [x]:", so we add 1 to curNumber every time to keep track of which interval we are on.
        curNumber += 1
    if re.search("xmin", line):
        curXmin = float("".join(re.findall(r'[0123456789.]', line))) #This just means "take only the numeral characters and . from the current line and set curXmin to that".
    if re.search("xmax", line):
        curXmax = float("".join(re.findall(r'[0123456789.]', line))) #Same as curXmin above
    if re.search("text =", line):
        curText = "".join(re.findall(r'"(.*?)"', line)) #curText is set to whatever in the current line is between quotes.
        curTier.append(interval(curNumber,curXmin,curXmax,curText)) #Add the current interval to "curTier" list.

    try: #The program tries to set checkIfLast to whatever the _next_ item in the TextGrid file is. If there is no next item, skip this and go to the "except IndexError:" section.
        checkIfLast = lines[i+1] #checkIfLast is just a dummy variable, its only purpose is for this check.
    except IndexError: #If we have reached the end of the TextGrid file:
        tiers.append(curTier) #Add the last tier to the "tiers" list

    i += 1
    
### Routine for copying data from one part of a TextGrid to another ###
editedTiers = copy.deepcopy(tiers)

curTier = 0
timeDifference = 0.0
setTimeDifference = 0.0

startCopyInterval = copy.deepcopy(tiers[2][0]) #2 and 0 are dummy values
startPasteInterval = copy.deepcopy(tiers[2][0])
endCopyInterval = copy.deepcopy(tiers[2][0])
endPasteInterval = copy.deepcopy(tiers[2][0])

for tier in tiers:
    tempIntervals = []
    i = 0
    
    while(i < len(tier)): 
        if(tier[i].xmin >= startCopy and tier[i-1].xmin < startCopy): #search through tier to find which interval's xmin is closest to startCopy, then store it in startCopyInterval
            startCopyInterval = copy.deepcopy(tier[i])
        if(tier[i].xmin >= endCopy and tier[i-1].xmin < endCopy): #search through tier to find which interval's xmin is closest to  endCopy,  then store it in endCopyInterval
            endCopyInterval = copy.deepcopy(tier[i-1])
        if(tier[i].xmin >= paste and tier[i-1].xmin < paste): #search through tier to find which interval's xmin is closest to  paste,    then store it in startPasteInterval
            startPasteInterval = copy.deepcopy(tier[i])
        timeDifference = startPasteInterval.xmin - startCopyInterval.xmin
        if(tier[i].xmin >= endCopyInterval.xmin+timeDifference and tier[i-1].xmin < endCopyInterval.xmin+timeDifference): #search through tier to find which interval's xmin is closest to  endCopy+timeDifference,    then store it in endPasteInterval
            endPasteInterval = copy.deepcopy(tier[i]) 
        i += 1
        
    
    i = 0
    while(i < len(tier)): #Copy interval data into temporary list
        if(tiers[curTier][i].xmin >= startCopyInterval.xmin and tiers[curTier][i].xmin < endCopyInterval.xmin): #Doesn't work for microtiming tier
            tempIntervals.append(copy.deepcopy(tiers[curTier][i])) 
        i += 1 
    
    #The timeDifference needs to be the same for tiers 6, 7, and 8, otherwise the microtiming tier will be misaligned. 6 and 7 are usually aligned, but 8 (the microtiming layer) isn't, so we have to do it manually.
    if(curTier == 6): #...So we copy the value from 6 into a separate variable (setTimeDifference)...
        setTimeDifference = copy.deepcopy(timeDifference)-microtimingOffset
    if(curTier == 8): #...And use that variable for tier 8!
        timeDifference = setTimeDifference
    
    for interval in tempIntervals: #Add time offset to temporary list data
        interval.xmin = interval.xmin+timeDifference
        interval.xmax = interval.xmax+timeDifference
    
    i = 0
    while(i < len(editedTiers[curTier])): #Weirdly, if you just use a normal index such as editedTiers[curTier][0], it gives an "index out of range" error. So we need to do this weird workaround where we put it in a loop to make it work.
        if(i == startPasteInterval.number):
            try:
                insertAt = copy.deepcopy(editedTiers[curTier][i].number-1) #insertAt will be the interval that we start copying data into.
            except IndexError:
                pass
        i += 1
    
    i = 0
    while(i < len(tier)): #Clear paste area
        if(tiers[curTier][i].xmin >= startPasteInterval.xmin and tiers[curTier][i].xmin < endPasteInterval.xmin):
            editedTiers[curTier].remove(editedTiers[curTier][startPasteInterval.number-1])
        i += 1
    
    tempIntervals.reverse() #For some reason, tempIntervals is backwards. So we need to just reverse it.
    for interval in tempIntervals: #Copy temporary list data to paste area
        editedTiers[curTier].insert(insertAt-1, interval) 
        
    curTier += 1
    


tiers = editedTiers #Overwrite tiers list with editedTiers list. We don't have to do this, but it makes the following code a little more readable, since we just have to write tiers[?] instead of editedTiers[?].
### Routine for turning interval data back into TextGrid format and writing to a .TextGrid file ##
createNew = open("Copied_"+filename, "a") #Create a Copied_[filename].TextGrid file, just in case it doesn't exist already.
createNew.close()
with open("Copied_"+filename, 'r+') as f2: 
    f2.truncate()
    f2.write("File type = \"ooTextFile\"\n")
    f2.write("Object class = \"TextGrid\"\n")
    f2.write("\n")
    f2.write("xmin = 0 \n")
    totalLength = 0
    for interval in tiers[2]:
        totalLength += interval.length
    f2.write("xmax = "+str(totalLength)+" \n")
    f2.write("tiers? <exists> \n")
    f2.write("size = "+str(len(tiers)-2)+" \n")
    f2.write("item []: \n")
    i = -1
    for tier in tiers:
        if(i > 0):
            f2.write("    item ["+str(i)+"]:\n")
            f2.write("        class = \"IntervalTier\" \n")
            f2.write("        name = \"\" \n")
            f2.write("        xmin = 0 \n")
            f2.write("        xmax = "+str(totalLength)+" \n")
            f2.write("        intervals: size = "+str(len(tier))+" \n")
            j = 1
            for interval in tier:
                f2.write("        intervals ["+str(j)+"]:\n")
                f2.write("            xmin = "+str(interval.xmin)+" \n")
                try:
                    f2.write("            xmax = "+str(tier[j].xmin)+" \n") #xmax = next interval's xmin. Just a sanity check to make sure the timings make sense.
                except IndexError:
                    f2.write("            xmax = "+str(interval.xmax)+" \n")
                f2.write("            text = \""+interval.text+"\" \n")
                j += 1
        i += 1
    f2.close()


