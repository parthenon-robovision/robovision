from subprocess import check_output, Popen, PIPE
import pty
import json
import re
from collections import namedtuple
import os

DESCRIPTORS = ('acomp', 'amod', 'appos', 'det',
    'predet', 'mwe', 'rcmod', 'nn', 'num', 'quantmod')
SUBJECTS = ('dobj', 'iobj', 'pobj', 'obj', 'subj', 'nsubj', 'csubj')

Node = namedtuple('Node', ['value', 'children'])
Term = namedtuple('Term', ['id', 'word', 'pos', 'parent', 'function'])
Thing = namedtuple('Thing', ['noun', 'descriptors'])

def _line_to_terms(line):
    return Term(id=int(line[0]), word=line[1], pos=line[4].lower(), parent=int(line[6]), function=line[7])

def _make_tree(root, descriptions):
    children = [desc for desc in descriptions if desc.parent == root.id]
    if len(children) == 0:
        return Node(value=root, children=None)
    children = [_make_tree(child, descriptions) for child in children]
    return Node(value=root, children=children)

def print_tree(tree, lead):
    print '{}{} ({}, {})'.format(lead, tree.value.word, tree.value.pos, tree.value.function)
    if tree.children is None:
        return
    for child in tree.children:
        print_tree(child, '{}\t'.format(lead))

def _crawl_descriptors(children, thing):
    if children is None:
        return
    for child in children:
        if child.value.function in DESCRIPTORS:
            thing.descriptors.append(child.value)
            if child.children is not None:
                _crawl_descriptors(child.children, thing)

def _crawl_tree(node, done):
    if (node.value.function in SUBJECTS
        or node.value.function == 'ROOT' and node.value.pos == 'nn'
        or node.value.function == 'conj' and node.value.pos == 'nn'):
        thing = Thing(noun=node.value, descriptors=[])
        _crawl_descriptors(node.children, thing)
        done.append(thing)

    if node.children is None:
        return

    for child in node.children:
        _crawl_tree(
            child,
            done
        )

def list_subjects(phrase):
    name = check_output('whoami', shell=True)
    safe_phrase = str(phrase).replace("'", '')
    try:
        master_fd, slave_fd = pty.openpty()
        parser = Popen(
            ['/usr/bin/docker', 'run', '--rm', '-i', 'local/syntaxnet-docker', 'syntaxnet/demo.sh'],
            # ['sudo docker run --rm -i tensorflow/syntaxnet:v01 sudo syntaxnet/demo.sh'],
            # ['sudo', 'docker', 'restart', 'syntaxnet'],
            stdin=PIPE,
            stdout=PIPE
        )
    except Exception as e:
        print e
        raise
    lines = parser.communicate(phrase)[0].split('\n')
    table = []
    for line in lines:
        if re.match('^\d+.*$', line):
            table.append(line.split('\t')[:-1])

    terms = [_line_to_terms(line) for line in table]

    for term in terms:
        if term.parent == 0:
            root = term
            break

    node = _make_tree(root, terms)

    things = []
    _crawl_tree(node, things)
    subjects = []
    for thing in things:
        descriptors = sorted(thing.descriptors, key=lambda a: a.id)
        subject = thing.noun.word.lower()
        if len(descriptors) > 0:
            subject = ' {}'.format(subject)

        subjects.append('{}{}'.format(' '.join([descriptor.word.lower() for descriptor in descriptors]), subject))

    return subjects
