from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, Site


SUPPORTED_LOCALES = (
    ("en", "English"),
    ("fr", "French"),
)


FEATURED_TILE_BLOCKS = [
    (
        "tile",
        blocks.StructBlock(
            [
                ("title", blocks.CharBlock()),
                ("description", blocks.TextBlock()),
                ("cta_label", blocks.CharBlock()),
                ("cta_href", blocks.CharBlock()),
            ]
        ),
    ),
]


NARRATIVE_SECTION_BLOCKS = [
    (
        "rich_section",
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock(required=False)),
                ("body", blocks.RichTextBlock()),
            ]
        ),
    ),
    (
        "feature_stack",
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock(required=False)),
                (
                    "items",
                    blocks.ListBlock(
                        blocks.StructBlock(
                            [
                                ("title", blocks.CharBlock()),
                                ("body", blocks.RichTextBlock(required=False)),
                            ]
                        )
                    ),
                ),
            ]
        ),
    ),
    (
        "gallery",
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock(required=False)),
                ("images", blocks.ListBlock(ImageChooserBlock())),
                ("caption", blocks.CharBlock(required=False)),
            ]
        ),
    ),
    (
        "faq",
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock(required=False)),
                (
                    "items",
                    blocks.ListBlock(
                        blocks.StructBlock(
                            [
                                ("question", blocks.CharBlock()),
                                ("answer", blocks.RichTextBlock()),
                            ]
                        )
                    ),
                ),
            ]
        ),
    ),
    (
        "cta_section",
        blocks.StructBlock(
            [
                ("heading", blocks.CharBlock(required=False)),
                ("body", blocks.RichTextBlock(required=False)),
                ("button_label", blocks.CharBlock()),
                ("button_url", blocks.CharBlock()),
            ]
        ),
    ),
]


class HomePage(Page):
    hero_eyebrow_en = models.CharField(max_length=255, blank=True)
    hero_eyebrow_fr = models.CharField(max_length=255, blank=True)
    hero_title_en = models.CharField(max_length=255, blank=True)
    hero_title_fr = models.CharField(max_length=255, blank=True)
    hero_body_en = RichTextField(blank=True)
    hero_body_fr = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    intro_heading_en = models.CharField(max_length=255, blank=True)
    intro_heading_fr = models.CharField(max_length=255, blank=True)
    intro_body_en = RichTextField(blank=True)
    intro_body_fr = RichTextField(blank=True)
    featured_tiles_en = StreamField(FEATURED_TILE_BLOCKS, blank=True, default=list, use_json_field=True)
    featured_tiles_fr = StreamField(FEATURED_TILE_BLOCKS, blank=True, default=list, use_json_field=True)
    sections_en = StreamField(NARRATIVE_SECTION_BLOCKS, blank=True, default=list, use_json_field=True)
    sections_fr = StreamField(NARRATIVE_SECTION_BLOCKS, blank=True, default=list, use_json_field=True)
    seo_title_en = models.CharField(max_length=255, blank=True)
    seo_title_fr = models.CharField(max_length=255, blank=True)
    seo_description_en = models.TextField(blank=True)
    seo_description_fr = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_eyebrow_en"),
                FieldPanel("hero_eyebrow_fr"),
                FieldPanel("hero_title_en"),
                FieldPanel("hero_title_fr"),
                FieldPanel("hero_body_en"),
                FieldPanel("hero_body_fr"),
                FieldPanel("hero_image"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("intro_heading_en"),
                FieldPanel("intro_heading_fr"),
                FieldPanel("intro_body_en"),
                FieldPanel("intro_body_fr"),
            ],
            heading="Intro",
        ),
        MultiFieldPanel(
            [
                FieldPanel("featured_tiles_en"),
                FieldPanel("featured_tiles_fr"),
            ],
            heading="Featured tiles",
        ),
        MultiFieldPanel(
            [
                FieldPanel("sections_en"),
                FieldPanel("sections_fr"),
            ],
            heading="Sections",
        ),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_en"),
                FieldPanel("seo_title_fr"),
                FieldPanel("seo_description_en"),
                FieldPanel("seo_description_fr"),
            ],
            heading="SEO",
        ),
    ]

    subpage_types = ["pages.NarrativePage"]

    def _localized_value(self, locale: str, *, en_value="", fr_value=""):
        normalized = (locale or "").strip().lower()
        if normalized.startswith("fr"):
            return fr_value or en_value or ""
        return en_value or fr_value or ""

    def hero_for(self, locale: str):
        return {
            "eyebrow": self._localized_value(locale, en_value=self.hero_eyebrow_en, fr_value=self.hero_eyebrow_fr),
            "title": self._localized_value(locale, en_value=self.hero_title_en, fr_value=self.hero_title_fr),
            "body": self._localized_value(locale, en_value=self.hero_body_en, fr_value=self.hero_body_fr),
            "image": self.hero_image,
        }

    def intro_for(self, locale: str):
        return {
            "heading": self._localized_value(locale, en_value=self.intro_heading_en, fr_value=self.intro_heading_fr),
            "body": self._localized_value(locale, en_value=self.intro_body_en, fr_value=self.intro_body_fr),
        }

    def featured_tiles_for(self, locale: str):
        if (locale or "").strip().lower().startswith("fr"):
            return self.featured_tiles_fr
        return self.featured_tiles_en

    def sections_for(self, locale: str):
        if (locale or "").strip().lower().startswith("fr"):
            return self.sections_fr
        return self.sections_en

    def seo_for(self, locale: str):
        return {
            "title": self._localized_value(locale, en_value=self.seo_title_en, fr_value=self.seo_title_fr),
            "description": self._localized_value(
                locale,
                en_value=self.seo_description_en,
                fr_value=self.seo_description_fr,
            ),
        }


class NarrativePage(Page):
    class RouteKey(models.TextChoices):
        ABOUT = "about", "About"
        STUDIOS = "studios", "Studios"
        FILM_PROJECTS = "film-projects", "Film projects"
        CINEMA = "cinema", "Cinema"
        CONTACT = "contact", "Contact"

    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name="narrative_pages")
    route_key = models.CharField(max_length=64, choices=RouteKey.choices)
    language_code = models.CharField(max_length=2, choices=SUPPORTED_LOCALES, default="en")
    subtitle = models.CharField(max_length=255, blank=True)
    hero_title = models.CharField(max_length=255, blank=True)
    hero_body = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sections = StreamField(NARRATIVE_SECTION_BLOCKS, blank=True, default=list, use_json_field=True)
    primary_cta_label = models.CharField(max_length=120, blank=True)
    primary_cta_url = models.CharField(max_length=255, blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("site"),
                FieldPanel("route_key"),
                FieldPanel("language_code"),
            ],
            heading="Routing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("subtitle"),
                FieldPanel("hero_title"),
                FieldPanel("hero_body"),
                FieldPanel("hero_image"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("sections"),
            ],
            heading="Sections",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_url"),
            ],
            heading="Primary CTA",
        ),
        MultiFieldPanel(
            [
                FieldPanel("meta_title"),
                FieldPanel("meta_description"),
            ],
            heading="SEO",
        ),
    ]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["site", "route_key", "language_code"],
                name="unique_narrative_page_per_site_route_locale",
            )
        ]
