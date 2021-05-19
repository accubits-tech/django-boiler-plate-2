import os
import uuid
from datetime import datetime, timedelta
from threading import Thread
from django.utils.dateparse import parse_date

import requests
from basicauth import decode
from basicauth import encode
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import status, exceptions
from rest_framework import viewsets
from rest_framework.response import Response

from authentication.authentication import JwtTokensAuthentication
import logging

from jwt_utils.jwt_validator import jwt_validator, refresh_token_validator
from users.models import Token, UserSearch, UserBookmark, UserNote, UserNotification
from jwt_utils.jwt_generator import jwt_generator
from web_crawler import settings
from utils.datetime_utils import calculate_time_difference, convert_to_str_time, convert_str_time, convert_str_date
from utils.mail_utils import send_email
from utils.message_utils import get_message
from utils.pagination import CustomPageNumberPagination
from utils.validation_utils import (
    validate_email,
    validate_password,
    validate_null_or_empty,
)
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    ImageSerializer,
    ForgotPasswordSerializer,
    UserSearchSerializer,
    DashboardSerializer,
    UserBookmarkSerializer,
    UserNotesSerializer,
    MonitorySerializer,
    UserNotificationsSerializer,
    RefreshTokenSerializer)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'debug.log'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
})

logger = logging.getLogger(__name__)

# Create your views here.


class RegisterViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):

        email = request.data.get("email")
        user_name = request.data.get("user_name", "")
        password = request.data.get("password", None)

        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(email, 307, validations)
        validations = validate_null_or_empty(password, 305, validations)
        validations = validate_null_or_empty(user_name, 304, validations)

        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp)

        if not validate_email(email):
            return Response({"code": 604, "message": get_message(604)})

        if not validate_password(password):
            return Response({"code": 618, "message": get_message(618)})

        user_obj = get_user_model().objects.filter(email=email).count()
        if user_obj >= 1:
            return Response({"code": 621, "message": get_message(621)})

        user = get_user_model().objects.create_user(request.data)

        return Response(
            {"code": 200, "message": get_message(200), "user_id": user._get_pk_val()}
        )


class LoginViewSet(viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        account_type = request.data.get("account_type", "normal")
        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(email, 307, validations)
        if account_type == "normal":
            validations = validate_null_or_empty(password, 305, validations)

        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp)
        try:
            user_obj = get_user_model().objects.get(email=email, is_verified=True)
            if account_type == "normal":
                valid = user_obj.check_password(password)
            else:
                valid = True
            if not valid:
                logger.error({"code": 503, "message": get_message(503)})
                return Response(
                    {"code": 503, "message": get_message(503)},
                    status=status.HTTP_204_NO_CONTENT,
                )
            access_token = jwt_generator(
                user_obj.id,
                settings.JWT_SECRET,
                settings.TOKEN_EXPIRY,
                "access",
                user_obj.is_superuser,
            )
            refresh_token = jwt_generator(
                user_obj.id,
                settings.JWT_SECRET,
                settings.REFRESH_TOKEN_EXPIRY,
                "refresh",
                user_obj.is_superuser,
            )
            Token.objects.filter(user_id=user_obj).update(is_expired=1)

            Token.objects.update_or_create(
                user_id=user_obj,
                access_token=access_token,
                refresh_token=refresh_token,
                defaults={"updated_at": datetime.now()},
            )
            return Response(
                
                {
                    "code": 200,
                    "message": get_message(200),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user_obj.pk,
                    "email": user_obj.email,
                }
            )

        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JwtTokensAuthentication]
    pagination_class = CustomPageNumberPagination
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all().exclude(is_superuser=1)

    def list(self, request, *args, **kwargs):
        if request.user.get("is_admin", False):
            return super().list(request)
        return Response(
            {"code": 200, "message": get_message(200), "results": [], "count": 0}
        )

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request)

    def update(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        user_image = request.data.get("image_url")
        try:
            get_user_model().objects.filter(pk=user_id).update(image_url=user_image)
            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response({"code": 114, "message": get_message(114)})


class LogoutViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = [JwtTokensAuthentication]
    serializer_class = ()

    def create(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        token_id = request.headers.get("Authorization", "")
        try:
            token_obj = Token.objects.get(access_token=token_id, user_id=user_id)
            token_obj.is_expired = 1
            token_obj.save()
            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response({"code": 114, "message": get_message(114)})


class ForgotPasswordViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = ForgotPasswordSerializer

    def create(self, request, *args, **kwargs):

        email_id = request.data.get("email")
        try:
            user_obj = get_user_model().objects.get(email=email_id)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:
            current_time = datetime.now()
            exp_time = current_time + timedelta(milliseconds=300000)
            exp_at = exp_time.strftime("%Y-%m-%d %H:%M:%S")

            token_url = encode(user_obj.email, exp_at)
            token = token_url.split("Basic")
            reset_url = "http://localhost:8000/?token=" + str(token[1])

            messages = {
                "first_name": user_obj.first_name,
                "last_name": user_obj.last_name,
                "html": "users/reset_password_email.html",
                "reset_url": reset_url,
                "subject": "Reset Password Link",
            }
            mail_thread = Thread(target=send_email, args=(email_id, messages))
            mail_thread.start()
            return Response(
                {
                    "code": 200,
                    "message": "A password reset mail is send to the registered email",
                }
            )

        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get("password")
        token = request.data.get("token")
        token = "Basic " + token
        email, exp_at = decode(token)

        try:

            user_obj = get_user_model().objects.get(email=email)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:

            current_time = datetime.now()
            time_difference = calculate_time_difference(
                exp_at, convert_to_str_time(current_time)
            )

            if time_difference < 0:
                return Response(
                    {"code": 206, "message": get_message(206)},
                    status=status.HTTP_204_NO_CONTENT,
                )

            if not validate_password(password):
                return Response({"code": 618, "message": get_message(618)})

            user_obj.set_password(password)
            user_obj.updated_at = datetime.now()
            user_obj.save()
            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response({"code": 114, "message": get_message(114)})


class ChangePasswordViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def create(self, request, *args, **kwargs):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        user_id = request.user.get("user_id")
        try:
            user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as e:
            logger.error(e)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:
            valid = user_obj.check_password(current_password)
            if not valid:
                return Response({"code": 619, "message": get_message(619)})

            if not validate_password(new_password):
                return Response({"code": 618, "message": get_message(618)})

            user_obj.set_password(new_password)
            user_obj.updated_at = datetime.now()
            user_obj.save()

            return Response({"code": 200, "message": get_message(200)})
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({"code": 114, "message": get_message(114)})


class RefreshTokenViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    authentication_classes = (JwtTokensAuthentication,)
    serializer_class = RefreshTokenSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        refresh_token = request.data.get("refresh_token", "")
        try:
            user_obj = get_user_model().objects.get(pk=user_id)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )

        payload = refresh_token_validator(refresh_token)
        if not payload:
            return Response(
                {"code": 401, "message": get_message(401)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if payload and payload.get("type", "") != "refresh":
            return Response(
                {"code": 505, "message": get_message(505)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            access_token = jwt_generator(
                user_obj.id,
                settings.JWT_SECRET,
                settings.TOKEN_EXPIRY,
                "access",
                user_obj.is_superuser,
            )
            refresh_token = jwt_generator(
                user_obj.id,
                settings.JWT_SECRET,
                settings.REFRESH_TOKEN_EXPIRY,
                "refresh",
                user_obj.is_superuser,
            )
            Token.objects.filter(user_id=user_obj).update(is_expired=1)

            Token.objects.update_or_create(
                user_id=user_obj,
                access_token=access_token,
                refresh_token=refresh_token,
                defaults={"updated_at": datetime.now()},
            )
            return Response(

                {
                    "code": 200,
                    "message": get_message(200),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user_obj.pk,
                    "email": user_obj.email,
                }
            )
        except Exception as ex:
            logger.error(ex)
            return Response({"code": 114, "message": get_message(114)})


class UploadImageViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    serializer_class = ImageSerializer
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        pass

    def create(self, request, *args, **kwargs):
        image = request.data.get("name")
        image_category = request.data.get("image_category", "user")
        directory_name = "user_images/"

        image_ext = str(image).split(".")[-1]
        image_name = uuid.uuid4().hex
        name = directory_name + image_name + "." + image_ext
        path = default_storage.save(name, ContentFile(image.read()))
        os.path.join(settings.MEDIA_ROOT, path)
        return Response({"code": 200, "message": get_message(200), "image_url": path})


class UserNotesViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    serializer_class = UserNotesSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        user_id = self.request.user.get("user_id")
        start_date = self.request.query_params.get("from")
        end_date = self.request.query_params.get("to")
        queryset = UserNote.objects.filter(user_id=user_id)

        if start_date:
            min_time = datetime.min.time()
            start_date = datetime.combine(convert_str_date(start_date), min_time)
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            max_time = datetime.max.time()
            end_date = datetime.combine(convert_str_date(end_date), max_time)
            queryset = queryset.filter( created_at__lte=end_date)

        return queryset

    def create(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        note_text = request.data.get("note_text")

        # check content id exist in micro service
        try:
            user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist:
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:
            UserNote.objects.create(user_id=user_obj, note_text=note_text)
            return Response({"code": 200, "message": get_message(200)})
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({"code": 114, "message": get_message(114)})


class UserNotificationsViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    serializer_class = UserNotificationsSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        user_id = self.request.user.get("user_id")
        queryset = UserNotification.objects.filter(user_id=user_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        notification_text = request.data.get("notification_text")

        # check content id exist in micro service
        try:
            user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:
            queryset = UserNotification.objects.create(
                user_id=user_obj, notification_text=notification_text
            )
            return Response({"code": 200, "message": get_message(200)})
        except Exception as e:
            logger.error(e)
            return Response({"code": 114, "message": get_message(114)})


class UserBookmarkViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    serializer_class = UserBookmarkSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        user_id = self.request.user.get("user_id")
        queryset = UserBookmark.objects.filter(user_id=user_id)

        return queryset

    def create(self, request, *args, **kwargs):
        content_id = request.data.get("content_id")
        content_text = request.data.get("content_text")
        content_url = request.data.get("content_url")
        user_id = request.user.get("user_id")

        # check content id exist in micro service
        try:
            user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )
        try:
            UserBookmark.objects.create(
                user_id=user_obj,
                content_id=content_id,
                content_text=content_text,
                content_url=content_url,
            )
            return Response({"code": 200, "message": get_message(200)})
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({"code": 114, "message": get_message(114)})


class UserSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """list user searches ie, recent search

    create:
    saves the searches dependent of user
    """

    permission_classes = ()
    serializer_class = UserSearchSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        search_value = self.request.query_params.get("search_value", None)
        user_id = self.request.user.get("user_id")
        queryset = UserSearch.objects.filter(user_id=user_id)

        if search_value:
            queryset = queryset.filter(search_value__icontains=search_value)

        queryset = queryset.order_by("-created_at")
        return queryset

    # def list(self, request, *args, **kwargs):
    #     user_id = self.request.user.get("user_id")
    #     queryset = UserSearch.objects.filter(user_id=user_id)
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     search_value = request.data.get("search_value")
    #     search_type = request.data.get("search_type", "api")
    #     user_id = request.user.get("user_id")
    #     try:
    #         user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
    #     except ObjectDoesNotExist:
    #         return Response(
    #             {"code": 204, "message": get_message(204)},
    #             status=status.HTTP_204_NO_CONTENT,
    #         )
    #     try:
    #         UserSearch.objects.create(
    #             user_id=user_obj,
    #             search_value=search_value,
    #             search_type=search_type,
    #         )
    #
    #         return Response({"code": 200, "message": get_message(200)})
    #     except Exception as e:
    #         print(e)
    #         return Response({"code": 114, "message": get_message(114)})


class PlatformSearchViewSet(viewsets.ModelViewSet):
    """
    platform based search
    """

    permission_classes = ()
    serializer_class = UserSearchSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def create(self, request, *args, **kwargs):

        search_value = request.data.get("search_value", None)
        record_id = request.data.get("record_id", "")
        record_type = request.data.get("record_type", "")
        search_type = request.data.get("search_type", "platform")
        skip = request.data.get("index", 0)
        top = request.user.get("limit", 10)
        user_id = request.user.get("user_id")
        count = 0

        if not search_value:
            return Response(
                {"code": 306, "message": get_message(306)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        try:
            user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_204_NO_CONTENT,
            )

        try:
            body = {
                "query": search_value,
                "record_id": record_id,
                "record_type": record_type,
                "skip": skip,
                "top": top,
            }

            base_url = settings.WEB_CRAWLER_BASE_URL
            try:
                api_result = requests.post(base_url + "fetch/records", json=body)
                api_response = api_result.json()
                logger.info(api_response)
                api_response = api_response.get("result", {})
                search_result_id = api_response.get("search_id", "")
                patent_count = api_response.get("patents", {}).get("total_count", 0)
                patent_id = api_response.get("patents", {}).get("id", "")
                patent_name = api_response.get("patents", {}).get("name", "")
                innovator_count = api_response.get("innovators", {}).get(
                    "total_count", 0
                )
                innovator_id = api_response.get("innovators", {}).get("id", "")
                innovator_name = api_response.get("innovators", {}).get("name", "")
                print(search_result_id)

            except Exception as e:
                logger.error(e)
                print(e)
                return Response({"code": 114, "message": get_message(114)})
            try:
                """if its platform - search result id needs to be checked. if it is url based,
                search value will be checked"""

                search_obj = UserSearch.objects.get(
                    user_id=user_id, search_result_id=search_result_id
                )
                count = search_obj.search_count
                search_obj.search_count = count + 1
                search_obj.updated_at = datetime.now()
                search_obj.save()
            except ObjectDoesNotExist as e:
                logger.error(e)
                UserSearch.objects.create(
                    user_id=user_obj,
                    search_value=search_value,
                    search_type=search_type,
                    search_result_id=search_result_id,
                    search_count=count + 1,
                    patent_count=patent_count,
                    patent_id=patent_id,
                    patent_name=patent_name,
                    innovator_count=innovator_count,
                    innovator_id=innovator_id,
                    innovator_name=innovator_name,
                )

            return Response(
                {"code": 200, "message": get_message(200), "results": api_response}
            )

        except Exception as e:
            logger.error(e)
            print(e)
            return Response({"code": 114, "message": get_message(114)})


class DashboardCountViewSet(viewsets.ReadOnlyModelViewSet):
    """list : the count showing in dashboard"""

    permission_classes = ()
    serializer_class = DashboardSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def list(self, request, *args, **kwargs):

        key = request.query_params.get("key", "api")
        user_id = request.user.get("user_id")
        result = {}

        if key == "api":
            api_count = 0
            queryset = (
                UserSearch.objects.filter(user_id=user_id)
                .values("user_id")
                .annotate(count=Count("search_value"))
            )
            total_api_count_list = list(queryset.values_list("count", flat=True))
            if total_api_count_list:
                api_count = total_api_count_list[0]
            result[key] = api_count

        if key == "patent":
            patent_count = 0
            queryset = (
                UserSearch.objects.filter(user_id=user_id)
                .values("user_id")
                .annotate(count=Sum("patent_count"))
            )
            patent_api_count_list = list(queryset.values_list("count", flat=True))
            if patent_api_count_list:
                patent_count = patent_api_count_list[0]
            result[key] = patent_count

        if key == "innovator":
            patent_count = 0
            queryset = (
                UserSearch.objects.filter(user_id=user_id)
                .values("user_id")
                .annotate(count=Sum("innovator_count"))
            )
            patent_api_count_list = list(queryset.values_list("count", flat=True))
            if patent_api_count_list:
                patent_count = patent_api_count_list[0]
            result[key] = patent_count

        return Response({"code": 200, "message": get_message(200), "results": result})


class MonitoryViewSet(viewsets.ModelViewSet):
    """list  monitoring list

    create:
    saves the Monitory values
    """

    permission_classes = ()
    serializer_class = UserSearchSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        search_value = self.request.query_params.get("search_value", None)
        user_id = self.request.user.get("user_id")
        queryset = UserSearch.objects.filter(user_id=user_id, needs_monitoring=True)

        if search_value:
            queryset = queryset.filter(search_value__icontains=search_value)

        queryset = queryset.order_by("-created_at")
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = MonitorySerializer(data=request.data)
        is_valid = serializer.is_valid()
        if not is_valid:
            return Response({"code": 309, "message": get_message(309)})

        data = dict(serializer.validated_data)
        search_value_id = data.get("search_value_id")
        user_id = request.user.get("user_id")

        try:
            UserSearch.objects.filter(
                search_result_id=search_value_id, user_id=user_id
            ).update(needs_monitoring=True, updated_at=datetime.now())

            return Response({"code": 200, "message": get_message(200)})
        except Exception as e:
            logger.error(e)
            print(e)
            return Response({"code": 114, "message": get_message(114)})
