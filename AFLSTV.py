import math
from random import shuffle
from typing import Dict, List, Optional, Tuple
import pandas

#Options
_INFILEPATH = "player_data.csv" #location of the match data. Needs to be Fryzigg
removeFinals = True #excludes finals games from calculations
selectionType = "ALLAUS" #controls how many players are selected "ALLAUS" - 23 (with interchange and sub noted), "BROWNLOW" - 1 brownlow winner, enter any other number  as a string for a custom value
voteField = "rating_points" #which field to use
voteFieldName = "rating points" #name of the field in output
enableLog = True #outputs to a log file
verboseLog = True #if enableLog == True then this outputs every single player elimination and selection in order
#########

outLog: List[str] = [] #output log

#convenience method to print players id and name
def playerToStr(id: int):
    pl = uniquePlayers[uniquePlayers["player_id"] == id]

    fn = pl["player_first_name"].iloc[0]
    ln = pl["player_last_name"].iloc[0]
    team = pl["player_team"].iloc[0]

    return f"{id} - {fn} {ln} ({team})"

#function to print to screen and log if enabled
def logAndPrint(s: str):
    if enableLog:
        outLog.append(s)
    
    print(s)

#class for ballot
class Ballot:
    def __init__(self):
        self.orderedVote = []
        self.remainingValue = 1.0
        self.exhausted = False

    def getTop(self) -> Optional[Tuple[int,float]]:
        global elected, eliminated

        countedVotes = [p for p in self.orderedVote if p[0] not in elected and p[0] not in eliminated]

        if len(countedVotes) == 0:
            self.exhausted = True
            return None
        else:
            return countedVotes[0]

#read and load data
playerData = None
with open(_INFILEPATH) as pdFile:
    playerData = pandas.read_csv(pdFile)
    pdFile.close()

#remove finals
if removeFinals:
    playerData = playerData[~playerData["match_round"].str.contains("Final", na=False)]

match_ids = playerData["match_id"].drop_duplicates()
matches: List[pandas.DataFrame] = []
for m in match_ids:
    matchFrame = playerData[playerData["match_id"] == m]

    matches.append(matchFrame)

logAndPrint(f"{len(matches)} matches considered")

uniquePlayers = playerData[["player_id","player_first_name","player_last_name","player_team"]].drop_duplicates()
player_ids = uniquePlayers["player_id"].to_list()
shuffle(player_ids) #shuffles the list to scan for starting-condition dependent errors.
logAndPrint(f"{len(player_ids)} players eligible")
logAndPrint("--------")



totalCandidates = len(player_ids)
teamsize = 0
if selectionType == "ALLAUS":
    teamsize = 23
elif selectionType == "BROWNLOW":
    teamsize = 1
else:
    try:
        teamsize = int(selectionType)
    except:
        exit(-1)

elected = []
eliminated = []
remaining = []

numGames = match_ids.count()
quota = math.floor(numGames/(teamsize + 1)) + 1
ballots: List[Ballot] = []
accruedPoints: Dict[int,float] = dict.fromkeys(player_ids,0.0)

for m in matches:
    sortedMatch = m.sort_values(by=[voteField], ascending=False)
    orderedPlayers = sortedMatch["player_id"]
    orderedScore = sortedMatch[voteField]

    b = Ballot()
    for z in zip(orderedPlayers,orderedScore):
        b.orderedVote.append((z[0],z[1]))
        accruedPoints[z[0]] += z[1]

    ballots.append(b)

while len(elected) < teamsize:
    #tally votes
    validCandidates = [id for id in player_ids if id not in elected and id not in eliminated]
    if len(validCandidates) == 0:
        break

    votePiles: Dict[int,List[Ballot]] = dict.fromkeys(validCandidates)
    for v in votePiles:
        votePiles[v] = []

    for b in ballots:
        if b.remainingValue > 0.0 and not b.exhausted:
            topCandidate = b.getTop()
            if topCandidate is not None:
                votePiles[topCandidate[0]].append(b)
    
    currentTally = dict.fromkeys(validCandidates, 0.0)
    for cand in votePiles:
        pile = votePiles[cand]
        for b in pile:
            currentTally[cand] += b.remainingValue

    #check for elected candidates
    bestCandidate = max(currentTally, key=lambda x: (currentTally[x],accruedPoints[x]))
    
    if currentTally[bestCandidate] >= quota:
        #candidate elected. distribute surplus value in future votes

        elected.append(bestCandidate)
        surplus = currentTally[bestCandidate] - quota
        sValue = surplus / currentTally[bestCandidate]

        for b in votePiles[bestCandidate]:
            b.remainingValue *= sValue

        if enableLog and verboseLog:
            outLog.append(f"{playerToStr(bestCandidate)} ELECTED - with {currentTally[bestCandidate]} B.O.G equivalents.")
    
    else:
        #eliminate the worst candidate and redistribute
        worstCandidate = min(currentTally, key=lambda x: (currentTally[x],accruedPoints[x]))
        eliminated.append(worstCandidate)

        if enableLog and verboseLog:
            outLog.append(f"{playerToStr(worstCandidate)} ELIMINATED with {currentTally[worstCandidate]} B.O.G. equivalents and {accruedPoints[worstCandidate]} {voteFieldName}.")

    remaining = [id for id in player_ids if id not in elected and id not in eliminated]

    #if the number of players remaining forms a full team with no extra, no need to elimnate further
    if len(remaining) + len(elected) == teamsize:
        outLog.append("--------")
        outLog.append("VOTES EXHAUSTED.")
        outLog.append("--------")
        remaining.sort(key= lambda x: currentTally[x],reverse=True)
        
        if enableLog and verboseLog:
            for r in remaining:
                outLog.append(f"{playerToStr(r)} ELECTED with {currentTally[r]} B.O.G equivalents.")

        break

if enableLog and verboseLog:
    outLog.append("--------")

#collect ballots
i = 0 #lazy counter for interchange/substitute
logAndPrint(f"quota: {quota} B.O.G. equivalents")
logAndPrint(f"ballots collected: {len(ballots)}")
logAndPrint(f"earned quota: {len(elected)}")
logAndPrint(f"best of rest: {len(remaining)}")
logAndPrint("--------")
logAndPrint("FULL QUOTAS")
logAndPrint("--------")
for e in elected:
    outStr = playerToStr(e)
    if selectionType == "ALLAUS":
        if i in range(18,23):
            outStr += " (INTERCHANGE)"
        elif i == 23:
            outStr += " (INJURY SUBSTITUTE)"

    logAndPrint(outStr)
    i += 1

logAndPrint("--------")
logAndPrint("REMAINING")
logAndPrint("--------")
for r in remaining:
    outStr = playerToStr(r)
    if selectionType == "ALLAUS":
        if i in range(18,22):
            outStr += " (INTERCHANGE)"
        elif i == 22:
            outStr += " (INJURY SUBSTITUTE)"

    logAndPrint(outStr)
    i += 1

logAndPrint("--------")

if enableLog:
    with open("logOut.txt","w") as outF:
        outF.write("\n".join(outLog))
        outF.close()