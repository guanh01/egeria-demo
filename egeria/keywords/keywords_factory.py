
from keywords import default_keywords

keywords_maps = {
	'default': default_keywords
}

def get_keywords(doc='default'):
	if doc not in keywords_maps:
		doc = 'default'
		# print 'Use the default keywords set.'
    	# raise ValueError('Name of keywords selection unknown %s' % doc)

	print 'Use the keywords set for', doc 
	return keywords_maps[doc]
