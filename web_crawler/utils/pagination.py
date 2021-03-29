# -*- coding: utf-8 -*-
"""DRF pagination settings."""
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination


def _get_count(queryset):
    """Determine an object count, supporting querysets or regular lists."""
    try:
        return queryset.count()
    except (AttributeError, TypeError):
        return len(queryset)


class StandardResultsSetPagination(LimitOffsetPagination):
    """Standard pagination style used by most endpoints."""

    max_limit = 100
    ordering = "id"

    def paginate_queryset(self, queryset, request, view=None):
        """Override LimitOffsetPagination to get hacked `_count` from view."""
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        if hasattr(view, "_count"):
            self.count = view._count
        else:
            self.count = _get_count(queryset)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset : self.offset + self.limit])


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 200
