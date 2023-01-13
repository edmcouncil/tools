from compare.ontology_folder_comparer import compare_ontology_folders

compare_ontology_folders(
    folder_1='../resources/idmp_current',
    folder_2='../resources/idmp_master_v0.1.0',
    results_folder_path='test_results/',
    verbose=True)