# Approach:
# http://practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-simple-substitution-cipher/
# The plan is to use a hill-climbing algorithm to generate a key that has a high fitness value.

import random       # Used to generate random swaps during the decode process.
import os           # Used to clear the screen.
import string       # Used to clear the punctuation from strings.

# Letter frequency analysis dictionaries.
import monographs
import bigraphs
import trigraphs
#import quadgraphs

mratings = monographs.mgraphs
bratings = bigraphs.bgraphs
tratings = trigraphs.tgraphs
#qratings = quadgraphs.qgraphs
ENGLISH = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')    # The normal plaintext key.

FILTER_MONO_GRAPHS = False    # Default disabled as it will reward the algorithm just for using popular letters.
#FILTER_QUAD_GRAPHS = False    # Default disabled as it requires a ton of memory. Crashes my poor little Virtual Machine when uncommented.

# This was used to convert public graphs and ratings into a python dictionary for easier formatting.
def makeDict():
    graphs = {}
    for line in open('trigraphs.txt'):
        key, count = line.split(' ')
        graphs[key] = int(count)

    # calculate log probabilities
    for key in graphs.keys():
        graphs[key] = float(graphs[key]/1000000000)

    f = open('bigraphs.py', 'w')
    f.write("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in graphs.items()) + "}")
    f.close()
    return

def encrypt(plainText, key):
    cipherText = plainText.upper()
    cipherText = cipherText.translate(str.maketrans('','',string.punctuation))

    for i in range(0, len(ENGLISH)):
        cipherText = cipherText.replace(ENGLISH[i], key[i].lower())

    return cipherText

def decrypt(cipherText, key):
    plainText = cipherText.upper()

    for i in range(0, len(ENGLISH)):
        plainText = plainText.replace(key[i], ENGLISH[i].lower())

    return plainText.lower()

# Assign a rating to the text based on the trigraphs.
def rate(text):
    rating = 0

    if FILTER_MONO_GRAPHS:
        for i in range(1, len(text)):
            bigraph = text[i].upper()
            if bigraph in bratings:
                rating += bratings[bigraph]
    for i in range(2, len(text)):
        bigraph = text[i - 2:i].upper()
        if bigraph in bratings:
            rating += bratings[bigraph]
    for i in range(3, len(text)):
        trigraph = text[i - 3:i].upper()
        if trigraph in tratings:
            rating += tratings[trigraph]
    # if FILTER_QUAD_GRAPHS:
    #     for i in range(4, len(text)):
    #         trigraph = text[i - 4:i].upper()
    #         if trigraph in tratings:
    #             rating += tratings[trigraph]

    return rating

if __name__ == "__main__":
    print("Welcome to the Simple Substitution Cipher tool!")
    choice = -1
    hills = 50      # Number of times to restart the climb to the top of the hill. This is done in order avoid getting stuck.
    steps = 5000    # Number of consecutive failed mutations before restarting.

    while choice != 0:
        choice = int(input("Menu:\n[1]: Brute Force attack using hill-climbing algorithm.\n[2]: Encrypt with known key.\n[3]: Decrypt with known key.\n[0]: Exit.\nEnter your choice: "))

        if choice == 1:
            choice = -1
            while choice != 0:
                os.system('clear') # Clear the screen.
                choice = int(input("Options:\n[1]: Hills: " + str(hills) + " - Total times the algorithm should restart in order to find a new key.\n[2]: Steps per hill: " + str(steps) + " - Number of consecutive unsuccessful mutations before ending the climb.\n[0]: Continue\nEnter your choice: "))
                if choice == 1:
                    hills = int(input("Enter the amount of times the algorith should restart the climb: "))
                elif choice == 2:
                    steps = int(input("Enter the amount of mutations per climb: "))
                else:
                    choice = 0

            cipherText = input("Enter cipher text to decrypt: ")
            cipherText = cipherText.replace(" ", "")
            currentKey = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')  # Used to store the current key being observed.
            bestKey = ""  # Store the best key so far.
            bestRating = 0  # Store the rating of the key.

            for i in range(1, hills):
                keyDict = {}  # Create a dictionary to map new letters to each value in the english list.
                tempKey = currentKey.copy()  # Create a copy of the key to generate a new mutation.

                # Create new random key for climb.
                for char in ENGLISH:
                    index = 0

                    if len(tempKey) > 0:
                        index = random.randint(0, len(tempKey) - 1)
                    keyDict[char] = tempKey[index]
                    del tempKey[index]
                key = []
                for k, value in sorted(keyDict.items()):
                    key.append(value)

                # Generate rating based off of key.
                rating = rate(decrypt(cipherText, key))

                # Proceed with mutations.
                j = 0
                while j < steps:
                    index1 = random.randint(0, 25)
                    index2 = random.randint(0, 25)

                    while index2 == index1:
                        index2 = random.randint(0, 25)

                    # Get the key and mutate it.
                    newKey = list(key[:])
                    newKey[index1] = key[index2]
                    newKey[index2] = key[index1]

                    # Get the new rating.
                    newRating = rate(decrypt(cipherText, newKey))

                    # Check if the mutation was successful.
                    if newRating > rating:
                        rating = newRating
                        key = newKey
                        j = 0
                    j += 1

                if rating >= bestRating:
                    bestKey = key
                    bestRating = rating
                print("Key " + str(i) + ": " + str(key) + " with rating: " + str(rating))

            print("\nBest key found: " + str(bestKey) + ", rating: " + str(bestRating) + "\nResult:\n" + decrypt(cipherText, bestKey))

            choice = -1
        elif choice == 2:
            plainText = input("Enter text to encrypt:")
            keyStr = input("Enter the key to encrypt it in (Default: EINZJRPHMAWTCYQLSKDVFOUGXB):")
            key = list('EINZJRPHMAWTCYQLSKDVFOUGXB')
            if keyStr.isalpha() and len(keyStr) == 26:
                key = list(keyStr.upper())
            else:
                keyStr = 'EINZJRPHMAWTCYQLSKDVFOUGXB'

            cipherText = encrypt(plainText, key)

            print("\nHere's the ciphertext encrypted using the key [" + keyStr + "]:\n" + cipherText)
        elif choice == 3:
            cipherText = input("Enter text to decrypt:")
            keyStr = input("Enter the key to decrypt it with (Default: EINZJRPHMAWTCYQLSKDVFOUGXB):")
            key = list('EINZJRPHMAWTCYQLSKDVFOUGXB')
            if keyStr.isalpha() and len(keyStr) == 26:
                key = list(keyStr.upper())
            else:
                keyStr = 'EINZJRPHMAWTCYQLSKDVFOUGXB'

            plainText = decrypt(cipherText, key)

            print("\nHere's the plaintext decrypted using the key [" + keyStr + "]:\n" + plainText)
        elif choice == 0:
            print("Thanks!")
        else:
            print("Invalid input!")
