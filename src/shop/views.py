

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView, CreateView, ListView
from shop.models import Review, Product
from shop.forms import ReviewForm
from django.contrib import messages
from django.core.paginator import Paginator


class CommentCreateView(CreateView):
    """
    Представление: для создания отзыва к продукту.
    """

    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        review = form.save(commit=False)
        review.product_id = self.kwargs.get('pk')
        review.author = self.request.user
        review.save()
        return redirect(review.product.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            #login_url = reverse('login')
            message = f"<p>Необходимо авторизоваться для добавления комментариев</p>"\
                      "<a href='{login_url}'>авторизоваться</a>"
            messages.info(request, mark_safe(message))
            return redirect(reverse(
                viewname='shop:product_detail',
                kwargs={'pk': self.kwargs.get('pk')}
            ))
        else:
            return super().dispatch(request, *args, **kwargs)


# class ReviewListView(ListView):
#     model = Review
#     template_name = 'shop/comments/comments.html'
#     context_object_name = 'reviews'
#     queryset = Review.objects.select_related('product').all()


class ProductDetailView(DetailView):
    model = Product

    template_name = 'shop/product.html'
    context_object_name = 'product'
    queryset = Product.objects.all()
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = self.object.reviews.all()

        # Определите количество элементов на странице и текущую страницу
        items_per_page = 3
        page_number = self.request.GET.get('page')

        # Создайте объект пагинации
        paginator = Paginator(reviews, items_per_page)

        # Получите страницу отзывов
        page_obj = paginator.get_page(page_number)

        # Добавьте объект пагинации в контекст
        context['page_obj'] = page_obj
        context['form'] = ReviewForm()
        return context

