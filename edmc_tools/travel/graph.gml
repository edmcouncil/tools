graph [
  directed 1
  node [
    id 0
    label "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/Substance"
  ]
  node [
    id 1
    label "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/MolecularWeight"
  ]
  node [
    id 2
    label "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/Structure"
  ]
  node [
    id 3
    label "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/SubstanceName"
  ]
  node [
    id 4
    label "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/LanguageIdentifier"
  ]
  node [
    id 5
    label "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/Language"
  ]
  node [
    id 6
    label "http://www.w3.org/2000/01/rdf-schema#Literal"
  ]
  node [
    id 7
    label "http://www.w3.org/2002/07/owl#Thing"
  ]
  node [
    id 8
    label "http://www.w3.org/2001/XMLSchema#string"
  ]
  node [
    id 9
    label "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/GeographicRegionIdentifier"
  ]
  node [
    id 10
    label "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/GeographicRegion"
  ]
  node [
    id 11
    label "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/SubstanceNameDomain"
  ]
  node [
    id 12
    label "https://www.omg.org/spec/Commons/Documents/Reference"
  ]
  node [
    id 13
    label "<class 'rdflib.term.Literal'>"
  ]
  edge [
    source 0
    target 1
    attr [
      property "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/hasMolecularWeight"
    ]
  ]
  edge [
    source 0
    target 2
    attr [
      property "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/hasStructure"
    ]
  ]
  edge [
    source 0
    target 3
    attr [
      property "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/hasSubstanceName"
    ]
  ]
  edge [
    source 0
    target 0
    attr [
      property "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/isRelatedSubstanceTo"
    ]
  ]
  edge [
    source 3
    target 4
    attr [
      property "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO21090-HarmonizedDatatypes/hasLanguageCode"
    ]
  ]
  edge [
    source 3
    target 0
    attr [
      property "https://www.omg.org/spec/Commons/Designators/isNameOf"
    ]
  ]
  edge [
    source 3
    target 9
    attr [
      property "https://www.omg.org/spec/Commons/RegulatoryAgencies/isApplicableInJurisdiction"
    ]
  ]
  edge [
    source 3
    target 11
    attr [
      property "https://www.omg.org/spec/Commons/Classifiers/isClassifiedBy"
    ]
  ]
  edge [
    source 3
    target 12
    attr [
      property "https://www.omg.org/spec/Commons/Designators/isDescribedBy"
    ]
  ]
  edge [
    source 3
    target 13
    attr [
      property "https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/hasSubstanceNameValue"
    ]
  ]
  edge [
    source 4
    target 5
    attr [
      property "https://www.omg.org/spec/Commons/Identifiers/identifies"
    ]
  ]
  edge [
    source 4
    target 8
    attr [
      property "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/hasTag"
    ]
  ]
  edge [
    source 5
    target 6
    attr [
      property "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/hasFrenchName"
    ]
  ]
  edge [
    source 5
    target 7
    attr [
      property "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/hasIndigenousName"
    ]
  ]
  edge [
    source 9
    target 10
    attr [
      property "https://www.omg.org/spec/Commons/Identifiers/identifies"
    ]
  ]
  edge [
    source 9
    target 8
    attr [
      property "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/hasTag"
    ]
  ]
  edge [
    source 11
    target 3
    attr [
      property "https://www.omg.org/spec/Commons/Classifiers/classifies"
    ]
  ]
]
