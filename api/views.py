from collections.abc import Mapping
from urllib.parse import urlsplit

from django.http import JsonResponse
from django.utils.text import slugify
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.models import Site

from api.serializers import (
    AboutPageSerializer,
    ContactPageSerializer,
    HomeSerializer,
    PersonDetailSerializer,
    ProjectDetailSerializer,
    ProjectsPageSerializer,
    SiteConfigSerializer,
    SpacesPageSerializer,
)
from pages.models import (
    AboutPage,
    ContactPage,
    HomePage,
    Person,
    Project,
    ProjectsPage,
    SpacesPage,
)
from siteconfig.models import BrandSettings, ContactSettings, SiteChromeSettings


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
    configured_site_ids = list(BrandSettings.objects.values_list("site_id", flat=True))
    configured_sites = Site.objects.filter(id__in=configured_site_ids)
    site = Site.objects.filter(hostname=hostname).first() if hostname else None

    if site is not None and site.id in configured_site_ids:
        return site

    if configured_sites.count() == 1:
        return configured_sites.first()

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


def _resolve_contact_settings(site):
    contact = ContactSettings.objects.filter(site=site).first()
    if contact is None:
        raise NotFound("Contact settings have not been configured for this site.")
    return contact


def _resolve_home_page(site):
    home_page = site.root_page.specific if site.root_page_id else None
    if not isinstance(home_page, HomePage):
        raise NotFound("Home page is not configured for this site.")
    return home_page


def _resolve_child_page(site, model_class):
    page = model_class.objects.child_of(site.root_page).live().first()
    if page is None:
        raise NotFound(f"{model_class.__name__} is not configured for this site.")
    return page


def _resolve_locale(request, *, default_locale: str, supported_locales: list[str]):
    locale = _clean_optional(request.query_params.get("locale")).lower() or default_locale.lower()
    if locale not in supported_locales:
        return default_locale.lower()
    return locale


def _localized_value(source, field_name: str, locale: str):
    if hasattr(source, "translated"):
        return source.translated(field_name, locale)
    if isinstance(source, Mapping):
        if locale.startswith("fr"):
            return source.get(f"{field_name}_fr") or source.get(field_name) or ""
        return source.get(field_name) or source.get(f"{field_name}_fr") or ""
    if locale.startswith("fr"):
        return getattr(source, f"{field_name}_fr", "") or getattr(source, field_name, "") or ""
    return getattr(source, field_name, "") or getattr(source, f"{field_name}_fr", "") or ""


def _localized_text(source, field_name: str, locale: str):
    return _clean_optional(_localized_value(source, field_name, locale))


def _image_payload(image, request):
    if not image:
        return None
    return {
        "url": request.build_absolute_uri(image.file.url),
        "title": _clean_optional(getattr(image, "title", "")),
    }


def _document_payload(document, request):
    if not document:
        return None
    return {
        "url": request.build_absolute_uri(document.file.url),
        "title": _clean_optional(getattr(document, "title", "")),
    }


def _gallery_item_payload(image, request, caption=""):
    payload = _image_payload(image, request)
    if payload is None:
        return None
    payload["caption"] = _clean_optional(caption)
    return payload


def _cta_payload(label: str, href: str):
    if not _clean_optional(label) and not _clean_optional(href):
        return None
    return {
        "label": _clean_optional(label),
        "href": _clean_optional(href),
    }


def _seo_payload(page, locale: str):
    return {
        "title": _localized_text(page, "seo_title_override", locale),
        "description": _localized_text(page, "seo_description_override", locale),
    }


def _site_payload(site, brand):
    site_name = _clean_optional(brand.site_name) or _clean_optional(site.site_name)
    return {
        "name": site_name,
        "slug": slugify(site_name or site.hostname),
        "hostname": _clean_optional(site.hostname),
    }


def _serialize_nav(chrome, locale: str):
    items = []
    for block in chrome.nav_items:
        value = block.value
        items.append(
            {
                "label": _localized_text(value, "label", locale),
                "href": _clean_optional(value.get("href")),
                "openInNewTab": bool(value.get("open_in_new_tab")),
            }
        )
    return items


def _serialize_footer(chrome, contact, locale: str):
    columns = []
    for block in chrome.footer_columns:
        value = block.value
        columns.append(
            {
                "title": _localized_text(value, "title", locale),
                "links": [
                    {
                        "label": _localized_text(link, "label", locale),
                        "href": _clean_optional(link.get("href")),
                        "openInNewTab": bool(link.get("open_in_new_tab")),
                    }
                    for link in value.get("links", [])
                ],
            }
        )

    socials = []
    if _clean_optional(contact.instagram):
        socials.append({"label": "Instagram", "href": contact.instagram, "openInNewTab": True})
    if _clean_optional(contact.vimeo):
        socials.append({"label": "Vimeo", "href": contact.vimeo, "openInNewTab": True})
    if _clean_optional(contact.linkedin):
        socials.append({"label": "LinkedIn", "href": contact.linkedin, "openInNewTab": True})

    return {
        "columns": columns,
        "socials": socials,
    }


def _serialize_announcement(chrome, locale: str):
    text = _localized_text(chrome, "announcement_text", locale)
    link_label = _localized_text(chrome, "announcement_link_label", locale)
    link_url = _clean_optional(chrome.announcement_link)
    if not any([text, link_label, link_url]):
        return None
    return {
        "text": text,
        "linkLabel": link_label,
        "linkUrl": link_url,
    }


def _serialize_contact_settings(contact):
    return {
        "email": _clean_optional(contact.email),
        "phone": _clean_optional(contact.phone),
        "address": _clean_optional(contact.address),
        "googleMapsLink": _clean_optional(contact.google_maps_link),
        "instagram": _clean_optional(contact.instagram),
        "vimeo": _clean_optional(contact.vimeo),
        "linkedin": _clean_optional(contact.linkedin),
    }


def _serialize_brand(brand, request):
    return {
        "siteName": _clean_optional(brand.site_name),
        "logoUrl": request.build_absolute_uri(brand.logo.file.url) if brand.logo else None,
        "primaryColor": brand.primary_color,
        "secondaryColor": brand.secondary_color,
    }


def _serialize_person_summary(person, request, locale: str):
    return {
        "name": _clean_optional(person.name),
        "slug": _clean_optional(person.slug),
        "hasPublicProfile": bool(person.has_public_profile),
        "role": _localized_text(person, "role", locale),
        "shortBio": _localized_text(person, "short_bio", locale),
        "profileImage": _image_payload(person.profile_image, request),
        "href": f"/people/{person.slug}" if person.has_public_profile else None,
    }


def _serialize_project_summary(project, request, locale: str):
    return {
        "title": _localized_text(project, "title", locale),
        "slug": _clean_optional(project.slug),
        "hasPublicPage": bool(project.has_public_page),
        "catalogSection": _localized_text(project, "catalog_section", locale),
        "type": _localized_text(project, "project_type", locale),
        "year": _clean_optional(project.year),
        "directors": _localized_text(project, "directors", locale),
        "listingSummary": _localized_text(project, "listing_summary", locale),
        "roles": _localized_text(project, "roles", locale),
        "shortDescription": _localized_text(project, "short_description", locale),
        "coverImage": _image_payload(project.cover_image, request),
        "href": f"/projects/{project.slug}" if project.has_public_page else None,
    }


def _serialize_gallery_items(gallery_items, request, locale: str):
    payload = []
    for item in gallery_items:
        serialized = _gallery_item_payload(item.image, request, item.translated("caption", locale))
        if serialized is not None:
            payload.append(serialized)
    return payload


def _serialize_space(space, request, locale: str):
    return {
        "name": _localized_text(space, "name", locale),
        "slug": _clean_optional(space.slug),
        "shortDescription": _localized_text(space, "short_description", locale),
        "mainImage": _image_payload(space.main_image, request),
        "gallery": _serialize_gallery_items(space.gallery_images.all(), request, locale),
        "area": _clean_optional(space.area),
        "capacity": _clean_optional(space.capacity),
        "equipment": _localized_text(space, "equipment", locale),
        "offerings": [
            {
                "title": _localized_text(offering, "title", locale),
                "description": _localized_text(offering, "description", locale),
                "dailyRate": _clean_optional(offering.daily_rate),
                "hourlyRate": _clean_optional(offering.hourly_rate),
                "capacity": _clean_optional(offering.capacity),
                "area": _clean_optional(offering.area),
                "includedFeatures": _localized_text(offering, "included_features", locale),
                "extraServices": _localized_text(offering, "extra_services", locale),
            }
            for offering in space.offerings.all()
        ],
        "bookingCta": _cta_payload(_localized_text(space, "booking_label", locale), space.booking_link),
    }


def _serialize_rich_content_blocks(stream_value, request, locale: str):
    sections = []
    for block in stream_value or []:
        value = block.value
        if block.block_type == "rich_text":
            sections.append(
                {
                    "type": "rich_text",
                    "heading": _clean_optional(value.get("heading")),
                    "body": _clean_optional(value.get("body")),
                }
            )
        elif block.block_type == "feature_grid":
            sections.append(
                {
                    "type": "feature_grid",
                    "heading": _clean_optional(value.get("heading")),
                    "intro": _clean_optional(value.get("intro")),
                    "items": [
                        {
                            "title": _clean_optional(item.get("title")),
                            "description": _clean_optional(item.get("description")),
                            "image": _image_payload(item.get("image"), request),
                            "href": _clean_optional(item.get("href")),
                        }
                        for item in value.get("items", [])
                    ],
                }
            )
        elif block.block_type == "gallery":
            sections.append(
                {
                    "type": "gallery",
                    "heading": _clean_optional(value.get("heading")),
                    "caption": _clean_optional(value.get("caption")),
                    "surface": _clean_optional(value.get("surface")) or "dark",
                    "images": [
                        _image_payload(image, request)
                        for image in value.get("images", [])
                        if _image_payload(image, request) is not None
                    ],
                }
            )
        elif block.block_type == "cta_band":
            sections.append(
                {
                    "type": "cta_band",
                    "heading": _clean_optional(value.get("heading")),
                    "text": _clean_optional(value.get("text")),
                    "cta": _cta_payload(value.get("label"), value.get("href")),
                }
            )
    return sections


def _serialize_home_blocks(stream_value, request, locale: str):
    sections = []
    for block in stream_value or []:
        value = block.value
        if block.block_type in {"feature_grid", "gallery", "cta_band"}:
            sections.extend(_serialize_rich_content_blocks([block], request, locale))
        elif block.block_type == "highlight_strip":
            sections.append(
                {
                    "type": "highlight_strip",
                    "heading": _localized_text(value, "heading", locale),
                    "items": [
                        {
                            "title": _localized_text(item, "title", locale),
                            "body": _localized_text(item, "body", locale),
                            "image": _image_payload(item.get("image"), request),
                            "linkLabel": _localized_text(item, "link_label", locale),
                            "href": _clean_optional(item.get("link_url")),
                        }
                        for item in value.get("items", [])
                    ],
                }
            )
        elif block.block_type == "project_highlights":
            sections.append(
                {
                    "type": "project_highlights",
                    "heading": _clean_optional(value.get("heading")),
                    "intro": _clean_optional(value.get("intro")),
                    "projects": [
                        _serialize_project_summary(project, request, locale)
                        for project in value.get("projects", [])
                    ],
                }
            )
        elif block.block_type == "collaborations":
            sections.append(
                {
                    "type": "collaborations",
                    "heading": _localized_text(value, "heading", locale),
                    "intro": _localized_text(value, "intro", locale),
                    "items": [
                        {
                            "name": _localized_text(item, "name", locale),
                            "note": _localized_text(item, "note", locale),
                            "image": _image_payload(item.get("image"), request),
                            "href": _clean_optional(item.get("link_url")),
                        }
                        for item in value.get("items", [])
                    ],
                }
            )
        elif block.block_type == "awards":
            sections.append(
                {
                    "type": "awards",
                    "heading": _localized_text(value, "heading", locale),
                    "items": [
                        {
                            "title": _localized_text(item, "title", locale),
                            "detail": _localized_text(item, "detail", locale),
                        }
                        for item in value.get("items", [])
                    ],
                }
            )
    return sections


def _serialize_person_profile_blocks(stream_value, request, locale: str):
    sections = []
    for block in stream_value or []:
        value = block.value
        if block.block_type in {"rich_text", "gallery", "cta_band"}:
            sections.extend(_serialize_rich_content_blocks([block], request, locale))
        elif block.block_type == "embed":
            sections.append(
                {
                    "type": "embed",
                    "heading": _clean_optional(value.get("heading")),
                    "embedUrl": _clean_optional(value.get("embed_url")),
                    "aspectRatio": _clean_optional(value.get("aspect_ratio")) or "wide",
                }
            )
        elif block.block_type == "project_highlights":
            sections.append(
                {
                    "type": "project_highlights",
                    "heading": _clean_optional(value.get("heading")),
                    "intro": _clean_optional(value.get("intro")),
                    "projects": [
                        _serialize_project_summary(project, request, locale)
                        for project in value.get("projects", [])
                    ],
                }
            )
        elif block.block_type == "audio_playlist":
            sections.append(
                {
                    "type": "audio_playlist",
                    "heading": _clean_optional(value.get("heading")),
                    "intro": _clean_optional(value.get("intro")),
                    "tracks": [
                        {
                            "title": _clean_optional(item.get("title")),
                            "artist": _clean_optional(item.get("artist")),
                            "coverImage": _image_payload(item.get("cover_image"), request),
                            "audioUrl": (
                                _document_payload(item.get("audio_file"), request) or {}
                            ).get("url")
                            or _clean_optional(item.get("audio_url")),
                            "externalUrl": _clean_optional(item.get("external_url")),
                        }
                        for item in value.get("tracks", [])
                    ],
                }
            )
    return sections


def _serialize_home(home_page, request, locale: str):
    media = None
    if _clean_optional(home_page.hero_video_url):
        media = {
            "type": "video",
            "videoUrl": _clean_optional(home_page.hero_video_url),
            "image": _image_payload(home_page.hero_image, request),
        }
    elif home_page.hero_image:
        media = {
            "type": "image",
            "image": _image_payload(home_page.hero_image, request),
        }

    return {
        "locale": locale,
        "hero": {
            "title": _localized_text(home_page, "hero_title", locale),
            "subtitle": _localized_text(home_page, "hero_subtitle", locale),
            "media": media,
            "primaryCta": _cta_payload(
                _localized_text(home_page, "primary_cta_label", locale),
                home_page.primary_cta_link,
            ),
            "secondaryCta": _cta_payload(
                _localized_text(home_page, "secondary_cta_label", locale),
                home_page.secondary_cta_link,
            ),
        },
        "sections": _serialize_home_blocks(home_page.translated("body", locale), request, locale),
        "seo": _seo_payload(home_page, locale),
    }


def _serialize_about_page(page, request, locale: str):
    return {
        "routeKey": "about",
        "locale": locale,
        "title": _localized_text(page, "title_display", locale) or _clean_optional(page.title),
        "introTitle": _localized_text(page, "intro_title", locale),
        "introText": _localized_text(page, "intro_text", locale),
        "introImage": _image_payload(page.intro_image, request),
        "services": _serialize_rich_content_blocks(page.translated("services", locale), request, locale),
        "studiosEquipment": _serialize_rich_content_blocks(
            page.translated("studios_equipment", locale),
            request,
            locale,
        ),
        "teamMembers": [
            _serialize_person_summary(item.person, request, locale)
            for item in page.team_members.select_related("person")
        ],
        "seo": _seo_payload(page, locale),
    }


def _serialize_spaces_page(page, request, locale: str):
    return {
        "routeKey": "spaces",
        "locale": locale,
        "title": _localized_text(page, "title_display", locale) or _clean_optional(page.title),
        "introText": _localized_text(page, "intro_text", locale),
        "spaces": [
            _serialize_space(item.space, request, locale)
            for item in page.spaces.select_related("space")
        ],
        "seo": _seo_payload(page, locale),
    }


def _serialize_projects_page(page, request, locale: str):
    sections = []
    for section in page.sections.all():
        sections.append(
            {
                "title": _localized_text(section, "title", locale),
                "intro": _localized_text(section, "intro", locale),
                "projects": [
                    _serialize_project_summary(item.project, request, locale)
                    for item in section.projects.select_related("project")
                ],
            }
        )

    return {
        "routeKey": "projects",
        "locale": locale,
        "title": _localized_text(page, "title_display", locale) or _clean_optional(page.title),
        "introText": _localized_text(page, "intro_text", locale),
        "sections": sections,
        "seo": _seo_payload(page, locale),
    }


def _serialize_contact_page(page, locale: str):
    return {
        "routeKey": "contact",
        "locale": locale,
        "title": _localized_text(page, "title_display", locale) or _clean_optional(page.title),
        "introText": _localized_text(page, "intro_text", locale),
        "formEmbed": _localized_text(page, "form_embed", locale),
        "mapEmbed": _clean_optional(page.map_embed),
        "seo": _seo_payload(page, locale),
    }


def _serialize_person_detail(person, request, locale: str):
    related_projects = [item.project for item in person.related_projects.select_related("project") if item.project.has_public_page]
    if not related_projects:
        related_projects = [
            item.project
            for item in person.project_collaborations.select_related("project")
            if item.project.has_public_page
        ]

    deduped_projects = []
    seen = set()
    for project in related_projects:
        if project.slug in seen:
            continue
        seen.add(project.slug)
        deduped_projects.append(project)

    return {
        **_serialize_person_summary(person, request, locale),
        "profileIntro": _localized_text(person, "profile_intro", locale),
        "primaryCta": _cta_payload(_localized_text(person, "primary_cta_label", locale), person.primary_cta_link),
        "fullBio": _localized_text(person, "full_bio", locale),
        "sections": _serialize_person_profile_blocks(person.translated("profile_sections", locale), request, locale),
        "links": [
            {"label": _clean_optional(link.label), "url": _clean_optional(link.url)}
            for link in person.links.all()
        ],
        "relatedProjects": [
            _serialize_project_summary(project, request, locale)
            for project in deduped_projects
        ],
    }


def _serialize_project_detail(project, request, locale: str):
    return {
        **_serialize_project_summary(project, request, locale),
        "metadata": {
            "format": _localized_text(project, "project_type", locale),
            "directors": _localized_text(project, "directors", locale),
            "productionYear": _clean_optional(project.year),
            "productionCountries": _localized_text(project, "production_countries", locale),
            "languages": _localized_text(project, "languages", locale),
        },
        "synopsis": _localized_text(project, "synopsis", locale),
        "fullDescription": _serialize_rich_content_blocks(project.translated("full_description", locale), request, locale),
        "gallery": _serialize_gallery_items(project.gallery_images.all(), request, locale),
        "videoEmbed": _clean_optional(project.video_embed),
        "collaborators": [
            _serialize_person_summary(item.person, request, locale)
            for item in project.collaborators.select_related("person")
        ],
        "credits": [
            {
                "role": _localized_text(credit, "role", locale),
                "value": _localized_text(credit, "value", locale),
                "person": _serialize_person_summary(credit.person, request, locale) if credit.person else None,
            }
            for credit in project.credits.select_related("person")
        ],
        "externalLinks": [
            {
                "label": _localized_text(link, "label", locale),
                "href": _clean_optional(link.url),
                "openInNewTab": True,
            }
            for link in project.external_links.all()
        ],
    }


class SiteConfigAPIView(APIView):
    def get(self, request):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        chrome = _resolve_site_chrome(site)
        contact = _resolve_contact_settings(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)

        payload = {
            "site": _site_payload(site, brand),
            "defaultLocale": brand.default_locale.lower(),
            "locales": [locale_code.lower() for locale_code in brand.supported_locales],
            "brand": _serialize_brand(brand, request),
            "nav": _serialize_nav(chrome, locale),
            "footer": _serialize_footer(chrome, contact, locale),
            "announcement": _serialize_announcement(chrome, locale),
            "contact": _serialize_contact_settings(contact),
        }
        serializer = SiteConfigSerializer(payload)
        return Response(serializer.data)


class HomeAPIView(APIView):
    def get(self, request):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        home_page = _resolve_home_page(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)
        payload = _serialize_home(home_page, request, locale)
        serializer = HomeSerializer(payload)
        return Response(serializer.data)


class PageAPIView(APIView):
    def get(self, request, route_key):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)

        if route_key == "about":
            payload = _serialize_about_page(_resolve_child_page(site, AboutPage), request, locale)
            serializer = AboutPageSerializer(payload)
        elif route_key == "spaces":
            payload = _serialize_spaces_page(_resolve_child_page(site, SpacesPage), request, locale)
            serializer = SpacesPageSerializer(payload)
        elif route_key == "projects":
            payload = _serialize_projects_page(_resolve_child_page(site, ProjectsPage), request, locale)
            serializer = ProjectsPageSerializer(payload)
        elif route_key == "contact":
            payload = _serialize_contact_page(_resolve_child_page(site, ContactPage), locale)
            serializer = ContactPageSerializer(payload)
        else:
            raise NotFound("Page not found for the requested route.")

        return Response(serializer.data)


class ProjectDetailAPIView(APIView):
    def get(self, request, slug):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)
        project = Project.objects.filter(slug=slug, has_public_page=True).first()
        if project is None:
            raise NotFound("Project not found.")
        payload = _serialize_project_detail(project, request, locale)
        serializer = ProjectDetailSerializer(payload)
        return Response(serializer.data)


class PersonDetailAPIView(APIView):
    def get(self, request, slug):
        site = _resolve_site(request)
        brand = _resolve_brand(site)
        locale = _resolve_locale(request, default_locale=brand.default_locale, supported_locales=brand.supported_locales)
        person = Person.objects.filter(slug=slug, has_public_profile=True).first()
        if person is None:
            raise NotFound("Person not found.")
        payload = _serialize_person_detail(person, request, locale)
        serializer = PersonDetailSerializer(payload)
        return Response(serializer.data)
