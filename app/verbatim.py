''' Decompose a sentence into a list of phrases with each phrase being about
a specific subject in the sentence.

Note: this was built to parse results from CloudSight and is aimed at simple
descriptions of images such as 'A man playing chess in a Panama hat.' Anything
that follows 'It was the best of times, it was the worst of times, ...' will
probably fail.
'''

from collections import namedtuple
import os
from subprocess import PIPE, Popen

DESCRIPTORS = ('acomp', 'amod', 'appos', 'det', 'predet', 'mwe', 'rcmod', 'nn',
               'num', 'quantmod', 'cc', 'conj')
SUBJECTS = ('dobj', 'iobj', 'pobj', 'obj', 'subj', 'nsubj', 'csubj')

class Node(namedtuple('Node', ['term', 'children'])):
    '''The building block for dependency graph construction.

    term -- a Term from the CoNLL representation.
    children -- all the Nodes/Terms that depend on this Node/Term.
    '''
    pass


class Term(namedtuple('Term', ['id', 'word', 'pos', 'parent', 'function'])):
    '''The properties of a word in a sentence we care about.

    id -- the index of the word in the sentence.
    word -- the word in string form.
    pos -- the word's part of speech in the sentence.
    parent -- the id of the term this term depends on.
    function -- the function of the word in the sentence.
    '''
    pass


class Subject(namedtuple('Subject', ['noun', 'descriptors'])):
    '''A thing and the words that describe it. Ideally, the descriptors make
    sense when comma separated and placed in front of noun.

    noun -- a string
    descriptors -- a list of strings
    '''
    pass

def _line_to_terms(line):
    '''Takes a valid, tab-separated CoNLL line and parses it into a Term.

    See https://nlp.stanford.edu/software/dependencies_manual.pdf
    '''
    return Term(
        id=int(line[0]),
        word=line[1],
        pos=line[4].lower(),
        parent=int(line[6]),
        function=line[7]
    )

def _terms_to_tree(terms):
    ''' Convert a list of Terms to a tree structure.

    See Node above.
    '''
    def _make_tree(root):
        children = [term for term in terms if term.parent == root.id]
        if len(children) == 0:
            return Node(term=root, children=None)
        children = [_make_tree(child) for child in children]
        return Node(term=root, children=children)

    for term in terms:
        if term.parent == 0:
            root = term
            break

    return _make_tree(root)

def _find_subjects(tree_root_node):
    '''Find all the subjects in the given tree along with their descriptors.'''
    def _crawl_descriptors(children, subject):
        if children is None:
            return
        skip = False
        for i in xrange(len(children)):
            if children[i].term.function in DESCRIPTORS:
                if children[i].term.function == 'cc' and children[i + 1].term.pos == 'nn':
                    skip = True
                    continue
                if children[i].term.pos != 'dt' and not skip:
                    subject.descriptors.append(children[i].term)
                else:
                    skip = False
                if children[i].children is not None:
                    _crawl_descriptors(children[i].children, subject)

    def _crawl_tree(node, done):
        if (node.term.function in SUBJECTS
                or node.term.function == 'ROOT' and node.term.pos == 'nn'
                or node.term.function == 'conj' and node.term.pos == 'nn'):
            subject = Subject(noun=node.term, descriptors=[])
            _crawl_descriptors(node.children, subject)
            done.append(subject)

        if node.children is None:
            return

        for child in node.children:
            _crawl_tree(
                child,
                done
            )

    done = []
    _crawl_tree(tree_root_node, done)
    return done

def list_subjects(phrase):
    '''Pull the subjects and the words that describe them out of the given
    phrase.

    phrase -- Any well formed sentence.

    returns -- a list of phrases, one for each subject.
    '''
    try:
        FNULL = open(os.devnull, 'w')
        parser = Popen(
            ['/usr/bin/docker', 'run', '--rm', '-i', 'local/syntaxnet-docker', 'syntaxnet/demo.sh'],
            stdin=PIPE,
            stdout=PIPE,
            stderr=FNULL
        )
    except Exception as e:
        print e
        raise
    lines = [line for line in parser.communicate(phrase)[0].split('\n') if line]

    if __name__ == '__main__':
        print '\n'.join(lines)

    table = [line.split('\t')[:-1] for line in lines]
    terms = [_line_to_terms(line) for line in table]
    subjects = _find_subjects(_terms_to_tree(terms))

    formatted_subjects = []
    for subject in subjects:
        descriptors = sorted(subject.descriptors, key=lambda a: a.id)
        subject = subject.noun.word.lower()
        if len(descriptors) > 0:
            subject = ' {}'.format(subject)

        formatted_subjects.append('{}{}'.format(
            ', '.join([descriptor.word.lower() for descriptor in descriptors]),
            subject
        ))

    return formatted_subjects

if __name__ == '__main__':
    print list_subjects('Everything must be made of thin, strong paper without cuts or glue')
