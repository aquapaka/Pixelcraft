# Pixelcraft, a monospaced font for developers who like Minecraft a bit too much.
# Copyright (C) 2022-2023 Idrees Hassan
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

import os
import fontforge
import json
import math
from generate_diacritics import generateDiacritics
from generate_examples import generateExamples
from polygonizer import PixelImage, generatePolygons
from generate_continuous_ligatures import generate_continuous_ligatures

PIXEL_SIZE = 120

characters = json.load(open("./characters.json", encoding="utf-8"))
diacritics = json.load(open("./diacritics.json", encoding="utf-8"))
ligatures = json.load(open("./ligatures.json", encoding="utf-8"))
ligatures += generate_continuous_ligatures("./continuous_ligatures.json")

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}

def generateFont():
	pixelcraft = fontforge.font()
	pixelcraft.fontname = "Pixelcraft"
	pixelcraft.familyname = "Pixelcraft"
	pixelcraft.fullname = "Pixelcraft"
	pixelcraft.copyright = "Aquapaka, https://github.com/aquapaka/Pixelcraft"
	pixelcraft.encoding = "UnicodeFull"
	pixelcraft.version = "1.0"
	pixelcraft.weight = "Regular"
	pixelcraft.ascent = PIXEL_SIZE * 8
	pixelcraft.descent = PIXEL_SIZE
	pixelcraft.em = PIXEL_SIZE * 9
	pixelcraft.upos = -PIXEL_SIZE # Underline position
	pixelcraft.addLookup("ligatures", "gsub_ligature", (), (("liga",(("dflt",("dflt")),("latn",("dflt")))),))
	pixelcraft.addLookupSubtable("ligatures", "ligatures-subtable")

	for character in characters:
		charactersByCodepoint[character["codepoint"]] = character
		pixelcraft.createChar(character["codepoint"], character["name"])
		pen = pixelcraft[character["name"]].glyphPen()
		top = 0
		drawn = character

		image, kw = generateImage(character)
		drawImage(image, pen, **kw)
		pixelcraft[character["name"]].width = PIXEL_SIZE * 6
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	pixelcraft.generate(outputDir + "Pixelcraft-no-ligatures.ttf")
	for ligature in ligatures:
		lig = pixelcraft.createChar(-1, ligature["name"])
		pen = pixelcraft[ligature["name"]].glyphPen()
		image, kw = generateImage(ligature)
		drawImage(image, pen, **kw)
		pixelcraft[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
		lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
	print(f"Generated {len(ligatures)} ligatures")

	pixelcraft.generate(outputDir + "Pixelcraft.ttf")
	pixelcraft.generate(outputDir + "Pixelcraft.otf")

def generateImage(character):
	image = PixelImage()
	kw = {}
	if "pixels" in character:
		arr = character["pixels"]
		leftMargin = character["leftMargin"] if "leftMargin" in character else 0
		x = math.floor(leftMargin)
		kw['dx'] = leftMargin - x
		descent = -character["descent"] if "descent" in character else 0
		y = math.floor(descent)
		kw['dy'] = descent - y
		image = image | imageFromArray(arr, x, y)
	if "reference" in character:
		other = generateImage(charactersByCodepoint[character["reference"]])
		kw.update(other[1])
		image = image | other[0]

	furthestX = findFurthestX(image)
	highestY = findHighestY(image)
	if "diacritic" in character:
		diacritic = diacritics[character["diacritic"]]
		arr = diacritic["pixels"]
		x = image.x
		y = highestY + 1
		# Side horn
		if "latin_small_letter_a_with_grave" == character["name"]:
			print(diacritic)
		if character["diacritic"] == "horn":
			x = furthestX + 1
			y = highestY - 2
		# Dot below
		elif character["diacritic"] == "dot_below":
			y = image.y - 2
		elif "diacriticSpace" in character:
			y += int(character["diacriticSpace"]) - 1
		image = image | imageFromArray(arr, x, y)
	if "additionalDiacritic" in character:
		additionalDiacritic = diacritics[character["additionalDiacritic"]]
		arr = additionalDiacritic["pixels"]
		x = image.x
		y = highestY - 1
		# Side horn
		if character["additionalDiacritic"] == "horn":
			x = furthestX + 1
			y = highestY - 2
		# Dot below
		if character["additionalDiacritic"] == "dot_below":
			y = image.y + 3
		elif "aditionalDiacriticSpace" in character:
			y += int(character["aditionalDiacriticSpace"]) - 1
		image = image | imageFromArray(arr, x, y)
	return (image, kw)

def findFurthestX(image):
	for x in range(image.x_end - 1, image.x, -1):
		for y in range(image.y, image.y_end):
			if image[x, y]:
				return x
	return image.x

def findHighestY(image):
	for y in range(image.y_end - 1, image.y, -1):
		for x in range(image.x, image.x_end):
			if image[x, y]:
				return y
	return image.y

def imageFromArray(arr, x=0, y=0):
	return PixelImage(
		x=x,
		y=y,
		width=len(arr[0]),
		height=len(arr),
		data=bytes(x for a in reversed(arr) for x in a),
	)

def drawImage(image, pen, *, dx=0, dy=0):
	for polygon in generatePolygons(image):
		start = True
		for x, y in polygon:
			x = (x + dx) * PIXEL_SIZE
			y = (y + dy) * PIXEL_SIZE
			if start:
				pen.moveTo(x, y)
				start = False
			else:
				pen.lineTo(x, y)
		pen.closePath()

generateFont()
# generateExamples(characters, ligatures, charactersByCodepoint)
