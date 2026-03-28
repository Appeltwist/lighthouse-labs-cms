from rest_framework import serializers


class SiteSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    hostname = serializers.CharField()


class ImageSerializer(serializers.Serializer):
    url = serializers.CharField()
    title = serializers.CharField(allow_blank=True, allow_null=True)
    caption = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class LinkSerializer(serializers.Serializer):
    label = serializers.CharField()
    href = serializers.CharField()
    openInNewTab = serializers.BooleanField(default=False)


class FooterColumnSerializer(serializers.Serializer):
    title = serializers.CharField()
    links = LinkSerializer(many=True)


class AnnouncementSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=True, allow_null=True)
    linkLabel = serializers.CharField(allow_blank=True, allow_null=True)
    linkUrl = serializers.CharField(allow_blank=True, allow_null=True)


class ContactSettingsSerializer(serializers.Serializer):
    email = serializers.CharField(allow_blank=True, allow_null=True)
    phone = serializers.CharField(allow_blank=True, allow_null=True)
    address = serializers.CharField(allow_blank=True, allow_null=True)
    googleMapsLink = serializers.CharField(allow_blank=True, allow_null=True)
    instagram = serializers.CharField(allow_blank=True, allow_null=True)
    vimeo = serializers.CharField(allow_blank=True, allow_null=True)
    linkedin = serializers.CharField(allow_blank=True, allow_null=True)


class BrandSerializer(serializers.Serializer):
    siteName = serializers.CharField()
    logoUrl = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    primaryColor = serializers.CharField()
    secondaryColor = serializers.CharField()


class FooterSerializer(serializers.Serializer):
    columns = FooterColumnSerializer(many=True)
    socials = LinkSerializer(many=True)


class SiteConfigSerializer(serializers.Serializer):
    site = SiteSerializer()
    defaultLocale = serializers.CharField()
    locales = serializers.ListField(child=serializers.CharField())
    brand = BrandSerializer()
    nav = LinkSerializer(many=True)
    footer = FooterSerializer()
    announcement = AnnouncementSerializer(allow_null=True)
    contact = ContactSettingsSerializer()


class CtaSerializer(serializers.Serializer):
    label = serializers.CharField(allow_blank=True, allow_null=True)
    href = serializers.CharField(allow_blank=True, allow_null=True)


class HeroMediaSerializer(serializers.Serializer):
    type = serializers.CharField()
    image = ImageSerializer(allow_null=True, required=False)
    videoUrl = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class HeroSerializer(serializers.Serializer):
    title = serializers.CharField(allow_blank=True, allow_null=True)
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    media = HeroMediaSerializer(allow_null=True, required=False)
    primaryCta = CtaSerializer(allow_null=True, required=False)
    secondaryCta = CtaSerializer(allow_null=True, required=False)


class SeoSerializer(serializers.Serializer):
    title = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)


class PersonSummarySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    hasPublicProfile = serializers.BooleanField()
    role = serializers.CharField(allow_blank=True, allow_null=True)
    shortBio = serializers.CharField(allow_blank=True, allow_null=True)
    profileImage = ImageSerializer(allow_null=True, required=False)
    href = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class ProjectSummarySerializer(serializers.Serializer):
    title = serializers.CharField()
    slug = serializers.CharField()
    hasPublicPage = serializers.BooleanField()
    catalogSection = serializers.CharField(allow_blank=True, allow_null=True)
    type = serializers.CharField(allow_blank=True, allow_null=True)
    year = serializers.CharField(allow_blank=True, allow_null=True)
    directors = serializers.CharField(allow_blank=True, allow_null=True)
    listingSummary = serializers.CharField(allow_blank=True, allow_null=True)
    roles = serializers.CharField(allow_blank=True, allow_null=True)
    shortDescription = serializers.CharField(allow_blank=True, allow_null=True)
    coverImage = ImageSerializer(allow_null=True, required=False)
    href = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class ProjectCreditSerializer(serializers.Serializer):
    role = serializers.CharField()
    value = serializers.CharField(allow_blank=True, allow_null=True)
    person = PersonSummarySerializer(allow_null=True, required=False)


class ProjectMetadataSerializer(serializers.Serializer):
    format = serializers.CharField(allow_blank=True, allow_null=True)
    directors = serializers.CharField(allow_blank=True, allow_null=True)
    productionYear = serializers.CharField(allow_blank=True, allow_null=True)
    productionCountries = serializers.CharField(allow_blank=True, allow_null=True)
    languages = serializers.CharField(allow_blank=True, allow_null=True)


class PersonDetailSerializer(PersonSummarySerializer):
    profileIntro = serializers.CharField(allow_blank=True, allow_null=True)
    primaryCta = CtaSerializer(allow_null=True, required=False)
    fullBio = serializers.CharField(allow_blank=True, allow_null=True)
    sections = serializers.ListField(child=serializers.JSONField(), required=False)
    links = serializers.ListField(child=serializers.DictField(), required=False)
    relatedProjects = ProjectSummarySerializer(many=True)


class ProjectDetailSerializer(ProjectSummarySerializer):
    metadata = ProjectMetadataSerializer()
    synopsis = serializers.CharField(allow_blank=True, allow_null=True)
    fullDescription = serializers.ListField(child=serializers.JSONField())
    gallery = ImageSerializer(many=True)
    videoEmbed = serializers.CharField(allow_blank=True, allow_null=True)
    collaborators = PersonSummarySerializer(many=True)
    credits = ProjectCreditSerializer(many=True)
    externalLinks = LinkSerializer(many=True)


class RichTextSectionSerializer(serializers.Serializer):
    type = serializers.CharField()
    heading = serializers.CharField(allow_blank=True, allow_null=True)
    body = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    intro = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    items = serializers.ListField(child=serializers.JSONField(), required=False)
    caption = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    images = serializers.ListField(child=serializers.JSONField(), required=False)
    cta = CtaSerializer(allow_null=True, required=False)
    projects = ProjectSummarySerializer(many=True, required=False)


class HomeSerializer(serializers.Serializer):
    locale = serializers.CharField()
    hero = HeroSerializer()
    sections = serializers.ListField(child=serializers.JSONField())
    seo = SeoSerializer()


class AboutPageSerializer(serializers.Serializer):
    routeKey = serializers.CharField()
    locale = serializers.CharField()
    title = serializers.CharField()
    introTitle = serializers.CharField(allow_blank=True, allow_null=True)
    introText = serializers.CharField(allow_blank=True, allow_null=True)
    introImage = ImageSerializer(allow_null=True, required=False)
    services = RichTextSectionSerializer(many=True)
    studiosEquipment = RichTextSectionSerializer(many=True)
    teamMembers = PersonSummarySerializer(many=True)
    seo = SeoSerializer()


class SpaceOfferingSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    dailyRate = serializers.CharField(allow_blank=True, allow_null=True)
    hourlyRate = serializers.CharField(allow_blank=True, allow_null=True)
    capacity = serializers.CharField(allow_blank=True, allow_null=True)
    area = serializers.CharField(allow_blank=True, allow_null=True)
    includedFeatures = serializers.CharField(allow_blank=True, allow_null=True)
    extraServices = serializers.CharField(allow_blank=True, allow_null=True)


class SpaceSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    shortDescription = serializers.CharField(allow_blank=True, allow_null=True)
    mainImage = ImageSerializer(allow_null=True, required=False)
    gallery = ImageSerializer(many=True)
    area = serializers.CharField(allow_blank=True, allow_null=True)
    capacity = serializers.CharField(allow_blank=True, allow_null=True)
    equipment = serializers.CharField(allow_blank=True, allow_null=True)
    offerings = SpaceOfferingSerializer(many=True)
    bookingCta = CtaSerializer(allow_null=True, required=False)


class SpacesPageSerializer(serializers.Serializer):
    routeKey = serializers.CharField()
    locale = serializers.CharField()
    title = serializers.CharField()
    introText = serializers.CharField(allow_blank=True, allow_null=True)
    spaces = SpaceSerializer(many=True)
    seo = SeoSerializer()


class ProjectSectionSerializer(serializers.Serializer):
    title = serializers.CharField()
    intro = serializers.CharField(allow_blank=True, allow_null=True)
    projects = ProjectSummarySerializer(many=True)


class ProjectsPageSerializer(serializers.Serializer):
    routeKey = serializers.CharField()
    locale = serializers.CharField()
    title = serializers.CharField()
    introText = serializers.CharField(allow_blank=True, allow_null=True)
    sections = ProjectSectionSerializer(many=True)
    seo = SeoSerializer()


class ContactPageSerializer(serializers.Serializer):
    routeKey = serializers.CharField()
    locale = serializers.CharField()
    title = serializers.CharField()
    introText = serializers.CharField(allow_blank=True, allow_null=True)
    formEmbed = serializers.CharField(allow_blank=True, allow_null=True)
    mapEmbed = serializers.CharField(allow_blank=True, allow_null=True)
    seo = SeoSerializer()
