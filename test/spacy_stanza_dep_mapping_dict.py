dep_stanza_to_spacy = {
    "acl": "acl",
    "acl:relcl": "relcl",
    "advcl": "advcl",
    "advmod": "advmod",
    "advmod:emph": "advmod",
    "advmod:lmod": "advmod",
    "amod": "amod",
    "appos": "appos",
    "aux": "aux",
    "aux:pass": "auxpass",
    "case": "prep",
    "cc": "cc",
    "cc:preconj": "preconj",
    "ccomp": "ccomp",
    "compound": "compound",
    "compound:lvc": "compound",
    "compound:prt": "prt",
    "compound:redup": "compound",
    "compound:svc": "compound",
    "conj": "conj",
    "cop": "ROOT",
    "csubj": "csubj",
    "csubj:pass": "csubjpass",
    "dep": "dep",
    "det": "det",
    "det:numgov": "det",
    "det:nummod": "det",
    "det:poss": "poss",
    "det:predet": "predet",
    "discourse": "intj",
    "dislocated": "dep",
    "expl": "expl",
    "expl:impers": "expl",
    "expl:pass": "expl",
    "expl:pv": "expl",
    "fixed": "dep",
    "flat": "compound",
    "flat:foreign": "dep",
    "flat:name": "dep",
    "goeswith": "dep",
    "iobj": "dative",
    "list": "dep",
    "mark": "mark",
    "nmod": "pobj",
    "nmod:poss": "poss",
    "nmod:tmod": "pobj",
    "nmod:npmod": "pobj",
    "nsubj": "nsubj",
    "nsubj:pass": "nsubjpass",
    "nummod": "nummod",
    "nummod:gov": "nummod",
    "obj": "dobj",
    "obl": "pobj",
    "obl:agent": "agent",
    "obl:arg": "pobj",
    "obl:lmod": "pobj",
    "obl:tmod": "npadvmod",
    "obl:npmod": "npadvmod",
    "orphan": "dep",
    "parataxis": "parataxis",
    "punct": "punct",
    "reparandum": "dep",
    "root": "ROOT",
    "vocative": "dep",
    "xcomp": "xcomp",
}

dep_spacy_to_stanza = {
    "ROOT": "root",
    "acl": "acl",
    "acomp": "xcomp",
    "advcl": "advcl",
    "advmod": "advmod",
    "agent": "case",
    "amod": "amod",
    "appos": "appos",
    "attr": "xcomp",
    "aux": "aux",
    "auxpass": "aux:pass",
    "case": "case",
    "cc": "cc",
    "ccomp": "ccomp",
    "compound": "compound",
    "conj": "conj",
    "csubj": "csubj",
    "csubjpass": "csubj:pass",
    "dative": "iobj",
    "dep": "dep",
    "det": "det",
    "dobj": "obj",
    "expl": "expl",
    "intj": "discourse",
    "mark": "mark",
    "meta": "dep",
    "neg": "advmod",
    "nmod": "compound",
    "npadvmod": "obl:npmod",
    "nsubj": "nsubj",
    "nsubjpass": "nsubj:pass",
    "nummod": "nummod",
    "oprd": "xcomp",
    "parataxis": "parataxis",
    "pcomp": "advcl",
    "pobj": "obl",
    "poss": "nmod:poss",
    "preconj": "cc:preconj",
    "predet": "det:predet",
    "prep": "case",
    "prt": "compound:prt",
    "punct": "punct",
    "quantmod": "advmod",
    "relcl": "acl:relcl",
    "xcomp": "xcomp"
}