from django.core.management import call_command
from django.test import TestCase, override_settings
from wagtail.models import Site

from pages.models import HomePage, NarrativePage
from siteconfig.models import BrandSettings, SiteChromeSettings


@override_settings(ALLOWED_HOSTS=["testserver", "lighthouse-labs.local", "localhost", "127.0.0.1"])
class LighthouseLabsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_lighthouse_labs_site", "--hostname", "lighthouse-labs.local")

    def test_seed_command_is_idempotent(self):
        call_command("seed_lighthouse_labs_site", "--hostname", "lighthouse-labs.local")
        self.assertEqual(Site.objects.filter(hostname="lighthouse-labs.local").count(), 1)
        self.assertEqual(HomePage.objects.count(), 1)
        self.assertEqual(NarrativePage.objects.count(), 10)

    def test_site_config_returns_expected_shape(self):
        response = self.client.get("/api/site-config", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["site"]["slug"], "lighthouse-labs")
        self.assertEqual(payload["defaultLocale"], "en")
        self.assertEqual(payload["locales"], ["en", "fr"])
        self.assertIn("brand", payload)
        self.assertIn("nav", payload)
        self.assertIn("footer", payload)

    def test_home_returns_french_content(self):
        response = self.client.get("/api/home", {"domain": "lighthouse-labs.local", "locale": "fr"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["locale"], "fr")
        self.assertGreaterEqual(len(payload["featuredTiles"]), 1)
        self.assertTrue(payload["featuredTiles"][0]["ctaHref"].startswith("/"))

    def test_narrative_page_returns_requested_locale(self):
        response = self.client.get("/api/pages/about", {"domain": "lighthouse-labs.local", "locale": "fr"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["routeKey"], "about")
        self.assertEqual(payload["locale"], "fr")
        self.assertIn("Lighthouse Labs", payload["title"])

    def test_narrative_page_falls_back_to_default_locale(self):
        response = self.client.get("/api/pages/cinema", {"domain": "lighthouse-labs.local", "locale": "de"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["locale"], "en")

    def test_unknown_page_returns_404(self):
        response = self.client.get("/api/pages/unknown", {"domain": "lighthouse-labs.local"})
        self.assertEqual(response.status_code, 404)

    def test_seed_creates_site_settings(self):
        site = Site.objects.get(hostname="lighthouse-labs.local")
        self.assertTrue(BrandSettings.objects.filter(site=site).exists())
        self.assertTrue(SiteChromeSettings.objects.filter(site=site).exists())
