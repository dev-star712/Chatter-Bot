"""
This module contains various text-comparison algorithms
designed to compare one statement to another.
"""
from chatterbot import utils
from chatterbot import languages
from chatterbot import tokenizers
from nltk.corpus import wordnet, stopwords
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from difflib import SequenceMatcher
import itertools


class Comparator:

    def __call__(self, statement_a, statement_b):
        return self.compare(statement_a, statement_b)

    def compare(self, statement_a, statement_b):
        return 0


class LevenshteinDistance(Comparator):
    """
    Compare two statements based on the Levenshtein distance
    of each statement's text.

    For example, there is a 65% similarity between the statements
    "where is the post office?" and "looking for the post office"
    based on the Levenshtein distance algorithm.
    """

    def compare(self, statement_a, statement_b):
        """
        Compare the two input statements.

        :return: The percent of similarity between the text of the statements.
        :rtype: float
        """

        # Return 0 if either statement has a falsy text value
        if not statement_a.text or not statement_b.text:
            return 0

        # Get the lowercase version of both strings
        statement_a_text = str(statement_a.text.lower())
        statement_b_text = str(statement_b.text.lower())

        similarity = SequenceMatcher(
            None,
            statement_a_text,
            statement_b_text
        )

        # Calculate a decimal percent of the similarity
        percent = round(similarity.ratio(), 2)

        return percent


class SynsetDistance(Comparator):
    """
    Calculate the similarity of two statements.
    This is based on the total maximum synset similarity between each word in each sentence.

    This algorithm uses the `wordnet`_ functionality of `NLTK`_ to determine the similarity
    of two statements based on the path similarity between each token of each statement.
    This is essentially an evaluation of the closeness of synonyms.
    """

    def __init__(self):
        super().__init__()

        self.language = languages.ENG

        self.stopwords = None

        self.word_tokenizer = None

        self.initialization_functions = [
            utils.download_nltk_wordnet,
            utils.download_nltk_stopwords
        ]

    def get_stopwords(self):
        """
        Get the list of stopwords from the NLTK corpus.
        """
        if self.stopwords is None:
            self.stopwords = stopwords.words(self.language.ENGLISH_NAME.lower())

        return self.stopwords

    def get_word_tokenizer(self):
        """
        Get the word tokenizer for this comparison algorithm.
        """
        if self.word_tokenizer is None:
            self.word_tokenizer = tokenizers.get_word_tokenizer(self.language)

        return self.word_tokenizer

    def compare(self, statement_a, statement_b):
        """
        Compare the two input statements.

        :return: The percent of similarity between the closest synset distance.
        :rtype: float

        .. _wordnet: http://www.nltk.org/howto/wordnet.html
        .. _NLTK: http://www.nltk.org/
        """
        word_tokenizer = self.get_word_tokenizer()

        tokens1 = word_tokenizer.tokenize(statement_a.text.lower())
        tokens2 = word_tokenizer.tokenize(statement_b.text.lower())

        # Get the stopwords for the current language
        stop_word_set = set(self.get_stopwords())

        # Remove all stop words from the list of word tokens
        tokens1 = set(tokens1) - stop_word_set
        tokens2 = set(tokens2) - stop_word_set

        # The maximum possible similarity is an exact match
        # Because path_similarity returns a value between 0 and 1,
        # max_possible_similarity is the number of words in the longer
        # of the two input statements.
        max_possible_similarity = min(
            len(tokens1),
            len(tokens2)
        ) / max(
            len(tokens1),
            len(tokens2)
        )

        max_similarity = 0.0

        # Get the highest matching value for each possible combination of words
        for combination in itertools.product(*[tokens1, tokens2]):

            synset1 = wordnet.synsets(combination[0])
            synset2 = wordnet.synsets(combination[1])

            if synset1 and synset2:

                # Get the highest similarity for each combination of synsets
                for synset in itertools.product(*[synset1, synset2]):
                    similarity = synset[0].path_similarity(synset[1])

                    if similarity and (similarity > max_similarity):
                        max_similarity = similarity

        if max_possible_similarity == 0:
            return 0

        return max_similarity / max_possible_similarity


class JaccardSimilarity(Comparator):
    """
    Calculates the similarity of two statements based on the Jaccard index.

    The Jaccard index is composed of a numerator and denominator.
    In the numerator, we count the number of items that are shared between the sets.
    In the denominator, we count the total number of items across both sets.
    Let's say we define sentences to be equivalent if 50% or more of their tokens are equivalent.
    Here are two sample sentences:

        The young cat is hungry.
        The cat is very hungry.

    When we parse these sentences to remove stopwords, we end up with the following two sets:

        {young, cat, hungry}
        {cat, very, hungry}

    In our example above, our intersection is {cat, hungry}, which has count of two.
    The union of the sets is {young, cat, very, hungry}, which has a count of four.
    Therefore, our `Jaccard similarity index`_ is two divided by four, or 50%.
    Given our similarity threshold above, we would consider this to be a match.

    .. _`Jaccard similarity index`: https://en.wikipedia.org/wiki/Jaccard_index
    """

    def __init__(self):
        super().__init__()

        import string

        self.punctuation_table = str.maketrans(dict.fromkeys(string.punctuation))

        self.language = languages.ENG

        self.stopwords = None

        self.lemmatizer = None

        self.word_tokenizer = None

        self.initialization_functions = [
            utils.download_nltk_wordnet,
            utils.download_nltk_averaged_perceptron_tagger,
            utils.download_nltk_stopwords
        ]

    def get_stopwords(self):
        """
        Get the list of stopwords from the NLTK corpus.
        """
        if self.stopwords is None:
            self.stopwords = stopwords.words(self.language.ENGLISH_NAME.lower())

        return self.stopwords

    def get_lemmatizer(self):
        """
        Get the lemmatizer.
        """
        if self.lemmatizer is None:
            self.lemmatizer = WordNetLemmatizer()

        return self.lemmatizer

    def get_word_tokenizer(self):
        """
        Get the word tokenizer for this comparison algorithm.
        """
        if self.word_tokenizer is None:
            self.word_tokenizer = tokenizers.get_word_tokenizer(self.language)

        return self.word_tokenizer

    def compare(self, statement_a, statement_b):
        """
        Return the calculated similarity of two
        statements based on the Jaccard index.
        """
        word_tokenizer = self.get_word_tokenizer()

        # Get the stopwords for the current language
        stopwords = self.get_stopwords()

        lemmatizer = self.get_lemmatizer()

        # Make both strings lowercase
        a = statement_a.text.lower()
        b = statement_b.text.lower()

        # Remove punctuation from each string
        a = a.translate(self.punctuation_table)
        b = b.translate(self.punctuation_table)

        pos_a = pos_tag(word_tokenizer.tokenize(a))
        pos_b = pos_tag(word_tokenizer.tokenize(b))

        lemma_a = [
            lemmatizer.lemmatize(
                token, utils.treebank_to_wordnet(pos)
            ) for token, pos in pos_a if token not in stopwords
        ]
        lemma_b = [
            lemmatizer.lemmatize(
                token, utils.treebank_to_wordnet(pos)
            ) for token, pos in pos_b if token not in stopwords
        ]

        # Calculate Jaccard similarity
        numerator = len(set(lemma_a).intersection(lemma_b))
        denominator = float(len(set(lemma_a).union(lemma_b)))
        ratio = numerator / denominator

        return ratio


# ---------------------------------------- #


levenshtein_distance = LevenshteinDistance()
synset_distance = SynsetDistance()
jaccard_similarity = JaccardSimilarity()
