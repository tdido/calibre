#!/usr/bin/env python
# License: GPLv3 Copyright: 2023, Kovid Goyal <kovid at kovidgoyal.net>


import os

from calibre.db.tests.base import BaseTest


class NotesTest(BaseTest):

    ae = BaseTest.assertEqual

    def test_notes(self):

        def create():
            cache = self.init_cache()
            cache.backend.notes.max_retired_items = 1
            return cache, cache.backend.notes

        cache, notes = create()
        authors = sorted(cache.all_field_ids('authors'))
        self.ae(cache.notes_for('authors', authors[0]), '')
        doc = 'simple notes for an author'
        h1 = cache.add_notes_resource(b'resource1', 'r1.jpg')
        h2 = cache.add_notes_resource(b'resource2', 'r1.jpg')
        self.ae(cache.get_notes_resource(h1)['name'], 'r1.jpg')
        self.ae(cache.get_notes_resource(h2)['name'], 'r1-1.jpg')
        note_id = cache.set_notes_for('authors', authors[0], doc, resource_ids=(h1, h2))
        self.ae(cache.notes_for('authors', authors[0]), doc)
        self.ae(cache.notes_resources_used_by('authors', authors[0]), frozenset({h1, h2}))
        self.ae(cache.get_notes_resource(h1)['data'], b'resource1')
        self.ae(cache.get_notes_resource(h2)['data'], b'resource2')
        doc2 = 'a different note to replace the first one'
        self.ae(note_id, cache.set_notes_for('authors', authors[0], doc2, resource_ids=(h1,)))
        self.ae(cache.notes_for('authors', authors[0]), doc2)
        self.ae(cache.notes_resources_used_by('authors', authors[0]), frozenset({h1}))
        self.ae(cache.get_notes_resource(h1)['data'], b'resource1')
        self.ae(cache.get_notes_resource(h2), None)
        self.assertTrue(os.path.exists(notes.path_for_resource(cache.backend.conn, h1)))
        self.assertFalse(os.path.exists(notes.path_for_resource(cache.backend.conn, h2)))