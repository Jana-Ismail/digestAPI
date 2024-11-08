from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import BookReview, Book
from .books import BookSerializer

class ReviewSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    book = BookSerializer(many=False)

    class Meta:
        model = BookReview
        fields = ['id', 'book', 'user', 'rating', 'comment', 'created', 'is_owner']
        read_only_fields = ['user']

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context['request'].user == obj.user


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request):
        # Get all reviews
        reviews = BookReview.objects.all()
        # Serialize the objects, and pass request to determine owner
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})

        # Return the serialized data with 200 status code
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        # Create a new instance of a review and assign property
        # values from the request payload using `request.data`
        book_id = request.data.get("book_id")
        # book = Book.objects.get(pk=book_id)

        review = BookReview.objects.create(
            book_id = book_id,
            user = request.auth.user,
            rating = request.data.get("rating"),
            comment = request.data.get("comment")
        )

        # Save the review
        # review.save()
        try:
            # Serialize the objects, and pass request as context
            serializer = ReviewSerializer(review, many=False, context={'request': request})
            # Return the serialized data with 201 status code
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            # Get the requested review
            review = BookReview.objects.get(pk=pk)
            # Serialize the object (make sure to pass the request as context)
            serializer = ReviewSerializer(review, many=False, context={'request': request})
            # Return the review with 200 status code
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BookReview.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            # Get the requested review
            review = BookReview.objects.get(pk=pk)

            # Check if the user has permission to delete
            # Will return 403 if authenticated user is not author
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except BookReview.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)