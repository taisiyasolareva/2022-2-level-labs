"""
Lab 4
Summarize text using TextRank algorithm
"""
from typing import Union
import re

from lab_3_keywords_textrank.main import TextEncoder, \
    TextPreprocessor

PreprocessedSentence = tuple[str, ...]
EncodedSentence = tuple[int, ...]


class Sentence:
    """
    An abstraction over the real-world sentences
    """

    def __init__(self, text: str, position: int) -> None:
        """
        Constructs all the necessary attributes
        """
        if not isinstance(text, str):
            raise ValueError
        if not isinstance(position, int) or isinstance(position, bool):
            raise ValueError
        self._text = text
        self._position = position
        self._preprocessed = ()
        self._encoded = ()

    def get_position(self) -> int:
        """
        Returns the attribute
        :return: the position of the sentence in the text
        """
        return self._position

    def set_text(self, text: str) -> None:
        """
        Sets the attribute
        :param text: the text
        :return: None
        """
        if not isinstance(text, str):
            raise ValueError
        self._text = text

    def get_text(self) -> str:
        """
        Returns the attribute
        :return: the text
        """
        return self._text

    def set_preprocessed(self, preprocessed_sentence: PreprocessedSentence) -> None:
        """
        Sets the attribute
        :param preprocessed_sentence: the preprocessed sentence (a sequence of tokens)
        :return: None
        """
        if not isinstance(preprocessed_sentence, tuple):
            raise ValueError
        for token in preprocessed_sentence:
            if not isinstance(token, str):
                raise ValueError
        self._preprocessed = preprocessed_sentence

    def get_preprocessed(self) -> PreprocessedSentence:
        """
        Returns the attribute
        :return: the preprocessed sentence (a sequence of tokens)
        """
        return self._preprocessed

    def set_encoded(self, encoded_sentence: EncodedSentence) -> None:
        """
        Sets the attribute
        :param encoded_sentence: the encoded sentence (a sequence of numbers)
        :return: None
        """
        if not isinstance(encoded_sentence, tuple):
            raise ValueError
        for number in encoded_sentence:
            if not isinstance(number, int):
                raise ValueError
        self._encoded = encoded_sentence

    def get_encoded(self) -> EncodedSentence:
        """
        Returns the attribute
        :return: the encoded sentence (a sequence of numbers)
        """
        return self._encoded


class SentencePreprocessor(TextPreprocessor):
    """
    Class for sentence preprocessing
    """

    def __init__(self, stop_words: tuple[str, ...], punctuation: tuple[str, ...]) -> None:
        """
        Constructs all the necessary attributes
        """
        super().__init__(stop_words, punctuation)
        # The super() function is used to give access to methods and properties of a parent or sibling class.
        # The super() function returns an object that represents the parent class.
        if not isinstance(stop_words, tuple) or not isinstance(punctuation, tuple):
            raise ValueError
        for word in stop_words:
            if not isinstance(word, str):
                raise ValueError
        for symbol in punctuation:
            if not isinstance(symbol, str):
                raise ValueError


    def _split_by_sentence(self, text: str) -> tuple[Sentence, ...]:
        """
        Splits the provided text by sentence
        :param text: the raw text
        :return: a sequence of sentences
        """
        if not isinstance(text, str):
            raise ValueError
        text = text.replace('\n', ' ').replace("  ", " ")
        text_list = re.split(r'(?<=[.!?])[\s\n]+', text)
        # splits into sentences
        split_sentences_list = []
        for index, sentence in enumerate(text_list):
            # sentence = sentence.lower().split()
            split_sentences_list.append(Sentence(str(sentence), index))
        return tuple(split_sentences_list)


    def _preprocess_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Enriches the instances of sentences with their preprocessed versions
        :param sentences: a list of sentences
        :return:
        """
        if not isinstance(sentences, tuple):
            raise ValueError
        for sentence in sentences:
            if not isinstance(sentence, Sentence):
                raise ValueError
        for sentence in sentences:
            text = sentence.get_text()
            preprocessing = TextPreprocessor.preprocess_text(self, text)
            sentence.set_preprocessed(preprocessing)

    def get_sentences(self, text: str) -> tuple[Sentence, ...]:
        """
        Extracts the sentences from the given text & preprocesses them
        :param text: the raw text
        :return:
        """
        if not isinstance(text, str):
            raise ValueError
        sentences = self._split_by_sentence(text)
        self._preprocess_sentences(sentences)
        return tuple(sentences)

class SentenceEncoder(TextEncoder):
    """
    A class to encode string sequence into matching integer sequence
    """

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes
        """
        super().__init__()
        self._last_index = 1000

    def _learn_indices(self, tokens: tuple[str, ...]) -> None:
        """
        Fills attributes mapping words and integer equivalents to each other
        :param tokens: a sequence of string tokens
        :return:
        """
        if not isinstance(tokens, tuple):
            raise ValueError
        for token in tokens:
            if not isinstance(token, str):
                raise ValueError
        new_tokens = (token for token in tokens if token not in self._word2id)
        for index, token in enumerate(new_tokens, 1000 + len(self._word2id)):
            self._word2id[token] = index
            self._id2word[index] = token

    def encode_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Enriches the instances of sentences with their encoded versions
        :param sentences: a sequence of sentences
        :return: a list of sentences with their preprocessed versions
        """
        if not isinstance(sentences, tuple):
            raise ValueError
        for sentence in sentences:
            if not isinstance(sentence, Sentence):
                raise ValueError
        for sentence in sentences:
            self._learn_indices(sentence.get_preprocessed())
            sentence.set_encoded(tuple(self._word2id[word] for word in sentence.get_preprocessed()))


def calculate_similarity(sequence: Union[list, tuple], other_sequence: Union[list, tuple]) -> float:
    """
    Calculates similarity between two sequences using Jaccard index
    :param sequence: a sequence of items
    :param other_sequence: a sequence of items
    :return: similarity score
    """
    if not isinstance(sequence, (list, tuple)) or not isinstance(other_sequence, (list, tuple)):
        raise ValueError
    if not sequence or not other_sequence:
        return 0
    set1 = set(sequence)
    set2 = set(other_sequence)
    joining = set1.intersection(set2)
    # пересечение
    return float(len(joining)) / (len(set1) + len(set2) - len(joining))


class SimilarityMatrix:
    """
    A class to represent relations between sentences
    """

    _matrix: list[list[float]]

    def __init__(self) -> None:
        """
        Constructs necessary attributes
        """
        self._matrix = []
        self._vertices = []

    def get_vertices(self) -> tuple[Sentence, ...]:
        """
        Returns a sequence of all vertices present in the graph
        :return: a sequence of vertices
        """
        return tuple(self._vertices)

    def calculate_inout_score(self, vertex: Sentence) -> int:
        """
        Retrieves a number of vertices that are similar (i.e. have similarity score > 0) to the input one
        :param vertex
        :return:
        """
        if vertex not in self._vertices:
            raise ValueError
        if not isinstance(vertex, Sentence):
            raise ValueError
        summarization = 0
        for index in self._matrix[self._vertices.index(vertex)]:
            if index > 0:
                summarization += 1
        return summarization

    def add_edge(self, vertex1: Sentence, vertex2: Sentence) -> None:
        """
        Adds or overwrites an edge in the graph between the specified vertices
        :param vertex1:
        :param vertex2:
        :return:
        """
        if not isinstance(vertex1, Sentence) or not isinstance(vertex2, Sentence):
            raise ValueError
        if vertex1 == vertex2:
            raise ValueError

        for vertex in vertex1, vertex2:
            if vertex not in self._vertices:
                self._vertices.append(vertex)
                self._matrix.append([])

        for i in self._matrix:
            for _ in self._vertices:
                if len(i) < len(self._vertices):
                    i.append(0)

        idx1 = self._vertices.index(vertex1)
        idx2 = self._vertices.index(vertex2)
        self._matrix[idx1][idx2] = calculate_similarity(vertex1.get_encoded(), vertex2.get_encoded())
        self._matrix[idx2][idx1] = calculate_similarity(vertex1.get_encoded(), vertex2.get_encoded())

    def get_similarity_score(self, sentence: Sentence, other_sentence: Sentence) -> float:
        """
        Gets the similarity score for two sentences from the matrix
        :param sentence
        :param other_sentence
        :return: the similarity score
        """
        if (sentence or other_sentence) not in self._vertices:
            raise ValueError
        index1 = self._vertices.index(sentence)
        index2 = self._vertices.index(other_sentence)
        return self._matrix[index1][index2]

    def fill_from_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Updates graph instance with vertices and edges extracted from sentences
        :param sentences
        :return:
        """
        if not isinstance(sentences, tuple) or not sentences:
            raise ValueError
        for sentence in sentences:
            for other_sentence in sentences:
                if sentence.get_encoded() != other_sentence.get_encoded():
                    self.add_edge(sentence, other_sentence)


class TextRankSummarizer:
    """
    TextRank for summarization
    """

    _scores: dict[Sentence, float]
    _graph: SimilarityMatrix

    def __init__(self, graph: SimilarityMatrix) -> None:
        """
        Constructs all the necessary attributes
        :param graph: the filled instance of the similarity matrix
        """
        self._graph = graph
        self._damping_factor = 0.85
        self._convergence_threshold = 0.0001
        self._max_iter = 50
        self._scores = {}

    def update_vertex_score(
            self, vertex: Sentence, incidental_vertices: list[Sentence], scores: dict[Sentence, float]
    ) -> None:
        """
        Changes vertex significance score using algorithm-specific formula
        :param vertex: a sentence
        :param incidental_vertices: vertices with similarity score > 0 for vertex
        :param scores: current vertices scores
        :return:
        """
        if not isinstance(vertex, Sentence) or not isinstance(incidental_vertices, list) or not isinstance(scores, dict):
            raise ValueError
        summa = sum((1 / self._graph.calculate_inout_score(vertex)) * scores[vertex]
                    for vertex in incidental_vertices)
        self._scores[vertex] = summa * self._damping_factor + (1 - self._damping_factor)

    def train(self) -> None:
        """
        Iteratively computes significance scores for vertices
        """
        vertices = self._graph.get_vertices()
        for vertex in vertices:
            self._scores[vertex] = 1.0

        for iteration in range(self._max_iter):
            prev_score = self._scores.copy()
            for scored_vertex in vertices:
                similar_vertices = [vertex for vertex in vertices
                                    if self._graph.get_similarity_score(scored_vertex, vertex) > 0]
                self.update_vertex_score(scored_vertex, similar_vertices, prev_score)
            abs_score_diff = [abs(i - j) for i, j in zip(prev_score.values(), self._scores.values())]

            if sum(abs_score_diff) <= self._convergence_threshold:  # convergence condition
                print("Converging at iteration " + str(iteration) + "...")
                break

    def get_top_sentences(self, n_sentences: int) -> tuple[Sentence, ...]:
        """
        Retrieves top n most important sentences in the encoded text
        :param n_sentences: number of sentence to retrieve
        :return: a sequence of sentences
        """
        if not isinstance(n_sentences, int) or isinstance(n_sentences, bool):
            raise ValueError
        return tuple(sorted(self._scores, key=lambda token: self._scores[token], reverse=True))[:n_sentences]

    def make_summary(self, n_sentences: int) -> str:
        """
        Constructs summary from the most important sentences
        :param n_sentences: number of sentences to include in the summary
        :return: summary
        """
        if not isinstance(n_sentences, int) or isinstance(n_sentences, bool):
            raise ValueError
        top = sorted(self.get_top_sentences(n_sentences), key=lambda x: x.get_position())
        return '\n'.join([sentence.get_text() for sentence in top])


class Buddy:
    """
    (Almost) All-knowing entity
    """

    def __init__(
            self,
            paths_to_texts: list[str],
            stop_words: tuple[str, ...],
            punctuation: tuple[str, ...],
            idf_values: dict[str, float],
    ):
        """
        Constructs all the necessary attributes
        :param paths_to_texts: paths to the texts from which to learn
        :param stop_words: a sequence of stop words
        :param punctuation: a sequence of punctuation symbols
        :param idf_values: pre-computed IDF values
        """
        pass

    def add_text_to_database(self, path_to_text: str) -> None:
        """
        Adds the given text to the existing database
        :param path_to_text
        :return:
        """
        pass

    def _find_texts_close_to_keywords(self, keywords: tuple[str, ...], n_texts: int) -> tuple[str, ...]:
        """
        Finds texts that are similar (i.e. contain the same keywords) to the given keywords
        :param keywords: a sequence of keywords
        :param n_texts: number of texts to find
        :return: the texts' ids
        """
        pass

    def reply(self, query: str, n_summaries: int = 3) -> str:
        """
        Replies to the query
        :param query: the query
        :param n_summaries: the number of summaries to include in the answer
        :return: the answer
        """
        pass
