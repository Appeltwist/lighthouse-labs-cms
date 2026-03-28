from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions
from django.core.management.base import BaseCommand
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection, Page, Site

from pages.models import (
    AboutPage,
    AboutPageTeamMember,
    ContactPage,
    HomePage,
    Person,
    PersonLink,
    PersonRelatedProject,
    Project,
    ProjectCollaborator,
    ProjectCredit,
    ProjectExternalLink,
    ProjectGalleryImage,
    ProjectsPage,
    ProjectsPageSection,
    ProjectsPageSectionProject,
    Space,
    SpaceGalleryImage,
    SpaceOffering,
    SpacesPage,
    SpacesPageSpace,
)
from siteconfig.models import BrandSettings, ContactSettings, SiteChromeSettings


BOOKING_URL = "https://lighthouse-lab.notion.site/1f3ab2317b4c80b7ab9ef5a765499d9f"
SHOWREEL_URL = "https://vimeo.com/657051216"
LOGO_ASSET_PATH = Path(settings.BASE_DIR) / "pages" / "seed_assets" / "branding" / "lighthouse-labs-logo.jpeg"
LOGO_URL = "https://lighthouse-labs.be/wp-content/uploads/sites/16/2021/12/LOGOlower.png"
MATTIS_SHOWREEL_EMBED_URL = "https://player.vimeo.com/video/950338293?badge=0&autopause=0&player_id=0&app_id=58479"
MATTIS_AUDIO_ASSET_DIR = Path(settings.BASE_DIR) / "pages" / "seed_assets" / "audio" / "mattis"

PERSON_IMAGE_URLS = {
    "nikos-appelqvist": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/079A2148-300x300.jpeg",
    "maxime-jouret": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/079A2197-300x300.jpg",
    "ngare-falise": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/079A1867-300x300.jpeg",
    "mattis-appelqvist": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/079A1906-300x300.jpeg",
    "marguerite-de-saint-andre": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/079A3530-300x300.jpeg",
    "matteo-robert-morales": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2025/09/RobertMorales_ElTiempoDeLasLuciernagas-300x300.jpg",
    "hugo-malidin": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2025/09/WhatsApp-Image-2025-09-03-at-14.50.44-300x300.jpeg",
}

PROJECT_IMAGE_URLS = {
    "here-be-monsters": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/HBM-scaled.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/HBM-scaled.jpg",
        ],
    },
    "le-passage": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/1ere-de-couverture.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/1ere-de-couverture.jpg",
        ],
    },
    "the-time-of-the-fireflies": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/TTOTF.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/11/TTOTF3.jpg",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/12/laurels.jpg",
        ],
    },
    "dashavatar": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/BETZA2.png",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/BETZA2.png",
        ],
    },
    "the-dictator-catherine-graindorge-feat-iggy-pop": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/iggyyy.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/11/iggysquare.jpg",
        ],
    },
    "terra-nostra": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/JONAH.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/JONAH.jpg",
        ],
    },
    "bhaba": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/BHABA-1.jpeg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/BHABA-1.jpeg",
        ],
    },
    "masterclass": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/masterclass-poster.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/masterclass-poster.jpg",
        ],
    },
    "pinacoteka": {
        "cover": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/TIM.jpg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/TIM.jpg",
        ],
    },
}

SPACE_IMAGE_URLS = {
    "light-lab-studio": {
        "main": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/11/STUDIO-1024x636-1.jpeg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/11/STUDIO-1024x636-1.jpeg",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/STUDIO-1024x636-2.jpeg",
        ],
    },
    "spectrum-studio": {
        "main": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/STUDIO-1024x636-2.jpeg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/STUDIO-1024x636-2.jpeg",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/10/STUDIO-1024x636-1.jpeg",
        ],
    },
    "canopy-hall": {
        "main": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2025/08/24072025-DSCF0929-Large-2.jpeg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2025/08/24072025-DSCF0929-Large-2.jpeg",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/12/collabs.jpg",
        ],
    },
    "basecamp-space": {
        "main": "https://lighthouse-labs.be/wp-content/uploads/sites/16/2025/08/24072025-DSCF0929-Large-2.jpeg",
        "gallery": [
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2025/08/24072025-DSCF0929-Large-2.jpeg",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/12/collabs.jpg",
        ],
    },
}

MATTIS_AUDIO_TRACKS = [
    {
        "slug": "ostvind",
        "title": "Østvind",
        "artist": "Mattis Appelqvist",
        "external_url": "https://soundcloud.com/user-87256164/ostvind/s-gaUVpH4rbcc",
        "cover_url": "https://i1.sndcdn.com/artworks-gsxBFr5qB8qEMi2B-qUdSFQ-original.jpg",
        "file_name": "ostvind.mp3",
    },
    {
        "slug": "luciernagas-1",
        "title": "Luciérnagas 1",
        "artist": "Mattis Appelqvist",
        "external_url": "https://soundcloud.com/user-87256164/luciernagas-1/s-BhkUhqG0Aqo",
        "cover_url": "https://i1.sndcdn.com/artworks-k9adXyUeA1zyv4JA-cDEZow-original.jpg",
        "file_name": "luciernagas-1.mp3",
    },
    {
        "slug": "healing",
        "title": "Healing",
        "artist": "Mattis Appelqvist",
        "external_url": "https://soundcloud.com/user-87256164/healing/s-ZOwK2bzmyoH",
        "cover_url": "https://i1.sndcdn.com/artworks-1k8dxvHHCmdfx6mK-Vj0V8Q-original.jpg",
        "file_name": "healing.mp3",
    },
    {
        "slug": "northern-light",
        "title": "Northern Light",
        "artist": "Mattis Appelqvist",
        "external_url": "https://soundcloud.com/user-87256164/northern-light/s-sXsIwMo8OWZ",
        "cover_url": "https://i1.sndcdn.com/artworks-1ZLKD1enMtEdOaM3-3c3qMA-original.jpg",
        "file_name": "northern-light.mp3",
    },
    {
        "slug": "i-was-still-here",
        "title": "I was still here",
        "artist": "Mattis Appelqvist",
        "external_url": "https://soundcloud.com/user-87256164/i-was-still-here/s-DKoOf2TogH9",
        "cover_url": "https://i1.sndcdn.com/artworks-k9adXyUeA1zyv4JA-cDEZow-original.jpg",
        "file_name": "i-was-still-here.mp3",
    },
]


class Command(BaseCommand):
    help = "Create or update the Lighthouse Labs v1 content architecture."

    def add_arguments(self, parser):
        parser.add_argument("--hostname", default="lighthouse-labs.local")
        parser.add_argument("--site-name", default="Lighthouse Labs")

    def handle(self, *args, **options):
        hostname = options["hostname"].strip().lower()
        site_name = options["site_name"].strip()
        self.image_model = get_image_model()
        self.document_model = get_document_model()
        self.root_collection = Collection.get_first_root_node()
        self.image_cache = {}

        site = Site.objects.filter(hostname=hostname).first()
        home_page = site.root_page.specific if site and site.root_page_id else None

        if not isinstance(home_page, HomePage):
            root_page = Page.get_first_root_node()
            home_page = HomePage(title=site_name, slug="lighthouse-labs")
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()
            if site is None:
                site = Site.objects.create(
                    hostname=hostname,
                    site_name=site_name,
                    root_page=home_page,
                    is_default_site=Site.objects.count() == 0,
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

        brand, _ = BrandSettings.objects.get_or_create(site=site)
        brand.site_name = site_name
        brand.default_locale = "fr"
        brand.supported_locales = ["fr", "en"]
        brand.primary_color = "#171513"
        brand.secondary_color = "#bb6b3c"
        brand_logo = self._import_local_image("Lighthouse Labs Logo", LOGO_ASSET_PATH)
        if brand_logo is None:
            brand_logo = self._import_remote_image("Lighthouse Labs Logo", LOGO_URL)
        if brand_logo is not None:
            brand.logo = brand_logo
        brand.save()

        chrome, _ = SiteChromeSettings.objects.get_or_create(site=site)
        chrome.nav_items = [
            {"type": "item", "value": {"label": "About", "label_fr": "A propos", "href": "/about"}},
            {"type": "item", "value": {"label": "Spaces", "label_fr": "Espaces", "href": "/spaces"}},
            {"type": "item", "value": {"label": "Projects", "label_fr": "Projets", "href": "/projects"}},
            {"type": "item", "value": {"label": "Contact", "label_fr": "Contact", "href": "/contact"}},
        ]
        chrome.footer_columns = [
            {
                "type": "column",
                "value": {
                    "title": "Explore",
                    "title_fr": "Explorer",
                    "links": [
                        {"label": "About", "label_fr": "A propos", "href": "/about"},
                        {"label": "Spaces", "label_fr": "Espaces", "href": "/spaces"},
                        {"label": "Projects", "label_fr": "Projets", "href": "/projects"},
                        {"label": "Contact", "label_fr": "Contact", "href": "/contact"},
                    ],
                },
            },
            {
                "type": "column",
                "value": {
                    "title": "Book a space",
                    "title_fr": "Reserver un espace",
                    "links": [
                        {"label": "Book online", "label_fr": "Reserver en ligne", "href": BOOKING_URL, "open_in_new_tab": True},
                        {"label": "Showreel", "label_fr": "Showreel", "href": SHOWREEL_URL, "open_in_new_tab": True},
                    ],
                },
            },
        ]
        chrome.announcement_text = ""
        chrome.announcement_text_fr = ""
        chrome.announcement_link_label = ""
        chrome.announcement_link_label_fr = ""
        chrome.announcement_link = ""
        chrome.save()

        ContactSettings.objects.update_or_create(
            site=site,
            defaults={
                "email": "info@f-lh.be",
                "phone": "+32 498 97 08 84",
                "address": "274 Rue des Allies, 1190 Forest, Brussels, Belgium",
                "google_maps_link": "https://www.google.com/maps/search/?api=1&query=274+Rue+des+Allies+1190+Forest+Belgium",
                "instagram": "",
                "vimeo": "",
                "linkedin": "",
            },
        )

        people = self._seed_people()
        projects = self._seed_projects(people)
        self._seed_person_related_projects(people, projects)
        self._seed_person_profiles(people, projects)
        spaces = self._seed_spaces()

        self._seed_home_page(home_page, projects, spaces)
        about_page = self._ensure_child_page(home_page, AboutPage, "about", "About")
        spaces_page = self._ensure_child_page(home_page, SpacesPage, "spaces", "Spaces")
        projects_page = self._ensure_child_page(home_page, ProjectsPage, "projects", "Projects")
        contact_page = self._ensure_child_page(home_page, ContactPage, "contact", "Contact")

        self._seed_about_page(about_page, people)
        self._seed_spaces_page(spaces_page, spaces)
        self._seed_projects_page(projects_page, projects)
        self._seed_contact_page(contact_page)

        self.stdout.write(self.style.SUCCESS(f"Lighthouse Labs v1 content is ready for {hostname}"))

    def _ensure_child_page(self, parent_page, model_class, slug, title):
        page = model_class.objects.child_of(parent_page).filter(slug=slug).first()
        if page is None:
            page = model_class(title=title, slug=slug)
            parent_page.add_child(instance=page)
        page.title = title
        return page

    def _import_remote_image(self, title, url):
        if not title or not url:
            return None

        file_name = Path(unquote(urlsplit(url).path)).name or f"{title.lower().replace(' ', '-')}.jpg"

        if title in self.image_cache:
            return self.image_cache[title]

        existing = self.image_model.objects.filter(title=title).first()

        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urlopen(request, timeout=20) as response:
                content = response.read()
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            self.stdout.write(self.style.WARNING(f"Could not import image '{title}' from {url}: {exc}"))
            self.image_cache[title] = None
            return None

        image = existing or self.image_model(title=title, collection=self.root_collection)
        image.title = title
        if not image.collection_id:
            image.collection = self.root_collection
        image.file.save(file_name, ContentFile(content), save=False)
        image.width, image.height = get_image_dimensions(image.file)
        image._set_image_file_metadata()
        image.save()
        self.image_cache[title] = image
        return image

    def _import_gallery(self, prefix, urls):
        images = []
        for index, url in enumerate(urls, start=1):
            image = self._import_remote_image(f"{prefix} {index}", url)
            if image is not None:
                images.append(image)
        return images

    def _import_local_image(self, title, file_path):
        path = Path(file_path)
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Could not import image '{title}': {path} does not exist."))
            return None

        if title in self.image_cache:
            return self.image_cache[title]

        existing = self.image_model.objects.filter(title=title).first()
        image = existing or self.image_model(title=title, collection=self.root_collection)
        image.title = title
        if not image.collection_id:
            image.collection = self.root_collection
        with path.open("rb") as source:
            image.file.save(path.name, ContentFile(source.read()), save=False)
        image.width, image.height = get_image_dimensions(image.file)
        image._set_image_file_metadata()
        image.save()
        self.image_cache[title] = image
        return image

    def _import_local_document(self, title, file_path):
        path = Path(file_path)
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Could not import document '{title}': {path} does not exist."))
            return None

        existing = self.document_model.objects.filter(title=title).first()
        document = existing or self.document_model(title=title, collection=self.root_collection)
        document.title = title
        if not document.collection_id:
            document.collection = self.root_collection
        with path.open("rb") as source:
            document.file.save(path.name, ContentFile(source.read()), save=False)
        document.save()
        return document

    def _seed_people(self):
        Person.objects.filter(slug__in=["mattis-appelt", "sarah-van-loon", "amalie-de-smet"]).delete()
        records = [
            {
                "slug": "nikos-appelqvist",
                "name": "Nikos Appelqvist",
                "has_public_profile": True,
                "email": "nikos.appelquist@gmail.com",
                "role": "D.O.P & Director",
                "role_fr": "D.O.P & Director",
                "short_bio": "Filmmaker and cinematographer involved in Lighthouse Labs documentary productions and development.",
                "short_bio_fr": "Cineaste et directeur de la photographie implique dans les productions et developpements documentaires de Lighthouse Labs.",
                "full_bio": "<p>Nikos Appelqvist works with Lighthouse Labs as a director and cinematographer across development, shooting, and the circulation of films.</p>",
                "full_bio_fr": "<p>Nikos Appelqvist accompagne Lighthouse Labs comme realisateur et directeur de la photographie, entre developpement, tournage et circulation des films.</p>",
                "links": [],
            },
            {
                "slug": "maxime-jouret",
                "name": "Maxime Jouret",
                "has_public_profile": True,
                "email": "max.jouret@gmail.com",
                "role": "Editor",
                "role_fr": "Monteur",
                "short_bio": "Editor and post-production collaborator working across films, music videos, and hybrid formats.",
                "short_bio_fr": "Monteur et collaborateur post-production sur des films, clips et formats hybrides.",
                "full_bio": "<p>Maxime Jouret contributes editing and editorial guidance to projects developed and hosted by Lighthouse Labs.</p>",
                "full_bio_fr": "<p>Maxime Jouret intervient sur le montage et l accompagnement editorial de projets accueillis par Lighthouse Labs.</p>",
                "links": [],
            },
            {
                "slug": "ngare-falise",
                "name": "N'gare Falise",
                "has_public_profile": True,
                "email": "n.falise@hotmail.com",
                "role": "D.O.P & Colorist",
                "role_fr": "D.O.P & Colorist",
                "short_bio": "Cinematographer and colorist working across film, music, and commissioned image-making.",
                "short_bio_fr": "Directeur de la photographie et coloriste intervenant sur des projets cinema, musicaux et publicitaires.",
                "full_bio": "<p>N'gare Falise collaborates with Lighthouse Labs on image and color finishing, with particular attention to texture and post-production workflows.</p>",
                "full_bio_fr": "<p>N'gare Falise accompagne Lighthouse Labs sur l image et l etalonnage, avec une attention particuliere aux textures et aux flux de finition.</p>",
                "links": [],
            },
            {
                "slug": "mattis-appelqvist",
                "name": "Mattis Appelqvist Dalton",
                "has_public_profile": True,
                "email": "mattis.dalton@gmail.com",
                "role": "Composer & Director",
                "role_fr": "Composer & Director",
                "short_bio": "Director and composer working across film production, music videos, and educational formats.",
                "short_bio_fr": "Realisateur et compositeur, implique dans la production de films, videos musicales et contenus educatifs.",
                "full_bio": "",
                "full_bio_fr": "",
                "links": [],
            },
            {
                "slug": "marguerite-de-saint-andre",
                "name": "Marguerite De Saint Andre",
                "has_public_profile": True,
                "email": "",
                "role": "Screenwriter & Producer",
                "role_fr": "Screenwriter & Producer",
                "short_bio": "Screenwriter and producer within the Lighthouse Labs team.",
                "short_bio_fr": "Scenariste et productrice au sein de l equipe Lighthouse Labs.",
                "full_bio": "<p>Marguerite De Saint Andre supports the development, writing, and production of films carried by Lighthouse Labs.</p>",
                "full_bio_fr": "<p>Marguerite De Saint Andre accompagne le developpement, l ecriture et la production de films portes par Lighthouse Labs.</p>",
                "links": [],
            },
            {
                "slug": "matteo-robert-morales",
                "name": "Matteo Robert Morales",
                "has_public_profile": True,
                "email": "",
                "role": "D.O.P & Director",
                "role_fr": "D.O.P & Director",
                "short_bio": "Cinematographer and director collaborating on documentary productions and artists’ moving-image work.",
                "short_bio_fr": "Directeur de la photographie et realisateur collaborant sur des productions documentaires et des videos d artistes.",
                "full_bio": "<p>Matteo Robert Morales works with Lighthouse Labs on documentary projects and short forms as a director and cinematographer.</p>",
                "full_bio_fr": "<p>Matteo Robert Morales collabore avec Lighthouse Labs sur des projets documentaires et des formes courtes, comme realisateur et directeur de la photographie.</p>",
                "links": [],
            },
            {
                "slug": "hugo-malidin",
                "name": "Hugo Malidin",
                "has_public_profile": True,
                "email": "",
                "role": "D.O.P & Colorist",
                "role_fr": "D.O.P & Colorist",
                "short_bio": "Cinematographer and colorist working within the studio’s wider production network.",
                "short_bio_fr": "Chef operateur et coloriste au sein du reseau de collaborateurs du studio.",
                "full_bio": "<p>Hugo Malidin contributes image and finishing expertise within Lighthouse Labs production workflows.</p>",
                "full_bio_fr": "<p>Hugo Malidin intervient sur l image et la finition au sein des workflows de Lighthouse Labs.</p>",
                "links": [],
            },
        ]

        seeded_people = {}
        for record in records:
            person, _ = Person.objects.get_or_create(slug=record["slug"], defaults={"name": record["name"]})
            person.name = record["name"]
            person.has_public_profile = record["has_public_profile"]
            person.email = record["email"]
            person.role = record["role"]
            person.role_fr = record["role_fr"]
            person.short_bio = record["short_bio"]
            person.short_bio_fr = record["short_bio_fr"]
            person.profile_intro = ""
            person.profile_intro_fr = ""
            person.primary_cta_label = ""
            person.primary_cta_label_fr = ""
            person.primary_cta_link = ""
            person.full_bio = record["full_bio"]
            person.full_bio_fr = record["full_bio_fr"]
            person.profile_sections = []
            person.profile_sections_fr = []
            profile_image = self._import_remote_image(
                f"{record['name']} Profile",
                PERSON_IMAGE_URLS.get(record["slug"]),
            )
            if profile_image is not None:
                person.profile_image = profile_image
            person.save()
            person.links.all().delete()
            for link in record["links"]:
                PersonLink.objects.create(person=person, **link)
            seeded_people[record["slug"]] = person
        return seeded_people

    def _seed_projects(self, people):
        Project.objects.filter(slug__in=["deep-channel-session", "iggy-pop-archive-clip"]).delete()
        post_production_records = [
            {"slug": "four-brothers", "title": "Four Brothers", "listing_summary": "Assistant editing - Maxime Jouret", "listing_summary_fr": "Assistanat - Maxime Jouret"},
            {"slug": "les-heures-creuses", "title": "Les Heures Creuses", "listing_summary": "Color grading - N'gare Falise", "listing_summary_fr": "Etalonnage - N'gare Falise"},
            {"slug": "ma-jolie-poupee-cherie", "title": "Ma jolie poupee cherie", "listing_summary": "Color grading - N'gare Falise", "listing_summary_fr": "Etalonnage - N'gare Falise"},
            {"slug": "alice-et-les-soleils", "title": "Alice et les Soleils", "listing_summary": "Color grading - N'gare Falise", "listing_summary_fr": "Etalonnage - N'gare Falise"},
            {"slug": "une-jeunesse-aimable", "title": "Une jeunesse aimable", "listing_summary": "Color grading - N'gare Falise", "listing_summary_fr": "Etalonnage - N'gare Falise"},
            {"slug": "combustion", "title": "Combustion", "listing_summary": "Editing - Maxime Jouret", "listing_summary_fr": "Montage - Maxime Jouret"},
            {"slug": "isaac-manque", "title": "Isaac - Manque", "listing_summary": "Editing - Maxime Jouret", "listing_summary_fr": "Montage - Maxime Jouret"},
            {"slug": "prattseul-cache-cache", "title": "Prattseul - Cache Cache", "listing_summary": "Editing - Maxime Jouret", "listing_summary_fr": "Montage - Maxime Jouret"},
            {"slug": "robbing-millions-same-skin", "title": "Robbing Millions - Same Skin", "listing_summary": "Editing - Maxime Jouret", "listing_summary_fr": "Montage - Maxime Jouret"},
            {"slug": "glauque-pas-le-choix", "title": "Glauque - Pas le choix", "listing_summary": "Editing - Maxime Jouret", "listing_summary_fr": "Montage - Maxime Jouret"},
            {"slug": "rive-amour", "title": "Rive - Amour", "listing_summary": "Editing - Maxime Jouret", "listing_summary_fr": "Montage - Maxime Jouret"},
            {"slug": "ser-semilla", "title": "Ser Semilla", "listing_summary": "Composition - Mattis Appelqvist / Mix - Nathan Foucray", "listing_summary_fr": "Composition - Mattis Appelqvist / Mix - Nathan Foucray"},
            {"slug": "home-movies", "title": "Home Movies", "listing_summary": "Composition - Mattis Appelqvist", "listing_summary_fr": "Composition - Mattis Appelqvist"},
        ]

        production_records = [
            {
                "slug": "here-be-monsters",
                "title": "Here be monsters",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Video",
                "project_type_fr": "Video",
                "year": "2022",
                "directors": "Mattis Appelqvist",
                "directors_fr": "Mattis Appelqvist",
                "production_countries": "Belgium",
                "production_countries_fr": "Belgique",
                "languages": "English",
                "languages_fr": "Anglais",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Video created for an installation by Katja Ebbel.",
                "short_description_fr": "Video creee pour une installation de Katja Ebbel.",
                "synopsis": "<p>Here be monsters is a video made for an installation by Katja Ebbel, produced within Lighthouse Labs' creative activity.</p>",
                "synopsis_fr": "<p>Here be monsters est une video realisee pour l installation de Katja Ebbel, produite dans le cadre des activites de Lighthouse Labs.</p>",
                "full_description": [
                    {
                        "type": "rich_text",
                        "value": {
                            "heading": "About the project",
                            "body": "<p>The project connects image, installation space, and concise writing through a lightweight production and an in-studio finishing workflow.</p>",
                        },
                    }
                ],
                "full_description_fr": [
                    {
                        "type": "rich_text",
                        "value": {
                            "heading": "A propos du projet",
                            "body": "<p>Le projet relie image, espace d installation et ecriture courte, avec une production legere et une finition realisee au studio.</p>",
                        },
                    }
                ],
                "video_embed": "https://player.vimeo.com/video/1018965125",
                "collaborators": ["mattis-appelqvist", "matteo-robert-morales"],
                "credits": [
                    {"role": "Director", "role_fr": "Direction", "value": "Mattis Appelqvist", "value_fr": "Mattis Appelqvist", "person": "mattis-appelqvist"},
                    {"role": "Artist", "role_fr": "Artiste", "value": "Katja Ebbel", "value_fr": "Katja Ebbel"},
                ],
                "external_links": [],
            },
            {
                "slug": "le-passage",
                "title": "La Quête du Rire",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Documentary",
                "project_type_fr": "Documentaire",
                "year": "In production",
                "directors": "Mattis Appelqvist Dalton",
                "directors_fr": "Mattis Appelqvist Dalton",
                "production_countries": "France, Belgium",
                "production_countries_fr": "France, Belgique",
                "languages": "French",
                "languages_fr": "Francais",
                "roles": "Development and production",
                "roles_fr": "Developpement et production",
                "short_description": "Documentary in production around transition, laughter, and collective experience.",
                "short_description_fr": "Documentaire en production autour du passage, du rire et du collectif.",
                "synopsis": "<p>La Quete du Rire follows a documentary inquiry into transition, laughter, and the circulation of a collective gesture.</p>",
                "synopsis_fr": "<p>La Quete du Rire suit une recherche documentaire autour du passage, du rire et de la circulation d un geste collectif.</p>",
                "full_description": [
                    {
                        "type": "rich_text",
                        "value": {
                            "heading": "Project status",
                            "body": "<p>The project is in production and continues its editorial development and fabrication through Lighthouse Labs.</p>",
                        },
                    }
                ],
                "full_description_fr": [
                    {
                        "type": "rich_text",
                        "value": {
                            "heading": "Etat du projet",
                            "body": "<p>Le projet est en production et poursuit son developpement editorial et sa fabrication a travers Lighthouse Labs.</p>",
                        },
                    }
                ],
                "video_embed": "",
                "collaborators": ["mattis-appelqvist", "marguerite-de-saint-andre"],
                "credits": [
                    {"role": "Director", "role_fr": "Direction", "value": "Mattis Appelqvist Dalton", "value_fr": "Mattis Appelqvist Dalton", "person": "mattis-appelqvist"},
                ],
                "external_links": [],
            },
            {
                "slug": "the-time-of-the-fireflies",
                "title": "The Time of the Fireflies",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Documentary",
                "project_type_fr": "Documentaire",
                "year": "2021",
                "directors": "Matteo Robert Morales & Mattis Appelqvist Dalton",
                "directors_fr": "Matteo Robert Morales & Mattis Appelqvist Dalton",
                "production_countries": "Belgium, U.S.A., Mexico",
                "production_countries_fr": "Belgique, U.S.A., Mexique",
                "languages": "Spanish, English",
                "languages_fr": "Espagnol, anglais",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Cross-border documentary about childhood, violence, and memory.",
                "short_description_fr": "Documentaire transfrontalier autour de l enfance, de la violence et de la memoire.",
                "synopsis": "<p>The Time of the Fireflies follows children living in territories marked by violence, borders, and memory, moving toward a fragile and incandescent imaginary.</p>",
                "synopsis_fr": "<p>The Time of the Fireflies suit des enfances prises dans des territoires traverses par la violence, la frontiere et la memoire, a la rencontre d un imaginaire fragile et incandescent.</p>",
                "full_description": [
                    {
                        "type": "rich_text",
                        "value": {
                            "heading": "Circulation",
                            "body": "<p>The film has circulated through festivals and continues to live through screenings, educational accompaniment, and public conversations.</p>",
                        },
                    },
                    {
                        "type": "cta_band",
                        "value": {
                            "heading": "Screenings and partnerships",
                            "text": "<p>Contact Lighthouse Labs for screenings, public conversations, and educational collaborations around the film.</p>",
                            "label": "Contact us",
                            "href": "/contact",
                        },
                    },
                ],
                "full_description_fr": [
                    {
                        "type": "rich_text",
                        "value": {
                            "heading": "Circulation",
                            "body": "<p>Le film a circule en festivals et continue a vivre par des projections, des accompagnements pedagogiques et des conversations publiques.</p>",
                        },
                    },
                    {
                        "type": "cta_band",
                        "value": {
                            "heading": "Projections et partenariats",
                            "text": "<p>Contactez Lighthouse Labs pour les projections, conversations publiques et collaborations pedagogiques autour du film.</p>",
                            "label": "Nous contacter",
                            "href": "/contact",
                        },
                    },
                ],
                "video_embed": "https://player.vimeo.com/video/471884194",
                "collaborators": ["mattis-appelqvist", "matteo-robert-morales"],
                "credits": [
                    {"role": "Directors", "role_fr": "Direction", "value": "Matteo Robert Morales & Mattis Appelqvist Dalton", "value_fr": "Matteo Robert Morales & Mattis Appelqvist Dalton"},
                ],
                "external_links": [
                    {"label": "Educational distribution", "label_fr": "Distribution pedagogique", "url": "https://www.videoproject.org/time-of-the-fireflies.html"},
                    {"label": "IMDb", "label_fr": "IMDb", "url": "https://www.imdb.com/title/tt15846994/"},
                    {"label": "MUBI", "label_fr": "MUBI", "url": "https://mubi.com/fr/films/the-time-of-the-fireflies"},
                ],
            },
            {
                "slug": "pinacoteka",
                "title": "Pinakoteka",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Video",
                "project_type_fr": "Video",
                "year": "2022",
                "directors": "Mattis Appelqvist",
                "directors_fr": "Mattis Appelqvist",
                "production_countries": "Belgium, France",
                "production_countries_fr": "Belgique, France",
                "languages": "Polish, English",
                "languages_fr": "Polonais, anglais",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Short-form video between performance, image, and the circulation of a voice.",
                "short_description_fr": "Video courte entre performance, image et circulation d une parole.",
                "synopsis": "<p>Pinakoteka develops a short form at the intersection of performance, speech, and a tightly framed visual device.</p>",
                "synopsis_fr": "<p>Pinakoteka developpe une forme courte a la croisee de la performance, de la parole et d un dispositif visuel resserre.</p>",
                "full_description_fr": [],
                "video_embed": "",
                "collaborators": ["mattis-appelqvist"],
                "credits": [
                    {"role": "Director", "role_fr": "Direction", "value": "Mattis Appelqvist", "value_fr": "Mattis Appelqvist", "person": "mattis-appelqvist"},
                ],
                "external_links": [],
            },
            {
                "slug": "dashavatar",
                "title": "Dashavatar",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Video essay",
                "project_type_fr": "Video essay",
                "year": "2020",
                "directors": "Nikos Appelqvist",
                "directors_fr": "Nikos Appelqvist",
                "production_countries": "India",
                "production_countries_fr": "Inde",
                "languages": "Dance",
                "languages_fr": "Danse",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Video essay around gesture, myth, and movement.",
                "short_description_fr": "Essai video autour du geste, du mythe et du mouvement.",
                "synopsis": "<p>Dashavatar unfolds as a video essay through dance and myth, observing gestures and forms of transmission.</p>",
                "synopsis_fr": "<p>Dashavatar est un essai video qui se deploie a travers la danse et le mythe, en observant des gestes et des formes de transmission.</p>",
                "full_description_fr": [],
                "video_embed": "",
                "collaborators": ["nikos-appelqvist"],
                "credits": [
                    {"role": "Director", "role_fr": "Direction", "value": "Nikos Appelqvist", "value_fr": "Nikos Appelqvist", "person": "nikos-appelqvist"},
                ],
                "external_links": [],
            },
            {
                "slug": "the-dictator-catherine-graindorge-feat-iggy-pop",
                "title": "The dictator. Feat. Iggy Pop",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Music video",
                "project_type_fr": "Music video",
                "year": "2022",
                "directors": "Elie Rabinovitch",
                "directors_fr": "Elie Rabinovitch",
                "production_countries": "Belgium",
                "production_countries_fr": "Belgique",
                "languages": "English",
                "languages_fr": "Anglais",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Music video for Catherine Graindorge feat. Iggy Pop.",
                "short_description_fr": "Clip pour Catherine Graindorge feat. Iggy Pop.",
                "synopsis": "<p>Music video created for Catherine Graindorge feat. Iggy Pop, with cinematography by Matteo Robert Morales.</p>",
                "synopsis_fr": "<p>Clip musical realise pour Catherine Graindorge feat. Iggy Pop, avec une image signee Matteo Robert Morales.</p>",
                "full_description_fr": [],
                "video_embed": "",
                "collaborators": ["matteo-robert-morales"],
                "credits": [
                    {"role": "Director", "role_fr": "Direction", "value": "Elie Rabinovitch", "value_fr": "Elie Rabinovitch"},
                    {"role": "Cinematography", "role_fr": "Image", "value": "Matteo Robert Morales", "value_fr": "Matteo Robert Morales", "person": "matteo-robert-morales"},
                ],
                "external_links": [],
            },
            {
                "slug": "terra-nostra",
                "title": "Terra Nostra",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Short film",
                "project_type_fr": "Court-metrage",
                "year": "In development",
                "directors": "",
                "directors_fr": "",
                "production_countries": "France, Belgium",
                "production_countries_fr": "France, Belgique",
                "languages": "French",
                "languages_fr": "Francais",
                "roles": "Development",
                "roles_fr": "Developpement",
                "short_description": "Short film in development.",
                "short_description_fr": "Court-metrage en developpement.",
                "synopsis": "<p>Terra Nostra continues a fiction development process through questions of territory, memory, and transmission.</p>",
                "synopsis_fr": "<p>Terra Nostra poursuit un developpement de fiction a travers une ecriture de territoire, de memoire et de transmission.</p>",
                "full_description_fr": [],
                "video_embed": "",
                "collaborators": ["marguerite-de-saint-andre"],
                "credits": [],
                "external_links": [],
            },
            {
                "slug": "bhaba",
                "title": "Bhaba",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Documentary",
                "project_type_fr": "Documentaire",
                "year": "In production",
                "directors": "Nikos Appelqvist",
                "directors_fr": "Nikos Appelqvist",
                "production_countries": "India, Belgium",
                "production_countries_fr": "Inde, Belgique",
                "languages": "English",
                "languages_fr": "Anglais",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Documentary in production around Bhaba and his environment.",
                "short_description_fr": "Documentaire en production autour de Bhaba et de son environnement.",
                "synopsis": "<p>Bhaba follows an environment, a protagonist, and forms of transmission built between documentary observation and poetic openness.</p>",
                "synopsis_fr": "<p>Bhaba suit un environnement, un personnage et des formes de transmission qui se construisent entre observation documentaire et ouverture poetique.</p>",
                "full_description_fr": [],
                "video_embed": "",
                "collaborators": ["nikos-appelqvist"],
                "credits": [
                    {"role": "Director", "role_fr": "Direction", "value": "Nikos Appelqvist", "value_fr": "Nikos Appelqvist", "person": "nikos-appelqvist"},
                ],
                "external_links": [
                    {"label": "Project page", "label_fr": "Page projet", "url": "http://nikosappel.com/projects/bhaba/"},
                ],
            },
            {
                "slug": "masterclass",
                "title": "Masterclass",
                "has_public_page": True,
                "catalog_section": "Lighthouse Labs Productions",
                "catalog_section_fr": "Productions Lighthouse Labs",
                "project_type": "Educational content",
                "project_type_fr": "Contenu educatif",
                "year": "In production",
                "directors": "Mattis Appelqvist & Nikos Appelqvist",
                "directors_fr": "Mattis Appelqvist & Nikos Appelqvist",
                "production_countries": "France, Belgium",
                "production_countries_fr": "France, Belgique",
                "languages": "French",
                "languages_fr": "Francais",
                "roles": "Production",
                "roles_fr": "Production",
                "short_description": "Educational content currently in production.",
                "short_description_fr": "Contenu educatif en production.",
                "synopsis": "<p>Masterclass develops an educational format connecting transmission, cinema, and content production through Lighthouse Labs.</p>",
                "synopsis_fr": "<p>Masterclass developpe un format educatif qui relie transmission, cinema et production de contenu a travers Lighthouse Labs.</p>",
                "full_description_fr": [],
                "video_embed": "",
                "collaborators": ["mattis-appelqvist", "nikos-appelqvist"],
                "credits": [
                    {"role": "Directors", "role_fr": "Direction", "value": "Mattis Appelqvist & Nikos Appelqvist", "value_fr": "Mattis Appelqvist & Nikos Appelqvist"},
                ],
                "external_links": [],
            },
        ]

        seeded_projects = {}

        for record in post_production_records:
            project, _ = Project.objects.get_or_create(slug=record["slug"], defaults={"title": record["title"]})
            project.title = record["title"]
            project.title_fr = record["title"]
            project.has_public_page = False
            project.catalog_section = "Post-Production"
            project.catalog_section_fr = "Post-production"
            project.cover_image = None
            project.project_type = ""
            project.project_type_fr = ""
            project.year = ""
            project.directors = ""
            project.directors_fr = ""
            project.production_countries = ""
            project.production_countries_fr = ""
            project.languages = ""
            project.languages_fr = ""
            project.roles = ""
            project.roles_fr = ""
            project.listing_summary = record["listing_summary"]
            project.listing_summary_fr = record["listing_summary_fr"]
            project.short_description = ""
            project.short_description_fr = ""
            project.synopsis = ""
            project.synopsis_fr = ""
            project.full_description = []
            project.full_description_fr = []
            project.video_embed = ""
            project.save()
            project.gallery_images.all().delete()
            project.collaborators.all().delete()
            project.credits.all().delete()
            project.external_links.all().delete()
            seeded_projects[record["slug"]] = project

        for record in production_records:
            project, _ = Project.objects.get_or_create(slug=record["slug"], defaults={"title": record["title"]})
            project.title = record["title"]
            project.title_fr = record.get("title_fr", record["title"])
            project.has_public_page = record["has_public_page"]
            project.catalog_section = record["catalog_section"]
            project.catalog_section_fr = record["catalog_section_fr"]
            image_config = PROJECT_IMAGE_URLS.get(record["slug"], {})
            cover_image = self._import_remote_image(
                f"{record['title']} Cover",
                image_config.get("cover"),
            )
            if cover_image is not None:
                project.cover_image = cover_image
            project.project_type = record.get("project_type", record["project_type_fr"])
            project.project_type_fr = record["project_type_fr"]
            project.year = record["year"]
            project.directors = record.get("directors", record["directors_fr"])
            project.directors_fr = record["directors_fr"]
            project.production_countries = record.get("production_countries", record["production_countries_fr"])
            project.production_countries_fr = record["production_countries_fr"]
            project.languages = record.get("languages", record["languages_fr"])
            project.languages_fr = record["languages_fr"]
            project.roles = record.get("roles", record["roles_fr"])
            project.roles_fr = record["roles_fr"]
            project.listing_summary = record.get("listing_summary", "")
            project.listing_summary_fr = record.get("listing_summary_fr", "")
            project.short_description = record.get("short_description", record["short_description_fr"])
            project.short_description_fr = record["short_description_fr"]
            project.synopsis = record.get("synopsis", record["synopsis_fr"])
            project.synopsis_fr = record["synopsis_fr"]
            project.full_description = record.get("full_description", [])
            project.full_description_fr = record["full_description_fr"]
            project.video_embed = record["video_embed"]
            project.save()

            project.gallery_images.all().delete()
            project.collaborators.all().delete()
            project.credits.all().delete()
            project.external_links.all().delete()

            for index, image in enumerate(
                self._import_gallery(f"{record['title']} Gallery", image_config.get("gallery", [])),
                start=1,
            ):
                ProjectGalleryImage.objects.create(
                    project=project,
                    image=image,
                    caption="",
                    caption_fr="",
                    sort_order=index,
                )

            for collaborator_slug in record["collaborators"]:
                ProjectCollaborator.objects.create(project=project, person=people[collaborator_slug])

            for credit in record["credits"]:
                ProjectCredit.objects.create(
                    project=project,
                    role=credit["role"],
                    role_fr=credit.get("role_fr", credit["role"]),
                    value=credit.get("value", ""),
                    value_fr=credit.get("value_fr", credit.get("value", "")),
                    person=people.get(credit.get("person", "")) if credit.get("person") else None,
                )

            for link in record["external_links"]:
                ProjectExternalLink.objects.create(
                    project=project,
                    label=link["label"],
                    label_fr=link.get("label_fr", link["label"]),
                    url=link["url"],
                )

            seeded_projects[record["slug"]] = project

        return seeded_projects

    def _seed_person_related_projects(self, people, projects):
        relations = {
            "mattis-appelqvist": [
                "the-time-of-the-fireflies",
                "le-passage",
                "pinacoteka",
                "masterclass",
            ],
            "nikos-appelqvist": [
                "dashavatar",
                "bhaba",
                "masterclass",
            ],
            "matteo-robert-morales": [
                "the-time-of-the-fireflies",
                "here-be-monsters",
            ],
        }

        for slug, person in people.items():
            person.related_projects.all().delete()
            for project_slug in relations.get(slug, []):
                PersonRelatedProject.objects.create(person=person, project=projects[project_slug])

    def _seed_person_profiles(self, people, projects):
        mattis = people.get("mattis-appelqvist")
        if mattis is None:
            return

        audio_tracks = []
        for track in MATTIS_AUDIO_TRACKS:
            cover_image = self._import_remote_image(f"Mattis Audio Cover {track['title']}", track["cover_url"])
            audio_document = self._import_local_document(
                f"Mattis Audio {track['title']}",
                MATTIS_AUDIO_ASSET_DIR / track["file_name"],
            )
            audio_tracks.append(
                {
                    "title": track["title"],
                    "artist": track["artist"],
                    "cover_image": cover_image.pk if cover_image else None,
                    "audio_file": audio_document.pk if audio_document else None,
                    "audio_url": "",
                    "external_url": track["external_url"],
                }
            )

        mattis.primary_cta_label = "Contact me"
        mattis.primary_cta_label_fr = "Contact me"
        mattis.primary_cta_link = "/contact"
        mattis.profile_sections = [
            {
                "type": "embed",
                "value": {
                    "heading": "Composition Showreel",
                    "embed_url": MATTIS_SHOWREEL_EMBED_URL,
                    "aspect_ratio": "wide",
                },
            },
            {
                "type": "project_highlights",
                "value": {
                    "heading": "Directing",
                    "intro": "",
                    "projects": [
                        projects["le-passage"].pk,
                        projects["the-time-of-the-fireflies"].pk,
                        projects["pinacoteka"].pk,
                    ],
                },
            },
            {
                "type": "audio_playlist",
                "value": {
                    "heading": "Composition samples",
                    "intro": "",
                    "tracks": audio_tracks,
                },
            },
            {
                "type": "project_highlights",
                "value": {
                    "heading": "Installation",
                    "intro": "",
                    "projects": [projects["here-be-monsters"].pk],
                },
            },
        ]
        mattis.profile_sections_fr = [
            {
                "type": "embed",
                "value": {
                    "heading": "Composition Showreel",
                    "embed_url": MATTIS_SHOWREEL_EMBED_URL,
                    "aspect_ratio": "wide",
                },
            },
            {
                "type": "project_highlights",
                "value": {
                    "heading": "Directing",
                    "intro": "",
                    "projects": [
                        projects["le-passage"].pk,
                        projects["the-time-of-the-fireflies"].pk,
                        projects["pinacoteka"].pk,
                    ],
                },
            },
            {
                "type": "audio_playlist",
                "value": {
                    "heading": "Composition samples",
                    "intro": "",
                    "tracks": audio_tracks,
                },
            },
            {
                "type": "project_highlights",
                "value": {
                    "heading": "Installation",
                    "intro": "",
                    "projects": [projects["here-be-monsters"].pk],
                },
            },
        ]
        mattis.save()

    def _seed_spaces(self):
        Space.objects.filter(slug__in=["main-studio", "editing-suite", "salon-space"]).delete()
        common_services_fr = (
            "<ul>"
            "<li>Cuisine et espace pause</li>"
            "<li>Vestiaires et acces jardin</li>"
            "<li>Chaises, tables et installation</li>"
            "<li>Projecteur et ecran</li>"
            "<li>Support AV, captation evenementielle et streaming multicamera</li>"
            "</ul>"
        )
        common_services_en = (
            "<ul>"
            "<li>Kitchen and break area</li>"
            "<li>Changing rooms and garden access</li>"
            "<li>Chairs, tables, and setup support</li>"
            "<li>Projector and screen</li>"
            "<li>AV support, event recording, and multicamera streaming</li>"
            "</ul>"
        )

        records = [
            {
                "slug": "light-lab-studio",
                "name": "Light Lab Studio",
                "name_fr": "Light Lab Studio",
                "short_description": "Post-production room for color grading and editing.",
                "short_description_fr": "Studio de post-production pour l etalonnage et le montage.",
                "area": "",
                "capacity": "",
                "equipment": "<ul><li>Three-screen setup</li><li>Mac Studio M4 Max</li><li>Color control panels</li><li>Adobe Suite</li></ul>",
                "equipment_fr": "<ul><li>Configuration trois ecrans</li><li>Mac Studio M4 Max</li><li>Pupitres de controle couleur</li><li>Adobe Suite</li></ul>",
                "booking_label": "Book online",
                "booking_label_fr": "Reserver en ligne",
                "booking_link": BOOKING_URL,
                "offerings": [
                    {
                        "title": "Color grading",
                        "title_fr": "Etalonnage",
                        "description": "Finishing room for grading sessions and client reviews.",
                        "description_fr": "Salle de finition pour les sessions d etalonnage et les revisions clients.",
                        "daily_rate": "EUR 180 / day excl. VAT",
                        "hourly_rate": "",
                        "capacity": "",
                        "area": "",
                        "included_features": "<p>Three-screen setup, grading controls, reference monitoring, and Adobe workflow.</p>",
                        "included_features_fr": "<p>Configuration trois ecrans, surfaces de controle, monitoring de reference et workflow Adobe.</p>",
                        "extra_services": "",
                        "extra_services_fr": "",
                    },
                    {
                        "title": "Editing",
                        "title_fr": "Montage",
                        "description": "Quiet edit room for picture work and review sessions.",
                        "description_fr": "Salle de montage calme pour le travail image et les revisions.",
                        "daily_rate": "EUR 50 / day excl. VAT",
                        "hourly_rate": "",
                        "capacity": "",
                        "area": "",
                        "included_features": "<p>Editing workstation, review display, and studio support on request.</p>",
                        "included_features_fr": "<p>Station de montage, ecran de revision et support studio sur demande.</p>",
                        "extra_services": "",
                        "extra_services_fr": "",
                    },
                ],
            },
            {
                "slug": "spectrum-studio",
                "name": "Spectrum Studio",
                "name_fr": "Spectrum Studio",
                "short_description": "Compact studio for color sessions and editing work.",
                "short_description_fr": "Studio compact pour l etalonnage et le montage.",
                "area": "",
                "capacity": "",
                "equipment": "<ul><li>Reference monitoring</li><li>Editing and color setup</li><li>Mac workstation</li><li>Adobe Suite</li></ul>",
                "equipment_fr": "<ul><li>Monitoring de reference</li><li>Configuration montage et couleur</li><li>Station Mac</li><li>Adobe Suite</li></ul>",
                "booking_label": "Book online",
                "booking_label_fr": "Reserver en ligne",
                "booking_link": BOOKING_URL,
                "offerings": [
                    {
                        "title": "Color grading",
                        "title_fr": "Etalonnage",
                        "description": "Color review and finishing sessions.",
                        "description_fr": "Sessions d etalonnage et de finition.",
                        "daily_rate": "EUR 150 / day excl. VAT",
                        "hourly_rate": "",
                        "capacity": "",
                        "area": "",
                        "included_features": "<p>Reference screen, color controls, and flexible review setup.</p>",
                        "included_features_fr": "<p>Ecran de reference, controles couleur et configuration de revision flexible.</p>",
                        "extra_services": "",
                        "extra_services_fr": "",
                    },
                    {
                        "title": "Editing",
                        "title_fr": "Montage",
                        "description": "Editing station for picture work and approvals.",
                        "description_fr": "Station de montage pour le travail image et les validations.",
                        "daily_rate": "EUR 50 / day excl. VAT",
                        "hourly_rate": "",
                        "capacity": "",
                        "area": "",
                        "included_features": "<p>Editing workstation, studio support, and quiet review environment.</p>",
                        "included_features_fr": "<p>Station de montage, support studio et environnement de revision calme.</p>",
                        "extra_services": "",
                        "extra_services_fr": "",
                    },
                ],
            },
            {
                "slug": "canopy-hall",
                "name": "Canopy Hall",
                "name_fr": "Canopy Hall",
                "short_description": "Large space for recording, workshops, conferences, and screenings.",
                "short_description_fr": "Grand espace pour l enregistrement, les workshops, conferences et projections.",
                "area": "150 m2",
                "capacity": "50 people",
                "equipment": "<ul><li>Wi-Fi</li><li>Break area</li><li>Flexible event layout</li></ul>",
                "equipment_fr": "<ul><li>Wi-Fi</li><li>Espace pause</li><li>Configuration evenementielle flexible</li></ul>",
                "booking_label": "Book online",
                "booking_label_fr": "Reserver en ligne",
                "booking_link": BOOKING_URL,
                "offerings": [
                    {
                        "title": "Recording",
                        "title_fr": "Recording",
                        "description": "Recording format for rehearsals, talks, and hybrid capture.",
                        "description_fr": "Format d enregistrement pour repetitions, talks et captations hybrides.",
                        "daily_rate": "EUR 400 / day excl. VAT",
                        "hourly_rate": "EUR 100 / hour excl. VAT",
                        "capacity": "50 people",
                        "area": "150 m2",
                        "included_features": "<p>Wi-Fi, break area, flexible layout, and on-site production support.</p>",
                        "included_features_fr": "<p>Wi-Fi, espace pause, implantation flexible et support de production sur place.</p>",
                        "extra_services": common_services_en,
                        "extra_services_fr": common_services_fr,
                    },
                    {
                        "title": "Workshop",
                        "title_fr": "Workshop",
                        "description": "Room setup for workshops, team sessions, and collaborative formats.",
                        "description_fr": "Configuration pour workshops, sessions d equipe et formats collaboratifs.",
                        "daily_rate": "EUR 400 / day excl. VAT",
                        "hourly_rate": "EUR 100 / hour excl. VAT",
                        "capacity": "50 people",
                        "area": "150 m2",
                        "included_features": "<p>Flexible seating, Wi-Fi, and break area.</p>",
                        "included_features_fr": "<p>Assises flexibles, Wi-Fi et espace pause.</p>",
                        "extra_services": common_services_en,
                        "extra_services_fr": common_services_fr,
                    },
                    {
                        "title": "Conference & screening",
                        "title_fr": "Conference & screening",
                        "description": "Configuration for screenings, talks, and public presentations.",
                        "description_fr": "Configuration pour projections, talks et presentations publiques.",
                        "daily_rate": "EUR 400 / day excl. VAT",
                        "hourly_rate": "EUR 100 / hour excl. VAT",
                        "capacity": "50 people",
                        "area": "150 m2",
                        "included_features": "<p>Projection-friendly layout, Wi-Fi, and break area.</p>",
                        "included_features_fr": "<p>Configuration adaptee a la projection, Wi-Fi et espace pause.</p>",
                        "extra_services": common_services_en,
                        "extra_services_fr": common_services_fr,
                    },
                ],
            },
            {
                "slug": "basecamp-space",
                "name": "Basecamp Space",
                "name_fr": "Basecamp Space",
                "short_description": "Smaller room for recording, workshops, and meetings.",
                "short_description_fr": "Espace plus compact pour l enregistrement, les workshops et les reunions.",
                "area": "60 m2",
                "capacity": "20 people",
                "equipment": "<ul><li>Wi-Fi</li><li>Flexible furniture</li><li>Meeting and workshop setup</li></ul>",
                "equipment_fr": "<ul><li>Wi-Fi</li><li>Mobilier flexible</li><li>Configuration reunion et workshop</li></ul>",
                "booking_label": "Book online",
                "booking_label_fr": "Reserver en ligne",
                "booking_link": BOOKING_URL,
                "offerings": [
                    {
                        "title": "Recording",
                        "title_fr": "Recording",
                        "description": "Compact capture and rehearsal format.",
                        "description_fr": "Format compact de captation et repetition.",
                        "daily_rate": "EUR 200 / day excl. VAT",
                        "hourly_rate": "EUR 60 / hour excl. VAT",
                        "capacity": "20 people",
                        "area": "60 m2",
                        "included_features": "<p>Wi-Fi, furniture, and flexible room layout.</p>",
                        "included_features_fr": "<p>Wi-Fi, mobilier et implantation flexible.</p>",
                        "extra_services": common_services_en,
                        "extra_services_fr": common_services_fr,
                    },
                    {
                        "title": "Workshop",
                        "title_fr": "Workshop",
                        "description": "Small-group workshop and facilitation setup.",
                        "description_fr": "Configuration pour workshop en petit groupe et facilitation.",
                        "daily_rate": "EUR 200 / day excl. VAT",
                        "hourly_rate": "EUR 60 / hour excl. VAT",
                        "capacity": "20 people",
                        "area": "60 m2",
                        "included_features": "<p>Flexible room setup and Wi-Fi.</p>",
                        "included_features_fr": "<p>Configuration flexible et Wi-Fi.</p>",
                        "extra_services": common_services_en,
                        "extra_services_fr": common_services_fr,
                    },
                    {
                        "title": "Meeting",
                        "title_fr": "Meeting",
                        "description": "Meeting room for production sessions and review points.",
                        "description_fr": "Salle de reunion pour sessions de production et points de revision.",
                        "daily_rate": "EUR 200 / day excl. VAT",
                        "hourly_rate": "EUR 60 / hour excl. VAT",
                        "capacity": "20 people",
                        "area": "60 m2",
                        "included_features": "<p>Meeting-ready layout, Wi-Fi, and support on request.</p>",
                        "included_features_fr": "<p>Configuration reunion, Wi-Fi et support sur demande.</p>",
                        "extra_services": common_services_en,
                        "extra_services_fr": common_services_fr,
                    },
                ],
            },
        ]

        seeded_spaces = {}
        for record in records:
            space, _ = Space.objects.get_or_create(slug=record["slug"], defaults={"name": record["name"]})
            image_config = SPACE_IMAGE_URLS.get(record["slug"], {})
            for field in [
                "name",
                "name_fr",
                "short_description",
                "short_description_fr",
                "area",
                "capacity",
                "equipment",
                "equipment_fr",
                "booking_label",
                "booking_label_fr",
                "booking_link",
            ]:
                setattr(space, field, record[field])
            main_image = self._import_remote_image(
                f"{record['name']} Main",
                image_config.get("main"),
            )
            if main_image is not None:
                space.main_image = main_image
            space.save()
            space.gallery_images.all().delete()
            space.offerings.all().delete()
            for index, image in enumerate(
                self._import_gallery(f"{record['name']} Gallery", image_config.get("gallery", [])),
                start=1,
            ):
                SpaceGalleryImage.objects.create(
                    space=space,
                    image=image,
                    caption="",
                    caption_fr="",
                    sort_order=index,
                )
            for offering in record["offerings"]:
                SpaceOffering.objects.create(space=space, **offering)
            seeded_spaces[record["slug"]] = space
        return seeded_spaces

    def _seed_home_page(self, home_page, projects, spaces):
        hero_image = self._import_remote_image(
            "Lighthouse Labs Home Hero",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/11/TTOTF3.jpg",
        )
        collaborations_montage = self._import_remote_image(
            "Lighthouse Labs Collaborations Montage",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/12/collabs.jpg",
        )
        awards_montage = self._import_remote_image(
            "Lighthouse Labs Awards Montage",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/12/laurels.jpg",
        )

        home_page.title = "Lighthouse Labs"
        home_page.hero_title = "Lighthouse Labs is a post production company based in Brussels"
        home_page.hero_title_fr = "Lighthouse Labs est une societe de post-production basee a Bruxelles"
        home_page.hero_subtitle = (
            "<p>We produce films, host post-production work, and open our spaces to screenings, workshops, and collaborations.</p>"
        )
        home_page.hero_subtitle_fr = (
            "<p>Nous produisons des films, accueillons des projets de post-production et ouvrons nos espaces a des projections, workshops et collaborations.</p>"
        )
        home_page.primary_cta_label = "Rent a studio"
        home_page.primary_cta_label_fr = "Louer un studio"
        home_page.primary_cta_link = "/spaces"
        home_page.secondary_cta_label = "Contact us"
        home_page.secondary_cta_label_fr = "Nous contacter"
        home_page.secondary_cta_link = "/contact"
        home_page.hero_video_url = (
            "https://player.vimeo.com/video/657051216"
            "?background=1&autoplay=1&loop=1&muted=1&title=0&byline=0&portrait=0"
        )
        if hero_image is not None:
            home_page.hero_image = hero_image
        home_page.body = [
            {
                "type": "feature_grid",
                "value": {
                    "heading": "Our spaces",
                    "intro": "<p>Studios and rooms for grading, editing, workshops, screenings, and hybrid production formats.</p>",
                    "items": [
                        {
                            "title": "Light Lab Studio",
                            "description": "Color grading and editing.",
                            "image": spaces["light-lab-studio"].main_image.pk if spaces["light-lab-studio"].main_image else None,
                            "href": "/spaces#light-lab-studio",
                        },
                        {
                            "title": "Spectrum Studio",
                            "description": "Compact finishing and review room.",
                            "image": spaces["spectrum-studio"].main_image.pk if spaces["spectrum-studio"].main_image else None,
                            "href": "/spaces#spectrum-studio",
                        },
                        {
                            "title": "Canopy Hall",
                            "description": "Recording, workshops, conferences, and screenings.",
                            "image": spaces["canopy-hall"].main_image.pk if spaces["canopy-hall"].main_image else None,
                            "href": "/spaces#canopy-hall",
                        },
                        {
                            "title": "Basecamp Space",
                            "description": "Meetings, workshops, and small-group recording.",
                            "image": spaces["basecamp-space"].main_image.pk if spaces["basecamp-space"].main_image else None,
                            "href": "/spaces#basecamp-space",
                        },
                    ],
                },
            },
            {
                "type": "gallery",
                "value": {
                    "heading": "Collaborations",
                    "images": [collaborations_montage.pk] if collaborations_montage else [],
                    "caption": "",
                    "surface": "light",
                },
            },
            {
                "type": "gallery",
                "value": {
                    "heading": "Awards & selections",
                    "images": [awards_montage.pk] if awards_montage else [],
                    "caption": "",
                    "surface": "light",
                },
            },
            {
                "type": "highlight_strip",
                "value": {
                    "heading": "News",
                    "items": [
                        {
                            "title": "Jury award for The Time of the Fireflies",
                            "body": "Recognized at New Orleans Film Festival.",
                            "image": projects["the-time-of-the-fireflies"].cover_image.pk if projects["the-time-of-the-fireflies"].cover_image else None,
                            "link_label": "Open project",
                            "link_url": "/projects/the-time-of-the-fireflies",
                        },
                        {
                            "title": "Golden Gate Award",
                            "body": "The Time of the Fireflies received the Golden Gate Award in San Francisco.",
                            "image": projects["the-time-of-the-fireflies"].cover_image.pk if projects["the-time-of-the-fireflies"].cover_image else None,
                            "link_label": "Open project",
                            "link_url": "/projects/the-time-of-the-fireflies",
                        },
                        {
                            "title": "New clip feat. Iggy Pop",
                            "body": "Latest music video production from the Lighthouse Labs catalogue.",
                            "image": projects["the-dictator-catherine-graindorge-feat-iggy-pop"].cover_image.pk if projects["the-dictator-catherine-graindorge-feat-iggy-pop"].cover_image else None,
                            "link_label": "Open project",
                            "link_url": "/projects/the-dictator-catherine-graindorge-feat-iggy-pop",
                        },
                    ],
                },
            },
        ]
        home_page.body_fr = [
            {
                "type": "feature_grid",
                "value": {
                    "heading": "Nos espaces",
                    "intro": "<p>Studios et salles pour l etalonnage, le montage, les workshops, les projections et les formats hybrides.</p>",
                    "items": [
                        {
                            "title": "Light Lab Studio",
                            "description": "Etalonnage et montage.",
                            "image": spaces["light-lab-studio"].main_image.pk if spaces["light-lab-studio"].main_image else None,
                            "href": "/spaces#light-lab-studio",
                        },
                        {
                            "title": "Spectrum Studio",
                            "description": "Salle compacte de finition et de revision.",
                            "image": spaces["spectrum-studio"].main_image.pk if spaces["spectrum-studio"].main_image else None,
                            "href": "/spaces#spectrum-studio",
                        },
                        {
                            "title": "Canopy Hall",
                            "description": "Recording, workshops, conferences et projections.",
                            "image": spaces["canopy-hall"].main_image.pk if spaces["canopy-hall"].main_image else None,
                            "href": "/spaces#canopy-hall",
                        },
                        {
                            "title": "Basecamp Space",
                            "description": "Reunions, workshops et captations en petit groupe.",
                            "image": spaces["basecamp-space"].main_image.pk if spaces["basecamp-space"].main_image else None,
                            "href": "/spaces#basecamp-space",
                        },
                    ],
                },
            },
            {
                "type": "gallery",
                "value": {
                    "heading": "Collaborations",
                    "images": [collaborations_montage.pk] if collaborations_montage else [],
                    "caption": "",
                    "surface": "light",
                },
            },
            {
                "type": "gallery",
                "value": {
                    "heading": "Prix & selections",
                    "images": [awards_montage.pk] if awards_montage else [],
                    "caption": "",
                    "surface": "light",
                },
            },
            {
                "type": "highlight_strip",
                "value": {
                    "heading": "Actualites",
                    "items": [
                        {
                            "title": "Prix du jury pour The Time of the Fireflies",
                            "body": "Le film a ete distingue au New Orleans Film Festival.",
                            "image": projects["the-time-of-the-fireflies"].cover_image.pk if projects["the-time-of-the-fireflies"].cover_image else None,
                            "link_label": "Voir le projet",
                            "link_url": "/projects/the-time-of-the-fireflies",
                        },
                        {
                            "title": "Golden Gate Award",
                            "body": "The Time of the Fireflies a recu le Golden Gate Award a San Francisco.",
                            "image": projects["the-time-of-the-fireflies"].cover_image.pk if projects["the-time-of-the-fireflies"].cover_image else None,
                            "link_label": "Voir le projet",
                            "link_url": "/projects/the-time-of-the-fireflies",
                        },
                        {
                            "title": "Nouveau clip feat. Iggy Pop",
                            "body": "Derniere production musicale du catalogue Lighthouse Labs.",
                            "image": projects["the-dictator-catherine-graindorge-feat-iggy-pop"].cover_image.pk if projects["the-dictator-catherine-graindorge-feat-iggy-pop"].cover_image else None,
                            "link_label": "Voir le projet",
                            "link_url": "/projects/the-dictator-catherine-graindorge-feat-iggy-pop",
                        },
                    ],
                },
            },
        ]
        home_page.seo_title_override = "Lighthouse Labs"
        home_page.seo_title_override_fr = "Lighthouse Labs"
        home_page.seo_description_override = "Post-production, film projects, and cinema-led spaces in Brussels."
        home_page.seo_description_override_fr = "Post-production, projets de films et espaces portes par le cinema a Bruxelles."
        home_page.save_revision().publish()

    def _seed_about_page(self, page, people):
        intro_image = self._import_remote_image(
            "Lighthouse Labs About Intro",
            "https://lighthouse-labs.be/wp-content/uploads/sites/16/2022/11/STUDIO-1024x636-1.jpeg",
        )
        page.title_display = "About"
        page.title_display_fr = "A propos"
        page.intro_title = "About"
        page.intro_title_fr = "A propos"
        page.intro_text = (
            "<p>Lighthouse Labs is a creative and collaborative space based in Brussels. We produce films from the original idea through festival circulation, and we also develop promotional videos, music videos, and educational content. The studio brings together equipped spaces for post-production, composition, color grading, and collective working formats.</p>"
        )
        page.intro_text_fr = (
            "<p>Lighthouse Labs est un espace de creation et de collaboration base a Bruxelles. Nous produisons des films depuis l idee originale jusqu a leur circulation en festival, et developpons aussi des videos promotionnelles, clips musicaux et contenus educatifs. Le studio rassemble des espaces equipes pour la post-production, la composition, l etalonnage et des formats de travail collectifs.</p>"
        )
        if intro_image is not None:
            page.intro_image = intro_image
        page.services = [
            {
                "type": "feature_grid",
                "value": {
                    "heading": "Services",
                    "intro": "<p>A straightforward offer with no automatic categories or archive clutter.</p>",
                    "items": [
                        {"title": "Development", "description": ""},
                        {"title": "Consultations", "description": ""},
                        {"title": "Production", "description": ""},
                        {"title": "Editing", "description": ""},
                        {"title": "Sound editing", "description": ""},
                        {"title": "Music composition", "description": ""},
                        {"title": "Color grading", "description": ""},
                    ],
                },
            }
        ]
        page.services_fr = [
            {
                "type": "feature_grid",
                "value": {
                    "heading": "Services",
                    "intro": "<p>Une offre simple et lisible, sans categories automatiques ni pages d archives.</p>",
                    "items": [
                        {"title": "Developpement", "description": ""},
                        {"title": "Consultations", "description": ""},
                        {"title": "Production", "description": ""},
                        {"title": "Montage", "description": ""},
                        {"title": "Montage son", "description": ""},
                        {"title": "Composition musicale", "description": ""},
                        {"title": "Etalonnage", "description": ""},
                    ],
                },
            }
        ]
        page.studios_equipment = [
            {
                "type": "feature_grid",
                "value": {
                    "heading": "Studios & equipment",
                    "intro": "<p>Lighthouse Labs spaces cover post-production needs as well as small- and medium-group working formats.</p>",
                    "items": [
                        {"title": "Editing studio", "description": ""},
                        {"title": "Sound editing studio", "description": ""},
                        {"title": "Color grading studio", "description": ""},
                        {"title": "Recording & photo studio", "description": ""},
                    ],
                },
            }
        ]
        page.studios_equipment_fr = [
            {
                "type": "feature_grid",
                "value": {
                    "heading": "Studios & equipements",
                    "intro": "<p>Les espaces de Lighthouse Labs couvrent les besoins de post-production et de travail en petit ou moyen groupe.</p>",
                    "items": [
                        {"title": "Studio de montage", "description": ""},
                        {"title": "Studio de montage son", "description": ""},
                        {"title": "Studio d etalonnage", "description": ""},
                        {"title": "Studio de captation & photo", "description": ""},
                    ],
                },
            }
        ]
        page.seo_title_override = "About Lighthouse Labs"
        page.seo_title_override_fr = "A propos de Lighthouse Labs"
        page.seo_description_override = "Overview of Lighthouse Labs, its services, and the team."
        page.seo_description_override_fr = "Presentation de Lighthouse Labs, de ses services et de l equipe."
        page.save_revision().publish()

        page.team_members.all().delete()
        for slug in [
            "nikos-appelqvist",
            "maxime-jouret",
            "ngare-falise",
            "mattis-appelqvist",
            "marguerite-de-saint-andre",
            "matteo-robert-morales",
            "hugo-malidin",
        ]:
            AboutPageTeamMember.objects.create(page=page, person=people[slug])

    def _seed_spaces_page(self, page, spaces):
        page.title_display = "Our Spaces"
        page.title_display_fr = "Espaces"
        page.intro_text = (
            f"<p>To book a space, call <a href='tel:+32498970884'>+32 498 97 08 84</a> or <a href='{BOOKING_URL}'>book online</a>.</p>"
        )
        page.intro_text_fr = (
            f"<p>Pour reserver un espace, appelez le <a href='tel:+32498970884'>+32 498 97 08 84</a> ou <a href='{BOOKING_URL}'>reservez en ligne</a>.</p>"
        )
        page.seo_title_override = "Our Spaces"
        page.seo_title_override_fr = "Espaces"
        page.seo_description_override = "Studios, rooms, and production spaces available through Lighthouse Labs."
        page.seo_description_override_fr = "Studios, salles et espaces de production proposes par Lighthouse Labs."
        page.save_revision().publish()

        page.spaces.all().delete()
        for slug in [
            "light-lab-studio",
            "spectrum-studio",
            "canopy-hall",
            "basecamp-space",
        ]:
            SpacesPageSpace.objects.create(page=page, space=spaces[slug])

    def _seed_projects_page(self, page, projects):
        page.title_display = "Projects"
        page.title_display_fr = "Nos Projets"
        page.intro_text = (
            f"<p>Lighthouse Labs produces films from the original idea through circulation. We also collaborate as editors, colorists, composers, and technical advisors. See also the <a href='{SHOWREEL_URL}'>showreel</a>.</p>"
        )
        page.intro_text_fr = (
            f"<p>Lighthouse Labs produit des films de l idee originale jusqu a leur circulation. Nous collaborons egalement comme monteurs, coloristes, compositeurs ou conseillers techniques. Voir aussi le <a href='{SHOWREEL_URL}'>showreel</a>.</p>"
        )
        page.seo_title_override = "Projects"
        page.seo_title_override_fr = "Nos Projets"
        page.seo_description_override = "Selection of post-production collaborations and Lighthouse Labs productions."
        page.seo_description_override_fr = "Selection de projets en post-production et productions Lighthouse Labs."
        page.save_revision().publish()

        page.sections.all().delete()

        post_production = ProjectsPageSection.objects.create(
            page=page,
            title="Post-Production",
            title_fr="Post-production",
            intro="<p>Collaborations in editing, grading, composition, and technical support.</p>",
            intro_fr="<p>Collaborations en montage, etalonnage, composition et accompagnement technique.</p>",
        )
        for slug in [
            "four-brothers",
            "les-heures-creuses",
            "ma-jolie-poupee-cherie",
            "alice-et-les-soleils",
            "une-jeunesse-aimable",
            "combustion",
            "isaac-manque",
            "prattseul-cache-cache",
            "robbing-millions-same-skin",
            "glauque-pas-le-choix",
            "rive-amour",
            "ser-semilla",
            "home-movies",
        ]:
            ProjectsPageSectionProject.objects.create(section=post_production, project=projects[slug])

        productions = ProjectsPageSection.objects.create(
            page=page,
            title="Lighthouse Labs Productions",
            title_fr="Productions Lighthouse Labs",
            intro="<p>Films, videos, and educational formats developed and produced by Lighthouse Labs.</p>",
            intro_fr="<p>Films, videos et formats educatifs developpes et produits par Lighthouse Labs.</p>",
        )
        for slug in [
            "here-be-monsters",
            "le-passage",
            "the-time-of-the-fireflies",
            "pinacoteka",
            "dashavatar",
            "the-dictator-catherine-graindorge-feat-iggy-pop",
            "terra-nostra",
            "bhaba",
            "masterclass",
        ]:
            ProjectsPageSectionProject.objects.create(section=productions, project=projects[slug])

    def _seed_contact_page(self, page):
        page.title_display = "Contact us"
        page.title_display_fr = "Contact"
        page.intro_text = (
            "<p>Reach Lighthouse Labs for studio bookings, project conversations, and post-production questions.</p>"
        )
        page.intro_text_fr = (
            "<p>Contactez Lighthouse Labs pour les reservations de studio, les conversations de projet et les questions de post-production.</p>"
        )
        page.form_embed = (
            "<div>"
            "<p><strong>Contact form placeholder</strong></p>"
            "<p>Replace this seeded block with your production form embed when you are ready to connect the live provider.</p>"
            "<p><a href='mailto:info@f-lh.be'>info@f-lh.be</a></p>"
            "</div>"
        )
        page.form_embed_fr = (
            "<div>"
            "<p><strong>Zone de formulaire</strong></p>"
            "<p>Remplacez ce bloc par l embed de votre fournisseur de formulaire lorsque le flux live sera choisi.</p>"
            "<p><a href='mailto:info@f-lh.be'>info@f-lh.be</a></p>"
            "</div>"
        )
        page.map_embed = ""
        page.seo_title_override = "Contact"
        page.seo_title_override_fr = "Contact"
        page.seo_description_override = "Get in touch with Lighthouse Labs in Brussels."
        page.seo_description_override_fr = "Contactez Lighthouse Labs a Bruxelles."
        page.save_revision().publish()
