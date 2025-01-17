from django.test import TestCase
from django.utils import timezone

from bookmarks.services import exporter
from bookmarks.tests.helpers import BookmarkFactoryMixin


class ExporterTestCase(TestCase, BookmarkFactoryMixin):
    def test_export_bookmarks(self):
        added = timezone.now()
        timestamp = int(added.timestamp())

        bookmarks = [
            self.setup_bookmark(url='https://example.com/1', title='Title 1', added=added,
                                description='Example description'),
            self.setup_bookmark(url='https://example.com/2', title='Title 2', added=added,
                                tags=[self.setup_tag(name='tag1'), self.setup_tag(name='tag2'),
                                      self.setup_tag(name='tag3')]),
            self.setup_bookmark(url='https://example.com/3', title='Title 3', added=added, unread=True),
            self.setup_bookmark(url='https://example.com/4', title='Title 4', added=added, shared=True),

        ]
        html = exporter.export_netscape_html(bookmarks)

        lines = [
            f'<DT><A HREF="https://example.com/1" ADD_DATE="{timestamp}" PRIVATE="1" TOREAD="0" TAGS="">Title 1</A>',
            '<DD>Example description',
            f'<DT><A HREF="https://example.com/2" ADD_DATE="{timestamp}" PRIVATE="1" TOREAD="0" TAGS="tag1,tag2,tag3">Title 2</A>',
            f'<DT><A HREF="https://example.com/3" ADD_DATE="{timestamp}" PRIVATE="1" TOREAD="1" TAGS="">Title 3</A>',
            f'<DT><A HREF="https://example.com/4" ADD_DATE="{timestamp}" PRIVATE="0" TOREAD="0" TAGS="">Title 4</A>',
        ]
        self.assertIn('\n\r'.join(lines), html)

    def test_escape_html_in_title_and_description(self):
        bookmark = self.setup_bookmark(
            title='<style>: The Style Information element',
            description='The <style> HTML element contains style information for a document, or part of a document.'
        )
        html = exporter.export_netscape_html([bookmark])

        self.assertIn('&lt;style&gt;: The Style Information element', html)
        self.assertIn(
            'The &lt;style&gt; HTML element contains style information for a document, or part of a document.',
            html
        )

    def test_handle_empty_values(self):
        bookmark = self.setup_bookmark()
        bookmark.title = ''
        bookmark.description = ''
        bookmark.website_title = None
        bookmark.website_description = None
        bookmark.save()
        exporter.export_netscape_html([bookmark])
