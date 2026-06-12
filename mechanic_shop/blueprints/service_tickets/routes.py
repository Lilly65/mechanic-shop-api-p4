from flask import request, jsonify
from mechanic_shop import db
from mechanic_shop.models.schemas import ServiceTicket, Mechanic, Inventory
from mechanic_shop.blueprints.service_tickets import service_tickets_bp
from mechanic_shop.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema


@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    """
    Create a new service ticket
    ---
    tags:
      - Service Tickets
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ServiceTicketInput'
    responses:
      201:
        description: Service ticket created successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
        examples:
          application/json:
            id: 1
            VIN: 1HGBH41JXMN109186
            service_date: 2026-05-22
            service_desc: Oil change and tire rotation
            customer_id: 1
            mechanic_ids: []
            parts: []
      400:
        description: Validation error
    definitions:
      ServiceTicketInput:
        type: object
        required:
          - VIN
          - service_date
          - service_desc
          - customer_id
        properties:
          VIN:
            type: string
            example: 1HGBH41JXMN109186
          service_date:
            type: string
            example: 2026-05-22
          service_desc:
            type: string
            example: Oil change and tire rotation
          customer_id:
            type: integer
            example: 1
      ServiceTicketResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          VIN:
            type: string
            example: 1HGBH41JXMN109186
          service_date:
            type: string
            example: 2026-05-22
          service_desc:
            type: string
            example: Oil change and tire rotation
          customer_id:
            type: integer
            example: 1
          mechanic_ids:
            type: array
            items:
              type: integer
            example: [1, 2]
          parts:
            type: array
            items:
              type: object
            example: [{id: 1, name: Oil Filter, price: 12.99}]
    """
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    new_ticket = ServiceTicket(
        VIN=ticket_data['VIN'],
        service_date=ticket_data['service_date'],
        service_desc=ticket_data['service_desc'],
        customer_id=ticket_data['customer_id']
    )
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201


@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    """
    Retrieve all service tickets
    ---
    tags:
      - Service Tickets
    responses:
      200:
        description: List of all service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicketResponse'
    """
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200


@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    """
    Assign a mechanic to a service ticket
    ---
    tags:
      - Service Tickets
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: The ID of the service ticket
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: The ID of the mechanic to assign
    responses:
      200:
        description: Mechanic assigned successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Mechanic already assigned to this ticket
      404:
        description: Ticket or mechanic not found
    """
    ticket   = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or Mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to this ticket"}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    """
    Remove a mechanic from a service ticket
    ---
    tags:
      - Service Tickets
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: The ID of the service ticket
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: The ID of the mechanic to remove
    responses:
      200:
        description: Mechanic removed successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Mechanic is not assigned to this ticket
      404:
        description: Ticket or mechanic not found
    """
    ticket   = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or Mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned to this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_service_ticket(ticket_id):
    """
    Add and remove multiple mechanics from a service ticket in one request
    ---
    tags:
      - Service Tickets
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: The ID of the service ticket to edit
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/TicketEditInput'
    responses:
      200:
        description: Ticket updated successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      404:
        description: Ticket not found
    definitions:
      TicketEditInput:
        type: object
        properties:
          add_ids:
            type: array
            items:
              type: integer
            example: [1, 2]
          remove_ids:
            type: array
            items:
              type: integer
            example: [3]
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data       = request.json
    add_ids    = data.get('add_ids', [])
    remove_ids = data.get('remove_ids', [])

    # Remove mechanics first to avoid conflicts before adding new ones
    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['PUT'])
def add_part_to_ticket(ticket_id, inventory_id):
    """
    Add an inventory part to a service ticket
    ---
    tags:
      - Service Tickets
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: The ID of the service ticket
      - in: path
        name: inventory_id
        type: integer
        required: true
        description: The ID of the inventory part to add
    responses:
      200:
        description: Part added to ticket successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Part already added to this ticket
      404:
        description: Ticket or part not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    part   = db.session.get(Inventory, inventory_id)

    if not ticket or not part:
        return jsonify({"error": "Ticket or part not found"}), 404

    if part in ticket.parts:
        return jsonify({"message": "Part already added to this ticket"}), 400

    # Append the part to the ticket's parts list.
    # SQLAlchemy handles the insert into the service_inventory junction table automatically.
    ticket.parts.append(part)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200