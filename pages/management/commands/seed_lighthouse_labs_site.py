from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from pages.models import HomePage, NarrativePage
from siteconfig.models import BrandSettings, SiteChromeSettings


PAGE_COPY = {
    "about": {
        "en": {
            "title": "About Lighthouse Labs",
            "subtitle": "A studio platform for cinema and film development.",
            "body": "<p>Lighthouse Labs brings together production thinking, cinema culture, and public storytelling under one editorial roof.</p>",
        },
        "fr": {
            "title": "A propos de Lighthouse Labs",
            "subtitle": "Une plateforme studio pour le cinema et le developpement de films.",
            "body": "<p>Lighthouse Labs rassemble la production, la culture cinematographique et le recit public sous une meme direction editoriale.</p>",
        },
    },
    "studios": {
        "en": {
            "title": "Studios",
            "subtitle": "Production spaces, collaborations, and resident initiatives.",
            "body": "<p>Use this page to introduce the studio ecosystem, resident teams, and current collaborations.</p>",
        },
        "fr": {
            "title": "Studios",
            "subtitle": "Espaces de production, collaborations et initiatives residentes.",
            "body": "<p>Utilisez cette page pour presenter l ecosysteme studio, les equipes residentes et les collaborations en cours.</p>",
        },
    },
    "film-projects": {
        "en": {
            "title": "Film Projects",
            "subtitle": "Projects in development, production, and release.",
            "body": "<p>This foundation page is ready to evolve into the public overview for productions and film projects.</p>",
        },
        "fr": {
            "title": "Projets de films",
            "subtitle": "Projets en developpement, en production et en diffusion.",
            "body": "<p>Cette page de base pourra evoluer vers une vue publique des productions et projets cinematographiques.</p>",
        },
    },
    "cinema": {
        "en": {
            "title": "Cinema",
            "subtitle": "Screenings, programs, and public-facing cinema activity.",
            "body": "<p>Use this page for screenings, curated programs, and the public cinema calendar once the catalog layer is added.</p>",
        },
        "fr": {
            "title": "Cinema",
            "subtitle": "Projections, programmes et activites cinema ouvertes au public.",
            "body": "<p>Utilisez cette page pour les projections, les programmes et le calendrier public lorsque la couche catalogue sera ajoutee.</p>",
        },
    },
    "contact": {
        "en": {
            "title": "Contact",
            "subtitle": "Editorial, partnerships, and studio inquiries.",
            "body": "<p>Point visitors to the right inbox for editorial, partnerships, or production-related conversations.</p>",
        },
        "fr": {
            "title": "Contact",
            "subtitle": "Editorial, partenariats et demandes liees au studio.",
            "body": "<p>Orientez les visiteurs vers la bonne boite mail pour l editorial, les partenariats ou les demandes de production.</p>",
        },
    },
}


class Command(BaseCommand):
    help = "Create or update the Lighthouse Labs starter site scaffold."

    def add_arguments(self, parser):
        parser.add_argument("--hostname", default="lighthouse-labs.local")
        parser.add_argument("--site-name", default="Lighthouse Labs")
        parser.add_argument("--site-slug", default="lighthouse-labs")

    def handle(self, *args, **options):
        hostname = options["hostname"].strip().lower()
        site_name = options["site_name"].strip()
        site_slug = options["site_slug"].strip()

        site = Site.objects.filter(hostname=hostname).first()
        home_page = site.root_page.specific if site and site.root_page_id else None

        if not isinstance(home_page, HomePage):
            root_page = Page.get_first_root_node()
            home_page = HomePage(title=f"{site_name} Home", slug=f"{site_slug}-home")
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()
            if site is None:
                site = Site.objects.create(
                    hostname=hostname,
                    site_name=site_name,
                    root_page=home_page,
                    is_default_site=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Created Wagtail site {hostname}"))
            else:
                site.root_page = home_page
                site.site_name = site_name
                site.save(update_fields=["site_name", "root_page"])
                self.stdout.write(self.style.SUCCESS(f"Updated Wagtail site {hostname}"))
        else:
            site.site_name = site_name
            site.root_page = home_page
            site.save(update_fields=["site_name", "root_page"])
            self.stdout.write(self.style.SUCCESS(f"Updated Wagtail site {hostname}"))

        home_page.hero_eyebrow_en = "Cinema Studios & Film Projects"
        home_page.hero_eyebrow_fr = "Studios de cinema et projets de films"
        home_page.hero_title_en = "Lighthouse Labs"
        home_page.hero_title_fr = "Lighthouse Labs"
        home_page.hero_body_en = (
            "<p>A new editorial and production platform for cinema studios, film development, and public-facing programs.</p>"
        )
        home_page.hero_body_fr = (
            "<p>Une nouvelle plateforme editoriale et de production pour les studios de cinema, le developpement de films et les programmes publics.</p>"
        )
        home_page.intro_heading_en = "A clean starter for the next phase"
        home_page.intro_heading_fr = "Une base claire pour la suite"
        home_page.intro_body_en = (
            "<p>This foundation keeps the CMS, site settings, and frontend architecture small while leaving room for a richer catalog later.</p>"
        )
        home_page.intro_body_fr = (
            "<p>Cette base garde le CMS, les reglages du site et l architecture frontend legers, tout en laissant de la place pour un catalogue plus riche ensuite.</p>"
        )
        home_page.featured_tiles_en = [
            {"type": "tile", "value": {"title": "Studios", "description": "Introduce spaces, collaborators, and production capacity.", "cta_label": "Explore studios", "cta_href": "/studios"}},
            {"type": "tile", "value": {"title": "Film Projects", "description": "Publish the next layer of projects and productions.", "cta_label": "See projects", "cta_href": "/film-projects"}},
            {"type": "tile", "value": {"title": "Cinema", "description": "Prepare public-facing screenings, programs, and cinema activity.", "cta_label": "Open cinema", "cta_href": "/cinema"}},
        ]
        home_page.featured_tiles_fr = [
            {"type": "tile", "value": {"title": "Studios", "description": "Presentez les espaces, les collaborateurs et la capacite de production.", "cta_label": "Explorer les studios", "cta_href": "/studios"}},
            {"type": "tile", "value": {"title": "Projets de films", "description": "Publiez ensuite les projets et productions.", "cta_label": "Voir les projets", "cta_href": "/film-projects"}},
            {"type": "tile", "value": {"title": "Cinema", "description": "Preparez les projections, les programmes et l activite publique du cinema.", "cta_label": "Ouvrir cinema", "cta_href": "/cinema"}},
        ]
        home_page.sections_en = [
            {
                "type": "feature_stack",
                "value": {
                    "heading": "What this starter includes",
                    "items": [
                        {"title": "Bilingual editorial pages", "body": "<p>English and French content are ready from day one.</p>"},
                        {"title": "Site-driven theming", "body": "<p>Brand colors, font token, navigation, and footer are editable in Wagtail settings.</p>"},
                    ],
                },
            }
        ]
        home_page.sections_fr = [
            {
                "type": "feature_stack",
                "value": {
                    "heading": "Ce que cette base comprend",
                    "items": [
                        {"title": "Pages editoriales bilingues", "body": "<p>Le contenu anglais et francais est pret des le premier jour.</p>"},
                        {"title": "Theme pilote par le site", "body": "<p>Les couleurs, la police, la navigation et le footer sont geres dans les reglages Wagtail.</p>"},
                    ],
                },
            }
        ]
        home_page.seo_title_en = "Lighthouse Labs"
        home_page.seo_title_fr = "Lighthouse Labs"
        home_page.seo_description_en = "Foundation CMS and website starter for cinema studios and film projects."
        home_page.seo_description_fr = "Base CMS et site web pour des studios de cinema et des projets de films."
        home_page.save_revision().publish()

        BrandSettings.objects.update_or_create(
            site=site,
            defaults={
                "site_slug": site_slug,
                "default_locale": "en",
                "supported_locales": ["en", "fr"],
                "color_primary": "#1d2a44",
                "color_secondary": "#6a1f2b",
                "color_accent": "#d9b26f",
                "background_color": "#f4efe7",
                "font_family_token": "Iowan Old Style, Georgia, serif",
            },
        )

        chrome, _ = SiteChromeSettings.objects.get_or_create(site=site)
        chrome.primary_nav = [
            {"type": "item", "value": {"label_en": "About", "label_fr": "A propos", "href": "/about"}},
            {"type": "item", "value": {"label_en": "Studios", "label_fr": "Studios", "href": "/studios"}},
            {"type": "item", "value": {"label_en": "Film Projects", "label_fr": "Projets de films", "href": "/film-projects"}},
            {"type": "item", "value": {"label_en": "Cinema", "label_fr": "Cinema", "href": "/cinema"}},
            {"type": "item", "value": {"label_en": "Contact", "label_fr": "Contact", "href": "/contact"}},
        ]
        chrome.footer_groups = [
            {
                "type": "group",
                "value": {
                    "title_en": "Explore",
                    "title_fr": "Explorer",
                    "links": [
                        {"label_en": "About", "label_fr": "A propos", "href": "/about"},
                        {"label_en": "Studios", "label_fr": "Studios", "href": "/studios"},
                        {"label_en": "Film Projects", "label_fr": "Projets de films", "href": "/film-projects"},
                    ],
                },
            },
            {
                "type": "group",
                "value": {
                    "title_en": "Visit",
                    "title_fr": "Visiter",
                    "links": [
                        {"label_en": "Cinema", "label_fr": "Cinema", "href": "/cinema"},
                        {"label_en": "Contact", "label_fr": "Contact", "href": "/contact"},
                    ],
                },
            },
        ]
        chrome.social_links = [
            {"type": "link", "value": {"label": "Instagram", "url": "https://instagram.com/lighthouselabs"}},
            {"type": "link", "value": {"label": "Vimeo", "url": "https://vimeo.com/lighthouselabs"}},
        ]
        chrome.contact_heading_en = "Contact"
        chrome.contact_heading_fr = "Contact"
        chrome.contact_body_en = "<p>Reach the Lighthouse Labs team for editorial, partnership, and studio inquiries.</p>"
        chrome.contact_body_fr = "<p>Contactez l equipe Lighthouse Labs pour les demandes editoriales, de partenariat et de studio.</p>"
        chrome.contact_email = "hello@lighthouselabs.example"
        chrome.announcement_label_en = "Now building"
        chrome.announcement_label_fr = "En construction"
        chrome.announcement_body_en = "The Lighthouse Labs starter is live."
        chrome.announcement_body_fr = "La base Lighthouse Labs est en ligne."
        chrome.announcement_link_label_en = "See contact"
        chrome.announcement_link_label_fr = "Voir contact"
        chrome.announcement_link_url = "/contact"
        chrome.save()

        for route_key, translations in PAGE_COPY.items():
            for locale, page_copy in translations.items():
                self._ensure_narrative_page(
                    home_page=home_page,
                    site=site,
                    route_key=route_key,
                    locale=locale,
                    title=page_copy["title"],
                    subtitle=page_copy["subtitle"],
                    body=page_copy["body"],
                )

        self.stdout.write(self.style.SUCCESS(f"Lighthouse Labs scaffold is ready for {hostname}"))

    def _ensure_narrative_page(self, *, home_page, site, route_key, locale, title, subtitle, body):
        page = NarrativePage.objects.filter(site=site, route_key=route_key, language_code=locale).first()
        if page is None:
            page = NarrativePage(
                title=title,
                slug=f"{route_key}-{locale}",
                site=site,
                route_key=route_key,
                language_code=locale,
            )
            home_page.add_child(instance=page)
        page.title = title
        page.site = site
        page.route_key = route_key
        page.language_code = locale
        page.subtitle = subtitle
        page.hero_title = title
        page.hero_body = body
        page.primary_cta_label = "Contact us" if locale == "en" else "Nous contacter"
        page.primary_cta_url = "/contact"
        page.sections = [
            {
                "type": "rich_section",
                "value": {
                    "heading": "Starter note" if locale == "en" else "Note de base",
                    "body": "<p>This page is seeded as editable foundation content and can be expanded in Wagtail.</p>"
                    if locale == "en"
                    else "<p>Cette page est semee comme contenu de base modifiable et peut etre enrichie dans Wagtail.</p>",
                },
            }
        ]
        page.meta_title = title
        page.meta_description = subtitle
        page.save_revision().publish()
