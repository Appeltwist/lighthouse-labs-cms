from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class FeatureItemBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    href = blocks.CharBlock(required=False)


class FeatureGridBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(required=False)
    items = blocks.ListBlock(FeatureItemBlock())


class RichTextSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock()


class GalleryBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    images = blocks.ListBlock(ImageChooserBlock())
    caption = blocks.CharBlock(required=False)
    surface = blocks.ChoiceBlock(
        choices=[
            ("dark", "Dark"),
            ("light", "Light"),
        ],
        required=False,
        default="dark",
    )


class CtaBandBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(required=False)
    label = blocks.CharBlock()
    href = blocks.CharBlock()


class ProjectHighlightsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(required=False)
    projects = blocks.ListBlock(SnippetChooserBlock("pages.Project"))


class HighlightItemBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    body = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_label = blocks.CharBlock(required=False)
    link_url = blocks.CharBlock(required=False)


class HighlightStripBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    items = blocks.ListBlock(HighlightItemBlock())


class CollaborationItemBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    image = ImageChooserBlock(required=False)
    link_url = blocks.CharBlock(required=False)
    note = blocks.TextBlock(required=False)


class CollaborationsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(required=False)
    items = blocks.ListBlock(CollaborationItemBlock())


class AwardItemBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    detail = blocks.CharBlock(required=False)


class AwardsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    items = blocks.ListBlock(AwardItemBlock())


class EmbedSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    embed_url = blocks.CharBlock()
    aspect_ratio = blocks.ChoiceBlock(
        choices=[
            ("wide", "Wide"),
            ("square", "Square"),
            ("portrait", "Portrait"),
        ],
        required=False,
        default="wide",
    )


class AudioTrackBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    artist = blocks.CharBlock(required=False)
    cover_image = ImageChooserBlock(required=False)
    audio_file = DocumentChooserBlock(required=False)
    audio_url = blocks.URLBlock(required=False)
    external_url = blocks.URLBlock(required=False)


class AudioPlaylistBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(required=False)
    tracks = blocks.ListBlock(AudioTrackBlock())


def rich_content_blocks():
    return [
        ("rich_text", RichTextSectionBlock()),
        ("feature_grid", FeatureGridBlock()),
        ("gallery", GalleryBlock()),
        ("cta_band", CtaBandBlock()),
    ]


def home_body_blocks():
    return [
        ("highlight_strip", HighlightStripBlock()),
        ("feature_grid", FeatureGridBlock()),
        ("project_highlights", ProjectHighlightsBlock()),
        ("gallery", GalleryBlock()),
        ("collaborations", CollaborationsBlock()),
        ("awards", AwardsBlock()),
        ("cta_band", CtaBandBlock()),
    ]


def person_profile_blocks():
    return [
        ("rich_text", RichTextSectionBlock()),
        ("embed", EmbedSectionBlock()),
        ("project_highlights", ProjectHighlightsBlock()),
        ("audio_playlist", AudioPlaylistBlock()),
        ("gallery", GalleryBlock()),
        ("cta_band", CtaBandBlock()),
    ]
