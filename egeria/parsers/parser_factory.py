

from parsers import cuda_parser , opencl_parser, openacc_parser  

parsers_map = {
	'cuda': cuda_parser,
	'opencl': opencl_parser,
	'openacc': openacc_parser
	}

def get_parse_fn(doc):
	if doc not in parsers_map:
		raise ValueError('Name of document parser unknown %s' % doc)
	parse_fn = parsers_map[doc].parse
	return parse_fn 
	