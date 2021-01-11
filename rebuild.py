def userInput():
	lineNum = input(int("What line would you like to rebuild from: "))
	counter = 0
	journalList = []
	fileOut = []
 
	with open(path, 'r') as csvFile:
    	reader = csv.reader(csvFile)
 
    	for row in reader:
        	journalList.append(row)
    	csvFile.close()
 
	tempFile = open("/home/kris/Desktop/Journal/tempfile", "w")
	while (linenum != counter):
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
    	counter += 1
	while i < len(fileOut):
    	print(fileOut[i])
    	tempFile.write(fileOut[i])
    	tempFile.write("\n")
    	i += 1
 
	tempFile.close()
