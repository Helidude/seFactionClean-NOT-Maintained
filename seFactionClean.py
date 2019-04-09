# seFactionClean by Ivar Vikestad 
# version 19.04.08
# Players should be removed first by Torch Essentials. 
# Example: !identity purge 14 (removes players not logged in for 14 days)
# This script clears the Sandbox.sbc for removed player references in factions

import xml.etree.cElementTree as et

SBC_PATH = "H:\\dev\\otherSources\\Sandbox.sbc"  # Directory Path for Sandbox.sbc
SBC_OUT_PATH ="H:\\dev\\otherSources\\output.xml" # Directory Path and name for the output file
PROTECTED_FACTIONS = ['SPID', 'SPRT']  # List of Factions to ignore

pf_list = list()  # Holds Id of players inProtected Factions
f_list = list()  # Holds Id of remaining factions
df_list = list() # Holds TAG of deleted factions

tree = et.parse(SBC_PATH)
sandbox = tree.getroot()

# Add missing namespace
sandbox.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

# Add all players IDs to p_list
# Player refrences not in this list, will be deleted
players = sandbox.findall('AllPlayersData/dictionary/item')
p_list = list()
for p in players:
    pid = p.find('Value/IdentityId').text
    p_list.append(pid)

# Save the NPCs!
npcs = sandbox.findall('NonPlayerIdentities')
for n in npcs:
    nid = n.find('long').text
    p_list.append(nid)	

# Cycle through and Remove playertrace from <Factions/Factions>
for factions in sandbox.findall('Factions/Factions'):
    for myObjectBuilder_Faction in factions.findall('MyObjectBuilder_Faction'):
        factionTag = myObjectBuilder_Faction.find('Tag').text
        fId = myObjectBuilder_Faction.find('FactionId').text
        print(factionTag, " ", fId)

        # For every faction.. get member info
        for members in myObjectBuilder_Faction.findall('Members'):
            for myObjectBuilder_FactionMember in members.findall('MyObjectBuilder_FactionMember'):
                memberId = myObjectBuilder_FactionMember.find('PlayerId').text
                # Keep these
                if memberId in p_list or factionTag in PROTECTED_FACTIONS:
                    print(memberId, " Member found... skipping")
                else:
                    # Remove inactive players from Faction
                    members.remove(myObjectBuilder_FactionMember)
                    print(memberId, " Member not found... deleting!")

                # Add Protected Faction Members to Array
                if factionTag in PROTECTED_FACTIONS:
                    pf_list.append(memberId)

            # Remove empty Factions
            if len(members) == 0:
                factions.remove(myObjectBuilder_Faction)
                df_list.append(factionTag)

# Add remaining factions to f_list
for factions in sandbox.findall('Factions/Factions'):
    for myObjectBuilder_Faction in factions.findall('MyObjectBuilder_Faction'):
        fId = myObjectBuilder_Faction.find('FactionId').text
        # Add faction ID to list
        f_list.append(fId)

# Remove player trace from <Factions/Players/dictionary>
for factions in sandbox.findall('Factions/Players/dictionary'):
    for item in factions.findall('item'):
        fId1 = item.find('Value').text

        if fId1 not in f_list:
            factions.remove(item)

# Remove player trace from <Factions/Relations>
for factions in sandbox.findall('Factions/Relations'):
    for item in factions.findall('MyObjectBuilder_FactionRelation'):
        fId1 = item.find('FactionId1').text
        fId2 = item.find('FactionId1').text

        if fId1 or fId2 in f_list:
            continue
        else:
            factions.remove(item)

# Remove player trace from <Identities/MyObjectBuilder_Identity>
for players in sandbox.findall('Identities'):
    for item in players.findall('MyObjectBuilder_Identity'):
        playerKey = item.find('IdentityId').text

        if playerKey not in p_list:
            players.remove(item)

# Remove player trace from <Gps/dictonary>
for players in sandbox.findall('Gps/dictionary'):
    for item in players.findall('item'):
        playerKey = item.find('Key').text

        if playerKey not in p_list:
            players.remove(item)

# Remove relations for <Factions/Requests/MyObjectBuilder_FactionRequests>
for factions in sandbox.findall('Factions/Requests'):
    for item in factions.findall('MyObjectBuilder_FactionRequests'):
        fId1 = item.find('FactionId').text

        if fId1 not in f_list:
            factions.remove(item)

# Remove relations for <MyObjectBuilder_SessionComponent xsi:type="MyObjectBuilder_SessionComponentContainerDropSystem"/Playerdata>
for players in sandbox.findall('MyObjectBuilder_SessionComponentContainerDropSystem/Playerdata'):
    for item in players.findall('PlayerContainerData'):
        playerKey = item.find('PlayerId').text

        if playerKey not in p_list:
            players.remove(item)

# <SessionComponents/MyObjectBuilder_SessionComponent xsi:type="MyObjectBuilder_SessionComponentContainerDropSystem">
print("Deleted Factions:", df_list)
tree.write(SBC_OUT_PATH, xml_declaration=True, encoding='UTF-8')
input("Press Enter to continue...")
