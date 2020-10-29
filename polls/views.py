from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question, Vote
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
import logging.config

from .settings import LOGGING



logging.config.dictConfig(LOGGING)
logs = logging.getLogger("polls")

def get_client_ip(request):
    """ Get the client's ip"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def user_in_logging(sender, request, user, **kwargs):
    logs.info(f'username: {user.username} ip: {get_client_ip(request)} login')

@receiver(user_logged_out)
def user_out_logging(sender, request, user, **kwargs):
    logs.info(f'username: {user.username} ip: {get_client_ip(request)} logout')

@receiver(user_login_failed)
def user_failed_in_logging(sender, request, credentials, **kwargs):
    logs.warning(f'username: {request.POST["username"]} ip: {get_client_ip(request)} fail login')


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, **kwargs):
        try:
            question = Question.objects.get(pk=kwargs['pk'])
            if not question.can_vote():
                return HttpResponseRedirect(reverse('polls:index'), messages.error(request, "poll is closed"))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('polls:index'), messages.error(request, "poll is not exist."))
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(object=self.get_object()))

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    if not question.can_vote():
        return HttpResponseRedirect(reverse('polls:index'))
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        Vote.objects.update_or_create(user=user, question=question, defaults={'choice': selected_choice})
        question.previous_choice = str(user.vote_set.get(question=question).choice)
        question.save()
        for choice in question.choice_set.all():
            choice.votes = Vote.objects.filter(question=question).filter(choice=choice).count()
            choice.save()
        logs.info(f'username: {user.username} ip: {get_client_ip(request)} vote on question id: {question_id}')
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
