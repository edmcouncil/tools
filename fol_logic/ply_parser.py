import re

from ply import lex, yacc

from fol_logic.objects.atomic_formula import AtomicFormula
from fol_logic.objects.conjunction import Conjunction
from fol_logic.objects.disjunction import Disjunction
from fol_logic.objects.equivalence import Equivalence
from fol_logic.objects.formula import Formula
from fol_logic.objects.implication import Implication
from fol_logic.objects.negation import Negation
from fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier

tokens = ['COMMA', 'LPAREN','RPAREN','VARIABLE', 'PREDICATE', 'CONJUNCTION', 'NEGATION', 'DISJUNCTION', 'IMPLICATION', 'EQUIVALENCE', 'EXISTS', 'ALL']

t_ignore = ' \t\r\n\f\v'

literals = ['(', ')', '[', ']', '{', '}']

precedence = \
    (
        ('left', 'EQUIVALENCE'),
        ('left', 'IMPLICATION'),
        ('left', 'DISJUNCTION'),
        ('left', 'CONJUNCTION'),
        ('left', 'NEGATION'),
        ('left', 'ALL', 'EXISTS')
    )

def t_COMMA(t):
    r','
    t.type = 'COMMA'
    return t

def t_LPAREN(t):
    r'\(|\{|\['
    t.type = 'LPAREN'
    return t

def t_RPAREN(t):
    r'\)|\{|\{'
    t.type = 'RPAREN'
    return t


def t_VARIABLE(t):
    r"\b[a-z]\d*'*\b"
    t.type = 'VARIABLE'
    return t

def t_PREDICATE(t):
    r'=|[A-Za-z]{2,}'
    t.type = 'PREDICATE'
    return t

def t_ALL(t):
    r'\u27C7'
    t.type = 'ALL'
    return t

def t_EXISTS(t):
    r'\u2203'
    t.type = 'EXISTS'
    return t

def t_NEGATION(t):
    r'\u00AC'
    t.type = 'NEGATION'
    return t

def t_CONJUNCTION(t):
    r'\u2227'
    t.type = 'CONJUNCTION'
    return t

def t_DISJUNCTION(t):
    r'\u2228'
    t.type = 'DISJUNCTION'
    return t

def t_IMPLICATION(t):
    r'\u2192'
    t.type = 'IMPLICATION'
    return t

def t_EQUIVALENCE(t):
    r'\u2194'
    t.type = 'EQUIVALENCE'
    return t

def t_error(t):
    print("Unknown character \"{}\"".format(t.value[0]))
    t.lexer.skip(1)


def p_formula(p):
    """
    formula : atom
            | negation
            | conjunction
            | disjunction
            | implication
            | equivalence
            | quantified_formula
    """
    p[0] = p[1]


def p_variable_seq(p):
    """
    variable_seq : VARIABLE
    variable_seq : VARIABLE COMMA variable_seq
    """
    if len(p) == 3:
        variable_seq = [p[1]]
        if isinstance(p[2], list):
            variable_seq += p[2]
        else:
            variable_seq.append(p[2])
        p[0] = variable_seq

    else:
        p[0] = [p[1]]


def p_atom(p):
    """
    atom : PREDICATE LPAREN variable_seq RPAREN
    """
    p[0] = AtomicFormula(predicate=p[1], variables=p[3])


# def p_quantification_seq(p):
#     """
#     quantification_seq  : ALL variable_seq
#                         | EXISTS variable_seq
#     quantification_seq : ALL variable_seq COMMA quantification_seq
#     quantification_seq : EXISTS variable_seq COMMA quantification_seq
#     """
#     if len(p) == 3:
#         quantification_seq = [p[1]]
#         if isinstance(p[2], list):
#             quantification_seq += p[2]
#         else:
#             quantification_seq.append(p[2])
#         p[0] = quantification_seq
#
#     else:
#         p[0] = [p[1]]

def p_all_quantified_formula(p):
    """
    all_quantified_formula : ALL variable_seq formula
    all_quantified_formula : ALL variable_seq COMMA formula
    """
    if len(p) == 4:
        p[0] = QuantifyingFormula(quantified_formula=p[3], variables=p[2], quantifier=Quantifier.UNIVERSAL)
    if len(p) == 5:
        p[0] = QuantifyingFormula(quantified_formula=p[4], variables=p[2], quantifier=Quantifier.UNIVERSAL)


def p_exist_quantified_formula(p):
    """
    exist_quantified_formula : EXISTS variable_seq formula
    exist_quantified_formula : EXISTS variable_seq COMMA formula
    """
    if len(p) == 4:
        p[0] = QuantifyingFormula(quantified_formula=p[3], variables=p[2], quantifier=Quantifier.EXISTENTIAL)
    if len(p) == 5:
        p[0] = QuantifyingFormula(quantified_formula=p[4], variables=p[2], quantifier=Quantifier.EXISTENTIAL)

def p_quantified_formula(p):
    """
    quantified_formula  : all_quantified_formula
                        | exist_quantified_formula
    """
    p[0] = p[1]
    
    
def p_negation(p):
    """
    negation : NEGATION formula
    """
    p[0] = Negation(arguments=[p[2]])
    p[2].is_self_standing = False

    
def p_conjunction(p):
    """
    conjunction : LPAREN formula CONJUNCTION formula RPAREN
    conjunction : formula CONJUNCTION formula
    """
    if len(p) == 6:
        p[0] = Conjunction(arguments=[p[2], p[4]])
        p[2].is_self_standing = False
        p[4].is_self_standing = False
    if len(p) == 4:
        p[0] = Conjunction(arguments=[p[1], p[3]])
        p[1].is_self_standing = False
        p[3].is_self_standing = False
        
        
def p_disjunction(p):
    """
    disjunction : LPAREN formula DISJUNCTION formula RPAREN
    disjunction : formula DISJUNCTION formula
    """
    if len(p) == 6:
        p[0] = Disjunction(arguments=[p[2], p[4]])
        p[2].is_self_standing = False
        p[4].is_self_standing = False
    if len(p) == 4:
        p[0] = Disjunction(arguments=[p[1], p[3]])
        p[1].is_self_standing = False
        p[3].is_self_standing = False
        
        
def p_implication(p):
    """
    implication : LPAREN formula IMPLICATION formula RPAREN
    implication : formula IMPLICATION formula
    """
    if len(p) == 6:
        p[0] = Implication(arguments=[p[2], p[4]])
        p[2].is_self_standing = False
        p[4].is_self_standing = False
    if len(p) == 4:
        p[0] = Implication(arguments=[p[1], p[3]])
        p[1].is_self_standing = False
        p[3].is_self_standing = False
        

def p_equivalence(p):
    """
    equivalence : LPAREN formula EQUIVALENCE formula RPAREN
    equivalence : formula EQUIVALENCE formula
    """
    if len(p) == 6:
        p[0] = Equivalence(arguments=[p[2], p[4]])
        p[2].is_self_standing = False
        p[4].is_self_standing = False
    if len(p) == 4:
        p[0] = Equivalence(arguments=[p[1], p[3]])
        p[1].is_self_standing = False
        p[3].is_self_standing = False
        

def p_error(p):
    # print("Syntax error in input!")
    # print(p)
    pass


def __is_error(obj) -> bool:
    return isinstance(obj, yacc.YaccSymbol) and obj.type == 'error'


def parse_formula_infix_notation(text: str) -> Formula:
    lex.lex(reflags=re.UNICODE)
    parser = yacc.yacc(write_tables=False)
    formula = yacc.parse(text)
    return formula
#
# formula = parse_formula_infix_notation('ComputingProcess(x) ↔ PlannedProcess(x) ∧ ∃y,∃a(Agent(y) ∧ (Algorithm(a) ∨ EncodedAlgorithm(a)) ∧ hasParticipantAtSomeTIme(x,y) ∧ genericallyDependsOnAtSomeTime(a,y) ∧ concretizesAtSomeTime(x,a) ∧ (∃o(ObjectiveSpecification(o) ∧ continuantPartOfAtAllTimes(o,a) ∧ achievesAtSomeTIme(x,o)) ∨  ∃i(InformationContentEntity(i) ∧ hasSpecifiedOutput(x,i)))')
# v=0