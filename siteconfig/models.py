from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string


def default_locales():
    return ["fr", "en"]


NAV_ITEM_BLOCKS = [
    (
        "item",
        blocks.StructBlock(
            [
                ("label", blocks.CharBlock()),
                ("label_fr", blocks.CharBlock(required=False)),
                ("href", blocks.CharBlock()),
                ("open_in_new_tab", blocks.BooleanBlock(required=False, default=False)),
            ]
        ),
    ),
]


FOOTER_COLUMN_BLOCKS = [
    (
        "column",
        blocks.StructBlock(
            [
                ("title", blocks.CharBlock()),
                ("title_fr", blocks.CharBlock(required=False)),
                (
                    "links",
                    blocks.ListBlock(
                        blocks.StructBlock(
                            [
                                ("label", blocks.CharBlock()),
                                ("label_fr", blocks.CharBlock(required=False)),
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


@register_setting
class BrandSettings(BaseSiteSetting):
    site_name = models.CharField(max_length=255, default="Lighthouse Labs")
    default_locale = models.CharField(max_length=2, default="fr")
    supported_locales = models.JSONField(default=default_locales, blank=True)
    logo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    primary_color = models.CharField(max_length=20, default="#1d2a44")
    secondary_color = models.CharField(max_length=20, default="#b85c38")

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site_name"),
                FieldPanel("default_locale"),
                FieldPanel("supported_locales"),
            ],
            heading="Site identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("logo"),
                FieldPanel("primary_color"),
                FieldPanel("secondary_color"),
            ],
            heading="Brand",
        ),
    ]


@register_setting
class SiteChromeSettings(BaseSiteSetting):
    nav_items = StreamField(NAV_ITEM_BLOCKS, blank=True, default=list, use_json_field=True)
    footer_columns = StreamField(FOOTER_COLUMN_BLOCKS, blank=True, default=list, use_json_field=True)
    announcement_text = models.CharField(max_length=255, blank=True)
    announcement_text_fr = models.CharField(max_length=255, blank=True)
    announcement_link_label = models.CharField(max_length=255, blank=True)
    announcement_link_label_fr = models.CharField(max_length=255, blank=True)
    announcement_link = models.CharField(max_length=255, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("nav_items"),
                FieldPanel("footer_columns"),
            ],
            heading="Navigation and footer",
        ),
        MultiFieldPanel(
            [
                FieldPanel("announcement_text"),
                FieldPanel("announcement_text_fr"),
                FieldPanel("announcement_link_label"),
                FieldPanel("announcement_link_label_fr"),
                FieldPanel("announcement_link"),
            ],
            heading="Announcement bar",
        ),
    ]


@register_setting
class ContactSettings(BaseSiteSetting):
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    google_maps_link = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    vimeo = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("phone"),
                FieldPanel("address"),
                FieldPanel("google_maps_link"),
            ],
            heading="Primary contact",
        ),
        MultiFieldPanel(
            [
                FieldPanel("instagram"),
                FieldPanel("vimeo"),
                FieldPanel("linkedin"),
            ],
            heading="Social links",
        ),
    ]
