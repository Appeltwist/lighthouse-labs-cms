from rest_framework import serializers


class SiteSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    hostname = serializers.CharField()


class BrandSerializer(serializers.Serializer):
    colorPrimary = serializers.CharField()
    colorSecondary = serializers.CharField()
    colorAccent = serializers.CharField()
    backgroundColor = serializers.CharField()
    fontFamily = serializers.CharField()
    logoUrl = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class NavItemSerializer(serializers.Serializer):
    label = serializers.CharField()
    href = serializers.CharField()
    openInNewTab = serializers.BooleanField(default=False)


class FooterLinkSerializer(serializers.Serializer):
    label = serializers.CharField()
    href = serializers.CharField()
    openInNewTab = serializers.BooleanField(default=False)


class FooterGroupSerializer(serializers.Serializer):
    title = serializers.CharField()
    links = FooterLinkSerializer(many=True)


class FooterContactSerializer(serializers.Serializer):
    heading = serializers.CharField(allow_blank=True, allow_null=True)
    body = serializers.CharField(allow_blank=True, allow_null=True)
    email = serializers.CharField(allow_blank=True, allow_null=True)


class SocialLinkSerializer(serializers.Serializer):
    label = serializers.CharField()
    url = serializers.CharField()


class FooterSerializer(serializers.Serializer):
    groups = FooterGroupSerializer(many=True)
    contact = FooterContactSerializer()
    socials = SocialLinkSerializer(many=True)


class AnnouncementSerializer(serializers.Serializer):
    label = serializers.CharField(allow_blank=True, allow_null=True)
    body = serializers.CharField(allow_blank=True, allow_null=True)
    linkLabel = serializers.CharField(allow_blank=True, allow_null=True)
    linkUrl = serializers.CharField(allow_blank=True, allow_null=True)


class SiteConfigSerializer(serializers.Serializer):
    site = SiteSerializer()
    defaultLocale = serializers.CharField()
    locales = serializers.ListField(child=serializers.CharField())
    brand = BrandSerializer()
    nav = NavItemSerializer(many=True)
    footer = FooterSerializer()
    announcement = AnnouncementSerializer(allow_null=True)


class ImageSerializer(serializers.Serializer):
    url = serializers.CharField()
    title = serializers.CharField(allow_blank=True, allow_null=True)


class HeroSerializer(serializers.Serializer):
    eyebrow = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    title = serializers.CharField(allow_blank=True, allow_null=True)
    body = serializers.CharField(allow_blank=True, allow_null=True)
    image = ImageSerializer(allow_null=True, required=False)


class IntroSerializer(serializers.Serializer):
    heading = serializers.CharField(allow_blank=True, allow_null=True)
    body = serializers.CharField(allow_blank=True, allow_null=True)


class FeaturedTileSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    ctaLabel = serializers.CharField()
    ctaHref = serializers.CharField()


class SeoSerializer(serializers.Serializer):
    title = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField(allow_blank=True, allow_null=True)


class StreamBlockSerializer(serializers.Serializer):
    type = serializers.CharField()
    value = serializers.JSONField()


class HomeSerializer(serializers.Serializer):
    site = SiteSerializer()
    locale = serializers.CharField()
    hero = HeroSerializer()
    intro = IntroSerializer()
    featuredTiles = FeaturedTileSerializer(many=True)
    sections = StreamBlockSerializer(many=True)
    seo = SeoSerializer()


class PrimaryCtaSerializer(serializers.Serializer):
    label = serializers.CharField(allow_blank=True, allow_null=True)
    url = serializers.CharField(allow_blank=True, allow_null=True)


class NarrativePageSerializer(serializers.Serializer):
    routeKey = serializers.CharField()
    locale = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True, allow_null=True)
    hero = HeroSerializer()
    sections = StreamBlockSerializer(many=True)
    primaryCta = PrimaryCtaSerializer(allow_null=True)
    seo = SeoSerializer()
