import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from boards.models import Card, Comment, Board, Column, CheckList, Mark, Favourite, Archive, LastSeen
from boards.forms import CommentForm, CardForm, ColumnForm, SearchUserForm, SearchMarkForm


User = get_user_model()


class LockedView(LoginRequiredMixin):
    login_url = "login"


"""             BOARD VIEWS         """


class BoardView(LockedView, generic.ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'board/board_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(members=self.request.user)
        return queryset


class CreateBoardView(LockedView, generic.CreateView):
    model = Board
    template_name = 'board/create_board.html'
    fields = ['title', 'background', 'members']
    success_url = reverse_lazy('board_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BoardDetailView(LockedView, generic.FormView, generic.DetailView):
    model = Board
    context_object_name = 'board'
    template_name = 'board/board_detail.html'
    form_class = ColumnForm
    success_url = '#'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['columns'] = Column.objects.filter(board=self.get_object())
        context['form'] = ColumnForm()
        saw = LastSeen.objects.filter(user=self.request.user, board=self.get_object())
        if saw:
            saw.update(seen=datetime.datetime.now())
        else:
            last_seen = LastSeen(
                user=self.request.user,
                board=self.get_object(),
                seen=datetime.datetime.now()
            )
            last_seen.save()
        print(saw)
        return context

    def post(self, request, *args, **kwargs):
        form = ColumnForm(request.POST)
        if form.is_valid():
            column = Column(
                name=form.cleaned_data['name'],
                board=self.get_object(),
            )
            column.save()
        return super().form_valid(form)


class UpdateBoardView(LockedView, generic.UpdateView):
    model = Board
    template_name = 'board/update_board.html'
    fields = ['title', 'background', 'members']

    def get_success_url(self):
        return reverse('board_detail', kwargs={'pk': self.get_object().id})


class BoardDeleteView(LockedView, generic.DeleteView):
    model = Board
    success_url = reverse_lazy('board_list')
    template_name = 'board/board_delete.html'


"""             CARD VIEWS         """


class CardMarkListView(LockedView, generic.ListView):
    model = Card
    template_name = 'card/card_mark_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(mark=self.kwargs['mark'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mark'] = self.mark.name
        return context


class CardListView(LockedView, generic.ListView):
    model = Card
    template_name = 'card/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.all().order_by('column')

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CardDetailView(LockedView, generic.FormView, generic.DetailView):
    model = Card
    context_object_name = 'card'
    template_name = 'card/card_detail.html'
    form_class = CommentForm
    success_url = '#'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(card=self.get_object()).order_by('-created_on')
        context['form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                text=form.cleaned_data['text'],
                card=self.get_object(),
                author=self.request.user
            )
            comment.save()
            
        return super().form_valid(form)


class CardCreateView(LockedView, generic.CreateView):
    model = Card
    fields = '__all__'
    template_name = 'card/card_create.html'
    context_object_name = 'card'
    success_url = reverse_lazy('board_list')


class CardUpdateView(LockedView, generic.UpdateView):
    model = Card
    form_class = CardForm
    success_url = reverse_lazy('card_list')
    template_name = 'card/card_update.html'


class CardDeleteView(LockedView, generic.DeleteView):
    model = Card
    success_url = reverse_lazy('card_list')
    template_name = 'card/card_delete.html'


"""             COLUMN VIEWS         """


class ColumnView(LockedView, generic.ListView):
    model = Column
    template_name = 'column/column_list.html'
    context_object_name = 'columns'


class ColumnDetailView(LockedView, generic.DetailView):
    model = Column
    template_name = 'column/column_detail.html'
    context_object_name = 'column'


class ColumnCreateView(LockedView, generic.CreateView):
    model = Column
    fields = '__all__'
    template_name = 'column/column_create.html'
    context_object_name = 'column'
    success_url = reverse_lazy('board_list')


class ColumnUpdateView(LockedView, generic.UpdateView):
    model = Column
    fields = ['name']
    template_name = 'column/column_update.html'

    def form_valid(self, form):
        form.instance.board = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('board_detail', kwargs={'pk': self.get_object().board.id})


class ColumnDeleteView(LockedView, generic.DeleteView):
    model = Column
    template_name = 'column/column_delete.html'

    def get_success_url(self):
        return reverse('board_detail', kwargs={'pk': self.get_object().board.id})


def search_by_user(request):
    form = SearchUserForm()
    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('user')
            users = User.objects.filter(email__icontains=title)

            return render(request, 'search_result.html', {'users': users[0]})

    return render(request, 'search.html', {'form': form})


def search_by_mark(request):
    form = SearchMarkForm()
    if request.method == 'POST':
        form = SearchMarkForm(request.POST)
        if form.is_valid():
            mark = form.cleaned_data.get('mark')
            marks = Card.objects.filter(mark__icontains=mark)

            return render(request, 'search_result1.html', {'cards': marks})

    return render(request, 'search.html', {'form': form})


"""             CHECKLIST VIEWS         """


class CheckListView(LockedView, generic.ListView):
    model = CheckList
    context_object_name = 'checklists'
    template_name = 'checklist/checklist_list.html'


class CheckListDetailView(LockedView, generic.DetailView):
    model = CheckList
    context_object_name = 'checklist'
    template_name = 'checklist/checklist_detail.html'


class ChecklistCreateView(LockedView, generic.CreateView):
    model = CheckList
    context_object_name = 'checklist'
    fields = '__all__'
    template_name = 'checklist/checklist_create.html'

    def get_success_url(self):
        return reverse('board_list')


class CheckListUpdateView(LockedView, generic.UpdateView):
    model = CheckList
    fields = '__all__'
    template_name = 'checklist/checklist_update.html'

    def get_success_url(self):
        return reverse('board_list')


class CheckListDeleteView(LockedView, generic.DeleteView):
    model = CheckList
    template_name = 'checklist/checklist_delete.html'

    def get_success_url(self):
        return reverse('board_list')


"""             MARK VIEWS         """


class MarkView(LockedView, generic.ListView):
    model = Mark
    context_object_name = 'marks'
    template_name = 'mark/mark_list.html'


class MarkDetailView(LockedView, generic.DetailView):
    model = Mark
    context_object_name = 'mark'
    template_name = 'mark/mark_detail.html'


class MarkCreateView(LockedView, generic.CreateView):
    model = Mark
    context_object_name = 'mark'
    fields = '__all__'
    template_name = 'mark/mark_create.html'

    def get_success_url(self):
        return reverse('board_list')


class MarkUpdateView(LockedView, generic.UpdateView):
    model = Mark
    context_object_name = 'mark'
    fields = '__all__'
    template_name = 'mark/mark_update.html'

    def get_success_url(self):
        return reverse('board_list')


class MarkDeleteView(LockedView, generic.DeleteView):
    model = Mark
    template_name = 'mark/mark_delete.html'

    def get_success_url(self):
        return reverse('board_list')


"""             FAVOURITE VIEWS         """


class FavouriteView(LockedView, generic.ListView):
    model = Favourite
    context_object_name = 'favourites'
    template_name = 'favourite/favourite_list.html'

    def get_queryset(self):
        user = self.request.user
        queryset = Favourite.objects.filter(author=user)
        return queryset


class FavouriteDetailView(LockedView, generic.DetailView):
    model = Favourite
    context_object_name = 'favourite'
    template_name = 'favourite/favourite_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get(**kwargs)
        context['columns'] = Column.objects.filter(board=self.get_object())
        return context


class FavouriteCreateView(LockedView, generic.CreateView):
    model = Favourite
    context_object_name = 'favourite'
    fields = ['board']
    template_name = 'favourite/favourite_create.html'
    success_url = reverse_lazy('favourite_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        product = self.get_form_kwargs()
        data = product.get('data')['board']

        if Favourite.objects.filter(board=data, author=self.request.user):
            return HttpResponse('You already have it in Favourites', content_type='text/plain')
        else:
            form = self.get_form()
            form.instance.author = self.request.user

            return super().form_valid(form)


class FavouriteUpdateView(LockedView, generic.UpdateView):
    model = Favourite
    context_object_name = 'favourite'
    fields = ['board']
    template_name = 'favourite/favourite_update.html'
    success_url = reverse_lazy('favourite_list')


class FavouriteDeleteView(LockedView, generic.DeleteView):
    model = Favourite
    success_url = reverse_lazy('favourite_list')
    template_name = 'favourite/favourite_delete.html'


"""             Archive VIEWS         """


class ArchiveView(LockedView, generic.ListView):
    model = Archive
    context_object_name = 'archives'
    template_name = 'archive/archive_list.html'


class ArchiveDetailView(LockedView, generic.DetailView):
    model = Archive
    context_object_name = 'archive'
    template_name = 'archive/archive_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get(**kwargs)
        context['columns'] = Column.objects.filter(board=self.get_object())
        return context


class ArchiveCreateView(LockedView, generic.CreateView):
    model = Archive
    context_object_name = 'archive'
    fields = ['board']
    template_name = 'archive/archive_create.html'
    success_url = reverse_lazy('archive_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArchiveUpdateView(LockedView, generic.UpdateView):
    model = Archive
    context_object_name = 'archive'
    fields = ['board']
    template_name = 'archive/archive_update.html'
    success_url = reverse_lazy('archive_list')


class ArchiveDeleteView(LockedView, generic.DeleteView):
    model = Archive
    success_url = reverse_lazy('archive_list')
    template_name = 'archive/archive_delete.html'


class LastSeenView(LockedView, generic.ListView):
    model = LastSeen
    template_name = 'board/last_seen_list.html'
    context_object_name = 'boards'

    def get_queryset(self):
        queryset = LastSeen.objects.filter(user=self.request.user,).order_by('-seen')
        return queryset
