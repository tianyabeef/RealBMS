# from django.db.models.signals import post_migrate
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth.models import Permission
# from django.dispatch import receiver
#
#
# @receiver(post_migrate)
# def add_view_permissions(sender, **kwargs):
#     """
#     Thanks to the method get on the Stack Overflow
#     as I don't know yet, the global permissions of add, change and delete for
#     every model is created when the model was stored into the ContentType,
#     we can simply send a signal after the migrations, that's the key:
#     https://stackoverflow.com/questions/23104449/view-permissions-in-django?noredirect=1
#     """
#     for content_type in ContentType.objects.all():
#         codename = "view_%s" % content_type.model
#         if not Permission.objects.filter(content_type=content_type,
#                                          codename=codename):
#             Permission.objects.create(
#                 content_type=content_type, codename=codename,
#                 name="Can view %s" % content_type.name
#             )
#             print("Added view permission for %s" % content_type.name)
