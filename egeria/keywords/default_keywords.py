

IMPERATIVE_WORDS = {'use', 'avoid', 'create', 'make', 'map', 'align', 
                         'add', 'change', 'ensure', 'call', 'unroll', 'move',
                         'select', 'schedule', 'switch', 'transform', 'pack'} 

XCOMP_GOVERNORS = {'prefer', 'best', 'faster', 'better','efficient', 'beneficial', 'appropriate'
                         'recommended', 'encouraged', 'leveraged', 'important', 'useful', 'required','controlled'}

FLAGGING_WORDS = {'better', 'best performance', 'higher performance', 
            'maximum performance', 'peak performance', 'improve the performance',
            'higher impact', 'more appropriate',  'should', 'high bandwidth', 'high throughput',
            'prefer','effective way', "one way to","the key to", "contribute to", 
            "can be used to", "can lead to", "reduce",  'can help', 'can be important','can be useful',
            'is important', "help avoid", 'can avoid',  'instead', 'is desirable',
            "good choice", 'ideal choice', 'good idea', 'good start', 'benefit', 'encouraged'}

KEY_PREDICATES = {'maximize', 'minimize', 'recommend','accomplish', 'achieve', 'avoid'}


KEY_SUBJECTS = {'programmer', 'developer', 'application', 'solution', \
                    'algorithm', 'optimization', 'guideline', 'technique'}

ALL_KEYWORDS = KEY_SUBJECTS | KEY_PREDICATES | FLAGGING_WORDS | XCOMP_GOVERNORS | IMPERATIVE_WORDS