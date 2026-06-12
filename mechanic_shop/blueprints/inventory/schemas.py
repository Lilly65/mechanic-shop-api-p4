from mechanic_shop import ma, db
from mechanic_shop.models.schemas import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        sqla_session = db.session

inventory_schema  = InventorySchema()
inventories_schema = InventorySchema(many=True)