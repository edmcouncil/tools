import re

from rdflib import URIRef


class Symbol:
    def __init__(self, origin):
        self.origin = origin
        if isinstance(origin, URIRef):
            if '#' in str(self.origin):
                self.letter = origin.fragment
            else:
                origin_fragments = str(self.origin).split(sep='/')
                origin_fragments.reverse()
                for index in range(len(origin_fragments)):
                    origin_fragment = origin_fragments[index]
                    if len(origin_fragment) > 0:
                        self.letter = origin_fragment
                        if index + 1 < len(origin_fragments):
                            if len(origin_fragments[index+1]) > 0:
                                self.letter = origin_fragments[index+1] + '-' + self.letter
                        return
        else:
            self.letter = str(origin)
        
    def to_tptp(self):
        pass
    
    @staticmethod
    def escape_tptp_chars(text: str):
        text = text.replace('-', '_')
        text = text.replace('+', '_')
        text = text.replace('.', '_')
        text = text.replace('/', '_')
        text = text.replace('!', '_')
        text = text.replace(':', '_')
        text = text.replace(';', '_')
        text = text.replace('?', '_')
        text = text.replace('=', '_')
        text = text.replace('%', '_')
        text = text.replace('&', '_')
        text = text.replace('$', '_')
        text = text.replace('@', '_')
        text = text.replace('|', '_')
        text = text.replace("'", '_')
        text = text.replace('"', '_')
        text = text.replace(' ', '_')
        text = text.replace('(', '_')
        text = text.replace(')', '_')
        text = text.replace('>', '_')
        text = text.replace('~', '_')
        text = text.replace('#', '_')
        text = text.replace(',', '_')
        text = text.replace('*', '_')
        text = text.replace('^', '_')
        text = text.replace('{', '_')
        text = text.replace('}', '_')
        text = text.replace('[', '_')
        text = text.replace(']', '_')
        text = text.replace('\n', '')
        text = text.replace('\t', '')
        text = re.sub(r'[^\x00-\x7F]+', '_', text)
        if text.startswith('_'):
            text = 's' + text
        
        return text
        
    def __repr__(self):
        return self.letter
    
    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.letter == other.letter
        if isinstance(other, str):
            return self.letter == other
    
    def __hash__(self):
        return self.letter.__hash__()