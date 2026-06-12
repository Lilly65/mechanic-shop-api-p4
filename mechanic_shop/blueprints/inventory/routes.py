from flask import request, jsonify
from mechanic_shop import db
from mechanic_shop.models.schemas import Inventory
from mechanic_shop.blueprints.inventory import inventory_bp
from mechanic_shop.blueprints.inventory.schemas import inventory_schema, inventories_schema


@inventory_bp.route('/', methods=['POST'])
def create_part():
    """
    Add a new part to inventory
    ---
    tags:
      - Inventory
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryInput'
    responses:
      201:
        description: Part created successfully
        schema:
          $ref: '#/definitions/InventoryResponse'
        examples:
          application/json:
            id: 1
            name: Oil Filter
            price: 12.99
      400:
        description: Validation error
    definitions:
      InventoryInput:
        type: object
        required:
          - name
          - price
        properties:
          name:
            type: string
            example: Oil Filter
          price:
            type: number
            example: 12.99
      InventoryResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
            example: Oil Filter
          price:
            type: number
            example: 12.99
    """
    try:
        part_data = inventory_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    new_part = Inventory(
        name=part_data['name'],
        price=part_data['price']
    )
    db.session.add(new_part)
    db.session.commit()
    return inventory_schema.jsonify(new_part), 201


@inventory_bp.route('/', methods=['GET'])
def get_parts():
    """
    Retrieve all inventory parts
    ---
    tags:
      - Inventory
    responses:
      200:
        description: List of all parts
        schema:
          type: array
          items:
            $ref: '#/definitions/InventoryResponse'
        examples:
          application/json:
            - id: 1
              name: Oil Filter
              price: 12.99
    """
    parts = Inventory.query.all()
    return inventories_schema.jsonify(parts), 200


@inventory_bp.route('/<int:id>', methods=['PUT'])
def update_part(id):
    """
    Update an existing inventory part by ID
    ---
    tags:
      - Inventory
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the part to update
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryInput'
    responses:
      200:
        description: Part updated successfully
        schema:
          $ref: '#/definitions/InventoryResponse'
      404:
        description: Part not found
    """
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    try:
        part_data = inventory_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    part.name  = part_data['name']
    part.price = part_data['price']
    db.session.commit()
    return inventory_schema.jsonify(part), 200


@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_part(id):
    """
    Delete an inventory part by ID
    ---
    tags:
      - Inventory
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the part to delete
    responses:
      200:
        description: Part deleted successfully
        examples:
          application/json:
            message: Part 1 deleted successfully
      404:
        description: Part not found
    """
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part {id} deleted successfully"}), 200