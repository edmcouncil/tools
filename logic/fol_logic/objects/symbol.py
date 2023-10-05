import re

from rdflib import URIRef


class Symbol:
    def __init__(self, origin_value:object, origin_type=str):
        self.origin = origin_value
        self.origin_type = origin_type
        self.__set_symbol_letter()
        
    def __set_symbol_letter(self):
        if isinstance(self.origin, URIRef):
            uri_parts = self.origin.split(sep='/')
            uri_namespace_parts = uri_parts[3:-1]
            namespace = '-'.join([part[0] for part in uri_namespace_parts])
            if '#' in str(self.origin):
                self.value = namespace + ':' + self.origin.fragment
            else:
                self.value = namespace + ':' + uri_parts[-1]
        else:
            self.value = str(self.origin)

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
        if not text[0].isalpha():
            text = 's' + text
        return text
        
    def __repr__(self):
        return self.value
    
    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        if isinstance(other, Symbol):
            return self.value == other.value and self.origin_type == self.origin_type
    
    def __hash__(self):
        return (str(self.value)+str(self.origin_type)).__hash__()