from collections.abc import Mapping
from urllib.parse import urlsplit

from django.http import JsonResponse
from django.utils.text import slugify
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.models import Site

from api.serializers import HomeSerializer, NarrativePageSerializer, SiteConfigSerializer
from pages.models import HomePage, NarrativePage
from siteconfig.models import BrandSettings, SiteChromeSettings


def health(_request):
    return JsonResponse({"status": "ok"})


def _clean_optional(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _extract_hostname(raw_value: str) -> str:
    value = _clean_optional(raw_value).lower()
    if not value:
        return ""
    if "://" in value:
        value = (urlsplit(value).hostname or "").lower()
    if ":" in value:
        value = value.split(":", 1)[0]
    return value


def _resolve_site(request):
    requested = request.query_params.get("domain") or request.get_host()
    hostname = _extract_hostname(requested)
    site = Site.objects.filter(hostname=hostname).first() if hostname else None
    if site is None and Site.objects.count() == 1:
        return Site.objects.first()
    if site is None:
        raise NotFound(f'No site found for hostname "{hostname or requested}".')
    return site


def _resolve_brand(site):
    brand = BrandSettings.objects.filter(site=site).first()
    if brand is None:
        raise NotFound("Brand settings have not been configured for this site.")
    return brand


def _resolve_site_chrome(site):
    chrome = SiteChromeSettings.objects.filter(site=site).first()
    if chrome is None:
        raise NotFound("Site chrome settings have not been configured for this site.")
    return chrome


def _resolve_home_page(site):
    home_page = site.root_page.specific if site.root_page_id else None
    if not isinstance(home_page, HomePage):
        raise NotFound("Home page is not configured for this site.")
    return home_page


def _resolve_locale(request, *, default_locale: str, supported_locales: list[str]):
    locale = _clean_optional(request.query_params.get("locale")).lower() or default_locale.lower()
    if locale not in supported_locales:
        return default_locale.lower()
    return locale


def _localize_text(locale: str, *, en_value="", fr_value=""):
    if locale.startswith("fr"):
        return _clean_optional(fr_value) or _clean_optional(en_value)
    return _clean_optional(en_value) or _clean_optional(fr_value)


def _image_payload(image, request):
    if not image:
        return None
    return {
        "url": request.build_absolute_uri(image.file.url),
        "title": _clean_optional(getattr(image, "title", "")),
    }


def _serialize_stream_value(value, request):
    if hasattr(value, "file") and hasattr(value, "title"):
        return _image_payload(value, request)
    if hasattr(value, "source"):
        return str(value)
    if isinstance(value, Mapping):
        return {key: _serialize_stream_value(item, request) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_stream_value(item, request) for item in value]
    return value


def _serialize_stream_field(stream_value, request):
    if not stream_value:
        return []
    return [
        {
            "type": block.block_type,
            "value": _serialize_stream_value(block.value, request),
        }
        for block in stream_value
    ]


def _serialize_nav(chrome, locale: str):
    items = []
    for block in chrome.primary_nav:
        value = block.value
        items.append(
            {
                "label": _localize_text(locale, en_value=value.get("label_en"), fr_value=value.get("label_fr")),
                "href": _clean_optional(value.get("href")),
                "openInNewTab": bool(value.get("open_in_new_tab")),
            }
        )
    return items


def _serialize_footer(chrome, locale: str):
    groups = []
    for block in chrome.footer_groups:
        value = block.value
        links = [
            {
                "label": _localize_text(locale, en_value=link.get("label_en"), fr_value=link.get("label_fr")),
                "href": _clean_optional(link.get("href")),
                "openInNewTab": bool(link.get("open_in_new_tab")),
            }
            for link in value.get("links", [])
        ]
        groups.append(
            {
                "title": _localize_text(locale, en_value=value.get("title_en"), fr_value=value.get("title_fr")),
                "links": links,
            }
        )
    socials = [{"label": _clean_optional(block.value.get("label")), "url": _clean_optional(block.value.get("url"))} for block in chrome.social_links]
    return {
        "groups": groups,
        "contact": {
            "heading": _localize_text(
                locale,
                en_value=chrome.contact_heading_en,
                fr_value=chrome.contact_heading_fr,
            ),
            "body": _localize_text(locale, en_value=chrome.contact_body_en, fr_value=chrome.contact_body_fr),
            "email": _clean_optional(chrome.contact_email),
        },
        "socials": socials,
    }


def _serialize_announcement(chrome, locale: str):
    label = _localize_text(locale, en_value=chrome.announcement_label_en, fr_value=chrome.announcement_label_fr)
    body = _localize_text(locale, en_value=chrome.announcement_body_en, fr_value=chrome.announcement_body_fr)
    link_label = _localize_text(
        locale,
        en_value=chrome.announcement_link_label_en,
        fr_value=chrome.announcement_link_label_fr,
    )
    link_url = _clean_optional(chrome.announcement_link_url)
    if not any([label, body, link_label, link_url]):
        return None
    return {
        "label": label,
        "body": body,
        "linkLabel": link_label,
        "linkUrl": link_url,
    }


def _site_payload(site, brand):
    return {
        "name": _clean_optional(site.site_name),
        "slug": _clean_optional(getattr(brand, "site_slug", "")) or slugify(site.site_name),
        "hostname": _clean_optional(site.hostname),
    }


def _brand_payload(brand, request):
    return {
        "colorPrimary": brand.color_primary,
        "colorSecondary": brand.color_secondary,
        "colorAccent": brand.color_accent,
        "backgroundColor": brand.background_color,
        "fontFamily": brand.font_family_token,
        "logoUrl": request.build_absolute_uri(brand.logo_image.file.url) if brand.logo_image else None,
    }


def _featured_tiles_payload(stream_value):
    tiles = []
    for block in stream_value:
        value = block.value
        tiles.append(
            {
                "title": _clean_optional(value.get("title")),
                "description": _clean_optional(value.get("description")),
                "ctaLabel": _clean_optional(value.get("cta_label")),
                "ctaHref": _clean_optional(value.get("cta_href")),
            }
        )
    return tiles


def _resolve_narrative_page(site, route_key: str, locale: str, default_locale: str):
    page = NarrativePage.objects.filter(site=site, route_key=route_key, language_code=locale).first()
    if page is None and locale != default_locale:
        page = NarrativePage.objects.filter(site=site, route_key=route_key, language_code=default_locale).first()
        locale = default_locale
    if page is None:
        raise NotFound("Page not found for the requested route.")
    return page, locale


class SiteConfigAPIView(APIView):
    def get(self, request):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        chrome = _resolve_site_chrome(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)
        payload = {
            "site": _site_payload(site, brand),
            "defaultLocale": brand.default_locale.lower(),
            "locales": [locale_code.lower() for locale_code in brand.supported_locales],
            "brand": _brand_payload(brand, request),
            "nav": _serialize_nav(chrome, locale),
            "footer": _serialize_footer(chrome, locale),
            "announcement": _serialize_announcement(chrome, locale),
        }
        serializer = SiteConfigSerializer(payload)
        return Response(serializer.data)


class HomeAPIView(APIView):
    def get(self, request):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        home_page = _resolve_home_page(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)
        hero = home_page.hero_for(locale)
        payload = {
            "site": _site_payload(site, brand),
            "locale": locale,
            "hero": {
                "eyebrow": _clean_optional(hero.get("eyebrow")),
                "title": _clean_optional(hero.get("title")),
                "body": _clean_optional(hero.get("body")),
                "image": _image_payload(hero.get("image"), request),
            },
            "intro": home_page.intro_for(locale),
            "featuredTiles": _featured_tiles_payload(home_page.featured_tiles_for(locale)),
            "sections": _serialize_stream_field(home_page.sections_for(locale), request),
            "seo": home_page.seo_for(locale),
        }
        serializer = HomeSerializer(payload)
        return Response(serializer.data)


class NarrativePageAPIView(APIView):
    def get(self, request, route_key):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)
        page, resolved_locale = _resolve_narrative_page(site, route_key, locale, brand.default_locale.lower())
        payload = {
            "routeKey": page.route_key,
            "locale": resolved_locale,
            "title": _clean_optional(page.title),
            "subtitle": _clean_optional(page.subtitle),
            "hero": {
                "title": _clean_optional(page.hero_title) or _clean_optional(page.title),
                "body": _clean_optional(page.hero_body),
                "image": _image_payload(page.hero_image, request),
            },
            "sections": _serialize_stream_field(page.sections, request),
            "primaryCta": {
                "label": _clean_optional(page.primary_cta_label),
                "url": _clean_optional(page.primary_cta_url),
            }
            if page.primary_cta_label or page.primary_cta_url
            else None,
            "seo": {
                "title": _clean_optional(page.meta_title),
                "description": _clean_optional(page.meta_description),
            },
        }
        serializer = NarrativePageSerializer(payload)
        return Response(serializer.data)
