from collections import namedtuple
import json
import os
import pty
import re
from subprocess import check_output, Popen, PIPE
import sys

DESCRIPTORS = ('acomp', 'amod', 'appos', 'det',
    'predet', 'mwe', 'rcmod', 'nn', 'num', 'quantmod', 'cc', 'conj')
SUBJECTS = ('dobj', 'iobj', 'pobj', 'obj', 'subj', 'nsubj', 'csubj')

Node = namedtuple('Node', ['value', 'children'])
Term = namedtuple('Term', ['id', 'word', 'pos', 'parent', 'function'])
Subject = namedtuple('Subject', ['noun', 'descriptors'])

def _line_to_terms(line):
    '''Takes a valid, tab-separated CoNLL line and parses it into a Term.

    See https://nlp.stanford.edu/software/dependencies_manual.pdf
    '''
    return Term(id=int(line[0]), word=line[1], pos=line[4].lower(), parent=int(line[6]), function=line[7])

def _terms_to_tree(terms):
    ''' Convert a list of Terms to a tree format.

    See Node above.
    '''
    def _make_tree(root):
        children = [term for term in terms if term.parent == root.id]
        if len(children) == 0:
            return Node(value=root, children=None)
        children = [_make_tree(child) for child in children]
        return Node(value=root, children=children)

    for term in terms:
        if term.parent == 0:
            root = term
            break

    return _make_tree(root)

def print_tree(tree, lead):
    if tree.children is None:
        return
    for child in tree.children:
        print_tree(child, '{}\t'.format(lead))

def _find_subjects(tree_root_node):
    '''Find all the subjects in the given tree along with their descriptors.'''
    def _crawl_descriptors(children, subject):
        if children is None:
            return
        skip = False
        for i in xrange(len(children)):
            if children[i].value.function in DESCRIPTORS:
                if children[i].value.function == 'cc' and children[i + 1].value.pos == 'nn':
                    skip = True
                    continue
                if children[i].value.pos != 'dt' and not skip:
                    subject.descriptors.append(children[i].value)
                else:
                    skip = False
                if children[i].children is not None:
                    _crawl_descriptors(children[i].children, subject)

    def _crawl_tree(node, done):
        if (node.value.function in SUBJECTS
            or node.value.function == 'ROOT' and node.value.pos == 'nn'
            or node.value.function == 'conj' and node.value.pos == 'nn'):
            subject = Subject(noun=node.value, descriptors=[])
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
    name = check_output('whoami', shell=True)
    safe_phrase = str(phrase).replace("'", '')
    try:
        master_fd, slave_fd = pty.openpty()
        parser = Popen(
            ['/usr/bin/docker', 'run', '--rm', '-i', 'local/syntaxnet-docker', 'syntaxnet/demo.sh'],
            stdin=PIPE,
            stdout=PIPE
        )
    except Exception as e:
        print e
        raise
    lines = parser.communicate(phrase)[0].split('\n')
    print '\n'.join(lines)
    table = []
    for line in lines:
        if re.match('^\d+.*$', line):
            table.append(line.split('\t')[:-1])

    terms = [_line_to_terms(line) for line in table]
    subjects = _find_subjects(_terms_to_tree(terms))

    formatted_subjects = []
    for subject in subjects:
        descriptors = sorted(subject.descriptors, key=lambda a: a.id)
        subject = subject.noun.word.lower()
        if len(descriptors) > 0:
            subject = ' {}'.format(subject)

        formatted_subjects.append('{}{}'.format(' '.join([descriptor.word.lower() for descriptor in descriptors]), subject))

    return formatted_subjects

print list_subjects('Everything must be made of thin, strong paper without cuts or glue')
