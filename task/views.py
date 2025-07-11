from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages

@login_required
def task_lists(request):
    status_filter = request.GET.get('status', 'all') # status_filter teke 'all' na ashle amra 2ta status pabo  - 1.pending, 2.completed
    category_filter = request.GET.get('category', 'all')
    tasks = Task.objects.filter(user = request.user)
    if status_filter != 'all':
        tasks = tasks.filter(is_completed = (status_filter == 'completed'))
    if category_filter != 'all':
        tasks = tasks.filter(category = category_filter)

    completed_tasks = tasks.filter(is_completed = True)
    pending_tasks = tasks.filter(is_completed = False)

    return render(request, 'task_lists.html', {
        'completed_tasks' : completed_tasks,
        'pending_task' : pending_tasks,
        'status_filter' : status_filter,
        'category_filter' : category_filter,
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('task_lists')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form' : form })

@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('task_lists')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form, 'edit': True})


@login_required
def task_details(request, task_id):
    task = get_object_or_404(Task, id = task_id, user = request.user)
    return render(request, 'task_details.html', {'task' : task})

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id = task_id, user = request.user)
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect('task_lists')

@login_required
def task_mark_completed(request, task_id):
    task = get_object_or_404(Task, id = task_id, user = request.user)
    task.is_completed = True
    task.save()
    messages.success(request, "Task mark completed successfully!")
    return redirect('task_lists')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # user created and saved in the db
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username =  username, password = password)
            login(request, user)
            messages.success(request, 'Account Created Successfully')
            return redirect('task_lists')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form' : form})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username.capitalize()}!")
        return super().form_valid(form)
