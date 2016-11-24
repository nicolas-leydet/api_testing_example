import pytest

multitest = pytest.mark.parametrize


@pytest.fixture
def existing_product():
    return {
        'id': 1,
        'name': 'Nike Shoes',
        'description': 'The Nike LunarEpic Low Flyknit Running Shoe is '
                       'lightweight and breathable with targeted cushioning '
                       'for a soft, effortless sensation underfoot.',
        'price': 23.89,
    }


@pytest.fixture
def new_product():
    return {
        'name': 'dead parrot',
        'description': 'Norwegian Blue',
        'price': 9.99,
    }


def test_get_existing_product(http, existing_product):
    '''
    GETing product with id=1 returns `existing_product`
    '''
    response = http('GET /product/1')
    assert response.status_code == 200
    assert response.json() == existing_product


def test_get_unknown_product(http):
    '''
    GETing a product that doesn't exist returns a 404.
    '''
    response = http('GET /product/111')
    assert response.status_code == 404


def test_post_product(http, new_product):
    '''
    POSTing a product should return the JSON product data with its new id.
    '''
    response = http('POST /product', json=new_product)
    assert response.status_code == 201  # assumed (was not specified)

    product = response.json()
    assert product == update(new_product, {'id': product['id']})


def test_patch_product(http, existing_product):
    '''
    PATCHing is used to update the fields of a product.
    '''
    response = http('PATCH /product/1', json={'price': 22})
    assert response.status_code == 200
    assert update(existing_product, {'price': 22}) == response.json()


def test_patch_product_id_error(http):
    '''
    PATCHing a product's id results in a 404.
    '''
    response = http('PATCH /product/1', json={'id': 2})
    assert response.status_code == 404


def test_patch_unknown_product(http):
    '''
    PATCHing a product which doesn't exist returns a 404.
    '''
    response = http('PATCH /product/111', json={'name': 'blue table'})
    assert response.status_code == 404


def test_post_with_negative_price_error(http, new_product):
    '''
    POSTing a product with a negative price returns a 400.
    '''
    response = http('POST /product', json=update(new_product, {'price': -42}))
    assert response.status_code == 400


def test_patch_with_negative_price_error(http, new_product):
    '''
    PATCHing a product with a negative price returns a 400.
    '''
    response = http('PATCH /product/1',
                    json=update(new_product, {'price': -42}))
    assert response.status_code == 400


def test_delete_product_error(http):
    '''
    DELETing requests are not supported and should return a 404.
    '''
    response = http('DELETE /product/1')
    assert response.status_code == 404  # Maybe it should be 405


# assumed behavior
@multitest('path', ['PATCH /product/1', 'POST /product'])
@multitest('invalid_json', ['', 'text', '{"name": fruit}'])
def test_invalid_payload(http, path, invalid_json):
    '''
    Request with an invalid json payload should return a 400
    '''
    response = http(path, data=invalid_json)
    assert response.status_code == 400


# Behavior not covered by the test server
def test_scenario_post_get(http, new_product):
    '''
    A POSTed product should be retreivable with a GET.
    '''
    response = http('POST /product', json=new_product)
    product = response.json()
    response = http('GET /product/{}'.format(product['id']))
    assert response.json() == product


def test_scenario_patch_get(http, new_product):
    '''
    A PATCHed product should be retreivable with a GET.
    '''
    response = http('POST /product', json=new_product)
    product = response.json()
    http('PATCH /product/{}'.format(product['id']), json={'price': 2})
    response = http('GET /product/{}'.format(product['id']))
    assert response.json() == update(product, {'price': 2})


def test_scenario_invalid_patch_get(http, new_product):
    '''
    A failed PATCHed request should not change a product
    '''
    response = http('POST /product', json=new_product)
    product = response.json()
    http('PATCH /product/{}'.format(product['id']),
         json={'price': -1, 'name': 'shoe'})  # should not effect anything
    response = http('GET /product/{}'.format(product['id']))
    assert response.json() == new_product


def update(dictionnary, update_with):
    '''
    Inlined dictionnary update
    '''
    dictionnary.update(update_with)
    return dictionnary
