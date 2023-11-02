from marshmallow import validate
from marshmallow import fields
from marshmallow import Schema
from marshmallow.decorators import post_load

from techtest.articles.models import Article
from techtest.regions.models import Region
from techtest.authors.models import Author
from techtest.regions.schemas import RegionSchema
from techtest.authors.schemas import AuthorSchema


class ArticleSchema(Schema):
    class Meta(object):
        model = Article

    id = fields.Integer()
    title = fields.String(validate=validate.Length(max=255))
    content = fields.String()
    regions = fields.Method(
        required=False, serialize="get_regions", deserialize="load_regions"
    )
    author = fields.Method(
        required=False, serialize="get_author", deserialize="load_author"
    )

    def get_regions(self, article):
        return RegionSchema().dump(article.regions.all(), many=True)

    def load_regions(self, regions):
        return [
            Region.objects.get_or_create(
                id=region.pop("id", None), defaults=region)[0]
            for region in regions
        ]

    def get_author(self, article):
        return AuthorSchema().dump(article.author)

    def load_author(self, author):
        return Author.objects.get_or_create(id=author.pop("id", None), defaults=author)[0]

    @post_load
    def update_or_create(self, data, *args, **kwargs):
        regions = data.pop("regions", None)
        author = data.pop("author", None)

        article, _ = Article.objects.update_or_create(
            id=data.pop("id", None), defaults=data
        )
        if isinstance(regions, list):
            article.regions.set(regions)

        if author:
            article.author = author
            article.save()
        else:
            article.author = None
            article.save()

        return article
