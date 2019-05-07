import time
from OpenDocx import get_text
import pickle
from PrepareHandContent import remove_non_glosses
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.models import load_model


start_time = time.time()


def time_elapsed(sec):
    """Calculates time to train model"""
    if sec < 60:
        return str(sec) + " sec"
    elif sec < (60 * 60):
        return str(sec / 60) + " min"
    else:
        return str(sec / (60 * 60)) + " hr"


# Set how many characters the model should look at before predicting an upcoming character
pre_characters = 5
print("Set training parameters...")


# # Import the training set of glosses for use as the single training text
# one_text_in = open("toktrain.pkl", "rb")
# one_text = " ".join(pickle.load(one_text_in))
# text_name = "Wb. Training Glosses"
# Import and clean Táin Bó Fraích for use as the single training text
one_text = " ".join((get_text("TBF_cleaned")).split("\n"))
while "  " in one_text:
    one_text = " ".join(one_text.split("  "))
text_name = "Táin Bó Fraích"
# Import test and train sets for character mapping
train_in = open("toktrain.pkl", "rb")
train_set = pickle.load(train_in)
test_in = open("toktest.pkl", "rb")
test_set = pickle.load(test_in)
x_train = remove_non_glosses(train_set)
x_test, y_test = test_set[0], test_set[1]
print("Loaded {}, training, and test data...".format(text_name))


# Combine all test and train sets into one list for later operations
all_testtrain = [one_text] + x_train + x_test + y_test


# Maps all characters in both sets
chars = sorted(list(set("".join(all_testtrain))))
chardict = dict((c, i + 1) for i, c in enumerate(chars))
chardict["$"] = 0
vocab_size = len(chardict)
print('    No. of characters: %d' % vocab_size)
rchardict = dict((i + 1, c) for i, c in enumerate(chars))
rchardict[0] = "$"
print("Mapped Characters...")


def encode(string_list):
    """Encodes a list of glosses using mapping"""
    num_list = list()
    for plain_string in string_list:
        encoded_string = [chardict[char] for char in plain_string]
        num_list.append(encoded_string)
    return num_list


def sequence(string_list):
    """Organises gloss content into sequences"""
    one_liner = " ".join(string_list)
    sequences = list()
    for i in range(pre_characters, len(one_liner)):
        # select sequence of tokens
        seq = one_liner[i - pre_characters: i + 1]
        # store this seq
        sequences.append(seq)
    print('    Total Sequences for {0}: {1}'.format(seq_name, len(sequences)))
    return sequences


# Organize into sequences
seq_name = "training"
x_train = sequence([one_text])
print("Organised {} into sequences...".format(text_name))


# Encode all glosses using mapping (for use with padding)
x_train = encode(x_train)
print("Encoded {}...".format(text_name))


# Separate training into input and output, and one hot encode all training sequences
sequences = np.array(x_train)
x_train, y_train = sequences[:, : - 1], sequences[:, - 1]
sequences = [to_categorical(x, num_classes=vocab_size) for x in x_train]
x_train = np.array(sequences)
y_train = to_categorical(y_train, num_classes=vocab_size)
print("One Hot encoded {}...".format(text_name))


# Define model
model = Sequential()
model.add(LSTM(40, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 2 Hidden Layers
model.add(LSTM(40, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
model.add(LSTM(27, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 3 Hidden Layers
model.add(LSTM(27, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 4 Hidden Layers
model.add(LSTM(18, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 5 Hidden Layers
model.add(LSTM(12, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 6 Hidden Layers
model.add(LSTM(8, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 7 Hidden Layers
model.add(LSTM(6, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 8 Hidden Layers
model.add(LSTM(4, input_shape=(x_train.shape[1], x_train.shape[2])))  # 9 Hidden Layers
model.add(Dense(vocab_size, activation='softmax'))
print(model.summary())
# Compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=1000, verbose=2)
print("Created Model...")


# Save the model
model.save('n5_TBF9HLTokeniser.h5')  # Name model
# # Save the mapping
# pickle.dump(chardict, open('char_mappingTBF.pkl', 'wb'))
print("Saved Model...")


# # Load the model
# model = load_model('n3_Tokeniser.h5')  # 1 Hidden Layer
# # Load the mapping
# chardict = pickle.load(open('char_mapping.pkl', 'rb'))


end_time = time.time()
seconds_elapsed = end_time - start_time
print("Time elapsed: " + time_elapsed(seconds_elapsed))


# Generate a sequence of characters with a language model
def generate_seq(model, mapping, seq_length, seed_text, n_chars):
    in_text = seed_text
    # Generate a fixed number of characters
    for _ in range(n_chars):
        # Encode the characters as integers
        encoded = [mapping[char] for char in in_text]
        # Truncate sequences to a fixed length
        encoded = pad_sequences([encoded], maxlen=seq_length, truncating='pre')
        # One hot encode
        encoded = to_categorical(encoded, num_classes=len(mapping))
        # encoded = encoded.reshape(1, encoded.shape[0], encoded.shape[1])  # Causes shaping error, comment out
        # Predict character
        yhat = model.predict_classes(encoded, verbose=0)
        # Reverse map integer to character
        out_char = ''
        for char, index in mapping.items():
            if index == yhat:
                out_char = char
                break
        # Append to input
        in_text += char
    return in_text


# test 1
print(generate_seq(model, chardict, pre_characters, '$$$$$', 20))
# test 2
print(generate_seq(model, chardict, pre_characters, '$$.i.', 20))
# test 3
print(generate_seq(model, chardict, pre_characters, '$aris', 20))


"""
Model 1: n5_TBFTokeniser.h5

One Hidden Layer
LSTM cells: 40
Epochs: 1000
Buffer: 5 pre-characters

   Epoch 1/1000
    - 3s - loss: 2.9281 - acc: 0.1807
   Epoch 1000/1000
    - 3s - loss: 0.9174 - acc: 0.6954

   Time elapsed: 43.73444213072459 min

   $$$$$r ind ordnasc ol ail
   $$.i. segait ⁊ ór di ór ⁊
   $aris illei tíri ni béo i


Model 2: n5_TBF2HLTokeniser.h5

Two Hidden Layers
LSTM cells: 40 x 40
Epochs: 1000
Buffer: 5 pre-characters

   Epoch 1/1000
    - 5s - loss: 2.9282 - acc: 0.1839
   Epoch 1000/1000
    - 4s - loss: 0.5109 - acc: 0.7786

   Time elapsed: 1.2472326714462705 hr

   $$$$$.i. ished and $$$$$.
   $$.i. ished and $$$$$.i. 
   $arisaib $$$$$.i. ished a


Model 3: n5_TBF4HLTokeniser.h5

Five Hidden Layers
LSTM cells: 40 x 40 x 27 x 27
Epochs: 1000
Buffer: 5 pre-characters

   Epoch 1/1000
    - 10s - loss: 2.9596 - acc: 0.1832
   Epoch 1000/1000
    - 8s - loss: 0.5349 - acc: 0.7785

   Time elapsed: 2.259919977254338 hr

   $$$$$ is é dírimm athesc 
   $$.i. conall cernach ara 
   $ariscet nechach issa tec


Model 4: n5_TBF9HLTokeniser.h5

Five Hidden Layers
LSTM cells: 40 x 40 x 27 x 27 x 18 x 12 x 8 x 6 x 4
Epochs: 1000
Buffer: 5 pre-characters

   Epoch 1/1000
    
   Epoch 1000/1000
    

   Time elapsed: 




"""

