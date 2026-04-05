from rest_framework import generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document, DocumentCategory
from .serializers import DocumentSerializer, DocumentCategorySerializer


class DocumentListAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        qs = Document.objects.select_related('category', 'uploaded_by')
        if self.request.user.role == 'citizen':
            qs = qs.filter(is_public=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class DocumentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentCategoryListAPIView(generics.ListAPIView):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
