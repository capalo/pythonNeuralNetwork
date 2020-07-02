#####
# Last updated 2.7.2020

# An artificial neural network to predict the outcomes of the matches in the popular video game Counter-Strike: Global Offensive.
# Python script to predict the probabilities using the parameters optimized by neuralNetwork.py.
# Uses the statCollector.py script to scrape the data needed to make the predictions.
# To get a prediction you need an URL to the hltv.org matchpage for example https://www.hltv.org/matches/2342394/fnatic-vs-big-cs-summit-6-europe [1]
# To see network`s restrictions and user instructions see the "to do WORD".
# UPDATE hltv.org/robots.txt has been updated (5.5.2020) to prevent all user agents from web scraping. This was not the case when we finished this project.
# -Created by: Henri Taskinen and Riku Kukkonen.


##### Libraries

# Standard libraries
from time import sleep
import random

# Third-party libraries
import requests
import numpy as np
from fake_useragent import UserAgent


def sigmoid(x):
    # An activation function that gives each neuron their activation value (between 0-1).
    return (1/(1+np.exp(-x)))

def shapeData(lst):
    # A function to shape the array of data to the right size.
    # Input: a list which contains the required data for the network.
    # Output: a numpy array (4350x1) that contains the same data as the input list.   
    arrayList = []
    for i in range(2):
        for j in range(25):
            for k in range(4):
                arrayList.append(lst[i][j][k])
    array = arrayList[0]
    for n in range(200):
        if n != 0:
            array = np.append(array, arrayList[n])
    return array

def htmlScraper(html):
    # Returns the HTML document of the input URL.
    variable=random.randint(1,2)
    if variable==1:
        user_agent = UserAgent().ie
    else:
        user_agent = UserAgent().chrome
    
    headers = {
            'User-Agent': user_agent,
        }
    html2= ""
    while html2 == "":
        try:
            # Scraping is delayed to respect hltv.org robots.txt.
            sleep((random.random()+1))
            html2 = requests.get(html, headers=headers).text
            htmlString = str(html2)
            break
        except Exception as e: 
            print(e)
            try:
                sleep(random.random()+1)
                html2 = requests.get(html, headers=headers).text
                htmlString = str(html2)
                break
            except Exception as e: 
                print(e)
                sleep((random.random()+1))
                continue
    return htmlString

def mapNametoNumber(mapName):
    # A function that gives each map a numerical value. 
    temp = 0
    if mapName == "Dust2":
        temp = 0.1
    if mapName == "Inferno":
        temp = 0.2
    if mapName == "Mirage":
        temp = 0.3
    if mapName == "Nuke":
        temp = 0.4
    if mapName == "Overpass":
        temp = 0.5
    if mapName == "Train":
        temp = 0.6
    if mapName == "Vertigo":
        temp = 0.7
    return np.array([[temp]])

def PlayerListReader(txt):
    # Returns the teams' and players' names from the matchpage's HTML document.
    newText = ""
    firstIndex=txt.find('class="player"')
    lastIndex=txt.rfind('class="player"')
    for i in range(firstIndex,lastIndex+500):
        newText+=txt[i]
    finalTexts=["","","","","","","","","",""]
    for i in range(10):
        for j in range(len(newText)):
            if i==0:
                if j != newText.find('"text-ellipsis">') + 15:
                    finalTexts[i]+=newText[j]
                else:
                    finalTexts[i]+=str(i)
            else:
                if j != finalTexts[i-1].find('"text-ellipsis">') + 15:
                    finalTexts[i]+=finalTexts[i-1][j]
                else:
                    finalTexts[i]+=str(i)
    finalText=finalTexts[-1]

    playerTxts=[""]*10
    for i in range(10):
        index=finalText.find('"text-ellipsis"' + str(i))
        j=""
        loop_index=0
        while j!="<":
            playerTxts[i]+=finalText[index+loop_index+16]
            loop_index+=1
            j=finalText[index+loop_index+16]
    team1Players = []
    team2Players = []
    for i in range(5):
        team1Players.append(playerTxts[i])
    for i in range(5, 10):
        team2Players.append(playerTxts[i])
    teamsIndex = txt.find("<title>")
    titleText = ""
    for i in range(teamsIndex + 7, teamsIndex + 57):
        titleText += txt[i]
    titleText = titleText.replace(" vs. ", "*")
    titleText = titleText.replace(" at ", "£")
    j = ""
    teamNames = [""]*2
    loop_index = 0
    while j != "*":
        teamNames[0] += titleText[loop_index]
        loop_index += 1
        j = titleText[loop_index]
    j = ""
    secondTeamIndex = titleText.find("*")
    loop_index = secondTeamIndex + 1
    while j != "£":
        teamNames[1] += titleText[loop_index]
        loop_index += 1
        j = titleText[loop_index]
    return team1Players, team2Players, teamNames

def mainPageSearcher(txt):
    # A function that is used to navigate hltv.org website.
    # Output: two URLs to teams' overview pages.
    index = txt.find(">Map stats<")
    newText = ""
    for i in range(index, index + 1500):
        newText+=txt[i]
    indexFO = newText.find("href=")
    indexLO = newText.rfind("href=")
    j = ""
    loopIndex = 0
    link1 = ""
    link2 = ""
    while j != '"':
        link1 += newText[indexFO + 6 + loopIndex]
        loopIndex += 1
        j = newText[indexFO + 6 + loopIndex]
    j = ""
    loopIndex = 0
    while j != '"':
        link2 += newText[indexLO + 6 + loopIndex]
        loopIndex += 1
        j = newText[indexLO + 6 + loopIndex]
    link1 = "https://www.hltv.org" + link1
    link2 = "https://www.hltv.org" + link2
    link1=link1.replace("amp;","")
    link2=link2.replace("amp;","")
    return link1, link2

def mapOverviewSearcher(txt):
    # Another function to navigate hltv.org website.
    # Input: HTML document of output of the previous function.
    # Output: URL to team's recent matches.
    index = txt.find(">Overview</a")
    j = ""
    loopIndex = 0
    link1 = ""
    while j!= '"':
        link1 += txt[index + 22 + loopIndex]
        loopIndex += 1
        j = txt[index + 22 + loopIndex]
    link1 = "https://www.hltv.org" + link1
    link1=link1.replace("amp;","")
    index = link1.rfind("startDate=")
    finaltxt = ""
    for i in range(index):
        finaltxt += link1[i]
    # Has to be changed according to the current year.
    finaltxt += "startDate=2020-01-01&endDate=2020-12-31"
    return finaltxt

def mapPageSearcher(txt):
    # Returns a list of URLs to team's 25 recent matches.
    # Input: HTML document of output of the previous function.
    newText = ""
    firstIndex=txt.find('time"><a href="')
    lastIndex=txt.rfind('time"><a href="')
    mapAmount = txt.count('time"><a href="')
    if mapAmount > 25:
        mapAmount = 25
    for i in range(firstIndex,lastIndex+1000):
        newText+=txt[i]
    txtList1 = [""]*mapAmount
    for i in range(mapAmount):
        for j in range(len(newText)):
            if i==0:
                if j != newText.find('time"><a href="'):
                    txtList1[i]+=newText[j]
                else:
                    txtList1[i]+=str(i)
            else:
                if j != txtList1[i-1].find('time"><a href="'):
                    txtList1[i]+=txtList1[i-1][j]
                else:
                    txtList1[i]+=str(i)
    finalText=txtList1[-1]
    linkList = [""]*mapAmount
    for i in range(mapAmount):
        index=finalText.find(str(i) + 'ime"><a href=')
        j=""
        loop_index=0
        if i >= 10:
            loop_index = 1
        while j!='"':
            
            linkList[i]+=finalText[index+loop_index+ 15]
            loop_index+=1
            j=finalText[index+loop_index+15]
    for i in range(mapAmount):
        linkList[i] = "https://www.hltv.org" + linkList[i]
        linkList[i] = linkList[i].replace("amp;","") 
    return linkList

def team_scores_reader(txt,team, testPlayer):
    # Function to collect data to make the prediction.
    # Inputs: HTML document of the match page.
    # Outputs: a matrix which has the results of the rounds, needed names (players and maps).
    txt=txt.replace('class="won">','voittaja')
    txt=txt.replace('class="lost">','haviaja')
    winners_index=txt.rfind("voittaja")
    losers_index=txt.rfind("haviaja")
    txt2=txt.replace("voittaja","")
    txt3=txt.replace("haviaja","")
    winners_score=""
    losers_score=""
    for i in range(winners_index,winners_index+2):
        if txt2[i]!="<":
            winners_score+=txt2[i]
    for j in range(losers_index,losers_index+2):
        if txt3[j]!="<":
            losers_score+=txt3[j]
    txt_to_find=[]
    txt_to_find.append(winners_score + " " + "-" + " " + losers_score)
    txt_to_find.append(losers_score + " " + "-" + " " + winners_score)
    txt_index=0
    for k in range(2):
        if txt.rfind(txt_to_find[k])!=-1:
            txt_index=k
    left_team_index=txt.rfind("team-left")
    right_team_index=txt.rfind("team-right")
    index=0
    matches_left=0
    for i in range(left_team_index+21, left_team_index+21 + len(team)):
        if txt[i]==team[index]:
            matches_left+=1
        index+=1
    index=0
    matches_right=0
    for i in range(right_team_index+22, right_team_index+22 + len(team)):
        if txt[i]==team[index]:
            matches_right+=1
        index+=1
    result_matrix=np.zeros((2,3),dtype=float)
    team_left=False
    if matches_left==len(team) and txt_index==0:
        result_matrix[0,0]=float(winners_score)
        result_matrix[1,0]=float(losers_score)
        team_left=True
    elif matches_left==len(team) and txt_index==1:
        result_matrix[0,0]=float(losers_score)
        result_matrix[1,0]=float(winners_score)
        team_left=True
    elif matches_right==len(team) and txt_index==0:
        result_matrix[0,0]=float(losers_score)
        result_matrix[1,0]=float(winners_score)
    elif matches_right==len(team) and txt_index==1:
        result_matrix[0,0]=float(winners_score)
        result_matrix[1,0]=float(losers_score)
    ct_score_index1=txt.find("ct-color")
    t_score_index1=txt.find("t-color")
    ct_first=True
    if ct_score_index1 < t_score_index1:
        ct_first=True
    else:
        ct_first=False
    ct_rounds1=""
    for i in range(ct_score_index1 + 10, ct_score_index1 + 12):
        if txt[i]!="<":
            ct_rounds1+=txt[i]
    ct_rounds1=float(ct_rounds1)
    if ct_first and team_left:
        result_matrix[0,1]=ct_rounds1
        result_matrix[1,2]=15-ct_rounds1
        result_matrix[1,1]=result_matrix[1,0]-result_matrix[1,2]
        result_matrix[0,2]=result_matrix[0,0]-result_matrix[0,1]
    elif ct_first and not(team_left):
        result_matrix[1,1]=ct_rounds1
        result_matrix[0,2]=15-ct_rounds1
        result_matrix[0,1]=result_matrix[0,0]-result_matrix[0,2]
        result_matrix[1,2]=result_matrix[1,0]-result_matrix[1,1]
    elif not(ct_first) and team_left:
        result_matrix[1,1]=ct_rounds1
        result_matrix[0,2]=15-ct_rounds1
        result_matrix[0,1]=result_matrix[0,0]-result_matrix[0,2]
        result_matrix[1,2]=result_matrix[1,0]-result_matrix[1,1]
    elif not(ct_first) and not(team_left):
        result_matrix[0,1]=ct_rounds1
        result_matrix[1,2]=15-ct_rounds1
        result_matrix[1,1]=result_matrix[1,0]-result_matrix[1,2]
        result_matrix[0,2]=result_matrix[0,0]-result_matrix[0,1]
    indexFO = txt.find('"stats-table"')
    indexLO = txt.rfind('"stats-table"')
    newText = ""
    for i in range(indexFO, indexLO + 7500):
        newText += txt[i]
    txtLength = len(newText)
    testPlayerIndex = newText.rfind(testPlayer + "<")
    finalText = ""
    constantTeamText = ""
    if testPlayerIndex > int(txtLength/2):
        for i in range(int(txtLength/2)):
            finalText += newText[i]
        for i in range(int(txtLength/2), txtLength):
            constantTeamText += newText[i]
    else:
        for i in range(int(txtLength/2), txtLength):
            finalText += newText[i]
        for i in range(int(txtLength/2)):
            constantTeamText += newText[i]
    playerList = [""]*5
    constantPlayerList = [""]*5
    for i in range(5):
        for j in range(len(finalText)):
            if i==0:
                if j != finalText.find('</a></td>'):
                    playerList[i]+=finalText[j]
                else:
                    playerList[i]+=str(i)
            else:
                if j != playerList[i-1].find('</a></td>'):
                    playerList[i]+=playerList[i-1][j]
                else:
                    playerList[i]+=str(i)
    finalText=playerList[-1]
    for i in range(5):
        for j in range(len(constantTeamText)):
            if i==0:
                if j != constantTeamText.find('</a></td>'):
                    constantPlayerList[i]+=constantTeamText[j]
                else:
                    constantPlayerList[i]+=str(i)
            else:
                if j != constantPlayerList[i-1].find('</a></td>'):
                    constantPlayerList[i]+=constantPlayerList[i-1][j]
                else:
                    constantPlayerList[i]+=str(i)
    finalConstantPlayerText=constantPlayerList[-1]
    finalPlayerList = [""]*5
    finalConstantPlayerList = [""]*5
    for i in range(5):
        index=finalText.find(str(i) + "/a></td>")
        j=""
        loop_index=0
        while j!='>':
            finalPlayerList[i]+=finalText[index-loop_index - 1]
            loop_index+=1
            j=finalText[index-loop_index - 1]
    finalPlayerList2 = [""]*5
    for i in range(5):
        index=finalConstantPlayerText.find(str(i) + "/a></td>")
        j=""
        loop_index=0
        while j!='>':
            finalConstantPlayerList[i]+=finalConstantPlayerText[index-loop_index - 1]
            loop_index+=1
            j=finalConstantPlayerText[index-loop_index - 1]
    finalConstantPlayerList2 = [""]*5
    for i in range(5):
        for j in range(len(finalPlayerList[i])):
            finalPlayerList2[i] += finalPlayerList[i][-j-1]
    for i in range(5):
        for j in range(len(finalConstantPlayerList[i])):
            finalConstantPlayerList2[i] += finalConstantPlayerList[i][-j-1]
    playedMap = ""
    mapFO = txt.find('bold">Map')
    j = ""
    loop_index = 0
    while j != " ":
        playedMap += txt[loop_index + mapFO + 23]
        loop_index += 1
        j = txt[loop_index + mapFO + 24]
    return result_matrix, finalPlayerList2, playedMap, finalConstantPlayerList2

def statstoFile(lst, path):
    #  Saves and processes the training data for the network.
    #  Inputs: path is the location of the folder where you want to save the training data. 
    #          lst is the return of of statCollector function.

    for i in range(2):
        for j in range(25):
            for k in range(4):
                if k == 0:
                    np.savetxt(path + "team_" + str(i) + "map_" + str(j) + ".csv", lst[i][j][k], delimiter = ",")
                elif k == 1:
                    np.savetxt(path + "team_" + str(i) + "result_" + str(j) + ".csv", lst[i][j][k], delimiter = ",")
                elif k == 2:
                    np.savetxt(path + "team_" + str(i) + "constantPlayerStats_" + str(j) + ".csv", lst[i][j][k], delimiter = ",")
                else:
                    np.savetxt(path + "team_" + str(i) + "enemyPlayerStats_" + str(j) + ".csv", lst[i][j][k], delimiter = ",")

def PlayerStats_reader(txt, players1, players2):
    # Collects players' statistics.
    # Inputs: HTML document (match page)
    #         players names
    # Outputs: two numpy matrices containing the data. 
    players1.sort()
    players2.sort()
    team1Playername1 = players1[0]
    team1Playername2 = players1[1]
    team1Playername3 = players1[2]
    team1Playername4 = players1[3]
    team1Playername5 = players1[4]
    team2Playername1 = players2[0]
    team2Playername2 = players2[1]
    team2Playername3 = players2[2]
    team2Playername4 = players2[3]
    team2Playername5 = players2[4]
    firstPlayername = ""
    player1FO = txt.rfind(">" + team1Playername1 + "<")
    player2FO = txt.rfind(">" + team1Playername2 + "<")
    player3FO = txt.rfind(">" + team1Playername3 + "<")
    player4FO = txt.rfind(">" + team1Playername4 + "<")
    player5FO = txt.rfind(">" + team1Playername5 + "<")
    if player1FO < player2FO and player1FO < player3FO and player1FO < player4FO and player1FO < player5FO:
        firstPlayername = team1Playername1
    elif player2FO < player1FO and player2FO < player3FO and player2FO < player4FO and player2FO < player5FO:
        firstPlayername = team1Playername2
    elif player3FO < player1FO and player3FO < player2FO and player3FO < player4FO and player3FO < player5FO:
        firstPlayername = team1Playername3
    elif player4FO < player1FO and player4FO < player2FO and player4FO < player3FO and player4FO < player5FO:
        firstPlayername = team1Playername4
    else:
        firstPlayername = team1Playername5
    t2firstPlayername = ""
    t2player1FO = txt.rfind(">" + team2Playername1 + "<")
    t2player2FO = txt.rfind(">" + team2Playername2 + "<")
    t2player3FO = txt.rfind(">" + team2Playername3 + "<")
    t2player4FO = txt.rfind(">" + team2Playername4 + "<")
    t2player5FO = txt.rfind(">" + team2Playername5 + "<")
    if t2player1FO < t2player2FO and t2player1FO < t2player3FO and t2player1FO < t2player4FO and t2player1FO < t2player5FO:
        t2firstPlayername = team2Playername1
    elif t2player2FO < t2player1FO and t2player2FO < t2player3FO and t2player2FO < t2player4FO and t2player2FO < t2player5FO:
        t2firstPlayername = team2Playername2
    elif t2player3FO < t2player1FO and t2player3FO < t2player2FO and t2player3FO < t2player4FO and t2player3FO < t2player5FO:
        t2firstPlayername = team2Playername3
    elif t2player4FO < t2player1FO and t2player4FO < t2player2FO and t2player4FO < t2player3FO and t2player4FO < t2player5FO:
        t2firstPlayername = team2Playername4
    else:
        t2firstPlayername = team2Playername5

    team1Last=False
    if txt.rfind(">" + t2firstPlayername + "<") < txt.rfind(">" + firstPlayername + "<"):
        team1Last = True
    team1StatsTxt = ""
    team2StatsTxt = ""
    if team1Last:
        team1StatstxtFO = txt.rfind(">" + firstPlayername + "<") - 1
        team1StatstxtLO = txt.rfind("</table>")
        team2StatstxtFO = txt.rfind(">" + t2firstPlayername + "<") - 1
        team2StatstxtLO = txt.find("</table>")
    else:
       
        team1StatstxtFO = txt.rfind(">" + firstPlayername + "<") - 1
        team1StatstxtLO = txt.find("</table>")
        team2StatstxtFO = txt.rfind(">" + t2firstPlayername + "<") - 1
        team2StatstxtLO = txt.rfind("</table>")
    for i in range(team1StatstxtFO, team1StatstxtLO):
        team1StatsTxt = team1StatsTxt + txt[i]
    for i in range(team2StatstxtFO, team2StatstxtLO):
        team2StatsTxt = team2StatsTxt + txt[i]  
    score_matrix_team1 = np.zeros((5, 8), dtype= float)
    score_matrix_team2 = np.zeros((5, 8), dtype= float)




    team1player1StatsTxt = ""
    team1player1StatsTxtFO = team1StatsTxt.rfind(team1Playername1 + "<")
    team1player1StatsTxtLO = team1StatsTxt.rfind("st-rating", team1player1StatsTxtFO, team1player1StatsTxtFO + 854 )
    
    team1player2StatsTxt = ""
    team1player2StatsTxtFO = team1StatsTxt.rfind(team1Playername2 + "<")
    team1player2StatsTxtLO = team1StatsTxt.rfind("st-rating", team1player2StatsTxtFO, team1player2StatsTxtFO + 854 )
    
    team1player3StatsTxt = ""
    team1player3StatsTxtFO = team1StatsTxt.rfind(team1Playername3 + "<")
    team1player3StatsTxtLO = team1StatsTxt.rfind("st-rating", team1player3StatsTxtFO, team1player3StatsTxtFO + 854 )
    
    team1player4StatsTxt = ""
    team1player4StatsTxtFO = team1StatsTxt.rfind(team1Playername4 + "<")
    team1player4StatsTxtLO = team1StatsTxt.rfind("st-rating", team1player4StatsTxtFO, team1player4StatsTxtFO + 854 )
    
    team1player5StatsTxt = ""
    team1player5StatsTxtFO = team1StatsTxt.rfind(team1Playername5 + "<")
    team1player5StatsTxtLO = team1StatsTxt.rfind("st-rating", team1player5StatsTxtFO, team1player5StatsTxtFO + 854 )

    team2player1StatsTxt = ""
    team2player1StatsTxtFO = team2StatsTxt.rfind(team2Playername1 + "<")
    team2player1StatsTxtLO = team2StatsTxt.rfind("st-rating", team2player1StatsTxtFO, team2player1StatsTxtFO + 854 )

    team2player2StatsTxt = ""
    team2player2StatsTxtFO = team2StatsTxt.rfind(team2Playername2 + "<")
    team2player2StatsTxtLO = team2StatsTxt.rfind("st-rating", team2player2StatsTxtFO, team2player2StatsTxtFO + 854 )

    team2player3StatsTxt = ""
    team2player3StatsTxtFO = team2StatsTxt.rfind(team2Playername3 + "<")
    team2player3StatsTxtLO = team2StatsTxt.rfind("st-rating", team2player3StatsTxtFO, team2player3StatsTxtFO + 854 )

    team2player4StatsTxt = ""
    team2player4StatsTxtFO = team2StatsTxt.rfind(team2Playername4 + "<")
    team2player4StatsTxtLO = team2StatsTxt.rfind("st-rating", team2player4StatsTxtFO, team2player4StatsTxtFO + 854 )

    team2player5StatsTxt = ""
    team2player5StatsTxtFO = team2StatsTxt.rfind(team2Playername5 + "<")
    team2player5StatsTxtLO = team2StatsTxt.rfind("st-rating", team2player5StatsTxtFO, team2player5StatsTxtFO + 854 )

    stringsToDelete = ["<", ")", " ", ")", "<", "<", " ", " "]
    team1Player1StatsList = ["", "", "", "", "", "", "", ""]
    team1Player2StatsList = ["", "", "", "", "", "", "", ""]
    team1Player3StatsList = ["", "", "", "", "", "", "", ""]
    team1Player4StatsList = ["", "", "", "", "", "", "", ""]
    team1Player5StatsList = ["", "", "", "", "", "", "", ""]
    team2Player1StatsList = ["", "", "", "", "", "", "", ""]
    team2Player2StatsList = ["", "", "", "", "", "", "", ""]
    team2Player3StatsList = ["", "", "", "", "", "", "", ""]
    team2Player4StatsList = ["", "", "", "", "", "", "", ""]
    team2Player5StatsList = ["", "", "", "", "", "", "", ""]
    team1Stats = [team1Player1StatsList, team1Player2StatsList, team1Player3StatsList, team1Player4StatsList, team1Player5StatsList]
    team2Stats = [team2Player1StatsList, team2Player2StatsList, team2Player3StatsList, team2Player4StatsList, team2Player5StatsList]

    team1Player1Indexes = []
    team1Player2Indexes = []
    team1Player3Indexes = []
    team1Player4Indexes = []
    team1Player5Indexes = []

    team2Player1Indexes = []
    team2Player2Indexes = []
    team2Player3Indexes = []
    team2Player4Indexes = []
    team2Player5Indexes = []

    spacingList = [11, 3, 13, 3, 12, 9, 7, 7]
    statsKeywords = ['"st-kills">', '> (', '"st-assists">', '">(', '"st-deaths">', '"st-adr">', 'title="', 'kills, '  ]

    for i in range(team1player1StatsTxtFO, team1player1StatsTxtLO):
        team1player1StatsTxt = team1player1StatsTxt + team1StatsTxt[i]
    for i in range(team1player2StatsTxtFO, team1player2StatsTxtLO):
        team1player2StatsTxt = team1player2StatsTxt + team1StatsTxt[i]
    for i in range(team1player3StatsTxtFO, team1player3StatsTxtLO):
        team1player3StatsTxt = team1player3StatsTxt + team1StatsTxt[i]
    for i in range(team1player4StatsTxtFO, team1player4StatsTxtLO):
        team1player4StatsTxt = team1player4StatsTxt + team1StatsTxt[i]
    for i in range(team1player5StatsTxtFO, team1player5StatsTxtLO):
        team1player5StatsTxt = team1player5StatsTxt + team1StatsTxt[i]
    for i in range(team2player1StatsTxtFO, team2player1StatsTxtLO):
        team2player1StatsTxt = team2player1StatsTxt + team2StatsTxt[i]
    for i in range(team2player2StatsTxtFO, team2player2StatsTxtLO):
        team2player2StatsTxt = team2player2StatsTxt + team2StatsTxt[i]
    for i in range(team2player3StatsTxtFO, team2player3StatsTxtLO):
        team2player3StatsTxt = team2player3StatsTxt + team2StatsTxt[i]
    for i in range(team2player4StatsTxtFO, team2player4StatsTxtLO):
        team2player4StatsTxt = team2player4StatsTxt + team2StatsTxt[i]
    for i in range(team2player5StatsTxtFO, team2player5StatsTxtLO):
        team2player5StatsTxt = team2player5StatsTxt + team2StatsTxt[i]

    team1PlayerTxts = [team1player1StatsTxt, team1player2StatsTxt, team1player3StatsTxt, team1player4StatsTxt, team1player5StatsTxt]
    team2PlayerTxts = [team2player1StatsTxt, team2player2StatsTxt, team2player3StatsTxt, team2player4StatsTxt, team2player5StatsTxt]
    for i in range(8):
        team1Player1Indexes.append(team1player1StatsTxt.rfind(statsKeywords[i]))
    for i in range(8):
        team1Player2Indexes.append(team1player2StatsTxt.rfind(statsKeywords[i])) 
    for i in range(8):
        team1Player3Indexes.append(team1player3StatsTxt.rfind(statsKeywords[i])) 
    for i in range(8):
        team1Player4Indexes.append(team1player4StatsTxt.rfind(statsKeywords[i]))
    for i in range(8):
        team1Player5Indexes.append(team1player5StatsTxt.rfind(statsKeywords[i])) 
    team1Indexes = [team1Player1Indexes, team1Player2Indexes, team1Player3Indexes, team1Player4Indexes, team1Player5Indexes]
    for i in range(8):
        team2Player1Indexes.append(team2player1StatsTxt.rfind(statsKeywords[i]))
    for i in range(8):
        team2Player2Indexes.append(team2player2StatsTxt.rfind(statsKeywords[i])) 
    for i in range(8):
        team2Player3Indexes.append(team2player3StatsTxt.rfind(statsKeywords[i])) 
    for i in range(8):
        team2Player4Indexes.append(team2player4StatsTxt.rfind(statsKeywords[i]))
    for i in range(8):
        team2Player5Indexes.append(team2player5StatsTxt.rfind(statsKeywords[i])) 
    team2Indexes = [team2Player1Indexes, team2Player2Indexes, team2Player3Indexes, team2Player4Indexes, team2Player5Indexes]

    for team in range(2):
        if team == 0:
            for i in range(5):
                for j in range(8):
                    if j != 5:
                        for k in range(team1Indexes[i][j] + spacingList[j], team1Indexes[i][j] + spacingList[j] + 2):
                            if team1PlayerTxts[i][k] != stringsToDelete[j]:
                                team1Stats[i][j] += team1PlayerTxts[i][k]
                    else:

                         for k in range(team1Indexes[i][j] + spacingList[j], team1Indexes[i][j] + spacingList[j] + 5):
                            if team1PlayerTxts[i][k] != stringsToDelete[j]:
                                team1Stats[i][j] += team1PlayerTxts[i][k]
        else:
            for i in range(5):
                for j in range(8):
                    if j != 5:
                        for k in range(team2Indexes[i][j] + spacingList[j], team2Indexes[i][j] + spacingList[j] + 2):
                            if team2PlayerTxts[i][k] != stringsToDelete[j]:
                                team2Stats[i][j] += team2PlayerTxts[i][k]
                    else:
                         for k in range(team2Indexes[i][j] + spacingList[j], team2Indexes[i][j] + spacingList[j] + 5):
                            if team2PlayerTxts[i][k] != stringsToDelete[j]:
                                team2Stats[i][j] += team2PlayerTxts[i][k]
    for team in range(2):
        if team == 0:
            for player in range(5):
                for stat in range(8):
                    score_matrix_team1[player, stat] = float(team1Stats[player][stat])
        else:
            for player in range(5):
                for stat in range(8):
                    score_matrix_team2[player, stat] = float(team2Stats[player][stat])
    return score_matrix_team1, score_matrix_team2

def statCollector(link):
    # Merges all the previous functions to return all the needed data.
    # Input: URL of the upcoming match [1].
    # Outputs: list of all the needed data
    #          names of the teams
    print("Data collecting started")
    team1Link = ""
    team2Link = ""   
    while True:
        team1Link, team2Link = mainPageSearcher((htmlScraper(link)))
        testText = ""
        testText2 = ""
        for i in range(26):
            testText += team1Link[i]
            testText2 += team2Link[i]
        if testText == "https://www.hltv.org/stats" and testText2 == "https://www.hltv.org/stats":
            break
        else:
            continue
    while True:
        team1MapsLink = mapOverviewSearcher(htmlScraper(team1Link))
        team2MapsLink = mapOverviewSearcher(htmlScraper(team2Link))
        testText = ""
        testText2 = ""
        for i in range(26):
            testText += team1MapsLink[i]
            testText2 += team2MapsLink[i]
        if testText == "https://www.hltv.org/stats" and testText2 == "https://www.hltv.org/stats":
            print("5%")
            break
        else:
            continue
    team1LinkList = []
    rightLinks=False
    while rightLinks==False:
        print("Processing...")
        while True:
            try:
                team1LinkList = mapPageSearcher(htmlScraper(team1MapsLink))
                break
            except Exception as e:
                print(e)
                continue
        rightLinks=True
        for i in range(len(team1LinkList)):
            testText=""
            if i == 10:
                print("8%")
            elif i == 20:
                print("13%")
            for j in range(len(team1LinkList[i])):
                if j <= 25:
                    testText+=team1LinkList[i][j]
            if testText!="https://www.hltv.org/stats":
                rightLinks=False

    print("15%")
    team2LinkList = []
    rightLinks=False
    while rightLinks==False:
        print("Processing...")
        while True:
            try:    
                team2LinkList = mapPageSearcher(htmlScraper(team2MapsLink))
                break
            except Exception as e:
                print(e)
                continue
        rightLinks=True
        for i in range(len(team2LinkList)):
            testText=""
            if i == 10:
                print("18%")
            elif i == 20:
                print("22%")
            for j in range(len(team2LinkList[i])):
                if j <= 25:
                    testText+=team2LinkList[i][j]
            if testText!="https://www.hltv.org/stats":
                rightLinks=False
    team1Players, team2Players, teamNames = PlayerListReader(htmlScraper(link))
    print("25%")
    print(); print()
    team1Players.sort()
    team2Players.sort()
    returnList = [] 
    mapList = []
    for index, i in enumerate(team1LinkList):
        changingList = []
        text = htmlScraper(i)
        while True:
            try:
                scoreMatrix, enemyPlayers, mapName, constantPlayers = team_scores_reader(text, teamNames[0], team1Players[2])
                break
            except Exception as e:
                print(e)
                text = htmlScraper(i)
                continue
        if set(team1Players) != set(constantPlayers):
            print("Roster change!")
            break
        print("#" + str(index + 1))
        print(enemyPlayers)
        team1Matrix, enemyMatrix = PlayerStats_reader(text, team1Players, enemyPlayers)
        changingList.append(mapNametoNumber(mapName))
        changingList.append(scoreMatrix)
        changingList.append(team1Matrix)
        changingList.append(enemyMatrix)
        mapList.append(changingList)
    mapList2 = []
    print("50%")
    for index, i in enumerate(team2LinkList):
        changingList = []
        text = htmlScraper(i)
        while True:
            try:
                scoreMatrix, enemyPlayers, mapName, constantPlayers = team_scores_reader(text, teamNames[1], team2Players[2])
                break
            except Exception as e:
                print(e)
                text = htmlScraper(i)
                continue
        if set(team2Players)!=set(constantPlayers):
            print("Roster change!")
            break
        print("#" + str(index + 1))
        print(enemyPlayers)
        team1Matrix, enemyMatrix = PlayerStats_reader(text, team2Players, enemyPlayers)
        changingList.append(mapNametoNumber(mapName))
        changingList.append(scoreMatrix)
        changingList.append(team1Matrix)
        changingList.append(enemyMatrix)
        mapList2.append(changingList)
    returnList.append(mapList)
    returnList.append(mapList2)
    
    return returnList, teamNames


class network:
    def __init__(self, inputL):
        # Initializes the network
        # Params: inputL is the whole training data and desiredOutput are the results (labels) of the matches.
        # Parameters and cache are stored in python dictionaries.
        # Loads the parameters.
        self.input = inputL
        self.output = np.array([[0]])
        self.param = {}
        self.cache= {}
        self.param["W1"]=np.loadtxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\W1.csv", delimiter= ",")
        self.param["W2"]=np.loadtxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\W2.csv", delimiter= ",")
        self.param["W3"]=np.loadtxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\W3.csv", delimiter= ",")
        self.param["b1"]=np.loadtxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\b1.csv", delimiter= ",")
        self.param["b2"]=np.loadtxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\b2.csv", delimiter= ",")
        self.param["b3"]=np.loadtxt("C:\\Users\\rikuk\\Documents\\AIprojekti\\b3.csv", delimiter= ",")
        self.param["W3"]=np.transpose(self.param["W3"][:,None])
        self.param["b1"]=self.param["b1"][:,None]
        self.param["b2"]=self.param["b2"][:,None]
    def forward(self):
        # Returns the output of the network (prediction for the match).
        Z_1 = np.zeros((50, 1)) 
        A_1 = np.zeros((50, 1))
        Z_2 = np.zeros((50, 1))
        A_2 = np.zeros((50, 1))
        Z_3 = np.zeros((1, 1))
        A_3 = np.zeros((1, 1))
        #1. layer
        # Calculating the dot products of weight vectors and the data.
        Z_1 = np.matmul(self.param["W1"], self.input[:,None])
        Z_1 = np.add(Z_1, self.param["b1"])
        A_1 = sigmoid(Z_1)
        self.cache["Z_1"], self.cache["A_1"] = Z_1, A_1
        #2. layer
        # Calculating the dot products of previous layer's activations and the weights of the second layer.  
        Z_2 = np.matmul(self.param["W2"], A_1)
        Z_2 = np.add(Z_2, self.param["b2"])
        A_2 = sigmoid(Z_2)
        self.cache["Z_2"], self.cache["A_2"] = Z_2, A_2
        #3.layer
        # Calculating the dot products of previous layer's activations and the weights of the third layer.  
        Z_3 = np.dot(self.param["W3"], A_2)
        Z_3 = np.add(Z_3, self.param["b3"])
        A_3 = sigmoid(Z_3)
        self.cache["Z_3"], self.cache["A_3"] = Z_3, A_3
        self.output = A_3
        return self.output
# Data is scraped and the prediction is printed.
tempData, teamNames = statCollector('https://www.hltv.org/matches/2342395/vitality-vs-big-cs-summit-6-europe')
data = shapeData(tempData)
neuralNetwork = network(data)
prediciton = neuralNetwork.forward()
print()
print("Joukkueen " + teamNames[0] + " todennäköisyys on " + str(np.round(100*prediciton[0,0])) + "%")
print("Joukkueen " + teamNames[1] + " todennäköisyys on " + str(np.round(100 - 100*prediciton[0,0])) + "%")
print()