from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet

from pages.blocks import home_body_blocks, person_profile_blocks, rich_content_blocks


SUPPORTED_LOCALES = (
    ("en", "English"),
    ("fr", "French"),
)


WAGTAIL_IMAGE_MODEL = get_image_model_string()


def normalize_locale(locale: str) -> str:
    return "fr" if (locale or "").strip().lower().startswith("fr") else "en"


class LocalizedFieldsMixin(models.Model):
    class Meta:
        abstract = True

    def translated(self, field_name: str, locale: str, default=""):
        language = normalize_locale(locale)
        primary_field = f"{field_name}_fr" if language == "fr" else field_name
        secondary_field = field_name if language == "fr" else f"{field_name}_fr"
        primary_value = getattr(self, primary_field, "")
        secondary_value = getattr(self, secondary_field, "")
        return primary_value or secondary_value or default


class SeoFieldsMixin(LocalizedFieldsMixin):
    seo_title_override = models.CharField(max_length=255, blank=True)
    seo_title_override_fr = models.CharField(max_length=255, blank=True)
    seo_description_override = models.TextField(blank=True)
    seo_description_override_fr = models.TextField(blank=True)

    class Meta:
        abstract = True


@register_snippet
class Person(LocalizedFieldsMixin, ClusterableModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    has_public_profile = models.BooleanField(default=False)
    email = models.EmailField(blank=True)
    profile_image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    role = models.CharField(max_length=255, blank=True)
    role_fr = models.CharField(max_length=255, blank=True)
    short_bio = models.TextField(blank=True)
    short_bio_fr = models.TextField(blank=True)
    profile_intro = RichTextField(blank=True)
    profile_intro_fr = RichTextField(blank=True)
    primary_cta_label = models.CharField(max_length=255, blank=True)
    primary_cta_label_fr = models.CharField(max_length=255, blank=True)
    primary_cta_link = models.CharField(max_length=255, blank=True)
    full_bio = RichTextField(blank=True)
    full_bio_fr = RichTextField(blank=True)
    profile_sections = StreamField(person_profile_blocks(), blank=True, default=list, use_json_field=True)
    profile_sections_fr = StreamField(person_profile_blocks(), blank=True, default=list, use_json_field=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("slug"),
                FieldPanel("has_public_profile"),
                FieldPanel("email"),
                FieldPanel("profile_image"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("role"),
                FieldPanel("role_fr"),
                FieldPanel("short_bio"),
                FieldPanel("short_bio_fr"),
                FieldPanel("profile_intro"),
                FieldPanel("profile_intro_fr"),
                FieldPanel("full_bio"),
                FieldPanel("full_bio_fr"),
            ],
            heading="Profile",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_label_fr"),
                FieldPanel("primary_cta_link"),
            ],
            heading="Call to action",
        ),
        MultiFieldPanel(
            [
                FieldPanel("profile_sections"),
                FieldPanel("profile_sections_fr"),
            ],
            heading="Profile sections",
        ),
        InlinePanel("links", label="Links"),
        InlinePanel("related_projects", label="Related projects"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PersonLink(Orderable):
    person = ParentalKey("pages.Person", on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=255)
    url = models.URLField(max_length=500)

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
    ]

    def __str__(self):
        return self.label


@register_snippet
class Project(LocalizedFieldsMixin, ClusterableModel):
    title = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True)
    has_public_page = models.BooleanField(default=False)
    catalog_section = models.CharField(max_length=255, blank=True)
    catalog_section_fr = models.CharField(max_length=255, blank=True)
    cover_image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    project_type = models.CharField(max_length=255, blank=True)
    project_type_fr = models.CharField(max_length=255, blank=True)
    year = models.CharField(max_length=32, blank=True)
    directors = models.CharField(max_length=255, blank=True)
    directors_fr = models.CharField(max_length=255, blank=True)
    production_countries = models.CharField(max_length=255, blank=True)
    production_countries_fr = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, blank=True)
    languages_fr = models.CharField(max_length=255, blank=True)
    roles = models.TextField(blank=True)
    roles_fr = models.TextField(blank=True)
    listing_summary = models.TextField(blank=True)
    listing_summary_fr = models.TextField(blank=True)
    short_description = models.TextField(blank=True)
    short_description_fr = models.TextField(blank=True)
    synopsis = RichTextField(blank=True)
    synopsis_fr = RichTextField(blank=True)
    full_description = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)
    full_description_fr = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)
    video_embed = models.TextField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("title_fr"),
                FieldPanel("slug"),
                FieldPanel("has_public_page"),
                FieldPanel("catalog_section"),
                FieldPanel("catalog_section_fr"),
                FieldPanel("cover_image"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("project_type"),
                FieldPanel("project_type_fr"),
                FieldPanel("year"),
                FieldPanel("directors"),
                FieldPanel("directors_fr"),
                FieldPanel("production_countries"),
                FieldPanel("production_countries_fr"),
                FieldPanel("languages"),
                FieldPanel("languages_fr"),
                FieldPanel("roles"),
                FieldPanel("roles_fr"),
                FieldPanel("listing_summary"),
                FieldPanel("listing_summary_fr"),
                FieldPanel("short_description"),
                FieldPanel("short_description_fr"),
                FieldPanel("synopsis"),
                FieldPanel("synopsis_fr"),
            ],
            heading="Summary",
        ),
        MultiFieldPanel(
            [
                FieldPanel("full_description"),
                FieldPanel("full_description_fr"),
                FieldPanel("video_embed"),
            ],
            heading="Detail content",
        ),
        InlinePanel("gallery_images", label="Gallery images"),
        InlinePanel("collaborators", label="Collaborators"),
        InlinePanel("credits", label="Credits"),
        InlinePanel("external_links", label="External links"),
    ]

    class Meta:
        ordering = ["-year", "title"]

    def __str__(self):
        return self.title


class PersonRelatedProject(Orderable):
    person = ParentalKey("pages.Person", on_delete=models.CASCADE, related_name="related_projects")
    project = models.ForeignKey("pages.Project", on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("project"),
    ]

    def __str__(self):
        return str(self.project)


class ProjectGalleryImage(Orderable, LocalizedFieldsMixin):
    project = ParentalKey("pages.Project", on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=255, blank=True)
    caption_fr = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
        FieldPanel("caption_fr"),
    ]

    def __str__(self):
        return getattr(self.image, "title", "Project image")


class ProjectCollaborator(Orderable):
    project = ParentalKey("pages.Project", on_delete=models.CASCADE, related_name="collaborators")
    person = models.ForeignKey("pages.Person", on_delete=models.CASCADE, related_name="project_collaborations")

    panels = [
        FieldPanel("person"),
    ]

    def __str__(self):
        return str(self.person)


class ProjectCredit(Orderable, LocalizedFieldsMixin):
    project = ParentalKey("pages.Project", on_delete=models.CASCADE, related_name="credits")
    role = models.CharField(max_length=255)
    role_fr = models.CharField(max_length=255, blank=True)
    value = models.CharField(max_length=255, blank=True)
    value_fr = models.CharField(max_length=255, blank=True)
    person = models.ForeignKey(
        "pages.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="credited_projects",
    )

    panels = [
        FieldPanel("role"),
        FieldPanel("role_fr"),
        FieldPanel("value"),
        FieldPanel("value_fr"),
        FieldPanel("person"),
    ]

    def __str__(self):
        return self.role


class ProjectExternalLink(Orderable, LocalizedFieldsMixin):
    project = ParentalKey("pages.Project", on_delete=models.CASCADE, related_name="external_links")
    label = models.CharField(max_length=255)
    label_fr = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=500)

    panels = [
        FieldPanel("label"),
        FieldPanel("label_fr"),
        FieldPanel("url"),
    ]

    def __str__(self):
        return self.label


@register_snippet
class Space(LocalizedFieldsMixin, ClusterableModel):
    name = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(blank=True)
    short_description_fr = models.TextField(blank=True)
    main_image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    area = models.CharField(max_length=255, blank=True)
    capacity = models.CharField(max_length=255, blank=True)
    equipment = RichTextField(blank=True)
    equipment_fr = RichTextField(blank=True)
    booking_label = models.CharField(max_length=255, blank=True)
    booking_label_fr = models.CharField(max_length=255, blank=True)
    booking_link = models.CharField(max_length=255, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("name_fr"),
                FieldPanel("slug"),
                FieldPanel("main_image"),
                FieldPanel("area"),
                FieldPanel("capacity"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("short_description"),
                FieldPanel("short_description_fr"),
                FieldPanel("equipment"),
                FieldPanel("equipment_fr"),
            ],
            heading="Space details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("booking_label"),
                FieldPanel("booking_label_fr"),
                FieldPanel("booking_link"),
            ],
            heading="Booking",
        ),
        InlinePanel("gallery_images", label="Gallery images"),
        InlinePanel("offerings", label="Offerings"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SpaceGalleryImage(Orderable, LocalizedFieldsMixin):
    space = ParentalKey("pages.Space", on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=255, blank=True)
    caption_fr = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
        FieldPanel("caption_fr"),
    ]

    def __str__(self):
        return getattr(self.image, "title", "Space image")


class SpaceOffering(Orderable, LocalizedFieldsMixin):
    space = ParentalKey("pages.Space", on_delete=models.CASCADE, related_name="offerings")
    title = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_fr = models.TextField(blank=True)
    daily_rate = models.CharField(max_length=255, blank=True)
    hourly_rate = models.CharField(max_length=255, blank=True)
    capacity = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=255, blank=True)
    included_features = RichTextField(blank=True)
    included_features_fr = RichTextField(blank=True)
    extra_services = RichTextField(blank=True)
    extra_services_fr = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("title_fr"),
        FieldPanel("description"),
        FieldPanel("description_fr"),
        FieldPanel("daily_rate"),
        FieldPanel("hourly_rate"),
        FieldPanel("capacity"),
        FieldPanel("area"),
        FieldPanel("included_features"),
        FieldPanel("included_features_fr"),
        FieldPanel("extra_services"),
        FieldPanel("extra_services_fr"),
    ]

    def __str__(self):
        return self.title


class HomePage(SeoFieldsMixin, Page):
    max_count = 1

    hero_title = models.CharField(max_length=255, blank=True)
    hero_title_fr = models.CharField(max_length=255, blank=True)
    hero_subtitle = RichTextField(blank=True)
    hero_subtitle_fr = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_video_url = models.URLField(blank=True)
    primary_cta_label = models.CharField(max_length=255, blank=True)
    primary_cta_label_fr = models.CharField(max_length=255, blank=True)
    primary_cta_link = models.CharField(max_length=255, blank=True)
    secondary_cta_label = models.CharField(max_length=255, blank=True)
    secondary_cta_label_fr = models.CharField(max_length=255, blank=True)
    secondary_cta_link = models.CharField(max_length=255, blank=True)
    body = StreamField(home_body_blocks(), blank=True, default=list, use_json_field=True)
    body_fr = StreamField(home_body_blocks(), blank=True, default=list, use_json_field=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_title_fr"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_subtitle_fr"),
                FieldPanel("hero_image"),
                FieldPanel("hero_video_url"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_cta_label"),
                FieldPanel("primary_cta_label_fr"),
                FieldPanel("primary_cta_link"),
                FieldPanel("secondary_cta_label"),
                FieldPanel("secondary_cta_label_fr"),
                FieldPanel("secondary_cta_link"),
            ],
            heading="Calls to action",
        ),
        MultiFieldPanel(
            [
                FieldPanel("body"),
                FieldPanel("body_fr"),
            ],
            heading="Body",
        ),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_title_override_fr"),
                FieldPanel("seo_description_override"),
                FieldPanel("seo_description_override_fr"),
            ],
            heading="SEO",
        ),
    ]

    subpage_types = [
        "pages.AboutPage",
        "pages.SpacesPage",
        "pages.ProjectsPage",
        "pages.ContactPage",
        "pages.StandardPage",
    ]


class StandardPage(SeoFieldsMixin, Page):
    title_display = models.CharField(max_length=255, blank=True)
    title_display_fr = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    subtitle_fr = models.CharField(max_length=255, blank=True)
    hero_image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)
    body_fr = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("title_display"),
                FieldPanel("title_display_fr"),
                FieldPanel("subtitle"),
                FieldPanel("subtitle_fr"),
                FieldPanel("hero_image"),
            ],
            heading="Heading",
        ),
        MultiFieldPanel(
            [
                FieldPanel("body"),
                FieldPanel("body_fr"),
            ],
            heading="Body",
        ),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_title_override_fr"),
                FieldPanel("seo_description_override"),
                FieldPanel("seo_description_override_fr"),
            ],
            heading="SEO",
        ),
    ]


class AboutPage(SeoFieldsMixin, Page):
    title_display = models.CharField(max_length=255, blank=True)
    title_display_fr = models.CharField(max_length=255, blank=True)
    intro_title = models.CharField(max_length=255, blank=True)
    intro_title_fr = models.CharField(max_length=255, blank=True)
    intro_text = RichTextField(blank=True)
    intro_text_fr = RichTextField(blank=True)
    intro_image = models.ForeignKey(
        WAGTAIL_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    services = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)
    services_fr = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)
    studios_equipment = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)
    studios_equipment_fr = StreamField(rich_content_blocks(), blank=True, default=list, use_json_field=True)

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("title_display"),
                FieldPanel("title_display_fr"),
                FieldPanel("intro_title"),
                FieldPanel("intro_title_fr"),
                FieldPanel("intro_text"),
                FieldPanel("intro_text_fr"),
                FieldPanel("intro_image"),
            ],
            heading="Intro",
        ),
        MultiFieldPanel(
            [
                FieldPanel("services"),
                FieldPanel("services_fr"),
            ],
            heading="Services",
        ),
        MultiFieldPanel(
            [
                FieldPanel("studios_equipment"),
                FieldPanel("studios_equipment_fr"),
            ],
            heading="Studios and equipment",
        ),
        InlinePanel("team_members", label="Team members"),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_title_override_fr"),
                FieldPanel("seo_description_override"),
                FieldPanel("seo_description_override_fr"),
            ],
            heading="SEO",
        ),
    ]


class AboutPageTeamMember(Orderable):
    page = ParentalKey("pages.AboutPage", on_delete=models.CASCADE, related_name="team_members")
    person = models.ForeignKey("pages.Person", on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("person"),
    ]

    def __str__(self):
        return str(self.person)


class SpacesPage(SeoFieldsMixin, Page):
    title_display = models.CharField(max_length=255, blank=True)
    title_display_fr = models.CharField(max_length=255, blank=True)
    intro_text = RichTextField(blank=True)
    intro_text_fr = RichTextField(blank=True)

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("title_display"),
                FieldPanel("title_display_fr"),
                FieldPanel("intro_text"),
                FieldPanel("intro_text_fr"),
            ],
            heading="Page intro",
        ),
        InlinePanel("spaces", label="Spaces"),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_title_override_fr"),
                FieldPanel("seo_description_override"),
                FieldPanel("seo_description_override_fr"),
            ],
            heading="SEO",
        ),
    ]


class SpacesPageSpace(Orderable):
    page = ParentalKey("pages.SpacesPage", on_delete=models.CASCADE, related_name="spaces")
    space = models.ForeignKey("pages.Space", on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("space"),
    ]

    def __str__(self):
        return str(self.space)


class ProjectsPage(SeoFieldsMixin, Page):
    title_display = models.CharField(max_length=255, blank=True)
    title_display_fr = models.CharField(max_length=255, blank=True)
    intro_text = RichTextField(blank=True)
    intro_text_fr = RichTextField(blank=True)

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("title_display"),
                FieldPanel("title_display_fr"),
                FieldPanel("intro_text"),
                FieldPanel("intro_text_fr"),
            ],
            heading="Page intro",
        ),
        InlinePanel("sections", label="Sections"),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_title_override_fr"),
                FieldPanel("seo_description_override"),
                FieldPanel("seo_description_override_fr"),
            ],
            heading="SEO",
        ),
    ]


class ProjectsPageSection(Orderable, LocalizedFieldsMixin, ClusterableModel):
    page = ParentalKey("pages.ProjectsPage", on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    title_fr = models.CharField(max_length=255, blank=True)
    intro = RichTextField(blank=True)
    intro_fr = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("title_fr"),
        FieldPanel("intro"),
        FieldPanel("intro_fr"),
        InlinePanel("projects", label="Projects"),
    ]

    def __str__(self):
        return self.title


class ProjectsPageSectionProject(Orderable):
    section = ParentalKey("pages.ProjectsPageSection", on_delete=models.CASCADE, related_name="projects")
    project = models.ForeignKey("pages.Project", on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("project"),
    ]

    def __str__(self):
        return str(self.project)


class ContactPage(SeoFieldsMixin, Page):
    title_display = models.CharField(max_length=255, blank=True)
    title_display_fr = models.CharField(max_length=255, blank=True)
    intro_text = RichTextField(blank=True)
    intro_text_fr = RichTextField(blank=True)
    form_embed = models.TextField(blank=True)
    form_embed_fr = models.TextField(blank=True)
    map_embed = models.TextField(blank=True)

    parent_page_types = ["pages.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("title_display"),
                FieldPanel("title_display_fr"),
                FieldPanel("intro_text"),
                FieldPanel("intro_text_fr"),
            ],
            heading="Intro",
        ),
        MultiFieldPanel(
            [
                FieldPanel("form_embed"),
                FieldPanel("form_embed_fr"),
                FieldPanel("map_embed"),
            ],
            heading="Embeds",
        ),
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_title_override_fr"),
                FieldPanel("seo_description_override"),
                FieldPanel("seo_description_override_fr"),
            ],
            heading="SEO",
        ),
    ]
