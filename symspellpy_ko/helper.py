import pandas as pd
from .unicode import split_syllables


def build_decomposed_dictionary(input_filename: str, output_file: str):
    vocab = pd.read_csv(input_filename, sep=" ", names=["term", "count"])
    vocab.term = vocab.term.map(split_syllables)
    vocab.to_csv(output_file, sep=" ", header=None, index=None)


def build_decomposed_bigram_dictionary(input_filename: str, output_file: str):
    bigrams = pd.read_csv(input_filename, sep=" ", names=["term1", "term2", "count"])
    bigrams.term1 = bigrams.term1.map(split_syllables)
    bigrams.term2 = bigrams.term2.map(split_syllables)
    bigrams.to_csv(output_file, sep=" ", header=None, index=None)
