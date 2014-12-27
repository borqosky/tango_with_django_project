from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from rango.models import Category, Page


def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    p.save()
    return p


class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        Ensure_views_are_positive should results True for categories where views are zero or positive
        """
        cat = add_cat('test')
        self.assertEqual(cat.views >= 0, True)


class PageMethodTests(TestCase):
    def test_ensure_last_or_first_visit_is_future(self):
        """
        Ensure the last visit or first visit is not in the future
        """
        cat = add_cat('test')
        page = add_page(cat, "Python", "http:/python.org", views=45)
        page_first_visit = page.first_visit
        self.assertLess(page.first_visit, timezone.now())

        page.views += 1
        page.save()
        self.assertGreater(page.last_visit, page.first_visit)
        self.assertEqual(page.first_visit, page_first_visit)
        self.assertLess(page.last_visit, timezone.now())

    def test_ensure_last_visit_equal_or_after_first_visit(self):
        """
        Ensure the last visit or first visit is not in the future
        """
        cat = add_cat('test')
        page = add_page(cat, "Python", "http:/python.org", views=45)
        self.assertGreaterEqual(page.last_visit, page.first_visit)


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no categories present.')
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        add_cat('test', 1, 1)
        add_cat('temp', 1, 1)
        add_cat('tmp', 1, 1)
        add_cat('tmp test temp', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tmp test temp')

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)
