from flask import request, jsonify
from mechanic_shop import db, limiter, cache
from mechanic_shop.models.schemas import Mechanic
from mechanic_shop.blueprints.mechanics import mechanics_bp
from mechanic_shop.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from sqlalchemy import func


@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
def create_mechanic():
    """
    Create a new mechanic
    ---
    tags:
      - Mechanics
    parameters:
      - in: body
        name: body
        required: true
        description: Mechanic data
        schema:
          $ref: '#/definitions/MechanicInput'
    responses:
      201:
        description: Mechanic created successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
        examples:
          application/json:
            id: 1
            name: John Smith
            email: john@mechanicshop.com
            phone: 555-6789
            salary: 55000.0
      400:
        description: Validation error
    definitions:
      MechanicInput:
        type: object
        required:
          - name
          - email
          - phone
          - salary
        properties:
          name:
            type: string
            example: John Smith
          email:
            type: string
            example: john@mechanicshop.com
          phone:
            type: string
            example: 555-6789
          salary:
            type: number
            example: 55000.00
      MechanicResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
            example: John Smith
          email:
            type: string
            example: john@mechanicshop.com
          phone:
            type: string
            example: 555-6789
          salary:
            type: number
            example: 55000.0
    """
    # Rate limiting is applied here to prevent bulk creation of mechanic records,
    # which should be an infrequent operation performed only by administrators.
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    new_mechanic = Mechanic(
        name=mechanic_data['name'],
        email=mechanic_data['email'],
        phone=mechanic_data['phone'],
        salary=mechanic_data['salary']
    )
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    """
    Retrieve all mechanics
    ---
    tags:
      - Mechanics
    responses:
      200:
        description: List of all mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
        examples:
          application/json:
            - id: 1
              name: John Smith
              email: john@mechanicshop.com
              phone: 555-6789
              salary: 55000.0
    """
    # Caching is applied here because the mechanics list changes infrequently
    # and serving a cached response reduces unnecessary database queries.
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    """
    Update an existing mechanic by ID
    ---
    tags:
      - Mechanics
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the mechanic to update
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicInput'
    responses:
      200:
        description: Mechanic updated successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    mechanic.name   = mechanic_data['name']
    mechanic.email  = mechanic_data['email']
    mechanic.phone  = mechanic_data['phone']
    mechanic.salary = mechanic_data['salary']
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    """
    Delete a mechanic by ID
    ---
    tags:
      - Mechanics
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the mechanic to delete
    responses:
      200:
        description: Mechanic deleted successfully
        examples:
          application/json:
            message: Mechanic 1 deleted successfully
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted successfully"}), 200


@mechanics_bp.route('/most-tickets', methods=['GET'])
def most_tickets():
    """
    Retrieve mechanics ordered by number of service tickets worked on
    ---
    tags:
      - Mechanics
    responses:
      200:
        description: Mechanics sorted from most to least tickets worked
        examples:
          application/json:
            - id: 1
              name: John Smith
              email: john@mechanicshop.com
              phone: 555-6789
              salary: 55000.0
              ticket_count: 4
    """
    # Join mechanics to the service_mechanics junction table directly,
    # count the junction rows per mechanic, and order by that count descending.
    # Joining through the junction table explicitly avoids the cartesian product
    # that occurs when joining through the relationship attribute.
    from mechanic_shop.models.schemas import service_mechanics

    results = (
        db.session.query(Mechanic, func.count(service_mechanics.c.ticket_id).label('ticket_count'))
        .join(service_mechanics, Mechanic.id == service_mechanics.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(service_mechanics.c.ticket_id).desc())
        .all()
    )

    output = []
    for mechanic, count in results:
        mechanic_data                 = mechanic_schema.dump(mechanic)
        mechanic_data['ticket_count'] = count
        output.append(mechanic_data)

    return jsonify(output), 200