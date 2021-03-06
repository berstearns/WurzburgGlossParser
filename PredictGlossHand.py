"""Level 3, 2, 2, 3"""

from PrepareHandContent import compile_tokenised_glosslist, get_unitoks, combinelists, compile_tokenised_testtrain
from CalculateBayes import bayes_tok
import time
import pickle
from SaveDocx import save_docx


def auth_check_glosshand(gloss):
    """Assesses statistical liklihood that a gloss belongs to a particular hand
       Measures: Bayesian Token analysis"""
    # Creates a list of sublists, each sublist representing a hand.
    # Each sublist contains the probability of each token in the gloss occurring in each hand.
    tok_problist = [[], [], []]
    # Creates three lists, one for each hand, containing the probabilities of each token.
    for token in gloss:
        if token != "*Latin*":
            for hand in range(3):
                handlist = tok_problist[hand]
                handlist.append(bayes_tok(token, hand + 1))
    # Replaces the list of token probabilities for each hand with an overall probability for each hand.
    for i in range(len(tok_problist)):
        hand_problist = tok_problist[i]
        multiplier = 1
        for prob in hand_problist:
            multiplier = multiplier * prob
        tok_problist[i] = multiplier
    most_probable_hand = 0
    highest_prob = 0
    # Looks at the three hands, finds the one with the highest probability for writing the gloss.
    for i in range(len(tok_problist)):
        if i == 0:
            highest_prob = tok_problist[i]
            most_probable_hand = i + 1
        elif tok_problist[i] > highest_prob:
            highest_prob = tok_problist[i]
            most_probable_hand = i + 1
    return most_probable_hand


def check_correct(gloss, hand):
    """Checks if a given gloss is in a given list"""
    glosshands = ["Wb. All Glosses", "Wb. Prima Manus", "Wb. Hand Two", "Wb. Hand Three"]
    if gloss in compile_tokenised_glosslist(glosshands[hand]):
        return "Correct: Hand = " + str(hand)
    else:
        for i in range(1, 4):
            if i != hand:
                if gloss in compile_tokenised_glosslist(glosshands[i]):
                    return "Incorrect: Hand = " + str(i)


def return_correction_list1():  # takes signifficantly longer to run than return_correction_list2
    start = time.time()
    """Calculates every gloss's most probable hand,
       checks to see if the gloss is actually from that hand,
       calculates how many glosses were assigned to the correct hand as a percentage"""
    allglosstoks = compile_tokenised_glosslist("Wb. All Glosses")
    all_corrections = []
    for gloss in allglosstoks[:10]:  # select how many glosses to use
        authguess = auth_check_glosshand(gloss)
        glosschecklist = [gloss, authguess, check_correct(gloss, authguess)]
        all_corrections.append(glosschecklist)
    correctcount = 0
    for i in all_corrections:
        print(i)
        correction = i[2]
        if correction[:7] == "Correct":
            correctcount += 1
    percent_correct = (100 / len(all_corrections) * correctcount)
    end = time.time()
    print(end - start)
    return str(percent_correct) + "% correct"


def return_correction_list2():
    start = time.time()
    """Calculates every gloss's most probable hand,
       checks to see if the gloss is actually from that hand,
       calculates how many glosses were assigned to the correct hand as a percentage"""
    allglosstoks = compile_tokenised_glosslist("Wb. All Glosses")
    # # OPTIONAL: Creates a dictionary of hand probabilities
    # # As the process takes a long time to run, it is advisable to do this once, and load from it in future (below)
    # allunitoks = get_unitoks(allglosstoks)  # select how many glosses to use
    # # Creates a dictionary, adds to it a list of hand probabilities (value) for every unique token (key)
    # allunitoksdict = {}
    # for token in allunitoks:
    #     if token != "*Latin*":
    #         allunitoksdict[token] = []
    #         thistokfreqs = allunitoksdict[token]
    #         for hand in range(3):
    #             thistokfreqs.append(bayes_tok(token, hand + 1))
    # # OPTIONAL: Saves the dictionary of hand probabilities created above as an object
    # # As the process takes a long time to run, it is advisable to do this once, and load from it in future (below)
    # pickle_out = open("unitokprobs_pickle2", "wb")
    # pickle.dump(allunitoksdict, pickle_out)
    # pickle_out.close()
    # OPTIONAL: Loads a pre-saved dictionary of hand probabilities if the file is available
    # Only possible if the file has been created using the step above
    pickle_in = open("unitokprobs_pickle2", "rb")
    allunitoksdict = pickle.load(pickle_in)
    # Creates three lists of hand probabilities for each token in the gloss
    all_corrections = []
    for gloss in allglosstoks:  # select how many glosses to use
        tok_problist = [[], [], []]
        for token in gloss:
            if token != "*Latin*":
                threehandprobs = allunitoksdict.get(token)
                for i in range(len(tok_problist)):
                    tok_problist[i].append(threehandprobs[i])
        # Replaces the list of token probabilities for each hand with an overall probability for each hand.
        for i in range(len(tok_problist)):
            hand_problist = tok_problist[i]
            multiplier = 1
            for prob in hand_problist:
                multiplier = multiplier * prob
            tok_problist[i] = multiplier
        most_probable_hand = 0
        highest_prob = 0
        # Looks at the three hands, finds the one with the highest probability for writing the gloss.
        for i in range(len(tok_problist)):
            if i == 0:
                highest_prob = tok_problist[i]
                most_probable_hand = i + 1
            elif tok_problist[i] > highest_prob:
                highest_prob = tok_problist[i]
                most_probable_hand = i + 1
        # Compiles a list of the tokenised gloss, the most probable hand, and the accuracy of the author guess.
        authguess = most_probable_hand
        glosschecklist = [" ".join(gloss), "Probable Hand: " + str(authguess), check_correct(gloss, authguess)]
        all_corrections.append(glosschecklist)
    # Calculates the percentage of glosses correctly assigned to a scribal hand.
    h1count = 0
    h2count = 0
    h3count = 0
    correctcount = 0
    h1correctcount = 0
    h2correctcount = 0
    h3correctcount = 0
    for i in all_corrections:
        correction = i[2]
        correcthand = int(correction[-1])
        if correcthand == 1:
            h1count += 1
        elif correcthand == 2:
            h2count += 1
        else:
            h3count += 1
        if correction[:7] == "Correct":
            correctcount += 1
            if correcthand == 1:
                h1correctcount += 1
            elif correcthand == 2:
                h2correctcount += 1
            else:
                h3correctcount += 1
    percent_correct = (100 / len(all_corrections) * correctcount)
    h1_correct = (100 / h1count * h1correctcount)
    h2_correct = (100 / h2count * h2correctcount)
    h3_correct = (100 / h3count * h3correctcount)
    end = time.time()
    time_taken = (str((end - start) / 60))
    print(time_taken[:4] + " min")
    return str(percent_correct) + "% correct total\n" + str(h1_correct) + "% correct for h1\n" + str(
        h2_correct) + "% correct for h2\n" + str(h3_correct) + "% correct for h3"


def return_correction_list3():
    start = time.time()
    """Calculates most probable hand (based on training sets) for every gloss (in test sets),
       checks to see if the gloss is actually from that hand,
       calculates how many glosses were assigned to the correct hand as a percentage"""
    pmtest = compile_tokenised_testtrain("Hand_1_hand_test")
    h2test = compile_tokenised_testtrain("Hand_2_hand_test")
    h3test = compile_tokenised_testtrain("Hand_3_hand_test")
    alltesttoks = combinelists([pmtest, h2test, h3test])
    # # OPTIONAL: Creates a dictionary of hand probabilities
    # # As the process takes a long time to run, it is advisable to do this once, and load from it in future (below)
    # pmtrain = compile_tokenised_testtrain("Hand_1_hand_training")
    # h2train = compile_tokenised_testtrain("Hand_2_hand_training")
    # h3train = compile_tokenised_testtrain("Hand_3_hand_training")
    # alltraintoks = combinelists([pmtrain, h2train, h3train])
    # allunitoks = get_unitoks(alltraintoks)  # select how many glosses to use from the training set
    # # Creates a dictionary, adds to it a list of hand probabilities (value) for every unique token (key)
    # allunitoksdict = {}
    # for token in allunitoks:
    #     if token != "*Latin*":
    #         allunitoksdict[token] = []
    #         thistokfreqs = allunitoksdict[token]
    #         for hand in range(3):
    #             thistokfreqs.append(bayes_tok(token, hand + 1, 1.0))
    # # OPTIONAL: Saves the dictionary of hand probabilities created above as an object
    # # As the process takes a long time to run, it is advisable to do this once, and load from it in future (below)
    # pickle_out = open("unitokprobs_pickle3", "wb")
    # pickle.dump(allunitoksdict, pickle_out)
    # pickle_out.close()
    # OPTIONAL: Loads a pre-saved dictionary of hand probabilities if the file is available
    # Only possible if the file has been created using the step above
    pickle_in = open("unitokprobs_pickle3", "rb")
    allunitoksdict = pickle.load(pickle_in)
    # Creates three lists of hand probabilities for each token in the gloss
    all_corrections = []
    for gloss in alltesttoks:  # select how many glosses use from the test set
        tok_problist = [[], [], []]
        for token in gloss:
            if token != "*Latin*":
                threehandprobs = allunitoksdict.get(token)
                if not threehandprobs:
                    threehandprobs = [0, 0, 0]
                for i in range(len(tok_problist)):
                    tok_problist[i].append(threehandprobs[i])
        # Replaces the list of token probabilities for each hand with an overall probability for each hand.
        for i in range(len(tok_problist)):
            hand_problist = tok_problist[i]
            multiplier = 1
            for prob in hand_problist:
                multiplier = multiplier * prob
            tok_problist[i] = multiplier
        most_probable_hand = 0
        highest_prob = 0
        # Looks at the three hands, finds the one with the highest probability for writing the gloss.
        for i in range(len(tok_problist)):
            if i == 0:
                highest_prob = tok_problist[i]
                most_probable_hand = i + 1
            elif tok_problist[i] > highest_prob:
                highest_prob = tok_problist[i]
                most_probable_hand = i + 1
        # Compiles a list of the tokenised gloss, the most probable hand, and the accuracy of the author guess.
        authguess = most_probable_hand
        glosschecklist = [" ".join(gloss), "Probable Hand: " + str(authguess), check_correct(gloss, authguess)]
        all_corrections.append(glosschecklist)
    # Calculates the percentage of glosses correctly assigned to a scribal hand.
    h1count = 0
    h2count = 0
    h3count = 0
    correctcount = 0
    h1correctcount = 0
    h2correctcount = 0
    h3correctcount = 0
    for i in all_corrections:
        correction = i[2]
        correcthand = int(correction[-1])
        if correcthand == 1:
            h1count += 1
        elif correcthand == 2:
            h2count += 1
        else:
            h3count += 1
        if correction[:7] == "Correct":
            correctcount += 1
            if correcthand == 1:
                h1correctcount += 1
            elif correcthand == 2:
                h2correctcount += 1
            else:
                h3correctcount += 1
    percent_correct = (100 / len(all_corrections) * correctcount)
    h1_correct = (100 / h1count * h1correctcount)
    h2_correct = (100 / h2count * h2correctcount)
    h3_correct = (100 / h3count * h3correctcount)
    end = time.time()
    time_taken = (str((end - start) / 60))
    print(time_taken[:4] + " min")
    return str(percent_correct) + "% correct total\n" + str(h1_correct) + "% correct for h1\n" + str(
        h2_correct) + "% correct for h2\n" + str(h3_correct) + "% correct for h3"


def return_correction_list4():
    start = time.time()
    """Saame as function 3, but with more calculations and used for testing."""
    pmtest = compile_tokenised_testtrain("Hand_1_hand_test")
    h2test = compile_tokenised_testtrain("Hand_2_hand_test")
    h3test = compile_tokenised_testtrain("Hand_3_hand_test")
    alltesttoks = combinelists([pmtest, h2test, h3test])
    # This file is a direct copy of unitokprobs_pickle3
    pickle_in = open("unitokprobs_pickle4", "rb")
    allunitoksdict = pickle.load(pickle_in)
    # Creates three lists of hand probabilities for each token in the gloss
    all_corrections = []
    for gloss in alltesttoks:  # select how many glosses use from the test set
        tok_problist = [[], [], []]
        for token in gloss:
            if token != "*Latin*":
                threehandprobs = allunitoksdict.get(token)
                if not threehandprobs:
                    threehandprobs = [0, 0, 0]
                for i in range(len(tok_problist)):
                    tok_problist[i].append(threehandprobs[i])
        # Replaces the list of token probabilities for each hand with an overall probability for each hand.
        for i in range(len(tok_problist)):
            hand_problist = tok_problist[i]
            multiplier = 1
            for prob in hand_problist:
                multiplier = multiplier * prob
            tok_problist[i] = multiplier
        most_probable_hand = 0
        highest_prob = 0
        # Looks at the three hands, finds the one with the highest probability for writing the gloss.
        for i in range(len(tok_problist)):
            if i == 0:
                highest_prob = tok_problist[i]
                most_probable_hand = i + 1
            elif tok_problist[i] > highest_prob:
                highest_prob = tok_problist[i]
                most_probable_hand = i + 1
        # Compiles a list of the tokenised gloss, the most probable hand, and the accuracy of the author guess.
        authguess = most_probable_hand
        glosschecklist = [" ".join(gloss), "Probable Hand: " + str(authguess), check_correct(gloss, authguess)]
        all_corrections.append(glosschecklist)
    # Calculates the percentage of glosses correctly assigned to a scribal hand.
    h1count = 0
    h2count = 0
    h3count = 0
    correctcount = 0
    h1correctcount = 0
    h2correctcount = 0
    h3correctcount = 0
    h1g2 = 0
    h1g3 = 0
    h2g1 = 0
    h2g3 = 0
    h3g1 = 0
    h3g2 = 0
    for i in all_corrections:
        correction = i[2]
        guess = i[1]
        correcthand = int(correction[-1])
        guesshand = int(guess[-1])
        if correcthand == 1:
            h1count += 1
        elif correcthand == 2:
            h2count += 1
        else:
            h3count += 1
        if correction[:7] == "Correct":
            correctcount += 1
            if correcthand == 1:
                h1correctcount += 1
            elif correcthand == 2:
                h2correctcount += 1
            else:
                h3correctcount += 1
        # If guess is wrong, compile counts for incorrectly assigned hands
        else:
            if correcthand == 1:
                if guesshand == 2:
                    h1g2 += 1
                elif guesshand == 3:
                    h1g3 += 1
            elif correcthand == 2:
                if guesshand == 1:
                    h2g1 += 1
                elif guesshand == 3:
                    h2g3 += 1
            else:
                if guesshand == 1:
                    h3g1 += 1
                elif guesshand == 2:
                    h3g2 += 1
    # Calculates percentage correctly assigned
    percent_correct = (100 / len(all_corrections) * correctcount)
    h1_correct = (100 / h1count * h1correctcount)
    h2_correct = (100 / h2count * h2correctcount)
    h3_correct = (100 / h3count * h3correctcount)
    # Calculates percentage incorrectly assigned for each hand/guess pair
    h1g2_incorrect = (100 / h1count * h1g2)
    h1g3_incorrect = (100 / h1count * h1g3)
    h2g1_incorrect = (100 / h2count * h2g1)
    h2g3_incorrect = (100 / h2count * h2g3)
    h3g1_incorrect = (100 / h3count * h3g1)
    h3g2_incorrect = (100 / h3count * h3g2)
    end = time.time()
    time_taken = (str((end - start) / 60))
    print(time_taken[:4] + " min")
    return str(percent_correct) + "% correct total\n" + str(h1_correct) + "% correct for h1\n" + str(
        h1g2_incorrect) + "% assigned 2\n" + str(h1g3_incorrect) + "% assigned 3\n" + str(
        h2_correct) + "% correct for h2\n" + str(h2g1_incorrect) + "% assigned 1\n" + str(
        h2g3_incorrect) + "% assigned 3\n" + str(h3_correct) + "% correct for h3\n" + str(
        h3g1_incorrect) + "% assigned 1\n" + str(h3g2_incorrect) + "% assigned 2"


# allglosstoks = compile_tokenised_glosslist("Wb. All Glosses")


# print(auth_check_glosshand(['.i.', 'díith', '.i.', '*Latin*', 'dernum']))

# print(check_correct(["tacráth"], 1))

# for gloss in allglosstoks[:10]:
#     authguess = auth_check_glosshand(gloss)
#     print(str(authguess) + " - " + check_correct(gloss, authguess))

# print(return_correction_list1())  # 1169.7852444648743 ticks on first ten glosses

# print(return_correction_list2())  # 695.408495426178 ticks on first ten glosses (26.315075874328613 ticks with pickle)

# print(return_correction_list3())  # 205.365735054016 ticks on first ten glosses (12.431609392166138 ticks with pickle)

# print(return_correction_list4())

# save_docx(return_correction_list2(), "Hands Predicted Correctly")
