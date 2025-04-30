from django.contrib.auth import get_user_model
from django.views.generic import ListView
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from langcorrect.contributions.helpers import get_contribution_data
from langcorrect.contributions.models import Contribution

User = get_user_model()


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_contributions(request, username):
    user = get_object_or_404(User, username=username)
    data = get_contribution_data(user)
    return Response(data=data)


class RankingListView(ListView):
    model = Contribution
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        if current_user.is_authenticated:
            context["self_ranking"] = Contribution.objects.get(
                user=current_user,
            )
        return context


rankings_list_view = RankingListView.as_view()
