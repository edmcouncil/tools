import logging
from collections import OrderedDict


sw_to_postgresql_datatype_map = \
    {
        'xsd:string': 'text',
        'xsd:nonNegativeInteger': 'int',
        'xsd:positiveInteger': 'int',
        'xsd:decimal': 'decimal',
        'xsd:boolean': 'boolean'
    }

MAX_POSTGRESQL_LENGTH = 62

def create_postgresql_datatypes(datatypes_dictionary: dict, order_datatypes: dict) -> str:
    order_datatypes = OrderedDict(sorted(order_datatypes.items()))
    
    filtered_datatypes_dictionary, filtered_order_datatypes = \
        __filter_out_datatypes_with_long_names(
            datatypes_dictionary=datatypes_dictionary,
            order_datatypes=order_datatypes)
    
    postgresql_datatypes_creation_sql = str()
    for rank, datatypes in filtered_order_datatypes.items():
        for datatype in datatypes:
            if datatype in sw_to_postgresql_datatype_map:
                continue
            postgress_datatype_parameters = list()
            postgresql_datatype_parameter_names = dict()
            if datatype in filtered_datatypes_dictionary:
                datatypes_attributes = filtered_datatypes_dictionary[datatype]
            else:
                datatypes_attributes = {(datatype, 'xsd:string')}
            for datatypes_attribute in datatypes_attributes:
                attribute_name = datatypes_attribute[0]
                postgresql_datatype_parameter_name = attribute_name.split(':')[1]
                if postgresql_datatype_parameter_name in postgresql_datatype_parameter_names:
                    postgresql_datatype_parameter_names[postgresql_datatype_parameter_name] += 1
                    postgresql_datatype_parameter_name = postgresql_datatype_parameter_name + '_' + str(postgresql_datatype_parameter_names[postgresql_datatype_parameter_name])
                else:
                    postgresql_datatype_parameter_names[postgresql_datatype_parameter_name] = 1
                datatype_parameter_type = datatypes_attribute[1]
                if datatype_parameter_type in sw_to_postgresql_datatype_map:
                    postgresql_datatype_parameter_type = sw_to_postgresql_datatype_map[datatype_parameter_type]
                else:
                    postgresql_datatype_parameter_type = __create_postgresql_term(datatype_parameter_type)
                postgress_datatype_parameter = (__create_postgresql_term(postgresql_datatype_parameter_name) + ' ' + postgresql_datatype_parameter_type).replace('-', '_')
                postgress_datatype_parameters.append(postgress_datatype_parameter)
            postgresql_datatype_name = __create_postgresql_term(datatype.replace('-', '_'))
            postgresql_datatype_creation_sql = ' '.join(['create type', postgresql_datatype_name, 'as', '(', ','.join(postgress_datatype_parameters), ')', ';'])
            postgresql_datatypes_creation_sql += postgresql_datatype_creation_sql + '\n\n'
    return postgresql_datatypes_creation_sql


def __create_postgresql_term(term: str) -> str:
    return '"' + term + '"'


def __filter_out_datatypes_with_long_names(datatypes_dictionary: dict, order_datatypes: dict) -> tuple:
    filtered_datatypes_dictionary = dict()
    filtered_order_datatypes = dict()
    
    for datatype, datatype_attributes in datatypes_dictionary.items():
        if len(datatype) > MAX_POSTGRESQL_LENGTH:
            continue
        filtered_datatype_attributes = list()
        for [datatype_attribute, datatype_attribute_type] in datatype_attributes:
            if len(datatype_attribute) > MAX_POSTGRESQL_LENGTH:
                continue
            if len(datatype_attribute_type) > MAX_POSTGRESQL_LENGTH:
                continue
            filtered_datatype_attributes.append([datatype_attribute, datatype_attribute_type])
        if len(filtered_datatype_attributes) == 0:
            continue
        filtered_datatypes_dictionary[datatype] = filtered_datatype_attributes
    
    for rank, datatypes in order_datatypes.items():
        filtered_datatypes = set()
        for datatype in datatypes:
            if len(datatype) > MAX_POSTGRESQL_LENGTH:
                continue
            filtered_datatypes.add(datatype)
        if len(filtered_datatypes) == 0:
            continue
        filtered_order_datatypes[rank] = filtered_datatypes
        
    return filtered_datatypes_dictionary, filtered_order_datatypes
    
    