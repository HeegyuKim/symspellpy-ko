__all__ = ["KoSymSpell"]

from re import I
import pkg_resources
import string
import unicodedata
from itertools import cycle
import math

from symspellpy import SymSpell, Verbosity
from symspellpy.symspellpy import SuggestItem, Composition
from symspellpy_ko.unicode import split_syllables, join_jamos


def get_resource(name):
    resource_package = __name__
    resource_path = "/".join(("res", name))
    filename = pkg_resources.resource_filename(resource_package, resource_path)
    return filename


class KoSymSpell(SymSpell):

    _decompose_korean = False

    def __init__(
        self, max_dictionary_edit_distance=2, prefix_length=7, count_threshold=1
    ):
        super().__init__(
            max_dictionary_edit_distance=max_dictionary_edit_distance,
            prefix_length=prefix_length,
            count_threshold=count_threshold,
        )

    def load_korean_dictionary(
        self, decompose_korean=True, load_bigrams=False, encoding="utf-8"
    ):
        self._decompose_korean = decompose_korean

        if decompose_korean:
            dict_path = "ko_50k_d.txt"
            bigram_path = "ko_bigrams_1M_d.txt"
        else:
            dict_path = "ko_50k.txt"
            bigram_path = "ko_bigrams_1M.txt"

        dict_path = get_resource(dict_path)
        bigram_path = get_resource(bigram_path)

        self.load_dictionary(dict_path, term_index=0, count_index=1, encoding=encoding)
        if load_bigrams:
            self.load_bigram_dictionary(
                bigram_path, term_index=0, count_index=2, encoding=encoding
            )

    def lookup(
        self,
        phrase,
        verbosity,
        max_edit_distance=None,
        include_unknown=False,
        ignore_token=None,
        transfer_casing=False,
    ):
        """Find suggested spellings for a given phrase word.

        한글 자소분해된 사전을 로드했을 경우 자소분해해주는 기능까지 추가함
        Parameters
        ----------
        phrase : str
            The word being spell checked.
        verbosity : :class:`Verbosity`
            The value controlling the quantity/closeness of the
            returned suggestions.
        max_edit_distance : int, optional
            The maximum edit distance between phrase and suggested
            words. Set to :attr:`_max_dictionary_edit_distance` by
            default
        include_unknown : bool, optional
            A flag to determine whether to include phrase word in
            suggestions, if no words within edit distance found.
        ignore_token : regex pattern, optional
            A regex pattern describing what words/phrases to ignore and
            leave unchanged
        transfer_casing : bool, optional
            A flag to determine whether the casing --- i.e., uppercase
            vs lowercase --- should be carried over from `phrase`.
        Returns
        -------
        suggestions : list
            suggestions is a list of :class:`SuggestItem` objects
            representing suggested correct spellings for the phrase
            word, sorted by edit distance, and secondarily by count
            frequency.
        Raises
        ------
        ValueError
            If `max_edit_distance` is greater than
            :attr:`_max_dictionary_edit_distance`
        """
        if self._decompose_korean:
            phrase = split_syllables(phrase)

        result = super().lookup(
            phrase,
            verbosity,
            max_edit_distance=max_edit_distance,
            include_unknown=include_unknown,
            ignore_token=ignore_token,
            transfer_casing=transfer_casing,
        )

        if self._decompose_korean:
            return [
                SuggestItem(join_jamos(sugg.term), sugg.distance, sugg.count)
                for sugg in result
            ]
        else:
            return result

    def lookup_compound(
        self,
        phrase,
        max_edit_distance,
        ignore_non_words=False,
        transfer_casing=False,
        split_phrase_by_space=False,
        ignore_term_with_digits=False,
    ):
        """`lookup_compound` supports compound aware automatic spelling
        correction of multi-word input strings with three cases:
        1. mistakenly inserted space into a correct word led to two
           incorrect terms
        2. mistakenly omitted space between two correct words led to
           one incorrect combined term
        3. multiple independent input terms with/without spelling
           errors
        Find suggested spellings for a multi-word input string
        (supports word splitting/merging).

        한글 자소분해된 사전을 로드했을 경우 자소분해해주는 기능까지 추가함

        Parameters
        ----------
        phrase : str
            The string being spell checked.
        max_edit_distance : int
            The maximum edit distance between input and suggested
            words.
        ignore_non_words : bool, optional
            A flag to determine whether numbers and acronyms are left
            alone during the spell checking process
        transfer_casing : bool, optional
            A flag to determine whether the casing --- i.e., uppercase
            vs lowercase --- should be carried over from `phrase`.
        split_by_space: bool, optional
            Splits the phrase into words simply based on space
        ignore_any_term_with_digits: bool, optional
            A flag to determine whether any term with digits
            is left alone during the spell checking process
        Returns
        -------
        suggestions_line : list
            suggestions_line is a list of :class:`SuggestItem` objects
            representing suggested correct spellings for `phrase`.
        """
        if self._decompose_korean:
            phrase = split_syllables(phrase)

        result = super().lookup_compound(
            phrase,
            max_edit_distance,
            ignore_non_words=ignore_non_words,
            transfer_casing=transfer_casing,
            split_phrase_by_space=split_phrase_by_space,
            ignore_term_with_digits=ignore_term_with_digits,
        )

        if self._decompose_korean:
            return [
                SuggestItem(join_jamos(sugg.term), sugg.distance, sugg.count)
                for sugg in result
            ]
        else:
            return result

    def word_segmentation(
        self,
        phrase,
        max_edit_distance=None,
        max_segmentation_word_length=None,
        ignore_token=None,
    ):
        """`word_segmentation` divides a string into words by inserting
        missing spaces at the appropriate positions misspelled words
        are corrected and do not affect segmentation existing spaces
        are allowed and considered for optimum segmentation
        `word_segmentation` uses a novel approach *without* recursion.
        https://medium.com/@wolfgarbe/fast-word-segmentation-for-noisy-text-2c2c41f9e8da
        While each string of length n can be segmented in 2^n−1
        possible compositions
        https://en.wikipedia.org/wiki/Composition_(combinatorics)
        `word_segmentation` has a linear runtime O(n) to find the optimum
        composition
        Find suggested spellings for a multi-word input string
        (supports word splitting/merging).

        자소분해한 한글을 합쳐버리기 때문에 원본 코드를 가져와서 수정함
        원본: https://github.com/mammothb/symspellpy/blob/e7a91a88f45dc4051b28b83e990fe072cabf0595/symspellpy/symspellpy.py#L946

        Parameters
        ----------
        phrase : str
            The string being spell checked.
        max_segmentation_word_length : int
            The maximum word length that should be considered.
        max_edit_distance : int, optional
            The maximum edit distance between input and corrected words
            (0=no correction/segmentation only).
        ignore_token : regex pattern, optional
            A regex pattern describing what words/phrases to ignore and
            leave unchanged
        Returns
        -------
        compositions[idx] :class:`Composition`
            The word segmented string, the word segmented and spelling
            corrected string, the edit distance sum between input
            string and corrected string, the sum of word occurence
            probabilities in log scale (a measure of how common and
            probable the corrected segmentation is).
        """

        # normalize ligatures: scientiﬁc -> scientific
        # 이 부분에서 한글 자소분해를 한게 합쳐져버려서 원본 코드를 가져와서 분해하게했음.
        phrase = unicodedata.normalize("NFKC", phrase).replace("\u002D", "")
        if self._decompose_korean:
            phrase = split_syllables(phrase)

        if max_edit_distance is None:
            max_edit_distance = self._max_dictionary_edit_distance
        if max_segmentation_word_length is None:
            max_segmentation_word_length = self._max_length
        array_size = min(max_segmentation_word_length, len(phrase))
        compositions = [Composition()] * array_size
        circular_index = cycle(range(array_size))
        idx = -1

        # outer loop (column): all possible part start positions
        for j in range(len(phrase)):
            # inner loop (row): all possible part lengths (from start
            # position): part can't be bigger than longest word in
            # dictionary (other than long unknown word)
            imax = min(len(phrase) - j, max_segmentation_word_length)
            for i in range(1, imax + 1):
                # get top spelling correction/ed for part
                part = phrase[j : j + i]
                separator_len = 0
                top_ed = 0
                top_log_prob = 0.0
                top_result = ""

                if part[0].isspace():
                    # remove space for levensthein calculation
                    part = part[1:]
                else:
                    # add ed+1: space did not exist, had to be inserted
                    separator_len = 1

                # remove space from part1, add number of removed spaces
                # to top_ed
                top_ed += len(part)
                # remove space.
                # add number of removed spaces to ed
                part = part.replace(" ", "")
                top_ed -= len(part)

                # v6.7: Lookup against the lowercase term
                results = self.lookup(
                    part.lower(),
                    Verbosity.TOP,
                    max_edit_distance,
                    ignore_token=ignore_token,
                )
                if results:
                    top_result = results[0].term
                    # v6.7: retain/preserve upper case
                    if len(part) > 0 and part[0].isupper():
                        top_result = top_result.capitalize()

                    top_ed += results[0].distance
                    # Naive Bayes Rule. We assume the word
                    # probabilities of two words to be independent.
                    # Therefore the resulting probability of the word
                    # combination is the product of the two word
                    # probabilities. Instead of computing the product
                    # of probabilities we are computing the sum of the
                    # logarithm of probabilities because the
                    # probabilities of words are about 10^-10, the
                    # product of many such small numbers could exceed
                    # (underflow) the floating number range and become
                    # zero. log(ab)=log(a)+log(b)
                    top_log_prob = math.log10(float(results[0].count) / float(self.N))
                else:
                    top_result = part
                    # default, if word not found. otherwise long input
                    # text would win as long unknown word (with
                    # ed=edmax+1), although there there should many
                    # spaces inserted
                    top_ed += len(part)
                    top_log_prob = math.log10(10.0 / self.N / math.pow(10.0, len(part)))

                dest = (i + idx) % array_size
                # set values in first loop
                if j == 0:
                    compositions[dest] = Composition(
                        part, top_result, top_ed, top_log_prob
                    )
                # pylint: disable=C0301,R0916
                elif (
                    i == max_segmentation_word_length
                    # replace values if better log_prob_sum, if same
                    # edit distance OR one space difference
                    or (
                        (
                            compositions[idx].distance_sum + top_ed
                            == compositions[dest].distance_sum
                            or compositions[idx].distance_sum + separator_len + top_ed
                            == compositions[dest].distance_sum
                        )
                        and compositions[dest].log_prob_sum
                        < compositions[idx].log_prob_sum + top_log_prob
                    )
                    # replace values if smaller edit distance
                    or compositions[idx].distance_sum + separator_len + top_ed
                    < compositions[dest].distance_sum
                ):
                    if (
                        len(top_result) == 1 and top_result[0] in string.punctuation
                    ) or (len(top_result) == 2 and top_result.startswith("'")):
                        compositions[dest] = Composition(
                            compositions[idx].segmented_string + part,
                            compositions[idx].corrected_string + top_result,
                            compositions[idx].distance_sum + top_ed,
                            compositions[idx].log_prob_sum + top_log_prob,
                        )
                    else:
                        compositions[dest] = Composition(
                            compositions[idx].segmented_string + " " + part,
                            (compositions[idx].corrected_string + " " + top_result),
                            (compositions[idx].distance_sum + separator_len + top_ed),
                            compositions[idx].log_prob_sum + top_log_prob,
                        )
            idx = next(circular_index)

        result = compositions[idx]

        if self._decompose_korean:
            return Composition(
                result.segmented_string,
                join_jamos(result.corrected_string),
                result.distance_sum,
                result.log_prob_sum,
            )
        else:
            return result
