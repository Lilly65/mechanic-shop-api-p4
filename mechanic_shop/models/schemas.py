from mechanic_shop import db

# Junction table linking service tickets to mechanics (many-to-many)
service_mechanics = db.Table(
    'service_mechanics',
    db.Column('ticket_id',   db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'),       primary_key=True)
)

# Junction table linking service tickets to inventory parts (many-to-many).
# One ticket can use many parts, and the same part can appear on many tickets.
service_inventory = db.Table(
    'service_inventory',
    db.Column('ticket_id',    db.Integer, db.ForeignKey('service_tickets.id'),  primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'),         primary_key=True)
)


class Customer(db.Model):
    __tablename__ = 'customers'

    id       = db.Column(db.Integer,     primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(100), nullable=False)
    phone    = db.Column(db.String(20),  nullable=False)
    password = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship('ServiceTicket', back_populates='customer')


class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'

    id           = db.Column(db.Integer,     primary_key=True)
    VIN          = db.Column(db.String(17),  nullable=False)
    service_date = db.Column(db.String(20),  nullable=False)
    service_desc = db.Column(db.String(255), nullable=False)
    customer_id  = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    customer  = db.relationship('Customer',  back_populates='service_tickets')
    mechanics = db.relationship('Mechanic',   secondary=service_mechanics, back_populates='service_tickets')
    parts     = db.relationship('Inventory',  secondary=service_inventory,  back_populates='service_tickets')


class Mechanic(db.Model):
    __tablename__ = 'mechanics'

    id     = db.Column(db.Integer,     primary_key=True)
    name   = db.Column(db.String(100), nullable=False)
    email  = db.Column(db.String(100), nullable=False)
    phone  = db.Column(db.String(20),  nullable=False)
    salary = db.Column(db.Float,       nullable=False)

    service_tickets = db.relationship('ServiceTicket', secondary=service_mechanics, back_populates='mechanics')


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id    = db.Column(db.Integer,     primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float,       nullable=False)

    service_tickets = db.relationship('ServiceTicket', secondary=service_inventory, back_populates='parts')