from enum import Enum
from typing import Tuple, List
from collections.abc import Callable
import re
from natasha import (
        Segmenter,
        MorphVocab,
        PER,
        NamesExtractor,
        NewsNERTagger,
        NewsEmbedding,
        Doc,
        LOC,
    )

class FillType(Enum):
    TOKEN = 'TOKEN'
    BIK = 'BIK'
    INN = 'INN'
    KPP = 'KPP'
    CORESPONDENT_ACCOUNT = 'CORESPONDENT_ACCOUNT'
    MAIL = 'MAIL'
    PHONE_NUMBER = 'PHONE_NUMBER'
    NAME = 'NAME'
    BIRTHDAY_DAY = 'BIRTHDAY_DAY'
    QUESTION = 'QUESTION'
    BANK = 'BANK'
    RASCHET_ACCOUNT = 'RASCHET_ACCOUNT'
    ADDRESS = "ADDRESS"

def is_mail(string: str) -> Tuple[bool, FillType]:
    result = '@' in string
    return result, FillType.MAIL


def is_phone_number(string: str) -> Tuple[bool, FillType]:
    regex = re.compile(r'\+?[78][\+()\s0-9]+')
    if re.fullmatch(regex, string):
        result = True
    else: 
        result = False
    return result, FillType.PHONE_NUMBER

def is_name(string: str) -> Tuple[bool, FillType]:
    regex = re.compile(r'\s*[A-ZА-ЯЁ][a-zа-яё]+\s+[A-ZА-ЯЁ][a-zа-яё]+\s*[A-ZА-ЯЁ]?[a-zа-яё]*\s*')
    if not re.fullmatch(regex, string):
        return False, FillType.NAME

    emb = NewsEmbedding()
    segmenter = Segmenter()
    morph_vocab = MorphVocab()
    ner_tagger = NewsNERTagger(emb)

    doc = Doc(string)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    for span in doc.spans:
        span.normalize(morph_vocab)

    for span in doc.spans:
        if span.type == PER:
            return True, FillType.NAME

    return False, FillType.NAME

def is_address(string: str) -> Tuple[bool, FillType]:
    #regex = re.compile(r'\s*[A-ZА-ЯЁ][a-zа-яё]+\s+[A-ZА-ЯЁ][a-zа-яё]+\s*[A-ZА-ЯЁ]?[a-zа-яё]*\s*')
    #if not re.fullmatch(regex, string):
       # return False, FillType.NAME

    emb = NewsEmbedding()
    segmenter = Segmenter()
    morph_vocab = MorphVocab()
    ner_tagger = NewsNERTagger(emb)

    doc = Doc(string)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    for span in doc.spans:
        span.normalize(morph_vocab)

    for span in doc.spans:
        if span.type == LOC:
            return True, FillType.ADDRESS

    return False, FillType.ADDRESS

def is_birthday(string: str) -> Tuple[bool, FillType]:
    regex = re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$')
    if re.fullmatch(regex, string):
        result = True
    else: 
        result = False
    return result, FillType.BIRTHDAY_DAY


def is_bik(string: str) -> Tuple[bool, FillType]:
    result = string[:2] == '04' and len(string) == 9
    return result, FillType.BIK


def is_inn(string: str) -> Tuple[bool, FillType]:
    result = len(string) <= 12 and len(string) > 8
    try:
        a = int(string)
    except:
        result = False
    return result, FillType.INN


def is_token(string: str) -> Tuple[bool, FillType]:
    result = len(string) == 40
    return result, FillType.TOKEN


def is_kpp(string: str) -> Tuple[bool, FillType]:
    result = len(string) == 9
    return result, FillType.KPP


def is_correspondent_account(string: str) -> Tuple[bool, FillType]:
    result = len(string) == 20 and \
             string[:3] == '301'
    return result, FillType.CORESPONDENT_ACCOUNT

def is_raschet_account(string: str) -> Tuple[bool, FillType]:
    result = (len(string) == 20)
    return result, FillType.RASCHET_ACCOUNT


def is_bank(string: str) -> Tuple[bool, FillType]:
    result = 'банк' in string.lower() or "бэнк" in string.lower()
    return result, FillType.BANK


def detect_type(string: str) -> FillType:
    checkers: List[Callable[str, Tuple[bool, FillType]]] = [
        is_bank,
        is_bik,
        is_kpp,
        is_phone_number,
        is_inn,
        is_token,
        is_correspondent_account,
        is_mail,
        is_name,
        is_birthday,
        is_raschet_account,
        is_address,
    ]
    for checker in checkers:
        is_type, _type = checker(string)
        if is_type:
            return _type
    return FillType.QUESTION


