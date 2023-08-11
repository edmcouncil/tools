import re

from rdflib import URIRef


class Symbol:
    def __init__(self, origin):
        self.origin = origin
        self.__set_symbol_letter()
        
    def __set_symbol_letter(self):
        if isinstance(self.origin, URIRef):
            uri_parts = self.origin.split(sep='/')
            uri_namespace_parts = uri_parts[3:-1]
            namespace = '-'.join([part[0] for part in uri_namespace_parts])
            if '#' in str(self.origin):
                self.letter = namespace + ':' + self.origin.fragment
            else:
                self.letter = namespace + ':' + uri_parts[-1]
        else:
            self.letter = str(self.origin)

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