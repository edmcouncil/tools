import pandas
from pyshacl import validate
from rdflib import Graph, SH, RDF


def validate_graph_with_shacl(graph: Graph, shacl: Graph, results_file_path: str):
    validation_results_dict = dict()
    conforms, results_graph, result_texts = \
        validate(
            data_graph=graph,
            shacl_graph=shacl,
            inference='both',
            abort_on_first=False,
            allow_infos=True,
            allow_warnings=True)
    validation_results = list(results_graph.subjects(object=SH.ValidationResult, predicate=RDF.type))
    for validation_result in validation_results:
        id = list(results_graph.objects(subject=validation_result, predicate=SH.sourceShape))[0]
        focus = list(results_graph.objects(subject=validation_result, predicate=SH.focusNode))[0]
        path = list(results_graph.objects(subject=validation_result, predicate=SH.resultPath))[0]
        component = list(results_graph.objects(subject=validation_result, predicate=SH.sourceConstraintComponent))[0]
        severity = list(results_graph.objects(subject=validation_result, predicate=SH.resultSeverity))[0]
        
        message = list(results_graph.objects(subject=validation_result, predicate=SH.resultMessage))[0]
        
        validation_results_dict = validation_results_dict | \
            {
                id: [severity, focus, path, component,  message]
            }
    validation_results_dataframe = pandas.DataFrame.from_dict(validation_results_dict, orient='index')
    validation_results_dataframe.columns = ['Severity', 'Focus' , 'Path', 'Type',  'Message']
    validation_results_dataframe.sort_values(by=['Severity','Focus', 'Type'], inplace=True)
    validation_results_dataframe.to_excel(results_file_path, index=False)