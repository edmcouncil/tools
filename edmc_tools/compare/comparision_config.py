class ComparisionConfig:
    def __init__(self, show_common=False, verbose=False, strict=True):
        self.show_common = show_common
        self.verbose = verbose
        self.strict = strict
        self.default_ontology_file_extension = '.rdf'
