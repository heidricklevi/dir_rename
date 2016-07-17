import os
import pprint
import re
import shutil
import sys

# clientRoot = "C:\\mockTestScript\\Clients\\"
# individTemplatePath = "C:\\mockTestScript\\templates\\File Structure Ind XXXX Last, First & Spouse\\2017 XXXX"
# businessTemplatePath = "C:\\mockTestScript\\templates\\File Structure BUS XXXX Business Name\\123117 XXXX"
# businessTemplatePathNotYear = "C:\\mockTestScript\\templates\\File Structure BUS XXXX Business Name"
# newBusinessPath = "C:\\mockTestScript\\clients\\File Structure BUS XXXX Business Name"
# fullIndividualTemplate = "C:\\mockTestScript\\templates\\File Structure Ind XXXX Last, First & Spouse"
# newIndClientLocation = "C:\\mockTestScript\\clients\\File Structure Ind XXXX Last, First & Spouse"

if os.path.exists("filepaths"):
    lines = [line.rstrip('\n') for line in open('filepaths')]

    clientRoot, individTemplatePath, businessTemplatePath, businessTemplatePathNotYear, \
    newBusinessPath, fullIndividualTemplate, newIndClientLocation = lines
else:
    print("This program cannot execute properly without the path definitions which are contained in the filepaths file."
          " Please store that file in the same directory as this executable.\n")

def isValidClientInput(clientID):
    assert (len(str(clientID)) == 4 and int(clientID)), "Client ID or Ind. Year must be exactly 4 digits"


def replaceXInPath(clientID, pathname):
    regex = re.compile(r'[X]{4}')
    return regex.sub(clientID, pathname)

# We need to present user with screen that offers select options based on use cases
# User needs to create a new client
# User needs to add an additional year to existing clients
# User should be asked to specify whether this is business or individual should it affect program flow


def recursiveWalk(rootDir, clientID):
    try:
        for entry in os.listdir(rootDir):
            newPath = os.path.join(rootDir, entry)
            finalPath = replaceXInPath(clientID, newPath)
            os.rename(newPath, finalPath)
            recursiveWalk(finalPath, clientID)

    except OSError as e:
        print(e, file=sys.stderr)


def checkClientForX():
    print("Please enter the ID of the Client you would like to inspect.")
    checkID = input()
    isValidClientInput(checkID)

    for dir in os.listdir(clientRoot):
        if dir[0:4] == checkID:
            newPath = os.path.join(clientRoot, dir)
            recursiveWalk(newPath, dir[0:4])

def isBusClient(clientPath):
    clientRegex = re.compile(r'\d{6}(\s)([X]{4}|\d{4})')
    if clientRegex.search(clientPath):
        return True
    else:
        return False

def isIndividualClient(clientPath):
    clientRegex = re.compile(r'\d{4}(\s)([X]{4}|\d{4})')
    if clientRegex.search(clientPath):
        return True
    else:
        return False

def afterCopy(pathname, oldYear, newYear, clientID):
    regex = re.compile(r'' + oldYear + '(\s)' + '[X]{4}')
    regex1 = re.compile(r'[X]{4}')
    for currentFolder, subFolder, fileName in os.walk(pathname):
        searchObject = regex.search(currentFolder)
        searchObject1 = regex1.search(currentFolder)

        if searchObject is not None or searchObject1 is not None:
            if searchObject:
                newPath = regex.sub(newYear + " " + clientID, currentFolder)
                os.rename(currentFolder, newPath)
            elif searchObject1:
                newPath = regex1.sub(clientID, currentFolder)
                os.rename(currentFolder, newPath)

            if regex.search(str(fileName)):
                file = ''.join(fileName)
                currentFolder = regex.sub(newYear + " " + clientID, currentFolder)
                fullFilePath = os.path.join(currentFolder, file)
                newPath = regex.sub(newYear + " " +  clientID, fullFilePath)
                os.rename(fullFilePath, newPath)

            elif regex1.search(str(fileName)):
                file = ''.join(fileName)
                currentFolder = regex1.sub(clientID, currentFolder)
                fullFilePath = os.path.join(currentFolder, file)
                newPath = regex1.sub(clientID, fullFilePath)
                os.rename(fullFilePath, newPath)


def checkAllClientsAndReplaceX():
    for dir in os.listdir(clientRoot):
            clientID = dir[0:4]
            newPath = os.path.join(clientRoot, dir)
            recursiveWalk(newPath, clientID)



def addNewYear():
    # determine whether we are adding to an individual or business client
    # get the latest year from correct template and increment by one
    # copy to respective client
    # replace 'XXXX' in newly added directory with client ID
    # move on to the next client repeating for each client

    busClients = []
    individClient = []
    print("Please Enter the desired year for Business Clients e.g. 123116")
    businessBaseName = input()
    assert (len(str(businessBaseName)) == 6 and int(businessBaseName)), "Business Year must be exactly 6 digits--123116"

    print("Please Enter the desired year for Individual Clients i.e. 2016")
    individBaseName = input()
    isValidClientInput(individBaseName)

    for client in os.listdir(clientRoot):
        if not os.path.isdir(clientRoot + client):
            print("Skipping " + client)
            continue
        subDirs = os.path.join(clientRoot, client)

        for dir in os.listdir(subDirs):
            if isBusClient(dir):
                busClients.append(client)
                # print("Successfully added " + client + "to Business clients.")
            elif isIndividualClient(dir):
                individClient.append(client)
                # print("Successfully added " + client + "to Individual clients.")

            if client in busClients:
                baseName = os.path.basename(businessTemplatePath)
                clientID = client[0:4]
                beforeIncrement = baseName[0:6]
                baseName = baseName.replace(beforeIncrement, businessBaseName+ " ")
                finalName = clientRoot + client + "\\" + str(baseName)
                newName = replaceXInPath(clientID, finalName)
                finalName = newName
                if not os.path.exists(finalName):
                    shutil.copytree(businessTemplatePath, finalName)
                afterCopy(finalName, beforeIncrement, businessBaseName, clientID)


            elif client in individClient:
                baseName = os.path.basename(individTemplatePath)
                clientID = client[0:4]
                beforeIncrement = baseName[0:4]
                baseName = baseName.replace(beforeIncrement, individBaseName+ " ")
                finalName = clientRoot + client + "\\" + str(baseName)
                newName = replaceXInPath(clientID, finalName)
                finalName = newName
                if not os.path.exists(finalName):
                    shutil.copytree(individTemplatePath, finalName)
                afterCopy(finalName, beforeIncrement, individBaseName, clientID)

    busClients = sorted(set(busClients))
    individClient = sorted(set(individClient))
    pprint.pprint(individClient)
    pprint.pprint(busClients)


def createNewClient():
    # Present user with option to choose Bus/Ind
    print("Is this a new Individual Client or Business client? ((b) for Business or (c) for ind. client")
    answer = input()

    answer = str.capitalize(answer)

    if answer == "B":
        print("Please enter the Business ID number for the new client")
        id = input()
        isValidClientInput(id)
        print("Please enter the name of the business")
        busName = input()
        #Get file structure from templates
        shutil.copytree(businessTemplatePathNotYear,newBusinessPath)

        baseName = id + " " + busName
        newName = clientRoot + baseName + "\\"
        os.rename(newBusinessPath, newName)

        #replace X's with user entered id number
        recursiveWalk(newName, id)

    elif answer == "C":
        print("Please enter the Individual Client ID number for the new Client")
        individID = input()
        isValidClientInput(individID)

        print("Please enter the individual's name")
        indName = input()

        shutil.copytree(fullIndividualTemplate,newIndClientLocation)

        dirName = individID + " " + indName
        newIndivName = clientRoot + dirName + "\\"
        os.rename(newIndClientLocation, newIndivName)
        recursiveWalk(dirName, individID)

        # Same as above only utilize the individual template


    else:
        print("The option you selected is not valid.")


def presentScreen():
    print("--------------------------------------------------------------------")
    print("What would you like to do?-----------------------Key to Press-------\n"
          "====================================================================\n"
          "Create a New Client?----------------|------------------N------------\n"
          "Add a directory year?---------------|------------------Y------------\n"
          "Replace all Xs by client ID?--------|------------------I------------\n"
          "Check/Replace Xs for all Clients?---|------------------C------------\n"
          "Display Current File Paths----------|------------------S------------\n"
          "Exit?-------------------------------|------------------E------------\n"
          "====================================================================")
    # print("\nWould you like to create a new client?---Type N---to create a new client")
    # print("Would you like to add a year to existing clients?----Type Y---to add a year to existing clients")
    # print("Would you like to replace Xs for a specific Client by ID?----Type I----to check a specific Client")
    # print("Would you like to check all clients for Xs and replace as needed?----Type C----to check all clients")
    # print("If you would like to exit, type----E----.")

def showDirectoryPaths():
    print("Client Root Directory: " + clientRoot + "\n")
    print("Individual Client Template Year Path: " + individTemplatePath)
    print("Individual Template Path: " + fullIndividualTemplate)
    print("Business Directory Year: " + businessTemplatePath)
    print("New Ind. Client Location: " + newIndClientLocation)
    print("New bus. Client Location: " + newBusinessPath)
    print("Business Directory Template: " + businessTemplatePathNotYear + "\n")

presentScreen()
userChoice = input()
userChoice = str.capitalize(userChoice)

def newIndividPath():
    global newIndClientLocation
    print("Please enter the new path for the new client (Applicable only when creating a new client)")
    newIndClientLocation = input()
    print("The new path for the new client is: " + newIndClientLocation)

def newBusPath():
    global newBusinessPath
    print("Please enter the new path for the new Business Client (Applicable only when creating a new bus client)")
    newBusinessPath = input()
    print("The new path for the new bus. client is: " + newBusinessPath)

def itemplate():
    global fullIndividualTemplate
    print("Please enter the new path for the individual template ")
    fullIndividualTemplate = input()
    print("The new individual path is: " + fullIndividualTemplate)


def businessYear():
    global businessTemplatePath
    print("Enter the new path for the business year: ")
    businessTemplatePath = input()
    print("The new business directory year is: " + businessTemplatePath)


def businessTemplate():
    global businessTemplatePathNotYear
    print("Enter the new path for Business Template ")
    businessTemplatePathNotYear = input()
    print("The new Business template path is: " + businessTemplatePathNotYear)


def clientRootPath():
    global clientRoot
    print("Type the new name of the root path")
    clientRoot = input()
    print("The new root directory path is: " + clientRoot)


def individualYearPath():
    global individTemplatePath
    print("Enter the new path for the individual directory year. ")
    individTemplatePath = input()
    print("The new individual year path is: " + individTemplatePath)


while userChoice != "E":
    if userChoice == "R":
        clientRootPath()
    elif userChoice == "L":
        newIndividPath()
    elif userChoice == "Z":
        newBusPath()
    elif userChoice == "D":
        individualYearPath()
    elif userChoice == "A":
        businessYear()
    elif userChoice == "T":
        itemplate()
    elif userChoice == "B":
        businessTemplate()
    elif userChoice == "N":
        createNewClient()
    elif userChoice == "Y":
        addNewYear()
    elif userChoice == "S":
        showDirectoryPaths()
    elif userChoice == "I":
        checkClientForX()
    elif userChoice == "C":
        checkAllClientsAndReplaceX()
    elif userChoice == "E":
        exit()
    presentScreen()
    userChoice = input()
    userChoice = str.capitalize(userChoice)


