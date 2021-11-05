from flask_restful import Resource
from Application.flask_imports import request
from Application.database.models import Comments

class CommentsApi(Resource):
    def get(self, id):
        return list(Comments.get_product_comments(id))

    def post(self, id):
        comment = request.json["comment"]
        product_id = request.json["productId"]
        Comments()(comment=comment,product_id=product_id,customer_id=id)

        return list(Comments.get_product_comments(product_id))