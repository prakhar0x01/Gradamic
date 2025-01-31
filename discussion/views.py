from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Comment
from django.contrib import messages
from .forms import CommentForm, TopicForm
from django.contrib.auth.decorators import login_required
from django.utils.html import escape


def topic_list(request):
    topics = Topic.objects.filter(is_approved=True).order_by('-stars')
    return render(request, 'discussion_list.html', {'topics': topics})


@login_required
def topic_detail(request, uuid):
    topic = get_object_or_404(Topic, uuid=uuid)
    return render(request, 'discussion_detail.html', {'topic': topic})

@login_required
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            # Escape special characters in content
            topic.content = escape(form.cleaned_data['content'])
            topic.save()
            return redirect('topic_list')
    else:
        form = TopicForm()
    
    return render(request, 'discussion_list.html', {'form': form})


@login_required
def add_comment(request, uuid):
    topic = get_object_or_404(Topic, uuid=uuid)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.topic = topic
            # Escape special characters in content
            comment.content = escape(form.cleaned_data['content'])
            comment.save()
            return redirect('topic_detail', uuid=uuid)
        else:
            messages.error(request, 'Failed to add comment. Please correct the errors.')
    else:
        form = CommentForm()
    
    return render(request, 'discussion_detail.html', {'topic': topic, 'form': form})



@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        # Remove the user from dislikes if they are changing their vote
        if request.user in comment.dislikes.all():
            comment.dislikes.remove(request.user)
    return redirect('topic_detail', uuid=comment.topic.uuid)


@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        # Remove the user from likes if they are changing their vote
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
    return redirect('topic_detail', uuid=comment.topic.uuid)



@login_required
def add_star(request, topic_uuid):
    topic = get_object_or_404(Topic, uuid=topic_uuid)
    topic.add_star(request.user)
    return redirect('topic_detail', uuid=topic_uuid)


@login_required
def remove_star(request, topic_uuid):
    topic = get_object_or_404(Topic, uuid=topic_uuid)
    topic.remove_star(request.user)
    return redirect('topic_detail', uuid=topic_uuid)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Check if the user has permission to edit the comment
    if comment.author != request.user:
        # You may want to return a 403 Forbidden response or redirect to an error page
        messages.warning(request, "Unauthorize attempt.")
        return redirect('topic_list')
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('topic_detail', uuid=comment.topic.uuid)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})



@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Check if the user has permission to delete the comment
    if comment.author != request.user:
        # You may want to return a 403 Forbidden response or redirect to an error page
        messages.warning(request, "Unauthorize attempt.")
        return redirect('topic_list')
    
    if request.method == 'POST':
        topic_uuid = comment.topic.uuid
        comment.delete()
        return redirect('topic_detail', uuid=topic_uuid)
    return render(request, 'delete_comment.html', {'comment': comment})