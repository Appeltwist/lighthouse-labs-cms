from io import BytesIO
from urllib.parse import urlparse

from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image as PilImage
from wagtail.images import get_image_model
from wagtail.models import Site

from pages.models import AboutPage, ContactPage, HomePage, Person, Project, ProjectsPage, Space, SpacesPage
from siteconfig.models import BrandSettings, ContactSettings, SiteChromeSettings


@override_settings(ALLOWED_HOSTS=["testserver", "lighthouse-labs.local", "localhost", "127.0.0.1"])
class LighthouseLabsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_lighthouse_labs_site", "--hostname", "lighthouse-labs.local")

    def test_seed_command_is_idempotent(self):
        call_command("seed_lighthouse_labs_site", "--hostname", "lighthouse-labs.local")
        self.assertEqual(Site.objects.filter(hostname="lighthouse-labs.local").count(), 1)
        self.assertEqual(HomePage.objects.count(), 1)
        self.assertEqual(AboutPage.objects.count(), 1)
        self.assertEqual(SpacesPage.objects.count(), 1)
        self.assertEqual(ProjectsPage.objects.count(), 1)
        self.assertEqual(ContactPage.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 7)
        self.assertEqual(Project.objects.count(), 22)

    def test_site_config_returns_expected_shape(self):
        response = self.client.get("/api/site-config", {"domain": "lighthouse-labs.local", "locale": "fr"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["site"]["slug"], "lighthouse-labs")
        self.assertEqual(payload["defaultLocale"], "fr")
        self.assertEqual(payload["locales"], ["fr", "en"])
        self.assertEqual(payload["brand"]["siteName"], "Lighthouse Labs")
        self.assertEqual(payload["contact"]["email"], "info@f-lh.be")
        self.assertEqual(payload["nav"][0]["label"], "A propos")

    def test_home_returns_structured_sections(self):
        response = self.client.get("/api/home", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["hero"]["primaryCta"]["href"], "/spaces")
        self.assertEqual(payload["hero"]["secondaryCta"]["href"], "/contact")
        section_types = [section["type"] for section in payload["sections"]]
        self.assertIn("feature_grid", section_types)
        self.assertIn("highlight_strip", section_types)
        self.assertGreaterEqual(section_types.count("gallery"), 2)
        self.assertNotIn("project_highlights", section_types)

    def test_home_space_feature_grid_uses_current_space_image(self):
        light_lab = Space.objects.get(slug="light-lab-studio")
        image_buffer = BytesIO()
        PilImage.new("RGB", (12, 12), color=(210, 140, 90)).save(image_buffer, format="PNG")
        image_buffer.seek(0)
        replacement = get_image_model().objects.create(
            title="Replacement Space Image",
            file=SimpleUploadedFile("replacement-space.png", image_buffer.read(), content_type="image/png"),
        )
        light_lab.main_image = replacement
        light_lab.save(update_fields=["main_image"])

        response = self.client.get("/api/home", {"domain": "lighthouse-labs.local", "locale": "fr"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        feature_grid = next(section for section in payload["sections"] if section["type"] == "feature_grid")
        light_lab_item = next(item for item in feature_grid["items"] if item["href"] == "/spaces#light-lab-studio")
        self.assertTrue(light_lab_item["image"]["url"].endswith(replacement.file.url))

    def test_about_page_is_translated_in_english_and_french(self):
        fr_response = self.client.get("/api/pages/about", {"domain": "lighthouse-labs.local", "locale": "fr"})
        self.assertEqual(fr_response.status_code, 200)
        fr_payload = fr_response.json()
        self.assertEqual(fr_payload["routeKey"], "about")
        self.assertEqual(fr_payload["locale"], "fr")
        self.assertEqual(fr_payload["title"], "A propos")
        self.assertEqual(len(fr_payload["teamMembers"]), 7)
        self.assertIsNotNone(fr_payload["teamMembers"][0]["href"])
        self.assertIsNotNone(fr_payload["teamMembers"][1]["href"])

        en_response = self.client.get("/api/pages/about", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(en_response.status_code, 200)
        en_payload = en_response.json()
        self.assertEqual(en_payload["locale"], "en")
        self.assertEqual(en_payload["title"], "About")
        self.assertIn("Lighthouse Labs is a creative and collaborative space", en_payload["introText"])
        self.assertEqual(en_payload["services"][0]["items"][0]["title"], "Development")

    def test_spaces_page_returns_structured_spaces(self):
        response = self.client.get("/api/pages/spaces", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["routeKey"], "spaces")
        self.assertEqual(len(payload["spaces"]), 4)
        self.assertEqual(payload["spaces"][0]["slug"], "light-lab-studio")
        self.assertEqual(payload["spaces"][0]["offerings"][0]["dailyRate"], "EUR 180 / day excl. VAT")
        canopy = next(space for space in payload["spaces"] if space["slug"] == "canopy-hall")
        self.assertEqual(canopy["offerings"][0]["hourlyRate"], "EUR 100 / hour excl. VAT")
        self.assertTrue(canopy["bookingCta"]["href"].startswith("https://lighthouse-lab.notion.site/"))

    def test_projects_page_is_curated_and_private_projects_do_not_link(self):
        response = self.client.get("/api/pages/projects", {"domain": "lighthouse-labs.local", "locale": "fr"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["routeKey"], "projects")
        self.assertEqual(len(payload["sections"]), 2)
        self.assertEqual(payload["sections"][0]["title"], "Post-production")
        self.assertEqual(len(payload["sections"][0]["projects"]), 13)
        self.assertIsNone(payload["sections"][0]["projects"][0]["href"])
        self.assertEqual(payload["sections"][1]["title"], "Productions Lighthouse Labs")
        self.assertEqual(payload["sections"][1]["projects"][0]["slug"], "here-be-monsters")
        self.assertEqual(payload["sections"][1]["projects"][0]["href"], "/projects/here-be-monsters")

        en_response = self.client.get("/api/pages/projects", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(en_response.status_code, 200)
        en_payload = en_response.json()
        self.assertEqual(en_payload["title"], "Projects")
        self.assertIn("produces films from the original idea", en_payload["introText"])
        self.assertIn("Collaborations in editing", en_payload["sections"][0]["intro"])

    def test_contact_page_falls_back_to_french_default_locale(self):
        response = self.client.get("/api/pages/contact", {"domain": "lighthouse-labs.local", "locale": "de"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["locale"], "fr")
        self.assertIn("Zone de formulaire", payload["formEmbed"])

    def test_public_project_detail_endpoint(self):
        response = self.client.get("/api/projects/the-time-of-the-fireflies", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["slug"], "the-time-of-the-fireflies")
        self.assertEqual(payload["metadata"]["productionCountries"], "Belgium, U.S.A., Mexico")
        self.assertEqual(payload["metadata"]["format"], "Documentary")
        self.assertEqual(len(payload["externalLinks"]), 3)
        self.assertGreaterEqual(len(payload["credits"]), 1)
        self.assertEqual(len(payload["collaborators"]), 2)
        self.assertIn("violence, borders, and memory", payload["synopsis"])

    def test_private_project_detail_returns_404(self):
        response = self.client.get("/api/projects/four-brothers", {"domain": "lighthouse-labs.local"})
        self.assertEqual(response.status_code, 404)

    def test_public_person_detail_endpoint_does_not_expose_email(self):
        response = self.client.get("/api/people/mattis-appelqvist", {"domain": "lighthouse-labs.local", "locale": "en"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["slug"], "mattis-appelqvist")
        self.assertGreaterEqual(len(payload["relatedProjects"]), 3)
        self.assertEqual(payload["primaryCta"]["href"], "/contact")
        self.assertEqual(payload["role"], "Composer & Director")
        section_types = [section["type"] for section in payload["sections"]]
        self.assertIn("embed", section_types)
        self.assertIn("audio_playlist", section_types)
        audio_section = next(section for section in payload["sections"] if section["type"] == "audio_playlist")
        self.assertEqual(len(audio_section["tracks"]), 5)
        self.assertTrue(audio_section["tracks"][0]["audioUrl"].endswith(".mp3"))
        self.assertNotIn("email", payload)

    def test_audio_media_supports_range_requests_for_seeking(self):
        response = self.client.get("/api/people/mattis-appelqvist", {"domain": "lighthouse-labs.local"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        audio_section = next(section for section in payload["sections"] if section["type"] == "audio_playlist")
        audio_path = urlparse(audio_section["tracks"][0]["audioUrl"]).path

        range_response = self.client.get(audio_path, HTTP_RANGE="bytes=0-1023")
        self.assertEqual(range_response.status_code, 206)
        self.assertEqual(range_response["Accept-Ranges"], "bytes")
        self.assertTrue(range_response["Content-Range"].startswith("bytes 0-1023/"))
        self.assertEqual(int(range_response["Content-Length"]), 1024)
        self.assertEqual(len(b"".join(range_response.streaming_content)), 1024)

    def test_private_person_detail_returns_404(self):
        Person.objects.create(name="Private Person", slug="private-person", has_public_profile=False)
        response = self.client.get("/api/people/private-person", {"domain": "lighthouse-labs.local"})
        self.assertEqual(response.status_code, 404)

    def test_seed_creates_site_settings(self):
        site = Site.objects.get(hostname="lighthouse-labs.local")
        self.assertTrue(BrandSettings.objects.filter(site=site).exists())
        self.assertTrue(SiteChromeSettings.objects.filter(site=site).exists())
        self.assertTrue(ContactSettings.objects.filter(site=site).exists())

    def test_health_and_admin_routes_resolve(self):
        self.assertEqual(self.client.get("/health/").status_code, 200)
        self.assertIn(self.client.get("/django-admin/").status_code, {200, 302})
        self.assertEqual(self.client.get("/cms/").status_code, 302)
