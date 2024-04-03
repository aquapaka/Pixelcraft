# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json


def generateDiacritics(characters, diacritics):
    # Create dictionaries for faster lookup
    charactersByName = {}
    diacriticsByCodepoint = {}
    for c in characters:
        charactersByName[c["name"]] = c["codepoint"]
    for d in diacritics:
        diacriticsByCodepoint[d] = 0

    # List to store generated dictionary
    charList = []

    # Parse the text file
    lines = open("./unicode.txt").readlines()
    for line in lines:
        # Find all lines with a WITH in them
        if not "WITH" in line:
            continue
        # Get the diacritic name
        splitOnWith = line.split("WITH")
        diacritic = splitOnWith[1].split(';')[0].strip().lower().replace(" ", "_")
        additionalDiacritic = ""
        if "_and_" in diacritic and not diacritic in diacriticsByCodepoint:
            additionalDiacritic = diacritic.split('_and_')[1]
            diacritic = diacritic.split('_and_')[0]
        name = splitOnWith[0].split(';')[1].strip().lower().replace(" ", "_")
        newName = name + "_with_" + diacritic
        if len(additionalDiacritic) > 0:
            newName = newName + "_and_" + additionalDiacritic
        if newName in charactersByName or not diacritic in diacriticsByCodepoint or (additionalDiacritic and not additionalDiacritic in diacriticsByCodepoint) or not name in charactersByName:
            continue
        codepoint = int(line.split(";")[0].strip(), 16)
        # Store in a dictionary for serialization
        char = {}
        char["character"] = chr(codepoint)
        char["name"] = newName
        char["codepoint"] = codepoint
        char["reference"] = charactersByName[name]
        char["diacritic"] = diacritic
        char["diacriticSpace"] = 1
        if len(additionalDiacritic) > 0:
            char["additionalDiacritic"] = additionalDiacritic
            char["aditionalDiacriticSpace"] = 1
        charList.append(char)

    for c in charList:
        characters.append(c)

    print("Added " + str(len(charList)) + " diacritic combinations")
    return characters