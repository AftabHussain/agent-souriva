# This module defines a common input/output format for model backends and a
# small offline backend used when no model server is needed.
# It uses only Python standard-library features.
#
# dataclass: a decorator that generates methods such as __init__() and __repr__()
# from declared fields, avoiding the need of boilerplate constructors.
from dataclasses import dataclass
# Protocol: declares a structural interface (a required set of methods).
# Sequence: a type hint for an ordered collection that supports indexing,
# e.g., a list or tuple. A Sequence need not be mutable.
from typing import Protocol, Sequence


# @decorator syntax applies a function/class decorator to the class below.
# frozen=True prevents normal reassignment of dataclass fields after creation.
# These fields are all strings or a float, so Evidence instances act as
# immutable records. (In general, frozen does not freeze nested mutable data.)
@dataclass(frozen=True)
# A class groups named fields and behavior. Here it represents one retrieved
# evidence item that may be supplied to an answer-generating model.
class Evidence:
    # Field declarations use name: type annotations. The annotations help
    # type checkers and dataclass generation; they do not by themselves
    # validate values when an instance is created.
    
    # text: passage content; id: identifier used for citations.
    text: str
    id: str
    
    # source and location: metadata describing where the passage came from.
    source: str
    location: str
    
    # score: numeric retrieval/relevance score (not used by MockModel below).
    score: float


# Another frozen dataclass for a model's returned answer and citations.
# Generated __init__ lets callers write ModelReply("answer", ("chunk-1",)).
@dataclass(frozen=True)
class ModelReply:
    # Main answer text. There is no default, so callers must supply it.
    text: str
    
    # tuple[str, ...] means a tuple of zero or more strings; the ellipsis
    # INSIDE the brackets expresses variable tuple length.
    # = () supplies an empty-tuple default when no citations are available.
    # This ... is different from the standalone ... in the Protocol below.
    citation_ids: tuple[str, ...] = ()


# A Protocol specifies the shape of acceptable backend objects.
# It is for *structural typing*: a separate class can satisfy this protocol
# by implementing a compatible answer() method, without inheriting from it.
# Static type checkers can verify compatibility; Protocol alone does not
# automatically enforce argument/return types at runtime.
class ModelAdapter(Protocol):
    """Boundary implemented by local mocks and production model servers."""

    # Method contract:
    #   self     : the instance on which answer() is called (implicit argument).
    #   question : user question, expected to be a string.
    #   evidence : any Sequence containing Evidence objects.
    #   -> ModelReply : expected return type (a return annotation).
    # Standalone ... is the Ellipsis object used as a placeholder body:
    # the protocol specifies WHAT a backend exposes, not HOW it answers.
    # Sequence[Evidence] accepts ordered collections such as lists
    # and tuples. Since this method only reads the evidence,
    # it does not need to require a mutable list.
    def answer(self, question: str, evidence: Sequence[Evidence]) -> ModelReply: ...


# MockModel is a concrete backend intended for testing and offline usage.
# It does not inherit from ModelAdapter but satisfies its method contract
# structurally by providing answer(question, evidence) -> ModelReply.
# "Deterministic" means identical inputs lead to identical outputs here;
# it does not call a language model or generate a new answer.
class MockModel:
    """Deterministic extractive backend for offline development and tests."""

    # The signature matches the Protocol's answer() requirement.
    # This is an instance method: Python supplies self when called on a
    # MockModel instance, e.g., MockModel().answer(question, evidence).
    def answer(self, question: str, evidence: Sequence[Evidence]) -> ModelReply:
        # The mock does not use the question to construct its answer.
        # del removes the local name 'question'; it does NOT delete or modify
        # the caller's string. It makes that deliberate non-use explicit.
        del question
        # An empty Sequence is falsy. This branch handles the no-evidence
        # case before trying to select passages.
        if not evidence:
            # Only the text argument is passed; citation_ids falls back to
            # the default empty tuple (). The reply therefore has no citations.
            return ModelReply("I do not have enough evidence to answer.")

        # Slice syntax [start:stop] returns entries up to but excluding stop.
        # [:2] means the first two items (or fewer if only one is available).
        # Evidence is already ordered by the caller; no ranking occurs here.
        selected = evidence[:2]
        # List comprehension: build a list by evaluating the expression
        # once for each item in selected.
        # Equivalent to a loop that appends self._first_sentence(item.text).
        # self._first_sentence(...) calls the helper defined later in this class.
        statements = [self._first_sentence(item.text) for item in selected]
        # Generator expression: (item.id for item in selected) yields each ID.
        # tuple(...) consumes those IDs into an immutable tuple, matching
        # ModelReply.citation_ids. Parentheses here are for the generator.
        citations = tuple(item.id for item in selected)
        # " ".join(iterable) combines strings separated by one space.
        # The multi-line parentheses allow the expression to span lines.
        rendered = " ".join(
            # zip(statements, citations) pairs elements by position:
            # e.g., ("Sentence A.", "id-1"), ("Sentence B.", "id-2").
            # zip stops at the shorter input; both lists have equal length here.
            # The f-string inserts each statement and citation ID, producing
            # something like "Sentence A. [id-1]". This is a generator
            # expression, so strings are produced as join() iterates.
            f"{statement} [{citation}]" for statement, citation in zip(statements, citations)
        )
        # Positional constructor arguments map to ModelReply's dataclass
        # fields in order: text=rendered, citation_ids=citations.
        return ModelReply(rendered, citations)

    # @staticmethod makes this helper callable without an instance.
    # It accepts only 'text' (no self or cls parameter), because it needs
    # no instance state. The leading underscore in _first_sentence is a
    # Python convention meaning "internal use", not enforced privacy.
    @staticmethod
    # -> str indicates that the helper is expected to return a string.
    def _first_sentence(text: str) -> str:

        line = " ".join(text.split())
        stop = line.find(". ")
        return line if stop < 0 else line[: stop + 1]

