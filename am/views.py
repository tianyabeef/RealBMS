from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth.models import Group
from django.db.models import Q


class AnaAutocompleteJsonView(AutocompleteJsonView):
    """The autocomplete json view for mapping user queryset with respect to the
    the group that the request.user in."""
    
    def get_group_users(self, query_condition=None):
        groups = Group.objects.filter(query_condition)
        users_queryset = [u for g in groups for u in g.user_set.all()]
        return users_queryset
    
    def get_queryset(self):
        # Attention: the hard code of group should be removed in the future,
        # These may cause some problems when the database are going to be
        # regenerated, last edited by liy, 11/16/2018, 10:41:03.
        ana_users = self.get_group_users(Q(id=9) | Q(id=10))
        sal_users = self.get_group_users(Q(id=3) | Q(id=7))
        exp_users = self.get_group_users(Q(id=1) | Q(id=11))
        mar_users = self.get_group_users(Q(id=4) | Q(id=12))
        fin_users = self.get_group_users(Q(id=5) | Q(id=14))
        
        if self.request.user in ana_users:
            users_queryset = ana_users
        elif self.request.user in mar_users:
            sal_users.extend(mar_users)
            users_queryset = sal_users
        elif self.request.user in sal_users:
            users_queryset = sal_users
        elif self.request.user in exp_users:
            users_queryset = exp_users
        elif self.request.user in fin_users:
            users_queryset = fin_users
        else:
            users_queryset = super().get_queryset()
        return users_queryset
