#!/usr/bin/python3
from difflib import SequenceMatcher
import argparse
import re
import ntpath

class DocumentExceptionGroup:
    'Keeps track of exceptions matched to doc id'
    def __init__(self, id):
        self.id = id
        self.exceptions = []

class Exception:
    'Keeps track of exceptions matched to doc id'
    def __init__(self, message):
        self.message = message
        self.isMatched = False

def splitLogMessages(_log):
    date_regex = re.compile(
        r'^\d+/\d+/\d+\s\d+:\d+:\d+\s*(?:AM|PM)\s*\n', re.M)
    return re.split(date_regex, _log)


def splitValidation(validation):
    newline_regex = re.compile(
        r'\n', re.M)
    return list(filter(None, list(set(re.split(newline_regex, validation)))))


def readFile(path):
    _file = open(path, encoding='utf8')
    _str = _file.read()
    _file.close()
    return _str

def matchLogs(exceptionStrings, validationTokens):
    documentExceptionGroups = []
    for validationToken in validationTokens:
        documentExceptionGroups.append(DocumentExceptionGroup(validationToken))
    exceptions = []
    for exceptionString in exceptionStrings:
        exceptions.append(Exception(exceptionString))

    for exception in exceptions:
        for documentExceptionGroup in documentExceptionGroups:
            if str(documentExceptionGroup.id) in exception.message:
                documentExceptionGroup.exceptions.append(exception)
                exception.isMatched = True
                break

    return (documentExceptionGroups, exceptions)

def similar(strA, strB):
    return SequenceMatcher(None, strA, strB).ratio()

def groupTokens(_tokens):
    _tokenGroups = [[_tokens[0]]]
    _isMatched = False
    for _token in _tokens[1:_tokens.__len__()]:
        for _tokenGroup in _tokenGroups:
            if similar(_tokenGroup[0], _token) > MATCH_RATIO:
                _tokenGroup.append(_token)
                _isMatched = True
                break
        if not _isMatched:
            _tokenGroups.append([_token])
        _isMatched = False

    return _tokenGroups

def writeDocumentExceptionGroups(_reportFile, documentExceptionGroups):
    count = 0
    for documentExceptionGroup in __documentExceptionGroups__:
        if documentExceptionGroup.exceptions.__len__() > 0:
            _reportFile.write('-----------------------------------------------\n')  
            _reportFile.write(__seperator__.join([str(count), ')\nId: ', str(documentExceptionGroup.id),
                                            '\n\n']))
            for exception in documentExceptionGroup.exceptions:
                _reportFile.write(__seperator__.join([exception.message, '\n']))
            _reportFile.write('\n\n')                                
            count += 1

def writeUnmatchedValidatorLogExceptions(_reportFile, _documentExceptionGroups):
    _reportFile.write('\n**********************************************************************************************************\n')
    _reportFile.write('\n\n\nUnmatched validator log exceptions!:\n')
    for _documentExceptionGroup in _documentExceptionGroups:
        if _documentExceptionGroup.exceptions.__len__() == 0:
            _reportFile.write(__seperator__.join([_documentExceptionGroup.id, '\n']))

def writeUnmatchedQualtraxLogExceptions(_reportFile, _exceptions):
    _reportFile.write('\n**********************************************************************************************************\n')
    _reportFile.write('\n\n\nUnmatched qualtrax log exceptions!:\n')
    exceptionMessages = []
    for _exception in _exceptions:
        if not _exception.isMatched:
            exceptionMessages.append(_exception.message)
    _tokenGroups = groupTokens(exceptionMessages)
    writeGroups(_reportFile, _tokenGroups)

def writeGroups(_reportFile, _tokenGroups):
    _count = 0
    for _tokenGroup in _tokenGroups:
        _reportFile.write(__seperator__.join([str(_count), ')\nCount: ', str(_tokenGroup.__len__()),
                                        '\n\n',
                                        _tokenGroup[0],
                                        '\n\n+++++++++++++++++++++++++++++++++++++++++++++++++++++\n']))
        _count += 1

def pathLeaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


REPORT_FILE_NAME_PREFIX = 'Report'
MATCH_RATIO = .95

__parser__ = argparse.ArgumentParser()
__parser__.add_argument("logFilePath", type=str, help="Path to qualtrax log file")
__parser__.add_argument("validationFilePath", type=str,
                        help="Path to file of new-line seperated file ids")
__parser__.add_argument("reportPath",
                        type=str,
                        help="The location the report will be created",
                        default=".\\",
                        nargs="?")

__args__ = __parser__.parse_args()
__log__ = readFile(__args__.logFilePath)
__validation__ = readFile(__args__.validationFilePath)
__logTokens__ = splitLogMessages(__log__)
__validationTokens__ = splitValidation(__validation__)
(__documentExceptionGroups__, __exceptions__) = matchLogs(__logTokens__, __validationTokens__)
__reportFileName__ = __args__.reportPath + REPORT_FILE_NAME_PREFIX + '-' + \
    pathLeaf(__args__.logFilePath) + '-' + pathLeaf(__args__.validationFilePath)
__reportFile__ = open(__reportFileName__, mode='w', encoding='utf8')
__seperator__ = ''

writeDocumentExceptionGroups(__reportFile__, __documentExceptionGroups__)

writeUnmatchedValidatorLogExceptions(__reportFile__, __documentExceptionGroups__)

writeUnmatchedQualtraxLogExceptions(__reportFile__, __exceptions__)

__reportFile__.close
