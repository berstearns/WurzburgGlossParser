import time
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
pre_characters = 3
print("Set training parameters...")


# Import test and train sets
train_in = open("toktrain.pkl", "rb")
train_set = pickle.load(train_in)
test_in = open("toktest.pkl", "rb")
test_set = pickle.load(test_in)
x_train = remove_non_glosses(train_set)
x_test, y_test = test_set[0], test_set[1]
print("Loaded training and test data...")


# Combine all test and train sets into one list for later operations
all_testtrain = x_train + x_test + y_test


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


# # Encode all glosses using mapping (for use with full-padding)
# x_train = encode(x_train)
# x_test = encode(x_test)
# y_test = encode(y_test)
# print("Encoded training and test data for padding...")


def decode(numstring_list):
    """Decodes a list of strings with characters mapped to numbers"""
    temp_list = list()
    for num_string in numstring_list:
        string_list = []
        for num_char in num_string:
            decoded_char = rchardict[num_char]
            string_list.append(decoded_char)
        temp_list.append("".join(string_list))
    return temp_list


def pad(num_list):
    """Pads a list of glosses so that they all come to same length"""
    max_len = max([len(x) for x in all_testtrain]) + pre_characters
    padded_array = np.array(pad_sequences(num_list, maxlen=max_len, padding="pre"))
    return padded_array


def min_pad(string_list):
    """Adds selected number of pre-characters to every gloss without padding"""
    prepad = "$" * pre_characters
    prechar_list = []
    for gloss in string_list:
        gloss = prepad + gloss
        prechar_list.append(gloss)
    return prechar_list


# # Pad all glosses to same length (for use with full-padding)
# x_train = pad(x_train)
# x_test = pad(x_test)
# y_test = pad(y_test)
# print("Padded training and test data...")


# # Decode all padded glosses to be sequenced (for use with full-padding)
# x_train = decode(x_train)
# x_test = decode(x_test)
# y_test = decode(y_test)
# print("Decoded padded training and test data...")


# Pad all glosses only with set number of pre-characters (for use with minimal-padding)
x_train = min_pad(x_train)
x_test = min_pad(x_test)
y_test = min_pad(y_test)
print("Padded training and test data...")


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
x_train = sequence(x_train)
seq_name = "testing 1"
x_test = sequence(x_test)
seq_name = "testing 2"
y_test = sequence(y_test)
print("Organised glosses into sequences...")


# # Save sequences to file
# seqs_out = open("x_train_seqs.pkl", "wb")
# pickle.dump(x_train, seqs_out)
# seqs_out.close()
# seqs_out = open("x_test_seqs.pkl", "wb")
# pickle.dump(x_test, seqs_out)
# seqs_out.close()
# seqs_out = open("y_test_seqs.pkl", "wb")
# pickle.dump(y_test, seqs_out)
# seqs_out.close()
# print("Saved gloss sequences...")


# # Load sequences from file
# seqs_in = open("x_train_seqs.pkl", "rb")
# x_train = pickle.load(seqs_in)
# seqs_in = open("x_test_seqs.pkl", "rb")
# x_test = pickle.load(seqs_in)
# seqs_in = open("y_test_seqs.pkl", "rb")
# y_test = pickle.load(seqs_in)
# print("Loaded gloss sequences...")


# Encode all glosses using mapping (for use with padding)
x_train = encode(x_train)
x_test = encode(x_test)
y_test = encode(y_test)
print("Encoded training and test data...")


# Separate training into input and output, and one hot encode all training sequences
sequences = np.array(x_train)
x_train, y_train = sequences[:, : - 1], sequences[:, - 1]
sequences = [to_categorical(x, num_classes=vocab_size) for x in x_train]
x_train = np.array(sequences)
y_train = to_categorical(y_train, num_classes=vocab_size)


# One hot encode all glosses
# x_train = to_categorical(x_train)
x_test = to_categorical(x_test)
y_test = to_categorical(y_test)
print("One Hot encoded training and test data...")


def vec_decode(string_list):
    """Decodes a list of strings with characters rendered as One Hot vectors"""
    temp_list = list()
    for encoded_string in string_list:
        string_list = []
        for char_vect in encoded_string:
            from_categorical = np.argmax(char_vect)
            # Remove any padding
            if from_categorical != 0:
                string_list.append(from_categorical)
        temp_list.append(string_list)
    temp_list2 = decode(temp_list)
    return temp_list2


# Define model
model = Sequential()
# model.add(LSTM(40, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))  # 2 Hidden Layers
model.add(LSTM(40, input_shape=(x_train.shape[1], x_train.shape[2])))
model.add(Dense(vocab_size, activation='softmax'))
print(model.summary())
# Compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=1000, verbose=2)
print("Created Model...")


def save_model():
    """Saves the model"""
    model.save('n3_Tokeniser.h5')  # 1 Hidden Layer
    # model.save('n3_2HLTokeniser.h5')  # 2 Hidden Layers
    # Save the mapping
    pickle.dump(chardict, open('char_mapping.pkl', 'wb'))
    return "Saved Model..."


# Save the model
print(save_model())


# # Load the model
# model = load_model('Tokeniser.h')  # 1 Hidden Layer
# # model = load_model('2HLTokeniser.h')  # 2 Hidden Layers
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
print(generate_seq(model, chardict, pre_characters, '$$$', 20))
# test 2
print(generate_seq(model, chardict, pre_characters, '.i.', 20))
# test 3
print(generate_seq(model, chardict, pre_characters, 'ari', 20))

