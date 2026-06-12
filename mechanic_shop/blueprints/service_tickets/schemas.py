from mechanic_shop import ma, db
from mechanic_shop.models.schemas import ServiceTicket
from marshmallow import fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        sqla_session = db.session
        include_fk = True

    # Returns only the id of each mechanic rather than the full mechanic object,
    # keeping the response lightweight while still showing who is assigned.
    mechanic_ids = fields.Method('get_mechanic_ids')

    # Returns the full details of each inventory part associated with the ticket
    # since part name and price are useful context alongside the ticket information.
    parts = fields.Method('get_parts')

    def get_mechanic_ids(self, obj):
        return [mechanic.id for mechanic in obj.mechanics]

    def get_parts(self, obj):
        return [
            {
                'id':    part.id,
                'name':  part.name,
                'price': part.price
            }
            for part in obj.parts
        ]

service_ticket_schema  = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)