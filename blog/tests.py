from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Post, Category, Tag, Comment


class BlogProjectTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.category = Category.objects.create(name='tech')
        self.tag = Tag.objects.create(name='django')

        self.post = Post.objects.create(
            title='Test Post',
            content='<p>This is a test blog post.</p>',
            author=self.user,
            category=self.category
        )
        self.post.tag.add(self.tag)

    def test_post_list_page_loads(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_details_page_loads(self):
        response = self.client.get(reverse('post_details', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'This is a test blog post')

    def test_category_filter_works(self):
        response = self.client.get(reverse('post_list'), {'category': 'tech'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_tag_filter_works(self):
        response = self.client.get(reverse('post_list'), {'tag': 'django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_search_works(self):
        response = self.client.get(reverse('post_list'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        response = self.client.get(reverse('singup'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_signup(self):
        response = self.client.post(reverse('singup'), {
            'username': 'newuser',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_page_requires_login_or_loads_after_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_posts_section_loads(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_view'), {'section': 'posts'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_create_post_after_login(self):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('post_create'), {
            'title': 'New Blog Post',
            'content': '<p>This is new content.</p>',
            'category': self.category.id,
            'tag': [self.tag.id],
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Blog Post').exists())

    def test_comment_can_be_added(self):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('post_details', args=[self.post.id]), {
            'content': 'This is a test comment.'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='This is a test comment.').exists())

    def test_like_post_works(self):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('like_post', args=[self.post.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.post.liked_users.filter(id=self.user.id).exists())

    def test_logout_works(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)