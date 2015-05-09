from rest_framework import serializers, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.contrib.auth import get_user_model
from rushtracker.models import Rush
from comments.models import Comment
from ranking.models import Ranking
from organization.models import Organization
from rushperiod.models import RushPeriod
from authentication.permissions import SameOrganizationPermission
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from authentication.models import UserProfile
from events.models import Event
from authentication.permissions import IsMyComment



class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization


class OrganizationViews(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    model = Organization
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.tenant_objects.all()


class RushPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = RushPeriod


class RushPeriodViews(viewsets.ModelViewSet):
    serializer_class = RushPeriodSerializer
    model = RushPeriod

    def get_queryset(self):
        return RushPeriod.tenant_objects.all()


class UserSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'is_staff', 'is_rush_committee',
                  'id', 'password', 'confirm',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = self.context['user']
        request = self.context['request']
        if validated_data['password'] == validated_data['confirm']:
            new_user = get_user_model().objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                organization=user.organization
            )
            user_profile = UserProfile(user=new_user)
            user_profile.save()
            return new_user


# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    model = get_user_model()

    def get_queryset(self):
        return get_user_model().tenant_objects.all().order_by('-is_rush_committee', 'email')

    def create(self, request):
        if not isinstance(request.data, list):
            is_many = False
        else:
            is_many = True
        serializer = UserSerializer(
            data=request.data, context={'user': request.user, 'request': request}, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @detail_route(methods=['patch'], url_path='change-rush-comm-status')
    def change_rush_comm(self, request, pk=None):
        user = self.get_object()
        user.is_rush_committee = not user.is_rush_committee
        perm_add = Permission.objects.get(codename='add_ranking')
        perm_delete = Permission.objects.get(codename='delete_ranking')
        if not user.is_rush_committee:
            user.user_permissions.remove(perm_add)
            user.user_permissions.remove(perm_delete)
        else:
            user.user_permissions.add(perm_add)
            user.user_permissions.add(perm_delete)
        user.save()
        return Response(UserSerializer(user).data)

    @detail_route(methods=['get'], url_path='reset-to-default-password')
    def reset_to_default_password(self, request, pk=None):
        user = self.get_object()
        if request.user.organization.default_password:
            user.set_password(request.user.organization.default_password)
            user.save()
            return Response({
                'message': 'Successful Reset!'
            })
        return Response({
            'message': 'Failure, no default password set'
        })

    def list(self, request):
        return super(UserViewSet, self).list(request)
    # cache is causing the old list to be returned.  override
    # get query set to fix


class RushSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rush
        fields = ('first_name', 'last_name', 'id')


class RushViewSet(viewsets.ModelViewSet):
    serializer_class = RushSerializer
    model = Rush

    def get_queryset(self):
        return Rush.tenant_objects.all()


class RushViewSetRanked(viewsets.ModelViewSet):
    # returns unranked kids
    model = Rush
    serializer_class = RushSerializer

    def get_queryset(self):
        already_ranked = Ranking.tenant_objects.filter(pk=self.request.user.id).values('rush')
        not_ranked = Rush.tenant_objects.exclude(pk__in=already_ranked)
        return not_ranked


class RankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ranking
        fields = ('rush', 'rank', 'id')

    def create(self, validated_data):
        user = self.context['user']
        request = self.context['request']
        rush = get_object_or_404(Rush, pk=request.data['rush'])
        if Ranking.tenant_objects.filter(rush__id=rush.id).filter(user__id=user.id).exists():
            raise serializers.ValidationError("You have already ranked this rush")
        if rush.organization == user.organization:
            rank = Ranking(user=user, rush=rush, rank=validated_data[
                           'rank'], organization=user.organization)
            rank.save()
            return rank
        raise serializers.ValidationError(
            "No Rush Found")
    def to_representation(self, instance):
        ret = super(RankSerializer, self).to_representation(instance)
        rush = Rush.tenant_objects.get(pk=ret['rush'])
        ret['rush'] = {
            'first_name': rush.first_name,
            'last_name': rush.last_name,
            'id': rush.id
        }
        return ret

class RankViewSet(viewsets.ModelViewSet):
    # returns ranked kids
    model = Ranking
    serializer_class = RankSerializer
    permission_classes = [
        permissions.IsAuthenticated, SameOrganizationPermission]

    def get_queryset(self):
        return Ranking.tenant_objects.filter(user__id=self.request.user.id).order_by('rush__first_name')

    def create(self, request):
        serializer = RankSerializer(
            data=request.data, context={'user': request.user, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @list_route(methods=['get'], url_path="get-unranked")
    def get_unranked(self, request):
        already_ranked = Ranking.tenant_objects.filter(
            user__id=request.user.id).values('rush')
        unranked = Rush.tenant_objects.exclude(
            pk__in=already_ranked).order_by('first_name')
        data = RushSerializer(unranked, many=True).data
        return Response(data)
    def partial_update(self, request, pk=None):
        #TODO: Update needs to be handled in a simliar fashion
        print "hi"
        request.data.pop('rush', None)
        return super(RankViewSet, self).partial_update(request, pk)
    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        #if this breaks check code base it is copied right from it
        instance = self.get_object()
        #TODO: error check that rush is there 
        request.data['rush'] = instance.rush.id
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class RankListViewSet(viewsets.ViewSet):
    model = Ranking

    """
    Returns the rankings of the kids 

    """

    def list(self, request, *args, **kwargs):
        all_rankings = Ranking.tenant_objects.filter(
            user__is_rush_committee=True)
        all_rushes = Rush.tenant_objects.all()
        rankList = []
        rank = {}
        for rush in all_rushes:
            specific_rank_value = all_rankings.filter(
                rush__id=rush.id).aggregate(Sum('rank'))
            specific_rank_value = specific_rank_value['rank__sum']
            if specific_rank_value != None:
                number_of_rankings = all_rankings.filter(
                    rush__id=rush.id).count()
                average_rank = specific_rank_value / number_of_rankings
                rankList.append({
                    'rush': RushSerializer(rush).data,
                    'rank': average_rank
                })
        return Response(rankList)


class CommentSerializer(serializers.ModelSerializer):
    # we could load all users onto comment serializer when it starts then sort
    # them by their pk TODO

    def __init__(self, *args, **kwargs):
        super(CommentSerializer, self).__init__(*args, **kwargs)
        # trying to enable caching maybe? I need to find a way to record DB
        # hits
        self.users = get_user_model().objects.all()

    class Meta:
        model = Comment
        fields = ('id', 'created_at', 'comment', 'user', 'rush', 'event')
        read_only_fields = ('id', 'created_at',)

    def to_representation(self, instance):
        ret = super(CommentSerializer, self).to_representation(instance)
        user = self.users.get(pk=ret['user'])
        ret['user'] = {
            'email': str(user),
            'id': user.id
        }
        return ret

    def validate_user(self, value):
        user = self.context['request'].user
        request = self.context['request']
        if not request.user.has_perm('chapter_admin'):
            return user
        if not value.organization == user.organization:
            raise serializers.ValidationError(
                {'user': 'No Matching User Found'})
        return value

    def validate_event(self, value):
        user = self.context['request'].user
        if value is None:
            return value
        if value.organization != user.organization:
            raise serializers.ValidationError(
                {'event': 'No Matching Event Found'})
        return value

    def validate_rush(self, value):
        user = self.context['request'].user
        if value.organization != user.organization:
            raise serializers.ValidationError(
                {'rush': 'No Matching Rush Found'})
        return value
        # maybe make a validator here for cleaning fields this really should
        # be what is used so that errors are explained correctly
        # errors up here render in whole page errors in
        # viewset render on their own


class CommentViewSet(viewsets.ModelViewSet):
    model = Comment
    # TODO: ISAUTHENTICATED PERMISSION, UPDATING
    permission_classes = [IsMyComment, permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.tenant_objects.all()

    # maybe t`here should be a seperate Admin serializer to make the
    # code and responsibilites more modular
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentSerializer
        else:
            return CommentSerializer
    # returns a list of comments, and a list of the user comments

    @detail_route(methods=['get'], url_path="get-comments")
    def get_comments_for_rush(self, request, pk=None):
        rush = get_object_or_404(Rush, pk=pk)
        serializer = CommentSerializer(rush.comment_set.all(), many=True)
        my_comments = Comment.tenant_objects.filter(
            rush=rush).filter(user=request.user)
        my_comments_serializer = CommentSerializer(my_comments, many=True)

        return Response({
            'all_comments': serializer.data,
            'my_comments': my_comments_serializer.data
        })

    def create(self, request):
        serializer = CommentSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(organization=request.user.organization,
                            rush_period=request.user.organization.active_rush_period)

            return Response(serializer.data)
        return Response(serializer.errors)

    def update(self, request, pk=None, *args, **kwargs):
        comment = self.get_object()
        if not request.user.has_perm('chapter_admin'):
            request.data['user'] = request.user.id
            request.data['rush'] = comment.rush.id
        return super(CommentViewSet, self).update(request, pk, **kwargs)


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        exclude = ['organization', ]


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    model = Event

    def get_queryset(self):
        return Event.tenant_objects.all()

    @detail_route(methods=['post'], url_path='add-rush')
    def add_to_attendance(self, request, pk=None):
        event = self.get_object()
        rush = request.data['rush']
        rush = get_object_or_404(Rush, rush)
        if rush.organization == request.user.organization:
            event.attendance.add(rush)
            return Response(Rush)
        else:
            return Response({
                'failure'
            })
