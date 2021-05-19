# -*- coding: utf-8 -*-
"""DRF pagination settings."""
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 200
