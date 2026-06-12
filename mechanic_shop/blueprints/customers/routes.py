from flask import request, jsonify
from mechanic_shop import db, limiter, cache
from mechanic_shop.models.schemas import Customer, ServiceTicket
from mechanic_shop.blueprints.customers import customers_bp
from mechanic_shop.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from mechanic_shop.utils import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash


@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: body
        description: Customer data required to create a new account
        required: true
        schema:
          $ref: '#/definitions/CustomerInput'
    responses:
      201:
        description: Customer created successfully
        schema:
          $ref: '#/definitions/CustomerResponse'
        examples:
          application/json:
            id: 1
            name: Jane Doe
            email: jane@example.com
            phone: 555-1234
      400:
        description: Validation error - missing or invalid fields
    definitions:
      CustomerInput:
        type: object
        required:
          - name
          - email
          - phone
          - password
        properties:
          name:
            type: string
            example: Jane Doe
          email:
            type: string
            example: jane@example.com
          phone:
            type: string
            example: 555-1234
          password:
            type: string
            example: securepassword123
      CustomerResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
            example: Jane Doe
          email:
            type: string
            example: jane@example.com
          phone:
            type: string
            example: 555-1234
    """
    try:
        customer_data = customer_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    new_customer = Customer(
        name=customer_data['name'],
        email=customer_data['email'],
        phone=customer_data['phone'],
        password=generate_password_hash(customer_data['password'])
    )
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


@customers_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a customer and receive a JWT token
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: body
        description: Customer email and password
        required: true
        schema:
          $ref: '#/definitions/LoginInput'
    responses:
      200:
        description: Login successful, token returned
        examples:
          application/json:
            token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
            message: Login successful
      401:
        description: Invalid email or password
    definitions:
      LoginInput:
        type: object
        required:
          - email
          - password
        properties:
          email:
            type: string
            example: jane@example.com
          password:
            type: string
            example: securepassword123
    """
    try:
        login_data = login_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    customer = Customer.query.filter_by(email=login_data['email']).first()

    if not customer or not check_password_hash(customer.password, login_data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token, "message": "Login successful"}), 200


@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_customers():
    """
    Retrieve a paginated list of all customers
    ---
    tags:
      - Customers
    parameters:
      - in: query
        name: page
        type: integer
        description: Page number to retrieve
        default: 1
      - in: query
        name: per_page
        type: integer
        description: Number of customers per page
        default: 10
    responses:
      200:
        description: Paginated list of customers
        examples:
          application/json:
            customers:
              - id: 1
                name: Jane Doe
                email: jane@example.com
                phone: 555-1234
            total: 1
            pages: 1
            current_page: 1
    """
    # Page number defaults to 1 if not provided in the query string.
    # Per_page controls how many results appear per page, defaulting to 10.
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    paginated = Customer.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "customers":    customers_schema.dump(paginated.items),
        "total":        paginated.total,
        "pages":        paginated.pages,
        "current_page": paginated.page
    }), 200


@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    """
    Retrieve a single customer by ID
    ---
    tags:
      - Customers
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the customer to retrieve
    responses:
      200:
        description: Customer found
        schema:
          $ref: '#/definitions/CustomerResponse'
        examples:
          application/json:
            id: 1
            name: Jane Doe
            email: jane@example.com
            phone: 555-1234
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return customer_schema.jsonify(customer), 200


@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Retrieve all service tickets belonging to the logged-in customer
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    responses:
      200:
        description: List of service tickets for the authenticated customer
        examples:
          application/json:
            - id: 1
              VIN: 1HGBH41JXMN109186
              service_date: 2026-05-22
              service_desc: Oil change
              customer_id: 1
              mechanic_ids: [1]
              parts: []
      401:
        description: Token is missing or invalid
    """
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    from mechanic_shop.blueprints.service_tickets.schemas import service_tickets_schema
    return service_tickets_schema.jsonify(tickets), 200


@customers_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_customer(customer_id, id):
    """
    Update an existing customer - requires authentication
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the customer to update
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerInput'
    responses:
      200:
        description: Customer updated successfully
        schema:
          $ref: '#/definitions/CustomerResponse'
      401:
        description: Token is missing or invalid
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    customer.name     = customer_data['name']
    customer.email    = customer_data['email']
    customer.phone    = customer_data['phone']
    customer.password = generate_password_hash(customer_data['password'])
    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customers_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id, id):
    """
    Delete a customer by ID - requires authentication
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the customer to delete
    responses:
      200:
        description: Customer deleted successfully
        examples:
          application/json:
            message: Customer 1 deleted successfully
      401:
        description: Token is missing or invalid
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} deleted successfully"}), 200