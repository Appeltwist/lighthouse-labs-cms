from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string


def default_locales():
    return ["en", "fr"]


NAV_ITEM_BLOCKS = [
    (
        "item",
        blocks.StructBlock(
            [
                ("label_en", blocks.CharBlock()),
                ("label_fr", blocks.CharBlock()),
                ("href", blocks.CharBlock()),
                ("open_in_new_tab", blocks.BooleanBlock(required=False, default=False)),
            ]
        ),
    ),
]


FOOTER_GROUP_BLOCKS = [
    (
        "group",
        blocks.StructBlock(
            [
                ("title_en", blocks.CharBlock()),
                ("title_fr", blocks.CharBlock()),
                (
                    "links",
                    blocks.ListBlock(
                        blocks.StructBlock(
                            [
                                ("label_en", blocks.CharBlock()),
                                ("label_fr", blocks.CharBlock()),
                                ("href", blocks.CharBlock()),
                                ("open_in_new_tab", blocks.BooleanBlock(required=False, default=False)),
                            ]
                        )
                    ),
                ),
            ]
        ),
    ),
]


SOCIAL_LINK_BLOCKS = [
    (
        "link",
        blocks.StructBlock(
            [
                ("label", blocks.CharBlock()),
                ("url", blocks.URLBlock()),
            ]
        ),
    ),
]


@register_setting
class BrandSettings(BaseSiteSetting):
    site_slug = models.SlugField(max_length=80, default="lighthouse-labs")
    default_locale = models.CharField(max_length=2, default="en")
    supported_locales = models.JSONField(default=default_locales, blank=True)
    color_primary = models.CharField(max_length=20, default="#1d2a44")
    color_secondary = models.CharField(max_length=20, default="#6a1f2b")
    color_accent = models.CharField(max_length=20, default="#d9b26f")
    background_color = models.CharField(max_length=20, default="#f4efe7")
    font_family_token = models.CharField(max_length=255, default="Iowan Old Style, Georgia, serif")
    logo_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site_slug"),
                FieldPanel("default_locale"),
                FieldPanel("supported_locales"),
            ],
            heading="Site identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("color_primary"),
                FieldPanel("color_secondary"),
                FieldPanel("color_accent"),
                FieldPanel("background_color"),
                FieldPanel("font_family_token"),
                FieldPanel("logo_image"),
            ],
            heading="Brand",
        ),
    ]


@register_setting
class SiteChromeSettings(BaseSiteSetting):
    primary_nav = StreamField(NAV_ITEM_BLOCKS, blank=True, default=list, use_json_field=True)
    footer_groups = StreamField(FOOTER_GROUP_BLOCKS, blank=True, default=list, use_json_field=True)
    social_links = StreamField(SOCIAL_LINK_BLOCKS, blank=True, default=list, use_json_field=True)
    contact_heading_en = models.CharField(max_length=255, blank=True)
    contact_heading_fr = models.CharField(max_length=255, blank=True)
    contact_body_en = RichTextField(blank=True)
    contact_body_fr = RichTextField(blank=True)
    contact_email = models.EmailField(blank=True)
    announcement_label_en = models.CharField(max_length=255, blank=True)
    announcement_label_fr = models.CharField(max_length=255, blank=True)
    announcement_body_en = models.CharField(max_length=255, blank=True)
    announcement_body_fr = models.CharField(max_length=255, blank=True)
    announcement_link_label_en = models.CharField(max_length=255, blank=True)
    announcement_link_label_fr = models.CharField(max_length=255, blank=True)
    announcement_link_url = models.CharField(max_length=255, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("primary_nav"),
                FieldPanel("footer_groups"),
                FieldPanel("social_links"),
            ],
            heading="Navigation",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_heading_en"),
                FieldPanel("contact_heading_fr"),
                FieldPanel("contact_body_en"),
                FieldPanel("contact_body_fr"),
                FieldPanel("contact_email"),
            ],
            heading="Footer contact",
        ),
        MultiFieldPanel(
            [
                FieldPanel("announcement_label_en"),
                FieldPanel("announcement_label_fr"),
                FieldPanel("announcement_body_en"),
                FieldPanel("announcement_body_fr"),
                FieldPanel("announcement_link_label_en"),
                FieldPanel("announcement_link_label_fr"),
                FieldPanel("announcement_link_url"),
            ],
            heading="Announcement",
        ),
    ]
