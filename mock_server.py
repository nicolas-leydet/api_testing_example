from bottle import run, abort, route, request, response


products = {
    1: {
        'id': 1,
        'name': 'Nike Shoes',
        'description': 'The Nike LunarEpic Low Flyknit Running Shoe is '
                       'lightweight and breathable with targeted cushioning '
                       'for a soft, effortless sensation underfoot.',
        'price': 23.89,
    }
}

indecies = {'product': 2}


@route('/product/<product_id:int>')
def get_product(product_id):
    try:
        return products[product_id]
    except KeyError:
        abort(404, 'product unknown')


@route('/product', method='POST')
def post_product():
    data = request.json
    if data is None:
        abort(400, 'invalid json')

    if data.get('price', 0) < 0:
        abort(400, 'price cannot be negative')

    data['id'] = indecies['product']
    products[indecies['product']] = data
    indecies['product'] += 1

    response.status = 201
    return data


@route('/product/<product_id:int>', method='PATCH')
def patch_product(product_id):
    try:
        product = products[product_id]
    except KeyError:
        abort(404, 'product unknown')

    patch = request.json
    if patch is None:
        abort(400, 'invalid json')

    if patch.get('price', 0) < 0:
        abort(400, 'price cannot be negative')

    if 'id' in patch:
        abort(404, 'id cannot be patched')

    product.update(patch)

    return product


@route('/product/<product_id:int>', method='DELETE')
def delete_product(product_id):
    abort(404, 'method not allowed')


run(host='localhost', port=8080, debug=True)
