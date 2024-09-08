from django.shortcuts import render
from django.http import Http404
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Post
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail

@require_POST 
def post_comment(request, post_id):
   post=get_object_or_404( Post, id=post_id, status=Post.Status.PUBLISHED)
   comment=None #a comment was posted
   form=CommentForm(data=request.POST)

   if form.is_valid(): #create comment object without saving it to the database
      comment=form.save(comment=False) #Assign the post to the comment
      comment.post =post #Save the comment to the database
      comment.save()
      #The save() method is available for ModelForm but not for Form instances since they are not linked to any model.
      return render(request, 'blog/post/comment.html',{'post':post, 'form': form, 'comment':comment} )


class PostListView(ListView):
   queryset=Post.published.all() 
   context_object_name='posts'
   paginate_by=3
   template_name= 'list.html'


def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)  # Show 3 posts per page
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {
        'posts': posts,
        'paginator': paginator,  # Include paginator for additional pagination info if needed
        'page': posts  # This can be used if you want to access current page info
    })

def post_detail(request, year, month, day, post):
    post=get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED, slug=post,publish_year=year, publish_month=month,publish_day=day)
    comments=post.comments.filter(active=True)
    form= CommentForm()

    return render(request, 'detail.html', {'post': post, 'comments':comments, 'form':form} )

def post_share(request, post_id):
   post=get_object_or_404(Post, id=post_id,status=Post.Status.PUBLISHED)
   sent= False
   if request.method == 'POST':
      form= EmailPostForm(request.POST)
   if form.is_valid():
      cd= form.cleaned_data
      post_url=request.build_absolute_uri( post.get_absolute_url())
      subject=(f"{cd['name']} ({cd['email']})" f"recommends you read{post.title}")
      message=(f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}")
      send_mail(subject=subject, message=message, from_email=None, recipient_list=[cd['to']] )
      sent=True
   else:
      form = EmailPostForm()
      return render( request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent} )
