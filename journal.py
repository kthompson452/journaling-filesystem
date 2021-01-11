import os, stat, csv
import pyinotify
import datetime
 
class EventProcessor(pyinotify.ProcessEvent):
    methodTypes = ["IN_DELETE",
                "IN_CLOSE_WRITE"]
 
#writes to journal file
def updateJournal(path, changeString):
    jnl = open(getJournalFile(path), "a")
    journalString = ""
    date = datetime.datetime.now()
    filename = path[29:]
    journalString += date.strftime("%A, %d %b %Y")
    journalString += "," 
    journalString += filename 
    journalString += ","
    journalString += str(getInode(path))
    journalString += ","
    journalString += changeString
    jnl.writelines(journalString)
    jnl.writelines("\n")
    jnl.close()
    return journalString
 
def rebuildFile(path):
    journalList = []
    fileOut = []
 
    with open(path, 'r') as csvFile:
        reader = csv.reader(csvFile)
 
        for row in reader:
            journalList.append(row)
        csvFile.close()
 
    tempFile = open("/home/kris/Desktop/Journal/tempfile", "w")
 
    i = 0
    while i < len(journalList):
        #if the journal line has a + in it, we add the line to the journal
        if journalList[i][4] == "+":
            lineLen = len(fileOut)
            #if this line appears later than how many entries are in fileOut[] 
            #(this prevents overflow, and puts empty spaces on each line until
            # we reach the line needed)
            if int(journalList[i][5]) > (lineLen - 1):
                j = int(journalList[i][5]) - (lineLen - 1)
                while j > 0:
                    fileOut.append("")
                    j -= 1
 
            fileOut[int(journalList[i][5])] = journalList[i][6]
 
 
        #if the journal line has a - in it, we remove from the journal
        if journalList[i][4] == "-":
            lineLen = len(fileOut)
            #if this line appears later than how many entries are in fileOut[] 
            #(this prevents overflow, and puts empty spaces on each line until
            # we reach the line needed)
            if int(journalList[i][5]) > (lineLen - 1):
                j = int(journalList[i][5]) - (lineLen - 1)
                while j > 0:
                    fileOut.append("")
                    j -= 1
 
            fileOut.pop(int(journalList[i][5]))
        i += 1
 
    i = 0
    if len(fileOut) != 0:
        fileOut.pop(0)
    while i < len(fileOut):
        print(fileOut[i])
        tempFile.write(fileOut[i])
        tempFile.write("\n")
        i += 1
 
    tempFile.close()
 
#returns inode for modified file
def getInode(path):
    command = "ls -l "
    command += path
    os.popen(command).read()
    st = os.stat(path)
    return st[stat.ST_INO]
 
#gets corresponding journal file from directory
def getJournalFile(path):
    fileName = path[29:]
    journalPath = "/home/kris/Desktop/Journal/"
    journalPath += fileName
    journalPath += ".jnl"
    fileExists = open(journalPath)
    fileExists.close()
    return journalPath
 
#checks differences for each line of modified file vs journaled file
def compareFiles(event): 
    file1 = open(event.pathname)
    rebuildFile(getJournalFile(event.pathname))
    file2 = open("/home/kris/Desktop/Journal/tempfile")
 
    file1Line = file1.readline()
    file2Line = file2.readline()
 
    changes = []
    changeCounter = 0
 
    line_no = 1
 
    while file1Line != '' or file2Line != '':
 
        file1Line = file1Line.rstrip()
        file2Line = file2Line.rstrip()
 
        if file1Line != file2Line:
 
            if file1Line == '' and file2Line != '':
                #changes += {"-", "Line-%d" % line_no, file2Line}
                changes.append("-")
                changes.append(str(line_no))
                changes.append(file2Line)
                changeCounter += 1
 
            elif file2Line != '':
                #changes += {"old", "Line-%d" %  line_no, file2Line}
                changes.append("old")
                changes.append(str(line_no))
                changes.append(file2Line)
                changeCounter += 1
        
            if file2Line == '' and file1Line != '':
                #changes += {"+", "Line-%d" % line_no, file1Line}
                changes.append("+")
                changes.append(str(line_no))
                changes.append(file1Line)
                changeCounter += 1
 
            elif file1Line != '':
                #changes += {"new", "Line-%d" % line_no, file1Line}
                changes.append("new")
                changes.append(str(line_no))
                changes.append(file1Line)
                changeCounter += 1
 
        file1Line = file1.readline()
        file2Line = file2.readline()
 
        line_no += 1
    file1.close()
    file2.close()
    return changes
 
#handles exception where journal file does not exist,
#therefore it is a new file
def newFile(path):
    print("Journal not found! Creating journal file...")
    fileName = path[29:]
    buildJournalString = "touch /home/kris/Desktop/Journal/"
    buildJournalString += fileName
    buildJournalString += ".jnl"
    os.system(buildJournalString)
    jnl = open(getJournalFile(path), "a")
    origFile = open(path)
    line = origFile.readline()
    jnlOut = []
    lineNum = 1
    while line != '':
        journalString = ""
        date = datetime.datetime.now()
        filename = path[29:]
        journalString += date.strftime("%A, %d %b %Y")
        journalString += "," 
        journalString += filename 
        journalString += ","
        journalString += str(getInode(path))
        journalString += ","
        journalString += "+,"
        journalString += str(lineNum)
        journalString += ","
        journalString += str(line)
        jnlOut.append(journalString)
        line = origFile.readline()
        lineNum += 1 
    jnl.writelines(jnlOut)
 
def readChanges(path, changes):
    print("Length of changes:" + str(len(changes)))
    print("Found " + str(len(changes)/3) + " changes.")
    totalCount = 0
    countOfChanges = (len(changes)/3)
    while countOfChanges > 0:
        if changes[totalCount] == "+":
            #Line is found in new file but not old file
            tst = "+," + changes[totalCount + 1] + "," + changes[totalCount + 2]
            print(updateJournal(path, tst))
            totalCount += 3
            countOfChanges -= 1
 
        elif changes[totalCount] == "-":
            #Line is found in old file but not new file
            tst = "-," + changes[totalCount + 1] + "," + changes[totalCount + 2]
            print(updateJournal(path, tst))
            totalCount += 3
            countOfChanges -= 1 
 
        elif changes[totalCount == "old"]:
            #Both files have this line number, but the old file contains this
            tst = "-," + changes[totalCount + 1] + "," + changes[totalCount + 2]
            print(updateJournal(path, tst))
            totalCount += 3
            countOfChanges -= 1
 
        elif changes[totalCount == "new"]:
            #Both files have this line number, but the new file contains this
            tst = "+," + changes[totalCount + 1] + "," + changes[totalCount + 2]
            print(updateJournal(path, tst))
            totalCount += 3 
            countOfChanges -= 1
 
def fileDelete(path):
    print("File Deleted")
    jnl = open(getJournalFile(path), "a")
    journalString = ""
    date = datetime.datetime.now()
    filename = path[29:]
    journalString += date.strftime("%A, %d %b %Y")
    journalString += "," 
    journalString += filename 
    journalString += ","
    journalString += "FILE-DELETED"
    jnl.writelines(journalString)
    jnl.writelines("\n")
    jnl.close()
    command = "cp "
    command += getJournalFile(path)
    command += " "
    command += getJournalFile(path)
    command += ".del"
    os.popen(command).read()
    command = "rm "
    command += getJournalFile(path)
    os.popen(command).read()
    return journalString
 
#monitors directory for modified files
def processGenerator(ep, method):
 
    def getMethodType(self, event):
        if method == "IN_CLOSE_WRITE":
            if ".swp" not in event.pathname:
                try:
                    print("Journal file found for %d.", event.pathname)
                    readChanges(event.pathname, compareFiles(event))
                except:
                    newFile(event.pathname)
        elif method == "IN_DELETE":
            if ".swp" not in event.pathname:
                fileDelete(event.pathname)
 
    getMethodType.__name__ = "process_{}".format(method)
    setattr(ep, getMethodType.__name__, getMethodType)
 
for method in EventProcessor.methodTypes:
    processGenerator(EventProcessor, method)
 
wm = pyinotify.WatchManager()
eventNotifier = pyinotify.Notifier(wm, EventProcessor())
 
watch_this = os.path.abspath("/home/kris/Desktop/Directory/")
wm.add_watch(watch_this, pyinotify.ALL_EVENTS)
eventNotifier.loop()
 
 
