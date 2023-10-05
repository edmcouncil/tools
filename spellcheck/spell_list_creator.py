import json

spell = ['kDa','laevorotatory','monobenzenesulphonate', 'datamodel', 'oligo','desacyl','epimeric','aliskiren','stoichoimetrical','rDNA', 'Harpagophytum', 'sp2', 'sp3', 'Planck', 'dihydroxy','guanidinyl','colourant', 'afucosylated','dialkyl', 'Avogadro', 'monomethanesulfonate','monophosphoryl', 'aptamer', 'martindale', 'prefixed', 'aldehyde', 'plasmid','deoxyribose', 'phosphodiester', 'separable','thymine', 'glycyl','ribose', 'ketone', 'reusability', 'annotation', 'subclass','medDRA', 'conformant', 'pharmacologically', 'datatype', 'informatics', 'ontology', 'ontologies', 'ab02sh', 'acceptability', 'acetonide', 'achiral', 'adjuvant', 'administrable', 'allergenic', 'allergenicity', 'amination', 'aminoethoxy', 'amlodipine', 'amplodipine', 'anion', 'anthropoid', 'benzathine', 'benzylpenicillin', 'besylate', 'bibliographic', 'bioactive', 'bioinformatics', 'bioontology', 'biopharma', 'biopolymer', 'biosimilar', 'biphenyls', 'bittner', 'blackwell', 'boolean', 'bzip', 'c20h25cln2o5', 'c21h31cln2o9s', 'c2cl', 'cahn', 'cation', 'cc2', 'cc2ccc', 'cc3ccccc3', "cd", 'cdc', 'cdx', 'charset', 'checksum', 'chelate', 'chelated', 'chiral', 'chirality', 'chiroptic', 'chlorophenyl',  'clathrate', 'comorbidity', 'conceptualization', 'conditionally', 'conformance', 'conformer', 'contemporarily', 'contraindication', 'cooccurring', 'countable', 'cryoprecipitate', 'csv', 'culturing', 'dataset', 'definitional', 'definitionally', 'degradant', 'delimiter', 'deprecated', 'descriptor', 'desmopressin', 'dextrorotatory', 'diacetate', 'diastereomer', 'dibasic', 'dicarboxylate', 'diester', 'dihydro', 'dihydropyridine', 'dimensionless', 'dimethicone', 'dipole', 'discontinuous', 'distributional', 'disulfide', 'disulphide', 'dodecyl', 'doseage', 'drugbank', 'dynavax', 'electrophoresis', 'eluted', 'emulsifier', 'enantiomer', 'enumeration', 'enumeration', 'epimerase', 'equimolar', 'equivalence', 'erythromycin', 'esterification', 'eudra', 'eudravigilance', 'excipient', 'extractive', 'gentamicin', 'germplasm', 'github', 'glaxosmithkline', 'gln', 'glutaraldehyde', 'glycan', 'glyceraldehyde', 'glyceryl', 'glycolate', 'glycoprotein', 'glycosylation', 'gmbh', 'goodchild', 'gzip', 'hartshorn', 'hepatorenal', 'heterogeneity', 'homogenic', 'homologous', 'hornworts', 'html', 'http', 'https', 'hutton', 'hydrogenation', 'hydrolysis', 'hydroxy', 'hydroxyl', 'hyperfine', 'inactivation', 'inchikey', 'industrially', 'infective', 'instrumentality', 'interconversion', 'interconvert', 'interventional', 'intraspecies', 'investigational', 'isoelectric', 'isolatable', 'isomeric', 'isomerization', 'isotopically', 'jsp', 'kanamycin', 'kmno4', 'lexical', 'ligand', 'linker', 'linkoping', 'livertox', 'liverworts', 'macrogol', 'macromolecular', 'maintainability', 'mcg', 'mediatype', 'mednet', 'mereological', 'mesylate', 'metamodel', 'metoprolol', 'microbiological', 'microcrystalline', 'microgram', 'micronization', 'micronized', 'middlesex', "mixture", 'modularization', 'moieties', 'moiety', 'molfile', 'monoacetate', 'monoclonal', 'monodisperse', 'monoesters', 'monohydrate', 'mycin', 'ncbi', 'nci', 'ncicb', 'ncit', 'nitroprusside', 'nlm', 'noncovalent', 'nonprescription', 'nonproprietary', 'norvasc', 'novartis', 'nucleon', 'nucleon', 'nucleoside', 'nuclide', 'nuclide', 'nullflavor', 'nullflavored', 'obolibrary', 'octahedral', 'oligonucleotides', 'oligosaccharide', 'onboarded', 'optionally', 'ordinating', 'oxoacid', 'paperboard', 'pectoris', 'pentahydrate', 'permeation', 'pfizer', 'pharmacodynamic', 'pharmacologic', 'pharmacopeia', 'pharmacopoeia', 'pharmacopoeias', 'pharmacovigilance', 'phenotype', 'phenotypic', 'phosphorylation', 'phpid', 'physiologic', 'pistoia', 'pka', 'planar', 'plantae', 'plc', 'pmc', 'polyacrylamide', 'polyclonal', 'polydisperse', 'polymerase', 'polymerization', 'polysaccharide', 'postcoordinated', 'potentiates', 'preclinical', 'predefined', 'prefilled', 'procumbens', 'prodrug', 'prolongation', 'propranolol', 'prospectively', 'proteomics', 'pubchem', 'pubmed', 'qtu', 'quantification', 'quantifies', 'quantitatively', 'r', 'racemate', 'racemic', 'radioanalytical', 'radionuclide', 'rdf', 'reactivity', 'reasoner', 'referential', 'reification', 'reified', 'resolvable', 'rfcs', 'ribonucleic', 'ritonavir', 'rke', 'roundwood', 'rxnorm', 'semifinished', 'serine', 'simethicone', 'solubility', 'solvate', 'spor', 'stearate', 'stereocenter', 'stereochemical', 'stereochemistries', 'stereochemistry', 'stoichiometric', 'stoichiometrical', 'stoichiometry', 'subclause', 'submitter', 'substituent', 'substituent', 'subtype', 'subtype', 'subunit', 'subunit', 'succinate', 'sulphation', 'superimposable', 'superproperty', 'supertype', 'svhcs', 'synthase', 'synthetase', 'taiwan', 'tartrate', 'tautomeric', 'temporally', 'terlipressin', 'terminologically', 'terminologies', 'tetrahedral', 'tetrahedron', 'tetrahydrate', 'thickener', 'throughput', 'titration', 'toxicant', 'transduced', 'transferase', 'translatable', 'translational', 'triamcinolone', 'trihydrate', 'trinomial', 'typographic', 'uncompressed', 'unencoded', 'unformatted', 'unicode', 'uniprot', 'unitage', 'unitary', 'unstandardized', 'varices', 'vasoactive', 'vasopressin', 'vasospastic', 'vocabularies', 'waals', 'webservice', 'wiswesser', 'www', 'xenobiotics', 'xml', 'xsd', 'zlib', 'α', 'γ', 'ε', 'μ', 'μg', 'ν', 'ρ']

spell.sort()
with open(file='spell.json', mode='w') as json_file:
    spell_json = json.dump(fp=json_file, obj=spell, indent=4)