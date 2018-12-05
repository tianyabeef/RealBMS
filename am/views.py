from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth.models import User
from django.db.models import Q


class AnaAutocompleteJsonView(AutocompleteJsonView):
    """The autocomplete json view for mapping user queryset with respect to the
    the group that the request.user in."""
    
    def get_group_users(self, query_condition=None):
        users_qs = User.objects.filter(query_condition).order_by("id")
        users_qs = self.model_admin.get_search_results(
            self.request, users_qs, self.term
        )[0]
        return users_qs.distinct()
    
    def get_queryset(self):
        # Attention: the hard code of group should be removed in the future,
        # These may cause some problems when the database are going to be
        # regenerated, last edited by liy, 11/16/2018, 10:41:03.
        ana_users = self.get_group_users(Q(groups__id=9) | Q(groups__id=10))
        sal_users = self.get_group_users(Q(groups__id=3) | Q(groups__id=7))
        exp_users = self.get_group_users(Q(groups__id=1) | Q(groups__id=11))
        mar_users = self.get_group_users(Q(groups__id=4) | Q(groups__id=12))
        fin_users = self.get_group_users(Q(groups__id=5) | Q(groups__id=14))
        cop_users = self.get_group_users(Q(groups__id=8))
        if self.request.user in ana_users:
            current = self.get_group_users(Q(pk=self.request.user.pk))
            manager = self.get_group_users(Q(groups__id=10))
            users_queryset = ana_users if current & manager else current
        elif self.request.user in mar_users:
            users_queryset = sal_users
        elif self.request.user in sal_users:
            current = self.get_group_users(Q(pk=self.request.user.pk))
            manager = self.get_group_users(Q(groups__id=7))
            users_queryset = sal_users if current & manager else current
        elif self.request.user in exp_users:
            current = self.get_group_users(Q(pk=self.request.user.pk))
            manager = self.get_group_users(Q(groups__id=11))
            users_queryset = exp_users if current & manager else current
        elif self.request.user in fin_users:
            users_queryset = fin_users
        elif self.request.user in cop_users:
            users_queryset = sal_users
        else:
            users_queryset = super().get_queryset()
        return users_queryset
